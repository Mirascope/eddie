"""The Typer CLI for Eddie's commands."""

import importlib.metadata

import typer

app = typer.Typer()


@app.command()
def hello(name: str):
    """Simply repeats `Hello {name}` back to the user."""
    print(f"Hello, {name}!")


@app.command()
def version():
    """Displays the current package version installed."""
    print(f"v{importlib.metadata.version('eddie-cli')}")
