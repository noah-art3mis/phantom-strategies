from admission import Admission
from fastapi.testclient import TestClient
from web_app import create_app


class Oracle:
    calls = 0

    def events(self, *args):
        self.calls += 1
        yield {"type": "done", "content": "answer"}


def test_repeated_consultations_are_rejected_before_provider_work():
    oracle = Oracle()
    client = TestClient(create_app(oracle))
    payload = {"question": "Why?", "strategy": "Spectral", "temperature": 1}
    for _ in range(3):
        assert client.post("/api/consult", json=payload).status_code == 200
    response = client.post("/api/consult", json=payload)
    assert response.status_code == 429
    assert 0 < int(response.headers["retry-after"]) <= 60
    assert oracle.calls == 3
    assert client.get("/api/health").status_code == 200


def test_rolling_windows_expire_and_hourly_quota_survives_minute_resets():
    now = [0.0]
    client = TestClient(create_app(Oracle(), Admission(lambda: now[0])))
    payload = {"question": "Why?", "strategy": "Spectral", "temperature": 1}
    for attempt in range(20):
        now[0] = (attempt // 3) * 60
        assert client.post("/api/consult", json=payload).status_code == 200
    now[0] = 420
    rejected = client.post("/api/consult", json=payload)
    assert rejected.status_code == 429
    assert rejected.headers["retry-after"] == "3180"
    now[0] = 3600
    assert client.post("/api/consult", json=payload).status_code == 200


def test_global_quota_applies_across_visitors_and_expires():
    now = [0.0]
    client = TestClient(
        create_app(Oracle(), Admission(lambda: now[0]), trust_proxy=True)
    )
    payload = {"question": "Why?", "strategy": "Spectral", "temperature": 1}
    for ip in range(30):
        assert (
            client.post(
                "/api/consult",
                json=payload,
                headers={"X-Forwarded-For": f"192.0.2.{ip}"},
            ).status_code
            == 200
        )
    headers = {"X-Forwarded-For": "192.0.2.99"}
    assert client.post("/api/consult", json=payload, headers=headers).status_code == 429
    now[0] = 60
    assert client.post("/api/consult", json=payload, headers=headers).status_code == 200


def test_forwarded_prefixes_cannot_bypass_limit_and_local_headers_are_ignored():
    payload = {"question": "Why?", "strategy": "Spectral", "temperature": 1}
    for trusted in (False, True):
        client = TestClient(create_app(Oracle(), trust_proxy=trusted))
        for attempt in range(4):
            headers = {"X-Forwarded-For": f"192.0.2.{attempt}, 203.0.113.1"}
            response = client.post("/api/consult", json=payload, headers=headers)
            assert response.status_code == (200 if attempt < 3 else 429)
