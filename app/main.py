from fastapi import FastAPI

from app.database import Base, engine
from app.routes.webhooks import router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="PulseEngine – Webhook Processing Service")
app.include_router(router)
