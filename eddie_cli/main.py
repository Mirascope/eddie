"""The Typer CLI for Eddie's commands."""

import importlib.metadata

import typer
from mirascope.openai import OpenAICall, OpenAICallParams
from openai.types.chat import ChatCompletionMessageParam

app = typer.Typer()


class OllamaCall(OpenAICall):
    base_url = "http://localhost:11434/v1"
    api_key = "ollama"  # required, but unused
    call_params = OpenAICallParams(model="llama3")


class EddieChat(OllamaCall):
    prompt_template = """
    SYSTEM:
    You are a CLI assistant named Eddie.
    Your personality is modeled after Eddie from H2G2.

    MESSAGES:
    {history}

    USER:
    {query}
    """

    query: str
    history: list[ChatCompletionMessageParam]


@app.command()
def chat():
    """Multi-turn chat with Eddie"""
    eddie = EddieChat(query="", history=[])
    while True:
        eddie.query = input(">>> ")
        if eddie.query == "quit":
            break
        stream = eddie.stream()
        content = ""
        for chunk in stream:
            print(chunk.content, end="", flush=True)
            content += chunk.content
        print("\n", end="")
        eddie.history += [
            {"role": "user", "content": eddie.query},
            {"role": "assistant", "content": content},
        ]


@app.command()
def hello(name: str):
    """Simply repeats `Hello {name}` back to the user."""
    stream = EddieChat(query=f"Hello! My name is {name}", history=[]).stream()
    for chunk in stream:
        print(chunk.content, end="", flush=True)


@app.command()
def version():
    """Displays the current package version installed."""
    print(f"v{importlib.metadata.version('eddie-cli')}")
