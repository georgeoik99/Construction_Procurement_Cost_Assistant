import pandas as pd

from src.assistant.response_generator import generate_assistant_response


def ask_procurement_assistant(query: str, df: pd.DataFrame) -> str:
    """
    Mock LLM layer.

    This simulates an AI assistant response without calling an external LLM API.
    Later, this can be replaced with an OpenAI-compatible API call.
    """

    return generate_assistant_response(query=query, df=df)