from sqlalchemy import text
from sqlalchemy.orm import Session


ORDER_HISTORY_QUERY = text(
    """
    SELECT id, status, total_amount, created_at
    FROM orders
    WHERE user_id = :user_id
    ORDER BY created_at DESC
    LIMIT 20
    """
)


def get_order_history(db: Session, user_id: int) -> list[dict]:
    result = db.execute(ORDER_HISTORY_QUERY, {"user_id": user_id})
    return [dict(row) for row in result.mappings()]