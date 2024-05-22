import datetime
import json

# from eddie.config import Settings
# settings = Settings()
import os
import pickle as pkl
import sys
from pathlib import Path
from typing import Callable, Generator

from mirascope import tags
from mirascope.logfire import with_logfire
from mirascope.openai import (
    OpenAICall,
    OpenAICallParams,
    OpenAICallResponseChunk,
    OpenAITool,
    OpenAIToolStream,
)
from openai.types.chat import ChatCompletionMessageParam
from pydantic import Field
from typer import get_app_dir


def load_memories() -> list[str]:
    """Loads Eddie's memories."""
    app_dir = Path(get_app_dir("eddie"))
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    filepath = app_dir / "memories.pkl"
    if not os.path.exists(filepath):
        with filepath.open(mode="wb") as f:
            pkl.dump([], f)
    with filepath.open(mode="rb") as f:
        return pkl.load(f)


def memorize(memory: str) -> str:
    """Saves the `memory` and returns it.

    Args:
        memory: A memory synthesized from a user query. This should just be a single
            sentence describing what should be memorized. For example, you might
            want to save something like "User is tall", "User likes baseball", etc.

    Returns:
        The saved `memory`.
    """
    return memory


@with_logfire
@tags(["version:0001"])
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

    When using the `Memorize` tool, you should output ONLY the 

    You have access to the following saved memories from the user:
    {memories}
    
    MESSAGES:
    {history}
    
    USER:
    {query}
    """

    query: str = ""
    memories: list[str] = Field(default_factory=load_memories)
    history: list[ChatCompletionMessageParam] = []
    call_params = OpenAICallParams(model="gpt-4o", tools=[memorize])

    @property
    def current_date_time(self) -> str:
        """Retruns the current time and date."""
        return str(datetime.datetime.now())

    @property
    def platform(self) -> str:
        """Returns information about the current system."""
        return sys.platform

    def add_memory(self, memory: str) -> None:
        """Saves `memory` to Eddie's memory."""
        self.memories.append(memory)
        filepath = Path(get_app_dir("eddie")) / "memories.pkl"
        with filepath.open(mode="wb") as f:
            pkl.dump(self.memories, f)

    def delete_memory(self, index: int) -> None:
        del self.memories[index]
        filepath = Path(get_app_dir("eddie")) / "memories.pkl"
        with filepath.open(mode="wb") as f:
            pkl.dump(self.memories, f)

    async def chat_async(
        self, user_query: str, handle_chunk_content: Callable[[str], None]
    ):
        return self.chat(user_query, handle_chunk_content)

    def chat(
        self,
        user_query: str,
        handle_chunk_content: Callable[[str], None],
    ) -> str:
        """Returns the content from an iteration of a chat turn."""

        def regenerate(
            chunk: OpenAICallResponseChunk,
            astream: Generator[OpenAICallResponseChunk, None, None],
        ) -> Generator[OpenAICallResponseChunk, None, None]:
            yield chunk
            for chunk in astream:
                yield chunk

        self.query = user_query
        self.history += [{"role": "user", "content": user_query}]

        stream = self.stream()
        first_chunk: OpenAICallResponseChunk = next(stream)
        generator = regenerate(first_chunk, stream)
        if first_chunk.delta.content is None:
            tool_stream = OpenAIToolStream.from_stream(generator)
            tools: list[OpenAITool] = []
            tool_messages = []
            for tool in tool_stream:
                if tool and tool.__class__.__name__ == "Memorize":
                    tools.append(tool)
                    memory = tool.fn(**tool.args)
                    self.add_memory(memory)
                    tool_messages += [
                        {
                            "role": "tool",
                            "content": memory,
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
            content = self.chat("", handle_chunk_content)
        else:
            content = ""
            for chunk in generator:
                handle_chunk_content(chunk.content)
                content += chunk.content
            self.history += [{"role": "assistant", "content": content}]

        # try not to hit context limit in exchange for short term memory loss
        self.history = self.history[-30:]
        return content
