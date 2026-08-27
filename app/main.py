from fastapi import FastAPI
from app.routers import webhooks, ws
from app.database import engine, Base
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="PulseEngine", lifespan=lifespan)

app.include_router(webhooks.router)
app.include_router(ws.router)

@app.get("/health")
async def health():
    return {"status": "ok"}