"""The Typer CLI for Eddie's commands."""

import importlib.metadata

import typer

from eddie.textual import Eddie

app = typer.Typer()


@app.command()
def run():
    """Runs `Eddie` the Textual App."""
    app = Eddie()
    app.run()


@app.command()
def version():
    """Displays the current package version installed."""
    print(f"v{importlib.metadata.version('eddie')}")
