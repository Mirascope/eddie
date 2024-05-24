# Eddie — the retro AI-powered CLI assistant

The key goal of Eddie is to serve as an educational resource for how to build real-world AI-powered applications using [Mirascope](https://github.com/Mirascope/mirascope).

https://github.com/Mirascope/eddie/assets/99370834/26b58035-d22d-432d-bb89-bffbee49b028

As we implement new features, we'll release detailed written walkthroughs to give you an inside look at the development process. By following along, you'll learn practical techniques and best practices for building your own AI-powered applications.

Here's what makes Eddie unique as a learning resource:

> [!NOTE]
> Eddie currently runs using OpenAI models; however, we want everything to run locally and are working on figuring out how to match the functional calling capabilities (namely streaming tools) in order to support a fully local and open-source Eddie.

1. Everything we use to build Eddie _will be_ open-source (see above note). This way everyone can follow along and experiment themselves super easily. Who doesn't want a personal AI at home they can run on their laptop?
2. We welcome and encourage external contributions. If there's an AI feature you'd like to see implemented in Eddie, you can submit a PR and even contribute to the accompanying educational content. Let's learn together!
3. Eddie has a fun personality (inspired by the character from The Hitchhiker's Guide to the Galaxy), and we've included an `eddie run` command that launches a retro-style Textual app. These creative touches make the learning process more engaging and memorable.

Your feedback and contributions will be invaluable in shaping Eddie into a comprehensive resource for learning to build with AI.

So dive in, check out the code, and let us know what you think!

Happy building!

## Installation

If you just want to play around with Eddie, simply install and run him:

```shell
pip install eddie-cli
eddie run
```

While we work on getting everything local, you'll also need to set your OpenAI API key for things to work:

```shell
# Set key
echo "export OPENAI_API_KEY='yourkey'" >> ~/.zshrc

# Reset shell
source ~/.zshrc

# Confirm things are all set
echo $OPENAI_API_KEY
```

## Commands

Eddie currently supports the following commands:

- `eddie version`: outputs the current version of the installed package
- `eddie chat`: multi-turn chat with Eddie directly in the command line
- `eddie run`: runs the Textual application for Eddie
- `eddie clear-memories`: clears Eddie's current memories of user information

> [!NOTE]
> The default model is `gpt-4o`.

## Walkthroughs

You can find the written walkthroughs in the [`walkthroughs`](./walkthroughs/) directory. We've labeled each walkthrough with the number corresponding to the order in which we've implemented things so it's easy to follow along.

## Roadmap

If there are any particular features or projects you would be interested in watching us build, let us know! In the meantime, this is what’s on our mind roughly:

- [X]  Basic chat with streaming
- [X]  Memories of user for personalization using tools
- [X]  Retro Textual CLI App (so Eddie looks like an on-board computer)
- [ ]  Match tool streaming functionality using local open-source LLM
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
