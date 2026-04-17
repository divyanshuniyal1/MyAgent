# memory/memory_service.py

from memory.db import SessionLocal
from memory.models import Message


def save_message(user_id: int, content: str, role: str, agent: str):
    db = SessionLocal()

    msg = Message(
        user_id=user_id,
        content=content,
        role=role,
        agent=agent
    )

    db.add(msg)
    db.commit()
    db.close()


def get_last_messages(user_id: int, limit: int = 5):
    db = SessionLocal()

    messages = (
        db.query(Message)
        .filter(Message.user_id == user_id)
        .order_by(Message.timestamp.desc())
        .limit(limit)
        .all()
    )

    db.close()

    return [
        {
            "role": m.role,
            "content": m.content
        }
        for m in reversed(messages)
    ]

def save_expense(user_id: int, amount: int):
    db = SessionLocal()

    msg = Message(
        user_id=user_id,
        content=f"Expense: {amount}",
        role="user",
        agent="expense"
    )

    db.add(msg)
    db.commit()
    db.close()