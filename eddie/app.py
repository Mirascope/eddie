from __future__ import annotations

import datetime
import importlib.metadata

from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer, Vertical
from textual.events import Key
from textual.reactive import reactive
from textual.widgets import Input, Static

from eddie.calls import EddieChat, load_memories


class MemoriesContainer(ScrollableContainer):
    BORDER_TITLE = "Memories"

    memories: list[str] = reactive(load_memories, recompose=True)

    def compose(self) -> ComposeResult:
        for memory in self.memories:
            yield Static(memory, classes="memory")


class ChatInput(Input):
    async def on_key(self, event: Key) -> None:
        if event.key == "enter":
            await self.submit()

    async def submit(self) -> None:
        message = self.value
        self.value = ""
        app: Eddie = self.app  # type: ignore
        await app.handle_user_message(message)


class ChatMessages(ScrollableContainer):
    BORDER_TITLE = "Chat"

    def compose(self) -> ComposeResult:
        yield Static(
            "Eddie: Oh, look who it is. In need of some assistance then?",
            classes="chat-message",
        )

    async def add_message(self, message: str, is_user: bool = False) -> None:
        sender = "You" if is_user else "Eddie"
        await self.mount(
            Static(
                f"{sender}: {message}",
                classes="chat-message",
            )
        )
        self.scroll_end()

    async def add_streaming_message(self) -> None:
        await self.mount(
            Static(
                "Eddie: ...",
                id="streaming-message",
                classes="chat-message",
            )
        )
        self.scroll_end()

    def update_streaming_message(self, content: str) -> None:
        streaming_message = self.query_one("#streaming-message", Static)
        streaming_message.update(f"Eddie: {content}")
        self.scroll_end()

    def remove_streaming_message(self) -> None:
        streaming_message = self.query_one("#streaming-message", Static)
        streaming_message.remove()


class ChatContainer(Vertical):
    def compose(self) -> ComposeResult:
        yield ChatMessages()
        yield ChatInput()

    def on_mount(self) -> None:
        self.query_one(ChatInput).focus()

    async def on_message_submitted(self, message: str) -> None:
        chat_messages = self.query_one(ChatMessages)
        await chat_messages.add_message(message, is_user=True)
        await chat_messages.add_streaming_message()

    async def post_message_submitted(self, message: str) -> None:
        chat_messages = self.query_one(ChatMessages)
        memories_container = self.app.query_one(
            "#memories-container", MemoriesContainer
        )
        chat: EddieChat = self.app.chat  # type: ignore
        content = await chat.chat_async(
            message,
            chat_messages.update_streaming_message,
        )
        memories_container.memories = self.app.chat.memories.copy()
        chat_messages.update_streaming_message(content)
        chat_messages.remove_streaming_message()
        await chat_messages.add_message(content)


class Eddie(App):
    """Eddie - The AI-powered CLI application styled as a retro on-board computer."""

    CSS_PATH = "app.tcss"

    chat: EddieChat = EddieChat()

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

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    async def handle_user_message(self, message: str) -> None:
        chat_container = self.query_one(ChatContainer)
        await chat_container.on_message_submitted(message)
        self.refresh()
        self.call_after_refresh(self.handle_eddie_response, message)

    async def handle_eddie_response(self, message: str) -> None:
        chat_container = self.query_one(ChatContainer)
        await chat_container.post_message_submitted(message)
