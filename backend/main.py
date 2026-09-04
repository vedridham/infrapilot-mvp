from typing import Annotated

from fastapi import Depends, FastAPI, Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.order_history import get_order_history


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