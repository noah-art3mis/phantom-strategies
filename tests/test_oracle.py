from types import SimpleNamespace

import pandas as pd
from semantic_search import semantic_search


def test_search_uses_explicit_credentials_and_leaves_corpus_unchanged(monkeypatch):
    def client(*, api_key, **options):
        assert api_key == "test-key"

        def create(**kwargs):
            assert kwargs == {"input": "Why?", "model": "text-embedding-3-small"}
            return SimpleNamespace(data=[SimpleNamespace(embedding=[1.0, 0.0])])

        return SimpleNamespace(embeddings=SimpleNamespace(create=create))

    monkeypatch.setattr("semantic_search.OpenAI", client)
    corpus = pd.DataFrame(
        {"content": ["wrong", "right"], "embedding": [[0.0, 1.0], [1.0, 0.0]]}
    )
    result = semantic_search("Why?", corpus, "test-key")
    assert result["content"] == "right"
    assert list(corpus.columns) == ["content", "embedding"]
