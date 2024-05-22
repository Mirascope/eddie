# Eddie — The AI-powered CLI Assistant

The primary purpose of Eddie is to demonstrate how to build real-world AI-powered applications. Everything that we use to build Eddie will be open-source and run locally on your machine so it’s private and secure. We will include videos of live coding everything along with detailed written walkthroughs.

## Installation

Eddie is not yet released. If you want, you can build from source. If you clone the repo, from the root directory you can run:

```python
poetry shell
poetry install
eddie {command}  # see commands below
```

If you don't have `poetry` installed you can run `pip install poetry`.

## Commands

Right now Eddie is powered using OpenAI's `gpt-4o` language model. However, we want everything to run locally and are working on figuring out how to match the function calling capabilities (primarily streaming) in order to support a fully local Eddie.

Eddie currently supports the following commands:

- `eddie version`: outputs the current version of the installed package.
- `eddie chat`: multi-turn chat with Eddie
- `eddie run`: runs the Textual application for Eddie

## Walkthroughs

!!! warning

    This section is under construction.

## Roadmap

If there are any particular features or projects you would be interested in watching us build, let us know! In the meantime, this is what’s on our mind roughly:

- [X]  Beautiful Textual CLI App (so Eddie looks like an on-board computer)
- [X]  Memories of user for personalization
- [ ]  RAG with Memory
- [ ]  Simple Gmail Tool-Use Agent
- [ ]  Researcher Agent
    - [ ]  Web Search Tools
    - [ ]  Web Scraping Tools
- [ ]  Technical Documentation Writer
- [ ]  Code Interpreter
- [ ]  Interpretable ML Data Scientist ([PyTorch Lattice](https://github.com/willbakst/pytorch-lattice) Bot)
- [ ]  API Documentation Assistant

## Versioning

Eddie uses [Semantic Versioning](https://semver.org/).

## License

This project is licensed under the terms of the [MIT License](https://github.com/Mirascope/eddie/blob/main/LICENSE).
