# Eddie — The AI-powered CLI Assistant

The primary purpose of Eddie is to demonstrate how to build real-world AI-powered applications. Everything that we use to build Eddie will be open-source and run locally on your machine so it’s private and secure. We will include videos of live coding everything along with detailed written walkthroughs.

## Installation

You can install Eddie on your own machine by running:

```bash
pip install eddie-cli
```

You can check that Eddie has been installed by running `eddie version`.

## Commands

Before running any command, you’ll need to run `ollama run llama3` to spin up your local LLM endpoint for Eddie to query. If you haven’t installed it yet, check out [Ollama](https://ollama.com/) and install it!

Eddie currently supports the following commands:

- `eddie version`: outputs the current version of the installed package.
- `eddie hello {name}`: prompt Eddie and say hello.
- `eddie chat`: multi-turn chat with Eddie

## Walkthroughs

### Initial Setup

[Link to blog post and video]

### Basic Chat

[Link to blog post and video]

## Roadmap

If there are any particular features or projects you would be interested in watching us build, let us know! In the meantime, this is what’s on our mind roughly:

- [ ]  Beautiful Textual CLI App (so Eddie looks like an on-board computer)
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
