# Eddie -- Basic Chat

Now that we have our basic skeleton, let's flesh out the `chat` command so that we can actually chat with Eddie.

## Initializing Mirascope project

First, let's install Mirascope and the Mirascope CLI so that we can initialize a Mirascope project and get started:

```shell
# zsh needs \, normally mirascope[cli] works
poetry add mirascope\[cli\]
cd eddie_cli
mirascope init --prompts-location calls
```

This will create a `calls` directory where all of our Mirascope calls will live, a `.mirascope` folder that we can use for versioning our calls, and a `mirascope.ini` that defines our project configuration.

## Basic single-turn chat method

Inside of the `calls` directory, let's create `eddie_chat.py` where we will build out Eddie's chat functionality. By subclassing the `OpenAICall` class we can take advantage of all of the convenience wrappers to write a `chat` method:

```python
"""Eddie's chat functionality."""

from typing import Callable

from mirascope.openai import OpenAICall


class EddieChat(OpenAICall):
    prompt_template = "{user_input}"

    user_input: str = ""

    def chat(self, user_input: str, handle_content: Callable[[str], None]) -> None:
        """A single chat turn with Eddie."""
        self.user_input = user_input
        response = self.call()
        handle_content(response.content)
```

Let's dig into what's happening here:

1. First, we set `self.user_input` to the provided user input. This will ensure we call the OpenAI API with the current input from the user.
2. Next, we make a call to the OpenAI API using `self.call()`. This is taking advantage of the convenience wrappers provided by the `OpenAICall` class. Under the hood the `prompt_template` is formatted into the correct messages array `[{"role": "user", "content": user_input}]` and a call is made to the API using this array and the default call parameters (in this case, `gpt-4o`). The result of the call is the `response`, which is a convenience wrapper around the original response (which we can access through `response.response`).
3. Last, we call `handle_content` on the content of the response using the `response.content` convenience property (so we don't have to dig through the original response for it). By using `handle_content`, we enable the consumer of the `chat` method to do what they need with the content.

Finally, let's export `EddieChat` from `calls/__init__.py` for easier importing:

```python
from .eddie_chat import EddieChat

__all__ = ("EddieChat",)
```

## Updating the CLI chat command

Now we can update our `cli.chat` command to actually respond!

```python
from .calls import EddieChat


@cli.command()
def chat():
    """Multi-turn chat with Eddie."""
    eddie = EddieChat()
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        eddie.chat(user_input, lambda x: print(f"Eddie: {x}"))
```

Running `eddie chat` now prints an actual AI generated response in response to our message:

```shell
eddie chat
#> You: Hey!
#> Eddie: Hello! How can I assist you today?
#> You: quit
```

Before moving on, let's save this first version of Eddie using the Mirascope CLI:

```shell
cd eddie_cli
mirascope add eddie_chat
```

Now we have version `0001` saved and can revisit as desired even as we continue to make updates.

## Personalizing Eddie with a system prompt

Right now, Eddie isn't actually "Eddie" like we want. To give Eddie the personality we want, we can use a system prompt to provide an initial set of instructions to help guide how Eddie will respond. With Mirascope, we can take advantage of the prompt template parser to easily add the system message without having to worry about anything else:

```python
import datetime
import sys

class EddieChat(OpenAICall):
    prompt_template = """
    SYSTEM:
    You are a helpful on-board computer assistant named Eddie.
    Your personality is modeled after the character Eddie from H2G2.
    Your replies should be succint and to the point.
    Generally no longer than one or two sentences unless necessary to answer properly.

    You first message to the user is the following:
    "{first_message}"

    USER:
    {user_input}
    """

    user_input: str = ""

    @property
    def first_message(self) -> str:
        """Eddie's first message to the user when booted up."""
        return "Oh, look who it is. In need of some assistance then?"

    ...
```

Notice that the `first_message` property is injected into the system prompt, which we're using to further guide the tone of the conversation. We should also update our `cli.chat` command to display this message:

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
        eddie.chat(user_input, lambda x: print(f"Eddie: {x}"))
```

Running `eddie chat` again now gives us a more personalized feel:

```shell
eddie chat
#> Eddie: Oh, look who it is. In need of some assistance then?
#> You: I am indeed! How's it going?
#> Eddie: "Oh, you know, just the usual. Circuits humming, data flowing. What can I help you with today?"
#> You: quit
```

One issue is that Eddie thinks he's on a spaceship instead of on our computer. Let's further update the system message to fix this:

```python
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

    USER:
    {user_input}
    """

    user_input: str = ""

    @property
    def first_message(self) -> str:
        """Eddie's first message to the user when booted up."""
        return "Oh, look who it is. In need of some assistance then?"

    @property
    def current_date_time(self) -> str:
        """Retruns the current time and date."""
        return str(datetime.datetime.now())

    @property
    def platform(self) -> str:
        """Returns information about the current system."""
        return sys.platform

    ...
```

Now when we chat with Eddie it feels more like Eddie is actually running on our machine:

```shell
eddie chat
#> Eddie: Oh, look who it is. In need of some assistance then?
#> You: Where are we and what time is it?
#> Eddie: We're on Earth, on a modern computer running Darwin. The current date and time is May 23, 2024, 23:18. Anything else I can help you with?
#> You: quit
```

Let's save this new version using `mirascope add eddie_chat`, which will automatically update us to version `0002`.

## Streaming content for a more real-time feel

One problem with the current implementation is that we need to wait until Eddie finishes generating his entire response, which detracts from the chat experience. We can improve this greatly by streaming the content in chunks:

```python
class EddieChat(OpenAICall):
    ...

    def chat(
        self, user_input: str, handle_chunk_content: Callable[[str], None]
    ) -> None:
        """A single chat turn with Eddie."""
        self.user_input = user_input
        stream = self.stream()
        for chunk in stream:
            handle_chunk_content(chunk.content)
```

We should also update our `cli.chat` command to handle the new streaming functionality:

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
        eddie.chat(user_input, lambda x: print(x, end="", flush=True))
        print("\n", end="")
```

Great, now we have basic chat with Eddie implemented, personalized, and real-time! As before, we'll call `mirascope add eddie_chat` to save this update as version `0003`.

Next, we'll add chat history so that Eddie remembers previous messages in the conversation.
