"""Password hashing and verification with Argon2id."""

from pwdlib import PasswordHash

_password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Return the Argon2id hash of a plaintext password."""
    return _password_hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Check a plaintext password against its stored hash."""
    return _password_hasher.verify(password, hashed_password)
