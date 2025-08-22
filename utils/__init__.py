# utils/__init__.py
"""
Utility package initializer.
Exports commonly used utility functions for easy imports.
Configures global logging on import.
"""

from .auth import hash_password, verify_password, generate_reset_code
from .email_utils import send_email
from .logger import configure_logging

# Configure global logging as soon as utils package is imported
configure_logging()
