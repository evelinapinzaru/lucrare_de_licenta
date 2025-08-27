# Standard library imports
from typing import Dict

# Third-party imports
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

session_users: Dict[str, str] = {}

__all__ = [
    "hash_password",
    "verify_password",
    "generate_avatar"
]

password_hasher = PasswordHasher(time_cost=2, memory_cost=49152, parallelism=1)

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:
        return password_hasher.verify(hashed, password)
    except VerificationError:
        return False

def generate_avatar(username: str) -> Dict[str, str]:
    initial = username[0].upper()
    colors = ["#DC2626", "#EA580C", "#D97706", "#CA8A04",
              "#65A30D", "#16A34A", "#059669", "#0891B2",
              "#0284C7", "#2563EB", "#4F46E5", "#7C3AED",
              "#9333EA", "#C026D3", "#DB2777", "#E11D48"]

    color_index = hash(username) % len(colors)

    return {
        "initial": initial,
        "bg_color": colors[color_index]
    }