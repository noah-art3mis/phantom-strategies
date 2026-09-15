from openai import OpenAI, Stream
from typing import Optional
from constants import REFERENCE_PROMPT


def completion_stream(
    api_key: str, model_id: Optional[str], messages: list, temp: float
) -> Stream:

    if model_id is None:
        raise ValueError("`model_id` cannot be None.")

    client = OpenAI(api_key=api_key, timeout=45, max_retries=0)
    stream = client.chat.completions.create(
        model=model_id,
        messages=messages,  # type: ignore
        temperature=temp,
        stream=True,
        # stream_options={"include_usage": True},
        max_tokens=256,
    )

    return stream


def format_messages(prompt: str, messages: Optional[list]) -> list:
    if messages is None:
        messages = []
        messages.append({"role": "user", "content": prompt})
    else:
        messages.append({"role": "assistant", "content": prompt})
    return messages


def make_book_name(api_key: str, snippet: str) -> str:

    model = "gpt-4o-mini-2024-07-18"
    prompt = REFERENCE_PROMPT
    prompt = prompt.replace(r"{{SNIPPET}}", snippet)
    messages = [{"role": "user", "content": prompt}]

    client = OpenAI(api_key=api_key, timeout=45, max_retries=0)
    response = client.chat.completions.create(
        model=model,
        messages=messages,  # type: ignore
        temperature=1,
        stream=False,
    )

    return response.choices[0].message.content  # type: ignore
