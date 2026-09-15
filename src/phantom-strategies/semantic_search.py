import numpy as np
import pandas as pd
from openai import OpenAI


def semantic_search(question: str, df: pd.DataFrame, api_key: str) -> pd.Series:
    client = OpenAI(api_key=api_key, timeout=45, max_retries=0)
    response = client.embeddings.create(input=question, model="text-embedding-3-small")
    vector = response.data[0].embedding
    scores = df["embedding"].apply(lambda item: _cosine_similarity(item, vector))
    return df.loc[scores.idxmax()]


def _cosine_similarity(a: np.ndarray, b: list):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
