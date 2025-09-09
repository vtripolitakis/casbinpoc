from __future__ import annotations
from fastapi import FastAPI
from routes.api import router as api_router
from routes.healthcheck import router as health_router
from routes.demo_middleware import router as demo_middleware_router

app = FastAPI(title="Casbin Resolver API")
app.include_router(api_router)
app.include_router(health_router)
app.include_router(demo_middleware_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
