from __future__ import annotations
from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz")
def health():
    return {"status": "ok"}
