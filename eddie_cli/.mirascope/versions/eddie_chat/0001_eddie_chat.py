"""Eddie's chat functionality."""

from typing import Callable

from mirascope import tags
from mirascope.openai import OpenAICall

prev_revision_id = None
revision_id = "0001"


@tags(["version:0001"])
class EddieChat(OpenAICall):
    prompt_template = "{user_input}"
    user_input: str = ""

    def chat(self, user_input: str, handle_content: Callable[[str], None]) -> None:
        """A single chat turn with Eddie."""
        self.user_input = user_input
        response = self.call()
        handle_content(response.content)
