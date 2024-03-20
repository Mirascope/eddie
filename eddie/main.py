"""Typer CLI Implementation."""
from rich.console import Console
from typer import Argument, Option, Typer

from . import __version__

app = Typer()


@app.command(help="Chat with Eddie")
def chat():
    """Starts a Rich Console chat with Eddie."""
    raise NotImplementedError()


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
