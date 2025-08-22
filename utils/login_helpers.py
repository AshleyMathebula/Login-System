"""
Login validation, authentication, and lockout management helpers.
"""

import logging
import time
from utils.auth import verify_password

class LoginLockoutManager:
    """
    Manages login attempts and lockout timings to prevent brute force attacks.
    """
    MAX_ATTEMPTS = 3
    LOCKOUT_DURATION = 300  # seconds (5 minutes)

    def __init__(self):
        self.failed_attempts = {}  # username -> int
        self.lockout_expiry = {}   # username -> timestamp

    def increment_failed_attempts(self, username: str) -> None:
        """
        Increment failed login attempts and set lockout expiry if max reached.
        """
        attempts = self.failed_attempts.get(username, 0) + 1
        self.failed_attempts[username] = attempts

        if attempts >= self.MAX_ATTEMPTS:
            self.lockout_expiry[username] = time.time() + self.LOCKOUT_DURATION
            logging.warning(f"User {username} locked out due to too many failed attempts.")

    def clear_lockout(self, username: str) -> None:
        """
        Clear failed attempts and lockout status for a user.
        """
        self.failed_attempts.pop(username, None)
        self.lockout_expiry.pop(username, None)

    def is_locked_out(self, username: str) -> bool:
        """
        Check if the user is currently locked out.

        Returns:
            bool: True if locked out, False otherwise.
        """
        expiry = self.lockout_expiry.get(username)
        if expiry is None:
            return False

        if time.time() > expiry:
            # Lockout expired
            self.clear_lockout(username)
            return False

        return True

    def get_remaining_lockout_minutes(self, username: str) -> int:
        """
        Get remaining lockout time in minutes.

        Returns 0 if not locked out.
        """
        expiry = self.lockout_expiry.get(username)
        if not expiry:
            return 0

        remaining = max(0, int((expiry - time.time()) / 60))
        return remaining

def validate_login_input(username: str, password: str) -> tuple[bool, str]:
    """
    Validate login inputs.

    Args:
        username (str): Email or username.
        password (str): Password.

    Returns:
        tuple[bool, str]: (True, "") if valid, else (False, error message).
    """
    if not username or not password:
        return False, "Please enter both username and password."

    if "@" not in username or "." not in username:
        return False, "Please enter a valid email address."

    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    return True, ""

def authenticate_user(db, username: str, password: str) -> tuple[bool, dict]:
    """
    Authenticate user credentials against the database.

    Args:
        db: Database instance.
        username (str): Email.
        password (str): Plaintext password.

    Returns:
        tuple[bool, dict]: (True, user_data) if authenticated, else (False, {}).
    """
    user = db.get_user_by_username(username)
    if not user:
        logging.warning(f"Authentication failed: user {username} not found.")
        return False, {}

    if not verify_password(user["password_hash"], password):
        logging.warning(f"Authentication failed: invalid password for user {username}.")
        return False, {}

    return True, user
