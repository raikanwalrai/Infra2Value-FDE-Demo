from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.incidents import router as incidents_router
from app.api.value_graph import router as value_graph_router


app = FastAPI(
    title="Infra2Value API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "infra2value-api",
    }


app.include_router(value_graph_router)
app.include_router(incidents_router)
