from typing import Annotated

from fastapi import Depends, FastAPI, Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.order_history import get_order_history
from app.diagnostics import (
    get_recent_deployments,
    get_top_slow_queries,
    get_query_plan,
)


app = FastAPI(
    title="InfraPilot API",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/orders/history/{user_id}")
def order_history(
    user_id: Annotated[int, Path(ge=1)],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    return get_order_history(db, user_id)


@app.get("/api/diagnostics/deployments")
def recent_deployments(
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    return get_recent_deployments(db)


@app.get("/api/diagnostics/slow-queries")
def top_slow_queries(
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    return get_top_slow_queries(db)


@app.get("/api/diagnostics/query-plan")
def query_plan(
    db: Annotated[Session, Depends(get_db)],
) -> list[str]:
    return get_query_plan(db)