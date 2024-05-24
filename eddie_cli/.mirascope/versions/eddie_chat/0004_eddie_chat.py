"""Eddie's chat functionality."""

import datetime
import sys
from typing import Callable

from mirascope import tags
from mirascope.openai import OpenAICall
from openai.types.chat import ChatCompletionMessageParam

prev_revision_id = "0003"
revision_id = "0004"


@tags(["version:0004"])
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
