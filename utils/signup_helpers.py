"""
Signup validation and user creation helpers.
"""

import re
import logging
from utils.auth import hash_password

def validate_signup_input(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    password: str,
    confirm_password: str
) -> tuple[bool, str]:
    """
    Validate signup form inputs.

    Args:
        first_name (str): User's first name.
        last_name (str): User's last name.
        email (str): User's email address.
        phone (str): User's phone number.
        password (str): Password.
        confirm_password (str): Confirmation password.

    Returns:
        tuple[bool, str]: (True, "") if valid, else (False, error message).
    """
    if not first_name or not last_name:
        return False, "Please enter your full name."

    email_regex = r"[^@]+@[^@]+\.[^@]+"
    if not re.match(email_regex, email):
        return False, "Invalid email address."

    phone_regex = r"^\+?\d{7,15}$"
    if not re.match(phone_regex, phone):
        return False, "Invalid phone number."

    if len(password) < 8:
        return False, "Password must be at least 8 characters long."

    if password != confirm_password:
        return False, "Passwords do not match."

    return True, ""

def create_user(db, first_name, last_name, email, phone, password) -> tuple[bool, str]:
    """
    Create a new user in the database.

    Args:
        db: Database instance.
        first_name (str): User's first name.
        last_name (str): User's last name.
        email (str): User's email.
        phone (str): User's phone number.
        password (str): Plaintext password.

    Returns:
        tuple[bool, str]: (True, "") on success, (False, error message) on failure.
    """
    existing_user = db.get_user_by_username(email)
    if existing_user:
        return False, "An account with this email already exists."

    password_hash = hash_password(password)
    success = db.create_user(first_name, last_name, email, phone, password_hash)
    if success:
        logging.info(f"New user created with this email:{email}")
        return True, ""
    else:
        return False, "Failed to create user. Please try again."
