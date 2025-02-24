from openai import OpenAI
from constants import ALLOWED_BASE_MODELS
from Model import Model


class OpenAIModel(Model):
    def __init__(self, id: str) -> None:
        super().__init__(id)
        self.source = "openai"

    def _check_allowed_models(self, model_id: str, allowed_models: list) -> None:
        result = any(model["model"] == model_id for model in allowed_models)
        if not result:
            raise ValueError(f"Model {id} not found.")

    # override
    def _get_completion(self, messages: list, temp: float, api_key: str) -> object:

        client = OpenAI(api_key=api_key)
        return client.chat.completions.create(
            model=self.id,
            messages=messages,  # type: ignore
            temperature=temp,
        )

    def _get_completion_stream(self, messages: list, temp: float, api_key: str):

        client = OpenAI(api_key=api_key)
        stream = client.chat.completions.create(
            model=self.id,
            messages=messages,  # type: ignore
            temperature=temp,
            stream=True,
        )

        return stream

    # def _stream(stream: object) -> str:
    #     for chunk in stream:
    #         if chunk.choices[0].delta.content is not None:
    #             return chunk.choices[0].delta.content

    # def generate(self, prompt: str, temp: float, api_key: str):
    #     messages = self.build_messages(prompt)
    #     response = self._get_completion_stream(messages, temp, api_key)

    #     completion = self._parse_completion(response)
    #     costs = self.calculate_cost(response)

    #     return completion, costs

    # override
    def _parse_completion(self, response: object) -> str:
        return response.choices[0].message.content  # type: ignore
