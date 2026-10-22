"""HTTP and static-file entry point for the standalone Prophetic Strategies website."""

import os
from ipaddress import ip_address
from pathlib import Path
from typing import Literal

from admission import Admission
from constants import STRATEGIES
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from oracle_stream import FAILURE, OracleResponse, log_failure
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool


class Consultation(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    question: str = Field(min_length=1, max_length=2000)
    strategy: Literal["Ficticious", "Chimerical", "Spectral", "Quixotic"]
    temperature: float = Field(ge=0, le=1)


class LiveOracle:
    def events(self, question, strategy, temperature):
        from Prophet import Prophet

        from utils import get_data

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                503, "The oracle is temporarily unavailable. Please try again later."
            )
        prophet = Prophet.get_prophet(
            strategy, api_key, temperature, [s["name"] for s in STRATEGIES]
        )
        result = prophet.search(question, get_data(prophet.table))
        stream = prophet.generate(result["content"], message_history=[])
        content = ""
        try:
            for chunk in stream:
                text = chunk.choices[0].delta.content if chunk.choices else None
                if text:
                    content += text
                    yield {"type": "delta", "text": text}
        finally:
            stream.close()
        if not content.strip():
            raise RuntimeError("Empty generation")
        reference = prophet.generate_reference(content, result)
        yield {
            "type": "done",
            "content": content,
            "author": prophet.author,
            "strategy": strategy,
            "book": reference["book"],
            "sentence": reference["sentence"],
        }


def create_app(oracle=None, admission=None, trust_proxy=None):
    app = FastAPI(title="Prophetic Strategies", docs_url=None, redoc_url=None)
    service = oracle if oracle is not None else LiveOracle()
    gate = admission if admission is not None else Admission()
    behind_proxy = (
        os.environ.get("RENDER") == "true" if trust_proxy is None else trust_proxy
    )

    async def admitted(request: Request):
        visitor = request.client.host if request.client else "unknown"
        if behind_proxy and request.headers.get("x-forwarded-for"):
            # The nearest proxy appends the peer; ignore client-supplied prefixes.
            candidate = request.headers["x-forwarded-for"].split(",")[-1].strip()
            try:
                visitor = str(ip_address(candidate))
            except ValueError:
                raise HTTPException(400, "Invalid forwarding address.") from None
        with gate.slot(visitor):
            yield

    @app.get("/api/strategies")
    def strategies():
        return STRATEGIES

    @app.post("/api/consult", dependencies=[Depends(admitted)])
    async def consult(request: Consultation):
        events = None
        try:
            events = service.events(
                request.question, request.strategy, request.temperature
            )
            first = await run_in_threadpool(next, events, None)
            if first is None:
                raise RuntimeError("Empty oracle stream")
            return OracleResponse(events, first)
        except HTTPException:
            if events is not None:
                await run_in_threadpool(events.close)
            raise
        except Exception as error:  # noqa: BLE001 - HTTP boundary must not expose provider diagnostics.
            if events is not None:
                await run_in_threadpool(events.close)
            log_failure(error)
            raise HTTPException(502, FAILURE) from None

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    dist = Path(__file__).resolve().parents[2] / "web" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="website")
    return app


app = create_app()
