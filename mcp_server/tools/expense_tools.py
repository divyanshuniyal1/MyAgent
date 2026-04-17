# mcp_server/tools/expense_tools.py

from memory.db import SessionLocal
from memory.models import Message


def add_expense(user_id: int, amount: int, note: str = ""):
    db = SessionLocal()
    try:
        msg = Message(
            user_id=user_id,
            content=f"Expense: {amount} | {note}",
            role="user",
            agent="expense"
        )
        db.add(msg)
        db.commit()
    finally:
        db.close()

    return f"Expense of {amount} added"


def get_expenses(user_id: int):
    db = SessionLocal()
    try:
        expenses = db.query(Message).filter(
            Message.user_id == user_id,
            Message.agent == "expense"
        ).all()
        return [e.content for e in expenses]
    finally:
        db.close()
