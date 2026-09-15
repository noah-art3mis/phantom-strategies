import pytest
from fastapi.testclient import TestClient
from web_app import create_app


class Oracle:
    def answer(self, question, strategy, temperature):
        assert (question, strategy, temperature) == (
            "What do I desire?",
            "Spectral",
            0.7,
        )
        return {
            "content": "The answer becomes another question.",
            "author": "Hegel",
            "strategy": strategy,
            "book": "An imagined book",
            "sentence": 42,
        }


def test_question_reaches_oracle_and_returns_its_answer():
    client = TestClient(create_app(Oracle()))
    response = client.post(
        "/api/consult",
        json={
            "question": "  What do I desire?  ",
            "strategy": "Spectral",
            "temperature": 0.7,
        },
    )
    assert response.status_code == 200
    assert response.json()["content"] == "The answer becomes another question."
    assert response.json()["author"] == "Hegel"


@pytest.mark.parametrize(
    "change",
    [
        {"question": "   "},
        {"question": "a" * 2001},
        {"strategy": "Unknown"},
        {"temperature": -0.1},
        {"temperature": 1.1},
    ],
)
def test_invalid_consultations_are_rejected_before_generation(change):
    client = TestClient(create_app(Oracle()))
    payload = {
        "question": "What do I desire?",
        "strategy": "Spectral",
        "temperature": 0.7,
    } | change
    assert client.post("/api/consult", json=payload).status_code == 422


def test_unconfigured_oracle_has_an_actionable_unavailable_state(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = TestClient(create_app())
    response = client.post(
        "/api/consult",
        json={"question": "Why?", "strategy": "Spectral", "temperature": 1},
    )
    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_provider_failure_does_not_expose_secrets():
    class BrokenOracle:
        def answer(self, *args):
            raise RuntimeError("private provider diagnostics")

    response = TestClient(create_app(BrokenOracle())).post(
        "/api/consult",
        json={"question": "Why?", "strategy": "Spectral", "temperature": 1},
    )
    assert response.status_code == 502
    assert "private" not in response.text


def test_strategies_expose_existing_choices_without_model_credentials():
    data = TestClient(create_app(Oracle())).get("/api/strategies").json()
    assert [item["name"] for item in data] == [
        "Ficticious",
        "Chimerical",
        "Spectral",
        "Quixotic",
    ]
    assert all(set(item) == {"name", "description"} for item in data)
