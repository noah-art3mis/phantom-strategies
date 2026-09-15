"""Stream oracle events without buffering the answer at the HTTP boundary."""

import json
import logging
import traceback
from pathlib import Path

import anyio
from starlette.concurrency import iterate_in_threadpool, run_in_threadpool
from starlette.responses import StreamingResponse

FAILURE = "The connection to the oracle was interrupted. Please try again."


def log_failure(error):
    # Never log exception messages, source lines, locals, or request content.
    frames = traceback.extract_tb(error.__traceback__)
    logging.getLogger(__name__).error(
        "Consultation failed: %s; frames=%s",
        type(error).__name__,
        " -> ".join(
            f"{Path(frame.filename).name}:{frame.lineno}:{frame.name}"
            for frame in frames
        ),
    )


class OracleResponse(StreamingResponse):
    def __init__(self, events, first):
        self.events = events
        super().__init__(
            self.encode(first),
            media_type="application/x-ndjson",
            headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
        )

    async def encode(self, first):
        yield json.dumps(first) + "\n"
        try:
            async for event in iterate_in_threadpool(self.events):
                yield json.dumps(event) + "\n"
        except Exception as error:  # noqa: BLE001 - serialize failures after headers have been sent.
            log_failure(error)
            yield json.dumps({"type": "error", "detail": FAILURE}) + "\n"

    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        finally:
            # Closing a suspended generator runs the provider stream's finally.
            # Shield cleanup from client disconnect cancellation.
            with anyio.CancelScope(shield=True):
                await run_in_threadpool(self.events.close)
                await self.body_iterator.aclose()
