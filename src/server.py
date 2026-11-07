"""FastAPI backend server for SiteSense Zero-Rework Construction Agent."""
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from src.models import WorkerQueryRequest, RFIDocument
from src.agent import SiteSenseRFIAgent
from src.config import HINDSIGHT_BANK_ID, USE_LIVE_HINDSIGHT

app = FastAPI(
    title="SiteSense RFI - Zero-Rework Construction Agent",
    description="Autonomous Site Agent powered by Vectorize Hindsight memory to eliminate costly construction errors.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global singleton agent
agent = SiteSenseRFIAgent()
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "hindsight_bank": HINDSIGHT_BANK_ID,
        "mode": "live_cloud" if USE_LIVE_HINDSIGHT else "local_simulator",
        "active_rfis_count": len(agent.get_all_rfis())
    }


@app.get("/api/rfis")
def list_rfis():
    return {"rfis": [r.model_dump() for r in agent.get_all_rfis()]}


@app.post("/api/rfis")
def ingest_rfi(rfi: RFIDocument):
    try:
        res = agent.add_rfi(rfi)
        return {"status": "success", "result": res, "rfi": rfi.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
def evaluate_query(query: WorkerQueryRequest):
    try:
        response = agent.evaluate_worker_query(query)
        return response.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memories")
def inspect_memories():
    return {
        "bank_id": agent.memory.bank_id,
        "memories": agent.memory.list_all_memories()
    }


@app.get("/api/benchmarks")
def get_benchmarks():
    return {"benchmarks": [b.model_dump() for b in agent.get_benchmarks()]}


# Serve static web frontend
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    def index():
        return FileResponse(str(STATIC_DIR / "index.html"))
