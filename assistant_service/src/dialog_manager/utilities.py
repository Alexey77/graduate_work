import hashlib


def get_hash(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()
