"""Eddie's retro Textual app."""

import asyncio
import datetime
import importlib.metadata
import time

from asyncer import asyncify
from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer, Vertical
from textual.events import Key
from textual.reactive import reactive
from textual.widgets import Input, Static

from .calls import EddieChat, load_memories


class MemoriesContainer(ScrollableContainer):
    """The container for Eddie's memories."""

    BORDER_TITLE = "Memories"

    memories: list[str] = reactive(load_memories, recompose=True)

    def compose(self) -> ComposeResult:
        for memory in self.memories:
            yield Static(memory, classes="memory")


class ChatInput(Input):
    """The input for user messages."""

    def on_key(self, event: Key) -> None:
        if event.key == "enter":
            self.submit()

    def submit(self) -> None:
        message = self.value
        self.value = ""
        chat_messages = self.app.query_one(ChatMessages)
        chat_messages.add_message(message, True)
        self.call_next(chat_messages.add_streaming_message, message)


class ChatMessages(ScrollableContainer):
    """The container for chat messages."""

    BORDER_TITLE = "Chat"

    def compose(self) -> ComposeResult:
        yield Static(
            f"Eddie: {self.app.eddie.first_message}",
            classes="chat-message",
        )

    def add_message(self, message: str, is_user: bool) -> None:
        """Adds a new chat message."""
        sender = "You" if is_user else "Eddie"
        self.mount(
            Static(
                f"{sender}: {message}",
                classes="chat-message",
            )
        )
        self.scroll_end()

    def add_streaming_message(self, message: str) -> None:
        """Adds a placeholder for a streaming message."""
        self.mount(Static("Eddie: ...", classes="chat-message", id="streaming-message"))
        asyncio.create_task(self.chat_with_eddie(message))

    async def chat_with_eddie(self, message: str) -> None:
        """Chats with Eddie based on the user `message`."""
        eddie_message = ""

        def update_and_refresh(content: str) -> None:
            nonlocal eddie_message
            eddie_message += content
            self.update_streaming_message(eddie_message)
            self.refresh()

        def handle_memory(memory: str) -> None:
            memories_container = self.app.query_one(MemoriesContainer)
            memories_container.memories = memories_container.memories + [memory]

        await asyncify(self.app.eddie.chat)(message, update_and_refresh, handle_memory)
        self.scroll_end()
        self.call_after_refresh(self.finalize_streaming_message, eddie_message)

    def update_streaming_message(self, content: str) -> None:
        """Updates the streaming placeholder message."""
        streaming_message = self.query_one("#streaming-message", Static)
        streaming_message.update(f"Eddie: {content}")
        self.scroll_end()

    def finalize_streaming_message(self, message: str) -> None:
        """Finalizes the streaming message into a normal message."""
        streaming_message = self.query_one("#streaming-message", Static)
        streaming_message.remove()
        self.add_message(message, False)
        self.scroll_end()


class ChatContainer(Vertical):
    """The container for the chat input and messages."""

    def compose(self) -> ComposeResult:
        yield ChatMessages()
        yield ChatInput()

    def on_mount(self) -> None:
        self.query_one(ChatInput).focus()


class EddieApp(App):
    """Eddie - the retro AI-powered CLI assistant."""

    CSS_PATH = "app.tcss"

    eddie: EddieChat = EddieChat()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Container(
            Static(
                f"Version: {importlib.metadata.version('eddie')}", classes="topbar-left"
            ),
            Static(f"{datetime.datetime.now().date()}", classes="topbar-right"),
            id="topbar",
        )
        yield Container(
            MemoriesContainer(id="memories-container"),
            ChatContainer(),
            id="memories-chat",
        )


__all__ = ("EddieApp",)
