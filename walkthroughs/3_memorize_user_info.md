# Eddie -- Memorize User Information

Although we've added chat history, this history only persists for the current conversation. This means that if I tell Eddie that my name is William, Eddie won't remember my name the next time I boot up the chat. Let's fix this by using tools to allow Eddie to decide to memorize information about the user.

## `Memorize` tool (function calling)

With Mirascope, we can provide Eddie with a tool for memorizing information just by writing a function. By giving Eddie access to this function, we're letting Eddie decide when to call the tool. This means that Eddie won't call the tool and will just respond normally if Eddie deems there's nothing worth remembering.

The function we'll write for Eddie will save the memory to a pickled array of memories and return the memory. We need to return the memory so that we can also live update Eddie's internal loaded memory.

```python
import os
import pickle as pkl
from pathlib import Path

from typer import get_app_dir


def load_memories() -> list[str]:
    """Loads Eddie's memories."""
    app_dir = Path(get_app_dir("eddie-cli"))
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    filepath = app_dir / "memories.pkl"
    if not os.path.exists(filepath):
        with filepath.open(mode="wb") as f:
            pkl.dump([], f)
    with filepath.open(mode="rb") as f:
        return pkl.load(f)


def memorize(memory: str) -> list[str]:
    """Saves the `memory` and returns the list of all memories.

    Args:
        memory: A memory synthesized from a user's input. This should just be a single
            sentence describing what should be memorized. For example, you might want
            to save something like "User is tall", "User likes golf", etc.

    Returns:
        The list of memories updated with the saved `memory`.
    """
    memories = load_memories()
    memories.append(memory)
    filepath = Path(get_app_dir("eddie-cli")) / "memories.pkl"
    with filepath.open(mode="wb") as f:
        pkl.dump(memories, f)
    return memories
```

Now we can give Eddie access to this tool through his call parameters. We should also update his system message to tell Eddie how best to use the tool:

```python
...
from mirascope.openai import OpenAICall, OpenAICallParams
from pydantic import Field


class EddieChat(OpenAICall):
    prompt_template = """
    SYSTEM:
    You are a helpful on-board computer assistant named Eddie.
    Your personality is modeled after the character Eddie from H2G2.
    You are currently running on a modern computer with platform {platform} on Earth.
    The current date and time is {current_date_time}.
    Your replies should be succint and to the point.
    Generally no longer than one or two sentences unless necessary to answer properly.

    You have access to a `Memorize` tool. You can call this tool to save memories.
    When you identify something worth saving, use the `Memorize` tool if you haven't already memorized it.

    You have access to the following saved memories from the user:
    {memories}
    
    You first message to the user is the following:
    "{first_message}"
    
    MESSAGES:
    {history}
    
    USER:
    {user_input}
    """

    call_params = OpenAICallParams(tools=[memorize])

    user_input: str = ""
    history: list[ChatCompletionMessageParam] = []
    memories: list[str] = Field(default_factory=load_memories)

    ...
```

## Handling when Eddie uses the `Memorize` tool

First, note that the `memorize` function is automatically converted into the `Memorize` tool, which has `memorize` attached as it's `fn`. We can use this to easily call the tool for Eddie when he wants. Then, we can re-insert the output of the tool call into the chat history so Eddie knows what tool calls he's made.

For simplicity, let's first revert back to making a call instead of streaming. Note that Eddie might call the `Memorize` tool multiple times for multiple memories, so we should handle that:

```python
class EddieChat(OpenAICall):
    ...

    def chat(
        self,
        user_input: str,
        handle_chunk_content: Callable[[str], None],
        handle_memories: Callable[[list[str]], None],
    ) -> None:
        """A single chat turn with Eddie."""
        self.user_input = user_input
        response = self.call()
        if tools := response.tools:
            tool_messages, new_memories = [], []
            for tool in tools:
                if tool:
                    self.memories = tool.fn(**tool.args)
                    new_memories.append(self.memories[-1])
                    # this needs a convenience wrapper in Mirascope...
                    tool_messages += [
                        {
                            "role": "tool",
                            "content": new_memories[-1],
                            "tool_call_id": tool.tool_call.id,
                            "name": tool.__class__.__name__,
                        }
                    ]
            handle_memories(new_memories)
            self.history += [
                response.message.model_dump(exclude={"function_call"})
            ] + tool_messages
            self.chat("", handle_chunk_content, handle_memories)
        else:
            handle_chunk_content(response.content)
            self.history += [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response.content},
            ]
            # protect context limit == short-term memory loss
            self.history = self.history[-30:]
```

Let's break this down:

1. First, we make a call, which gives us the `response` convenience wrapper.
2. Then, we access the `tools` property which will automatically convert any tool call outputs into an `OpenAITool` instance for convenience.
3. If there _are_ tools, then we iterate through the tools and call the attached function with the provided arguments. Note that `tool.args` here is a convenience property that provides the dictionary of arguments with which Eddie wants to call the tool.
4. We then insert the tool calls into the chat history. Repeat steps 1-4 by calling `chat` recursively until...
5. There are no tools, so we simply proceed as usual with a standard response.

Now we just need to update the `cli.chat` command to provide a memory handler and we're good to go:

```python
@cli.command()
def chat():
    """Multi-turn chat with Eddie."""
    eddie = EddieChat()
    print(f"Eddie: {eddie.first_message}")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print("Eddie: ", end="")
        eddie.chat(
            user_input,
            lambda x: print(x, end="", flush=True),
            lambda x: print(f"(ADDED MEMORIES: {x}) "),
        )
        print("\n", end="")
```

We can test this out by providing information we expect Eddie to memorize:

```shell
eddie chat
#> Eddie: Oh, look who it is. In need of some assistance then?
#> You: My name is William
#> Eddie: (ADDED MEMORIES: ["User's name is William"]) 
#  Oh, look who it is. In need of some assistance then?
#> You: quit
```

Unfortunately there is an issue with the Mirascope CLI at the time of writing this when trying to save calls that have functions. For now, I'm going to manually add the version so we don't lose track while we work on resolving this issue.

## Clearing Eddie's memories

Now that Eddie can add memories of user information, it's worth including the ability to forget these memories. Let's add a `cli.clear_memories` command:

```python
import os
from pathlib import Path

import typer

...

@cli.command()
def clear_memories():
    """Clears Eddie's memories of user information."""
    app_dir = Path(typer.get_app_dir("eddie-cli"))
    if not os.path.exists(app_dir):
        return
    filepath = app_dir / "memories.pkl"
    if filepath.is_file():
        filepath.unlink()
```

Now we can clear Eddie's memories by running `eddie clear-memories`.

## Updating `chat` to use streaming again

Now that we've successfully added the ability for Eddie to memorize user information, it's time to once again make it feel more real-time by streaming the responses.

The complication here is that this also requires streaming the tool calls. Luckily, Mirascope has some convenience wrappers that make it easy to stream tool calls with OpenAI.

```python
...
import json


class EddieChat(OpenAICall):
    ...

    def chat(
        self,
        user_input: str,
        handle_chunk_content: Callable[[str], None],
        handle_memory: Callable[[str], None],
    ) -> None:
        """A single chat turn with Eddie."""

        def regenerate(
            chunk: OpenAICallResponseChunk,
            astream: Generator[OpenAICallResponseChunk, None, None],
        ) -> Generator[OpenAICallResponseChunk, None, None]:
            yield chunk
            for chunk in astream:
                yield chunk

        self.user_input = user_input
        stream = self.stream()
        first_chunk = next(stream)
        generator = regenerate(first_chunk, stream)
        if first_chunk.delta and first_chunk.delta.content is None:
            tool_stream = OpenAIToolStream.from_stream(generator)
            tools, tool_messages, new_memories = [], [], []
            for tool in tool_stream:
                if tool:
                    tools.append(tool)
                    self.memories = tool.fn(**tool.args)
                    handle_memory(self.memories[-1])
                    new_memories.append(self.memories[-1])
                    # this needs a convenience wrapper in Mirascope...
                    tool_messages += [
                        {
                            "role": "tool",
                            "content": new_memories[-1],
                            "tool_call_id": tool.tool_call.id,
                            "name": tool.__class__.__name__,
                        }
                    ]
            self.history += [
                {
                    "content": None,
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tool.tool_call.id,
                            "function": {
                                "arguments": json.dumps(tool.args),
                                "name": tool.__class__.__name__,
                            },
                            "type": "function",
                        }
                        for tool in tools
                    ],
                }
            ] + tool_messages
            self.chat("", handle_chunk_content, handle_memory)
        else:
            content = ""
            for chunk in generator:
                handle_chunk_content(chunk.content)
                content += chunk.content
            self.history += [
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": content},
            ]
            # protect context limit == short-term memory loss
            self.history = self.history[-30:]
```

Let's break this down:

1. First, we updated `call()` -> `stream()` so that we can stream the chunks.
2. Next, we grab the first chunk in the stream so we can check if it's `delta.content` is `None`, in which case we can safely assume Eddie is calling a tool.
3. Now we need to recreate the generator so that it includes the first chunk we just grabbed.
4. Next, if we're receiving tool calls we create an `OpenAIToolStream` from the stream and iterate through the tools as we get them. The remaining handling of the tools is pretty much the same except that (1) we need to recreate the assistant message since we no longer have the nice fully formed response as before and (2) we can handle each memory individually to provide the real-time streaming feel.
5. Repeat steps 1-4 by recursively calling chat as before, stopping when...
6. There are no tools and we can handle Eddie's normal response.

We also need to update our `cli.chat` command to handle each memory as it's streamed:

```python
@cli.command()
def chat():
    """Multi-turn chat with Eddie."""
    eddie = EddieChat()
    print(f"Eddie: {eddie.first_message}")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print("Eddie: ", end="")
        eddie.chat(
            user_input,
            lambda x: print(x, end="", flush=True),
            lambda x: print(f"(ADDED MEMORY: {x})"),
        )
        print("\n", end="")
```

And that's it! Now Eddie can memorize user information without sacrificing the real-time feel of streaming!

Next, we're going to give Eddie a makeover with a retro-style Textual app :)
