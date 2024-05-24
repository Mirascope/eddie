"""Eddie's chat functionality."""

import datetime
import os
import pickle as pkl
import sys
from pathlib import Path
from typing import Callable

from mirascope import tags
from mirascope.openai import OpenAICall, OpenAICallParams
from openai.types.chat import ChatCompletionMessageParam
from pydantic import Field
from typer import get_app_dir

prev_revision_id = "0004"
revision_id = "0005"


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


@tags(["version:0005"])
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
