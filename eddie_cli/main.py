import importlib.metadata  # noqa: E402
import os
from pathlib import Path

import typer

from .app import EddieApp
from .calls import EddieChat

cli = typer.Typer()


@cli.command()
def version():
    """Displays the current package version installed."""
    print(f"v{importlib.metadata.version('eddie-cli')}")


@cli.command()
def clear_memories():
    """Clears Eddie's memories of user information."""
    app_dir = Path(typer.get_app_dir("eddie-cli"))
    if not os.path.exists(app_dir):
        return
    filepath = app_dir / "memories.pkl"
    if filepath.is_file():
        filepath.unlink()


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
        eddie.chat(
            user_input,
            lambda x: print(x, end="", flush=True),
            lambda x: print(f"(ADDED MEMORY: {x})"),
        )
        print("\n", end="")


@cli.command()
def run(dev: bool = False):
    """Run Eddie's retro Textual app."""
    eddie = EddieApp(watch_css=dev)
    eddie.run()


if __name__ == "__main__":
    cli()
