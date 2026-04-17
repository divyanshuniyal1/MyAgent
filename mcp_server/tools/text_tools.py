# mcp_server/tools/text_tools.py

def to_uppercase(text: str) -> str:
    return text.upper()


def to_lowercase(text: str) -> str:
    return text.lower()


def word_count(text: str) -> int:
    return len(text.split())


def reverse_text(text: str) -> str:
    return text[::-1]