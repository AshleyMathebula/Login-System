"""
Main entry point of the application.
Initializes the PySide6 GUI, creates all screens, and manages navigation using QStackedWidget.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from screens.welcome import WelcomeScreen
from screens.login import LoginScreen
from screens.signup import SignUpScreen
from screens.reset_password import PasswordResetScreen

from utils.logger import configure_logging
from utils.database import Database

# Configure logging globally at import time
configure_logging()


class LoginSystemApp(QMainWindow):
    """
    Main application window that manages screen navigation
    for the login system using a QStackedWidget.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login System")
        self.setGeometry(300, 100, 400, 450)

        # ✅ Create shared database object
        self.db = Database()

        # Create the stacked widget container for screens
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # ✅ Pass db to screens that need it
        self.welcome_screen = WelcomeScreen(self)
        self.login_screen = LoginScreen(self, db=self.db)
        self.signup_screen = SignUpScreen(self, db=self.db)
        self.password_reset_screen = PasswordResetScreen(self, db=self.db)

        # Add all screens to the stack
        self.stack.addWidget(self.welcome_screen)
        self.stack.addWidget(self.login_screen)
        self.stack.addWidget(self.signup_screen)
        self.stack.addWidget(self.password_reset_screen)

        # Show the welcome screen on startup
        self.stack.setCurrentWidget(self.welcome_screen)

        # Connect signals to handle navigation and events
        self.setup_connections()

    def setup_connections(self):
        """Connect signals emitted by screens to respective handlers and navigation."""

        # Welcome screen navigation
        self.welcome_screen.login_requested.connect(
            lambda: self.stack.setCurrentWidget(self.login_screen)
        )
        self.welcome_screen.signup_requested.connect(
            lambda: self.stack.setCurrentWidget(self.signup_screen)
        )
        self.welcome_screen.exit_requested.connect(self.close)  # Close the app

        # Login screen navigation and events
        self.login_screen.login_successful.connect(self.on_login_successful)
        self.login_screen.back_requested.connect(
            lambda: self.stack.setCurrentWidget(self.welcome_screen)
        )
        self.login_screen.password_reset_requested.connect(
            lambda: self.stack.setCurrentWidget(self.password_reset_screen)
        )

        # Signup screen navigation and events
        self.signup_screen.signup_successful.connect(self.on_signup_successful)
        self.signup_screen.back_requested.connect(
            lambda: self.stack.setCurrentWidget(self.welcome_screen)
        )

        # Password reset screen navigation and events
        self.password_reset_screen.reset_successful.connect(
            lambda: self.stack.setCurrentWidget(self.login_screen)
        )
        self.password_reset_screen.back_requested.connect(
            lambda: self.stack.setCurrentWidget(self.welcome_screen)
        )

    def on_login_successful(self, username: str):
        """
        Handler for successful login event.

        Args:
            username (str): The email/username of the logged-in user.
        """
        print(f"User '{username}' logged in.")
        # TODO: Replace with real post-login screen/navigation (e.g., dashboard)
        self.stack.setCurrentWidget(self.welcome_screen)

    def on_signup_successful(self, username: str):
        """
        Handler after successful signup.

        Navigates to login screen and pre-fills the username/email field.

        Args:
            username (str): The email of the newly signed up user.
        """
        self.stack.setCurrentWidget(self.login_screen)
        self.login_screen.input_username.setText(username)
        self.login_screen.input_password.clear()
        self.login_screen.input_password.setFocus()

    def closeEvent(self, event):
        """
        Handle cleanup before the application closes, such as closing the database connection.
        """
        if self.db:
            self.db.close()  # ✅ Close DB connection safely
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginSystemApp()
    window.show()
    sys.exit(app.exec())
