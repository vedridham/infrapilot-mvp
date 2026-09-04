import random
from datetime import datetime, timedelta, timezone

from faker import Faker
from sqlalchemy import text

from app.database import engine


USER_COUNT = 5_000
ORDERS_PER_USER = 10
BATCH_SIZE = 1_000

fake = Faker()
Faker.seed(42)
random.seed(42)


def chunks(items: list[dict], size: int) -> list[list[dict]]:
    return [items[index:index + size] for index in range(0, len(items), size)]


def main() -> None:
    with engine.begin() as connection:
        existing_user_count = connection.execute(
            text("SELECT COUNT(*) FROM users")
        ).scalar_one()

        if existing_user_count > 0:
            raise SystemExit(
                "The users table already contains data. "
                "Refusing to create duplicate synthetic data."
            )

        users = [
            {
                "email": fake.unique.email(),
                "display_name": fake.name(),
            }
            for _ in range(USER_COUNT)
        ]

        for batch in chunks(users, BATCH_SIZE):
            connection.execute(
                text(
                    "INSERT INTO users (email, display_name) "
                    "VALUES (:email, :display_name)"
                ),
                batch,
            )

        user_ids = connection.execute(
            text("SELECT id FROM users ORDER BY id")
        ).scalars().all()

        now = datetime.now(timezone.utc)
        orders: list[dict] = []

        for user_id in user_ids:
            for _ in range(ORDERS_PER_USER):
                created_at = now - timedelta(
                    days=random.randint(0, 180),
                    minutes=random.randint(0, 1_440),
                )
                orders.append(
                    {
                        "user_id": user_id,
                        "status": random.choices(
                            ["paid", "pending", "failed", "cancelled"],
                            weights=[80, 10, 5, 5],
                        )[0],
                        "total_amount": round(random.uniform(10, 500), 2),
                        "created_at": created_at,
                    }
                )

        for batch in chunks(orders, BATCH_SIZE):
            connection.execute(
                text(
                    "INSERT INTO orders "
                    "(user_id, status, total_amount, created_at) "
                    "VALUES (:user_id, :status, :total_amount, :created_at)"
                ),
                batch,
            )

        order_rows = connection.execute(
            text("SELECT id, status, total_amount, created_at FROM orders ORDER BY id")
        ).mappings().all()

        payments = [
            {
                "order_id": order["id"],
                "provider_reference": f"demo_{order['id']}",
                "status": "completed" if order["status"] == "paid" else "failed",
                "amount": order["total_amount"],
                "created_at": order["created_at"],
            }
            for order in order_rows
        ]

        for batch in chunks(payments, BATCH_SIZE):
            connection.execute(
                text(
                    "INSERT INTO payments "
                    "(order_id, provider_reference, status, amount, created_at) "
                    "VALUES "
                    "(:order_id, :provider_reference, :status, :amount, :created_at)"
                ),
                batch,
            )

    print(
        f"Created {USER_COUNT} users, "
        f"{len(orders)} orders, and {len(payments)} payments."
    )


if __name__ == "__main__":
    main()