"""FastAPI entrypoint. Read-only API over precomputed pipeline results."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import init_db
from app.api.routes import companies, scoring, outreach


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Rolling 10 — Customer Discovery", lifespan=lifespan)

# Angular dev server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(companies.router)
app.include_router(scoring.router)
app.include_router(outreach.router)


@app.get("/health")
def health():
    return {"status": "ok"}
