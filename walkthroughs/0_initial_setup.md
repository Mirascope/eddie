# Eddie -- Initial Setup

First things first, we created the `[eddie](https://github.com/Mirascope/eddie)` repo with an empty [README.md](https://github.com/Mirascope/eddie/blob/main/README.md) and the standard [MIT license](https://github.com/Mirascope/eddie/blob/main/LICENSE). This will be where we continue to build real-world examples of powerful AI-powered tooling — all running open-source on your machine.

## Package manager & project setup

Since `[uv](https://github.com/astral-sh/uv)` does not yet support the full build-release workflow (it’s on their roadmap though, which is exciting stuff), we will be using `[poetry](https://python-poetry.org/docs/)` as our package manager for the repo.

If you don’t already have `poetry` installed, you can run `pip install poetry`. We will then run `poetry init`, follow the steps, and end up with the following `pyproject.toml` configuration file, which will act as our package’s source of truth. We can then run `poetry add mypy ruff --group dev` to add `[ruff](https://github.com/astral-sh/ruff)` and `[mypy](https://mypy.readthedocs.io/en/stable/getting_started.html)` as dev dependencies for the project (which I add to all my projects).

```toml
# pyproject.toml
[tool.poetry]
name = "eddie-cli"
version = "0.1.0"
description = "Eddie -- the retro AI-powered CLI assistant"
authors = ["William Bakst <william@mirascope.io>"]
license = "MIT"
readme = "README.md"

[tool.poetry.scripts]
eddie = "eddie_cli.main:cli"

[tool.poetry.dependencies]
python = ">=3.9,<4.0"

[tool.poetry.group.dev.dependencies]
ruff = "^0.4.5"
mypy = "^1.10.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

We’ll also create an `eddie_cli` base folder with an where all of our project’s source code will live (including the `__init__.py`).

## Simple Typer CLI

The next step is to use the amazing [Typer](https://typer.tiangolo.com/) library to build the structure for our CLI app. One of the more basic features we will use is the ability to quickly and easily spin up commands for different actions, which will act as a great way for us to separate different workflows and functionality down the line.

To get started, we’ll first run `poetry add typer` to install the library. Then we’ll create a simple `[eddie_cli/main.py](http://main.py)` CLI app with two commands: version and chat.

```python
# main.py
import importlib.metadata  # noqa: E402

import typer

cli = typer.Typer()


@cli.command()
def version():
    """Displays the current package version installed."""
    print(f"v{importlib.metadata.version('eddie-cli')}")


@cli.command()
def chat():
    """Multi-turn chat with Eddie."""
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print("Eddie: Not Yet Implemented :(")


if __name__ == "__main__":
    cli()
```

Last, we’ll add an install script to our `pyproject.toml` so that we can access the CLI app directly through eddie instead of `python eddie_cli/main.py`:

```toml
# pyproject.toml
[tool.poetry.scripts]
eddie = 'eddie_cli.main:app'
```

Running the following should now work (and output the version number):

```shell
poetry install
eddie version
# v0.1.0
eddie chat
#> You: Hello!
#> Eddie: Not Yet Implemented :(
#> You: quit
```

And that's it! Now we have the skeleton on top of which we can build Eddie. Next, we'll add some basic chat functionality.
