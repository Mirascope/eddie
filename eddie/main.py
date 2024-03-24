"""Typer CLI Implementation."""
from textwrap import dedent
from typing import Optional

import wandb
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from typer import Typer

from . import __version__
from .calls import Chat
from .config import Settings
from .simple_code_block import SimpleCodeBlock

settings = Settings()
app = Typer()

wandb.login(key=settings.wandb_api_key)
wandb.init(project="eddie")


Markdown.elements["fence"] = SimpleCodeBlock


@app.command(help="Chat with Eddie")
def chat(base_url: Optional[str] = None, dirname: Optional[str] = None):
    """Starts a Rich Console chat with Eddie."""
    console = Console()

    # Display welcome banner
    banner = dedent(
        """
    ███████╗██████╗ ██████╗ ██╗███████╗
    ██╔════╝██╔══██╗██╔══██╗██║██╔════╝
    █████╗  ██║  ██║██║  ██║██║█████╗  
    ██╔══╝  ██║  ██║██║  ██║██║██╔══╝  
    ███████╗██████╔╝██████╔╝██║███████╗
    ╚══════╝╚═════╝ ╚═════╝ ╚═╝╚══════╝
        """
    )
    console.print(Panel(banner, expand=False, border_style="bold purple"))
    console.print(
        "Welcome to Eddie, your AI assistant! "
        f"-- [bold green]v{__version__}[/bold green]",
    )

    # Initialize Chat instance
    chat = Chat()

    while True:
        user_input = console.input("\n[bold green]Me:[/bold green] ")

        if user_input.lower() in ["quit", "exit", "bye"]:
            console.print("\n[bold blue]Eddie[/bold blue]:\nGoodbye! Have a great day.")
            break

        chat.user_message = user_input
        chat.history.append({"role": "user", "content": user_input})

        interrupted, error = False, None
        console.print("\n[bold blue]Eddie:[/bold blue] ")
        # with Live("", refresh_per_second=1, console=console) as live:
        #     try:
        #         content = ""
        #         for chunk in stream:
        #             content += chunk.content
        #             live.update(Markdown(content))
        #         content += "\n"
        #         live.update(Markdown(content))
        #     except KeyboardInterrupt:
        #         interrupted = True
        #     except Exception as e:
        #         error = e
        try:
            response, span = chat.call_with_trace()
            content = response.content
            console.print(Markdown(content))
            span.log("eddie_chat_call")
        except KeyboardInterrupt:
            interrupted = True
        except Exception as e:
            error = e

        if interrupted:
            console.print("[dim]Interrupted[/dim]")

        if error:
            console.print(f"LLM error: {error}", style="red")
            chat.history.append({"role": "assistant", "content": f"LLM error: {error}"})
        else:
            chat.history.append({"role": "assistant", "content": content})

        # Make sure we remain within the context limit by limiting the history.
        chat.history = chat.history[::-1][:10][::-1]


@app.command(help="Show the version")
def version():
    """Prints the currently installed version of the CLI."""
    console = Console()
    console.print("Eddie -- ", end="")
    console.print(
        f"v{__version__}",
        style="green bold",
        highlight=False,
    )


if __name__ == "__main__":
    app()
