import logging
import os
from datetime import datetime
from typing import Optional, Dict

import mysql.connector
from dotenv import load_dotenv

load_dotenv()  # loads .env file

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))


class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        self.conn.autocommit = True

    def close(self):
        self.conn.close()

    # ------------------- USERS -------------------

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        return user

    def create_user(self, first_name: str, last_name: str, email: str, phone: str, password_hash: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (first_name, last_name, email, phone_number, password_hash)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (first_name, last_name, email, phone, password_hash)
            )
            cursor.close()
            logging.info(f"Created user {email}")
            return True
        except mysql.connector.Error as e:
            logging.error(f"Failed to create user {email}: {e}")
            return False

    def update_user_password(self, user_id: int, new_password_hash: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE users SET password_hash=%s WHERE user_id=%s",
                (new_password_hash, user_id)
            )
            cursor.close()
            logging.info(f"Password updated for user_id {user_id}")
            return True
        except mysql.connector.Error as e:
            logging.error(f"Failed to update password for user_id {user_id}: {e}")
            return False

    # ------------------- PASSWORD RESET TOKENS -------------------

    def create_password_reset_token(self, user_id: int, token: str, expires_at: datetime) -> bool:
        """Store the reset token in uppercase."""
        token = token.strip().upper()
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES (%s, %s, %s)
                """,
                (user_id, token, expires_at)
            )
            cursor.close()
            logging.info(f"Created password reset token {token} for user_id {user_id}")
            return True
        except mysql.connector.Error as e:
            logging.error(f"Failed to create reset token for user_id {user_id}: {e}")
            return False

    def get_password_reset_token(self, token: str) -> Optional[Dict]:
        """Retrieve token case-insensitively. Expiry & used status checked in Python."""
        token = token.strip().upper()
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT * FROM password_reset_tokens
            WHERE UPPER(token)=%s
            """,
            (token,)
        )
        result = cursor.fetchone()
        cursor.close()
        return result

    def mark_token_used(self, token_id: int) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE password_reset_tokens SET is_used=TRUE WHERE token_id=%s",
                (token_id,)
            )
            cursor.close()
            logging.info(f"Marked token {token_id} as used")
            return True
        except mysql.connector.Error as e:
            logging.error(f"Failed to mark token {token_id} as used: {e}")
            return False

    # ------------------- LOGS -------------------

    def log_action(self, user_id: Optional[int], action: str, ip_address: Optional[str] = None) -> None:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO logs (user_id, action, ip_address) VALUES (%s, %s, %s)",
                (user_id, action, ip_address)
            )
            cursor.close()
            logging.info(f"Logged action '{action}' for user_id {user_id}")
        except mysql.connector.Error as e:
            logging.error(f"Failed to log action '{action}' for user_id {user_id}: {e}")
