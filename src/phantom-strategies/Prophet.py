from __future__ import annotations
from typing import Optional, Generator
from openai import Stream
import random
import pandas as pd

from utils import get_base_model, fake_stream, write_roman
from genai import completion_stream, format_messages, make_book_name
from semantic_search import semantic_search


class Prophet:
    def __init__(self, api_key: str, temp: float):
        self.name = None
        self.api_key = api_key
        self.temp = temp
        self.source = "openai"
        self.model_id = None
        self.table = None
        self.author = None

    def search(self, question: str, df: pd.DataFrame) -> pd.Series:
        return semantic_search(question, df)

    def generate_reference(self, content: str, search_result: pd.Series) -> dict:
        book_name = make_book_name(self.api_key, content)
        book_number = write_roman(random.randint(50, 100))

        return {
            "book": f"Book {book_number} - {book_name}",
            "sentence": random.randint(0, 1000),
            "content": content,
        }

    def generate(self, search_result: str, message_history: Optional[list]) -> Stream:
        messages = format_messages(search_result, message_history)
        stream = completion_stream(self.api_key, self.model_id, messages, self.temp)
        return stream

    def iterate(
        self, iterations: int, message_history: Optional[list], last_result: str
    ) -> Generator:
        for _ in range(iterations):
            yield self.generate(last_result, message_history)

    @staticmethod
    def get_prophet(
        strategy: str, api_key: str, temp: float, strategies: list[str]
    ) -> Prophet:
        match strategy:
            case "Oracular":
                return Oracle(api_key, temp)
            case "Ficticious":
                return Ficticious(api_key, temp)
            case "Fallacious":
                return Fallacious(api_key, temp)
            # case "Erratic":
            #     return Erratic(api_key, temp)
            case "Chimerical":
                return Chimerical(api_key, temp)
            case "Spectral":
                return Spectral(api_key, temp)
            # case "Apocryphal":
            #     return Apocryphal(api_key, temp)
            case "Quixotic":
                return Quixotic(api_key, temp)
            case "Mercurial":
                return Prophet.get_prophet(
                    random.choice(strategies), api_key, temp, strategies
                )
            case _:
                raise ValueError(f"Model {strategy} not found.")


class Oracle(Prophet):
    """Semantic search (SS) using `text-embedding-3-small`"""

    def __init__(self, api_key: str, temp: float):
        super().__init__(api_key, temp)
        self.name = "Oracle"
        self.model_id = "text-embedding-3-small"
        self.temp = None
        self.table = "lacan_book5"
        self.author = "Lacan"

    # override
    def generate(
        self, search_result: str, message_history: Optional[list]
    ) -> Generator:
        return fake_stream(search_result)

    # override
    def generate_reference(self, content: str, search_result: pd.Series) -> dict:
        return {
            "book": search_result["book"],
            "sentence": search_result["sentence"],
            "content": content,
        }


class Fallacious(Prophet):
    """SS + `gpt-4o` finetuned on Lacan's _Seminar Book V_"""

    def __init__(self, api_key: str, temp: float):
        super().__init__(api_key, temp)
        self.name = "Fallacious"
        self.model_id = "ft:gpt-4o-2024-08-06:personal:book5-prev-5000:9zPWBSz9"
        self.base_model = get_base_model(self.model_id)
        self.table = "lacan_book5"
        self.author = "Lacan"


class Ficticious(Prophet):
    """SS + `gpt-4o-mini` finetuned (FT) on Lacan's _Seminar Book V_"""

    def __init__(self, api_key: str, temp: float):
        super().__init__(api_key, temp)
        self.name = "Ficticious"
        self.model_id = "ft:gpt-4o-mini-2024-07-18:personal:book5-prev-5000:9zOZlylK"
        self.base_model = get_base_model(self.model_id)
        self.table = "lacan_book5"
        self.author = "Lacan"


# class Erratic(Prophet):
#     """Selects snippets randomly from Lacan's _Seminar Book V_"""

#     def __init__(self, api_key: str, temp: float):
#         super().__init__(api_key, temp)
#         self.name = "Erratic"
#         self.model_id = None
#         self.table = "lacan_book5"
#         self.author = "Lacan"

#     def search(self, question: str, df: pd.DataFrame) -> pd.Series:
#         # results = df.sample(iterations)
#         # result = " ".join(results["content"])
#         return df.sample(1).iloc[0]

#         # def search_iterative(df: pd.DataFrame, iterations: int = 1) -> str:
#         #     item = df.sample(1).iloc[0]
#         #     concatenated = concat_items(df, item, iterations)
#         #     return concatenated

#     # override
#     def generate(
#         self, search_result: str, message_history: Optional[list]
#     ) -> Generator:
#         return fake_stream(search_result)

#     # override
#     def generate_reference(self, content: str, search_result: pd.Series) -> dict:
#         return {
#             "book": search_result["book"],
#             "sentence": search_result["sentence"],
#             "content": content,
#         }


class Chimerical(Prophet):
    """SS + FT on Steiner's _An Outline of Occult Science_"""

    def __init__(self, api_key: str, temp: float):
        super().__init__(api_key, temp)
        self.name = "Chimerical"
        self.model_id = "ft:gpt-4o-mini-2024-07-18:personal:steiner:9zyuSD4q"
        self.base_model = get_base_model(self.model_id)
        self.table = "steiner_occult"
        self.author = "Steiner"


class Spectral(Prophet):
    """SS + FT on Hegel's _Philosophy of Mind_"""

    def __init__(self, api_key: str, temp: float):
        super().__init__(api_key, temp)
        self.name = "Spectral"
        self.model_id = "ft:gpt-4o-mini-2024-07-18:personal:hegel:A09OUjD3"
        self.base_model = get_base_model(self.model_id)
        self.table = "hegel_mind"
        self.author = "Hegel"


class Quixotic(Prophet):
    """SS + FT on Marcus Aurelius' _Meditations_"""

    def __init__(self, api_key: str, temp: float):
        super().__init__(api_key, temp)
        self.name = "Quixotic"
        self.model_id = "ft:gpt-4o-mini-2024-07-18:personal:marcus:A09OPfR7"
        self.base_model = get_base_model(self.model_id)
        self.table = "marcus_meditations"
        self.author = "Marcus Aurelius"


# class Apocryphal(Prophet):
#     """SS + FT on Mill's _On Liberty_"""

#     def __init__(self, api_key: str, temp: float):
#         super().__init__(api_key, temp)
#         self.name = "Apocryphal"
#         self.model_id = "ft:gpt-4o-mini-2024-07-18:personal:mill:A09IWIRD"
#         self.base_model = get_base_model(self.model_id)
#         self.table = "mill_liberty"
#         self.author = "Mill"
