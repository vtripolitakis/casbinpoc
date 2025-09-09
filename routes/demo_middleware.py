from __future__ import annotations
from fastapi import APIRouter, Request
from auth.middleware import requires

router = APIRouter()


@router.post("/demo-middleware")
@requires("read")
def demo_middleware(request: Request):
    return {"status": "ok", "message": "Access granted for demo middleware endpoint"}
