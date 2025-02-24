import tiktoken


def estimate_costs(model_id: str, n_tokens: int, allowed_models: list) -> float:
    """Estimate cost based on n_tokens. Can be uncertain."""

    if n_tokens < 0:
        raise ValueError("n_tokens must be a positive integer.")

    model_details = _get_model_details(model_id, allowed_models)
    input_cost = n_tokens * model_details["input_cost"]
    output_cost = n_tokens * model_details["output_cost"]
    total_cost = input_cost + output_cost
    return total_cost


def calculate_costs(model_id: str, response: object, allowed_models: list) -> float:
    """Calculate cost based on API response."""

    i_tokens = response.usage.prompt_tokens  # type: ignore
    o_tokens = response.usage.completion_tokens  # type: ignore

    model_details = _get_model_details(model_id, allowed_models)
    input_cost = i_tokens * model_details["input_cost"]
    output_cost = o_tokens * model_details["output_cost"]
    total_cost = input_cost + output_cost

    # print(f"\nActual Cost: {i_tokens} + {o_tokens} =  ${total_cost:.2f}")
    return total_cost


def _get_model_details(model_id: str, allowed_models: list) -> dict:
    for model in allowed_models:
        if model["model"] == model_id:
            return model

    raise ValueError(f"Model {model_id} not found.")


def get_n_tokens(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    tokenized = encoding.encode(text)
    n_tokens = len(tokenized)
    return n_tokens
