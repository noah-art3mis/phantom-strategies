import json
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


def test_full_consultation_searches_generates_and_assembles_reference(monkeypatch):
    from fastapi.testclient import TestClient
    from web_app import create_app

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    corpus = pd.DataFrame(
        {
            "content": ["An unrelated passage", "The seed passage"],
            "embedding": [[0.0, 1.0], [1.0, 0.0]],
        }
    )
    monkeypatch.setattr(
        "utils.get_data", lambda table: corpus if table == "hegel_mind" else None
    )
    calls = []

    class Stream:
        closed = False

        def __iter__(self):
            for text in (None, "A strange ", "reflection."):
                yield SimpleNamespace(
                    choices=[SimpleNamespace(delta=SimpleNamespace(content=text))]
                )

        def close(self):
            self.closed = True

    stream = Stream()

    def provider(*, api_key, **options):
        assert api_key == "test-key"

        def embed(**kwargs):
            assert kwargs["input"] == "Why?"
            return SimpleNamespace(data=[SimpleNamespace(embedding=[1.0, 0.0])])

        def generate(**kwargs):
            calls.append(kwargs)
            if kwargs["stream"]:
                return stream
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="The Unfamiliar Mind")
                    )
                ]
            )

        return SimpleNamespace(
            embeddings=SimpleNamespace(create=embed),
            chat=SimpleNamespace(completions=SimpleNamespace(create=generate)),
        )

    monkeypatch.setattr("semantic_search.OpenAI", provider)
    monkeypatch.setattr("genai.OpenAI", provider)
    response = TestClient(create_app()).post(
        "/api/consult",
        json={"question": "Why?", "strategy": "Spectral", "temperature": 0.7},
    )
    assert response.status_code == 200
    events = [json.loads(line) for line in response.iter_lines()]
    assert events[:2] == [
        {"type": "delta", "text": "A strange "},
        {"type": "delta", "text": "reflection."},
    ]
    result = events[-1]
    assert result["type"] == "done"
    assert result["content"] == "A strange reflection."
    assert result["author"] == "Hegel"
    assert result["strategy"] == "Spectral"
    assert "The Unfamiliar Mind" in result["book"]
    assert isinstance(result["sentence"], int)
    assert calls[0]["messages"] == [
        {"role": "assistant", "content": "The seed passage"}
    ]
    assert calls[0]["model"] == "ft:gpt-4o-mini-2024-07-18:personal:hegel:A09OUjD3"
    assert calls[0]["temperature"] == 0.7
    assert "A strange reflection." in calls[1]["messages"][0]["content"]
    assert stream.closed
    assert calls[1]["max_tokens"] == 80
