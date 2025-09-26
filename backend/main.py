import os, time
import structlog
from fastapi import FastAPI, Request
from psycopg import connect
from psycopg.rows import dict_row

logger = structlog.get_logger()
app = FastAPI(title="StackShaper Backend")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/stackshaper")

def db_conn():
    return connect(DATABASE_URL, row_factory=dict_row)

@app.middleware("http")
async def access_log(request: Request, call_next):
    start = time.time()
    resp = await call_next(request)
    duration_ms = int((time.time() - start) * 1000)
    logger.info(
        "http_request",
        method=request.method,
        path=str(request.url.path),
        status=resp.status_code,
        duration_ms=duration_ms,
    )
    return resp

@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "backend",
        "version": "v1.0.0"
    }


@app.get("/dbcheck")
def dbcheck():
    with db_conn() as con:
        with con.cursor() as cur:
            cur.execute("SELECT NOW() AS now;")
            row = cur.fetchone()
            return {"db": "ok", "now": str(row["now"])}
