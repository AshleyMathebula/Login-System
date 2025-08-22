"""
Authentication helpers: password hashing, verification, and reset code generation.
"""

import hashlib
import secrets

def hash_password(password: str) -> str:
    """
    Hash a plaintext password with a random salt using SHA-256.

    Args:
        password (str): Plaintext password to hash.

    Returns:
        str: Salt and hashed password concatenated as 'salt$hash'.
    """
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(stored: str, password: str) -> bool:
    """
    Verify a plaintext password against the stored salted hash.

    Args:
        stored (str): Stored password hash in format 'salt$hash'.
        password (str): Plaintext password to verify.

    Returns:
        bool: True if password matches, False otherwise.
    """
    try:
        salt, stored_hash = stored.split("$")
    except ValueError:
        return False

    computed_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return computed_hash == stored_hash

def generate_reset_code(length: int = 32) -> str:
    """
    Generate a cryptographically secure reset code.

    Args:
        length (int): Length of the hex reset code (default 32).

    Returns:
        str: Hexadecimal reset code string.
    """
    return secrets.token_hex(length // 2)
