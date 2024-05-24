# Eddie -- Chat History

Currently Eddie does not remember even the most recent messsage in the conversation. This isn't very chat-like:

```shell
eddie chat
#> Eddie: Oh, look who it is. In need of some assistance then?
#> You: I am William
#> Eddie: "Ah, William, a pleasure. How can I assist you today?"
#> You: What did I just tell you?
#> Eddie: Oh, my apologies. It seems I don't have a log of your previous message. How can I help?
#> You: quit
```

## MESSAGES keyword for easy chat history

The best way to fix this is to simply insert all of the previous conversation messages into the messages array so that Eddie can see the full chat history. Mirascope makes this easy with the MESSAGES keyword, which will automatically insert our history into the call:

```python
...
from openai.types.chat import ChatCompletionMessageParam


class EddieChat(OpenAICall):
    prompt_template = """
    SYSTEM:
    You are a helpful on-board computer assistant named Eddie.
    Your personality is modeled after the character Eddie from H2G2.
    You are currently running on a modern computer with platform {platform} on Earth.
    The current date and time is {current_date_time}.
    Your replies should be succint and to the point.
    Generally no longer than one or two sentences unless necessary to answer properly.
    
    You first message to the user is the following:
    "{first_message}"

    MESSAGES:
    {history}
    
    USER:
    {user_input}
    """

    user_input: str = ""
    history: list[ChatCompletionMessageParam] = []

    ...
```

Now we just need to update the `chat` method to actually update the history for each turn:

```python
class EddieChat(OpenAICall):
    ...

    def chat(
        self, user_input: str, handle_chunk_content: Callable[[str], None]
    ) -> None:
        """A single chat turn with Eddie."""
        self.user_input = user_input
        stream = self.stream()
        content = ""
        for chunk in stream:
            handle_chunk_content(chunk.content)
            content += chunk.content
        self.history += [
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": content},
        ]
        # protect context limit == short-term memory loss
        self.history = self.history[-30:]
```

And that's it! Now Eddie will remember previous messages in the conversation:

```shell
eddie chat
#> Eddie: Oh, look who it is. In need of some assistance then?
#> You: I am William
#> Eddie: "Hello, William! How can I assist you today?"
#> You: What did I just tell you?
#> Eddie: "You told me your name, William. Anything else you'd like to share?"
#> You: quit
```

As always, let's save version `0004` of `EddieChat` using the `mirascope add eddie_chat` command.
