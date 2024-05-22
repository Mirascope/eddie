"""The Typer CLI for Eddie's commands."""

import importlib.metadata
import os
from pathlib import Path

import typer

from eddie.app import Eddie
from eddie.calls import EddieChat

cli = typer.Typer()


@cli.command()
def run():
    """Runs `Eddie` the Textual App."""
    app = Eddie()
    app.run()


@cli.command()
def chat():
    """Runs `Eddie` the CLI chat interface."""
    app = EddieChat()
    while True:
        query = input("You: ")
        if query in ["quit", "exit"]:
            break
        app.chat(
            query,
            lambda x: print(x, end="", flush=True),
            lambda x: print(f"ADDING MEMORY: {x}"),
        )
        print("\n", end="")


@cli.command()
def version():
    """Displays the current package version installed."""
    print(f"v{importlib.metadata.version('eddie')}")
