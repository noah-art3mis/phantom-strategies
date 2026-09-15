"""HTTP and static-file entry point for the standalone Phantom website."""

import os
from pathlib import Path
from typing import Literal

from constants import STRATEGIES
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field


class Consultation(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    question: str = Field(min_length=1, max_length=2000)
    strategy: Literal["Ficticious", "Chimerical", "Spectral", "Quixotic"]
    temperature: float = Field(ge=0, le=1)


class LiveOracle:
    def answer(self, question, strategy, temperature):
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
        try:
            content = "".join(
                chunk.choices[0].delta.content or ""
                for chunk in stream
                if chunk.choices
            )
        finally:
            stream.close()
        if not content.strip():
            raise RuntimeError("Empty generation")
        reference = prophet.generate_reference(content, result)
        return {
            "content": content,
            "author": prophet.author,
            "strategy": strategy,
            "book": reference["book"],
            "sentence": reference["sentence"],
        }


def create_app(oracle=None):
    app = FastAPI(title="Phantom Strategies", docs_url=None, redoc_url=None)
    service = oracle if oracle is not None else LiveOracle()

    @app.get("/api/strategies")
    def strategies():
        return STRATEGIES

    @app.post("/api/consult")
    def consult(request: Consultation):
        try:
            return service.answer(
                request.question, request.strategy, request.temperature
            )
        except HTTPException:
            raise
        except Exception:  # noqa: BLE001 - HTTP boundary must not expose provider diagnostics.
            raise HTTPException(
                502, "The connection to the oracle was interrupted. Please try again."
            ) from None

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    dist = Path(__file__).resolve().parents[2] / "web" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="website")
    return app


app = create_app()
