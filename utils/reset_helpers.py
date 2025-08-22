"""
Helpers for password reset functionality.
"""

import logging
import secrets
import string
from datetime import datetime, timedelta
from utils.email_utils import send_email
from utils.auth import hash_password

# Token expiry time in minutes
RESET_TOKEN_EXPIRY_MINUTES = 5


def generate_reset_code(length: int = 6) -> str:
    """
    Generate a secure short reset code (uppercase alphanumeric).

    Args:
        length (int): Length of the code (default 6).

    Returns:
        str: Alphanumeric reset code.
    """
    alphabet = string.ascii_uppercase + string.digits  # A-Z, 0-9
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def create_reset_token(db, user_id: int) -> str | None:
    """
    Create a new password reset token for a user and store in DB.

    Args:
        db: Database instance
        user_id (int): User ID in DB

    Returns:
        str | None: Token string if created, else None
    """
    token = generate_reset_code().upper()  # Always uppercase
    expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRY_MINUTES)

    success = db.create_password_reset_token(user_id, token, expires_at)
    if success:
        logging.info(f"Created reset token {token} for user_id {user_id}")
        return token
    else:
        logging.error(f"Failed to create reset token for user_id {user_id}")
        return None


def send_reset_email(email: str, first_name: str, token: str) -> bool:
    """
    Send the password reset email with the token.
    """
    subject = "Password Reset Request"
    body = (
        f"Hello {first_name},\n\n"
        f"Use the following code to reset your password:\n\n"
        f"{token}\n\n"
        f"This code expires in {RESET_TOKEN_EXPIRY_MINUTES} minutes.\n\n"
        f"If you did not request this, please ignore this email."
    )
    return send_email(email, subject, body)


def validate_reset_token(db, token: str) -> bool:
    """
    Validate that the reset token exists, is unused, not expired.
    Case-insensitive comparison (stored uppercase).
    """
    token = token.strip().upper()  # normalize input
    token_data = db.get_password_reset_token(token)

    if not token_data:
        logging.info(f"Token not found: {token}")
        return False

    if token_data.get("is_used"):
        logging.info(f"Token already used: {token}")
        return False

    expires_at = token_data["expires_at"]
    # Convert string to datetime if necessary
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)

    if expires_at < datetime.utcnow():
        logging.info(f"Token expired: {token} | expires_at: {expires_at}")
        return False

    return True


def mark_token_used(db, token_id: int) -> bool:
    """
    Mark a reset token as used to prevent reuse.
    """
    return db.mark_token_used(token_id)


def reset_password(db, user_id: int, new_password: str) -> bool:
    """
    Update user's password hash in the database.
    """
    password_hash = hash_password(new_password)
    success = db.update_user_password(user_id, password_hash)

    if success:
        logging.info(f"Password reset successful for user_id {user_id}")
    else:
        logging.error(f"Failed to reset password for user_id {user_id}")

    return success
