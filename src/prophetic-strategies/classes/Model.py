from abc import ABC, abstractmethod
from constants import ALLOWED_BASE_MODELS
import tiktoken


class Model(ABC):

    def __init__(self, id: str) -> None:
        super().__init__()
        self._check_allowed_models(id, ALLOWED_BASE_MODELS)
        self.id = id
        self.source = None

    @abstractmethod
    def _check_allowed_models(self, id: str) -> None:
        pass

    @abstractmethod
    def estimate_costs(self, n_tokens: int) -> float:
        pass

    @abstractmethod
    def get_n_tokens(self, text: str) -> int:
        encoding = tiktoken.get_encoding("cl100k_base")
        tokenized = encoding.encode(text)
        n_tokens = len(tokenized)
        return n_tokens

    @abstractmethod
    def calculate_cost(self, response: object) -> float:
        pass

    @abstractmethod
    def _get_completion(self, messages: list, temp: float, api_key: str) -> str:
        pass

    @abstractmethod
    def _parse_completion(self, response: object) -> str:
        pass

    @abstractmethod
    def query(
        self,
        prompt: str,
        variable: str,
        temp: float,
        api_key: str | None,
    ) -> tuple[str, float]:
        pass

    def build_messages(self, prompt: str) -> list[dict]:
        messages = [{"role": "user", "content": prompt}]
        return messages

    def append_message(
        self, messages: list[dict], role: str, message: str
    ) -> list[dict]:
        messages.append({"role": role, "content": message})
        return messages
