from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Vertical
from textual.events import Key
from textual.reactive import reactive
from textual.widgets import Input, Static

from src.calls import EddieChat


class ChatMessage(Static):
    DEFAULT_CSS = """
    ChatMessage {
        background: #000000;
        color: #00FF00;
        margin: 0 0 1 0;
    }
    """


class ChatInput(Input):
    DEFAULT_CSS = """
    ChatInput {
        dock: bottom;
        width: 100%;
        min-height: 3;
        background: #000000;
        color: #00FF00;
        border: round #00FF00;
        # hover: pointer;
    }
    ChatInput:focus {
        border: round #FFD700;
        padding: 0 1;
    }
    """

    async def on_key(self, event: Key) -> None:
        if event.key == "enter":
            await self.submit()

    async def submit(self) -> None:
        message = self.value
        self.value = ""
        app: Eddie = self.app  # type: ignore
        app.handle_user_message(message)


class ChatMessages(ScrollableContainer):
    DEFAULT_CSS = """
    ChatMessages {
        background: #000000;
        color: #00FF00;
        border: round #00FF00;
        padding: 0 1;
        scrollbar-color: gold;
    }
    """

    def compose(self) -> ComposeResult:
        yield ChatMessage("Eddie: Oh, look who it is. In need of some assistance then?")

    def add_message(self, message: str, is_user: bool = False) -> None:
        sender = "You" if is_user else "Eddie"
        self.mount(ChatMessage(f"{sender}: {message}"))
        self.scroll_end()

    def add_streaming_message(self) -> None:
        self.mount(ChatMessage("Eddie: ...", id="streaming-message"))
        self.scroll_end()

    def update_streaming_message(self, content: str) -> None:
        streaming_message = self.query_one("#streaming-message", ChatMessage)
        streaming_message.update(f"Eddie: {content}")
        self.scroll_end()

    def remove_streaming_message(self) -> None:
        streaming_message = self.query_one("#streaming-message", ChatMessage)
        streaming_message.remove()


class ChatContainer(Vertical):
    chat_messages = reactive(ChatMessages())

    def compose(self) -> ComposeResult:
        yield self.chat_messages
        yield ChatInput()

    def on_mount(self) -> None:
        self.query_one(ChatInput).focus()

    async def on_message_submitted(self, message: str) -> None:
        chat_messages = self.query_one(ChatMessages)
        chat_messages.add_message(message, is_user=True)
        chat_messages.add_streaming_message()
        await self.stream_response(message)

    async def stream_response(self, message: str) -> None:
        chat: EddieChat = self.app.chat  # type: ignore
        chat.query = message
        stream = chat.stream_async()
        content = ""
        chat_messages = self.query_one(ChatMessages)
        async for chunk in stream:
            content += chunk.content
            chat_messages.update_streaming_message(content)
        chat_messages.remove_streaming_message()
        chat_messages.add_message(content)
        chat.history += [
            {"role": "user", "content": message},
            {"role": "assistant", "content": content},
        ]


class Eddie(App):
    """Eddie - The AI-powered CLI application styled as a retro on-board computer."""

    CSS = """
    ChatContainer {
        background: #000000;
        color: #00FF00;
        border: round #00FF00;
        padding: 0 1;  # Add consistent padding
    }
    """

    chat: EddieChat = EddieChat()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield ChatContainer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    async def send_message(self, message: str) -> None:
        await self.query_one(ChatContainer).on_message_submitted(message)

    def handle_user_message(self, message: str) -> None:
        self.call_later(self.send_message, message)
        self.query_one(ChatInput).value = ""
