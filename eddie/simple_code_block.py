"""
Source: https://github.com/samuelcolvin/aicli/blob/main/samuelcolvin_aicli.py
By: samuelcolvin

This code is used in accordance with the repository's license, and this reference
serves as an acknowledgment of the original author's contribution to this project.

The below code is a version of the source modified to fit this project's purpose.
"""
from rich.console import Console, ConsoleOptions, RenderResult
from rich.markdown import CodeBlock
from rich.syntax import Syntax
from rich.text import Text


class SimpleCodeBlock(CodeBlock):
    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        code = str(self.text).rstrip()
        yield Text(self.lexer_name, style="dim")
        yield Syntax(
            code,
            self.lexer_name,
            theme=self.theme,
            background_color="default",
            word_wrap=True,
        )
        yield Text(f"/{self.lexer_name}", style="dim")
