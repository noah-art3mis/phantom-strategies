import json
from threading import Event

import anyio
import pytest
from fastapi.testclient import TestClient
from starlette.requests import ClientDisconnect
from web_app import create_app

PAYLOAD = {"question": "Why?", "strategy": "Spectral", "temperature": 1}


async def invoke(app, ip, send):
    delivered = False

    async def receive():
        nonlocal delivered
        if not delivered:
            delivered = True
            return {
                "type": "http.request",
                "body": json.dumps(PAYLOAD).encode(),
                "more_body": False,
            }
        await anyio.sleep_forever()

    await app(
        {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.4"},
            "method": "POST",
            "scheme": "http",
            "path": "/api/consult",
            "query_string": b"",
            "root_path": "",
            "http_version": "1.1",
            "headers": [(b"content-type", b"application/json")],
            "client": (ip, 123),
            "server": ("localhost", 80),
        },
        receive,
        send,
    )


def test_partial_delivery_and_global_concurrency_release():
    release = Event()

    class SlowOracle:
        def events(self, *args):
            yield {"type": "delta", "text": "first"}
            assert release.wait(5), "test did not release reference generation"
            yield {"type": "done", "content": "first"}

    app = create_app(SlowOracle())

    async def scenario():
        chunks = [anyio.Event(), anyio.Event()]
        statuses = []

        async def running(index):
            async def send(message):
                if message[
                    "type"
                ] == "http.response.body" and b'"delta"' in message.get("body", b""):
                    chunks[index].set()

            await invoke(app, f"192.0.2.{index}", send)

        async def collect(message):
            if message["type"] == "http.response.start":
                statuses.append(message["status"])

        async with anyio.create_task_group() as tasks:
            tasks.start_soon(running, 0)
            tasks.start_soon(running, 1)
            try:
                with anyio.fail_after(4):
                    await chunks[0].wait()
                    await chunks[1].wait()
                assert not release.is_set()
                await invoke(app, "192.0.2.3", collect)
                assert statuses == [429]
            finally:
                release.set()
        await invoke(app, "192.0.2.3", collect)
        assert statuses == [429, 200]

    anyio.run(scenario)


def test_disconnect_closes_provider_and_does_not_generate_reference():
    closed = []
    references = []

    class Oracle:
        def events(self, *args):
            try:
                yield {"type": "delta", "text": "partial"}
                references.append(True)
                yield {"type": "done"}
            finally:
                closed.append(True)

    app = create_app(Oracle())

    async def scenario():
        async def disconnect(message):
            if message["type"] == "http.response.body":
                raise OSError("client disconnected")

        for ip in range(3):
            with pytest.raises(ClientDisconnect):
                await invoke(app, f"192.0.2.{ip}", disconnect)
        assert len(closed) == 3
        assert references == []

    anyio.run(scenario)


def test_midstream_failure_keeps_partial_output_and_releases_slot(caplog):
    class Oracle:
        def events(self, *args):
            yield {"type": "delta", "text": "partial"}
            raise RuntimeError("secret-provider-message")

    client = TestClient(create_app(Oracle()))
    for _ in range(3):
        response = client.post("/api/consult", json=PAYLOAD)
        events = [json.loads(line) for line in response.iter_lines()]
        assert events[0] == {"type": "delta", "text": "partial"}
        assert events[-1]["type"] == "error"
        assert "secret-provider-message" not in response.text
    assert "RuntimeError" in caplog.text
    assert "secret-provider-message" not in caplog.text
