from mirascope.openai import OpenAICall, OpenAICallParams
from openai.types.chat import ChatCompletionMessageParam


class EddieChat(OpenAICall):
    prompt_template = """
    SYSTEM:
    You are a helpful on-board computer assistant named Eddie.
    Your personality is modeled after the character Eddie from H2G2.
    Your replies should be succint and to the point.

    MESSAGES:
    {history}

    USER:
    {query}
    """

    query: str = ""
    history: list[ChatCompletionMessageParam] = []

    api_key = "ollama"  # unused but necessary with OpenAI
    base_url = "http://localhost:11434/v1"
    call_params = OpenAICallParams(model="llama3")
