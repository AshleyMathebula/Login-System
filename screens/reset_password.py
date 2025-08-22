import logging

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)

from utils.reset_helpers import (
    send_reset_email,
    create_reset_token,
    validate_reset_token,
    mark_token_used,
    reset_password,
)


class PasswordResetScreen(QWidget):
    """
    Password Reset screen for users to reset forgotten passwords.

    Signals:
        reset_successful: Emitted when password reset completes successfully.
        back_requested: Emitted when user wants to return to previous screen.

    Args:
        parent (QWidget): Parent widget.
        db (Database): Database instance for user data access.
    """
    reset_successful = Signal()
    back_requested = Signal()

    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db

        self._setup_ui()

    def _setup_ui(self):
        """Initialize UI components and layout."""
        layout = QVBoxLayout(self)

        title_label = QLabel("Reset Your Password")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Enter your registered email")
        layout.addWidget(self.input_email)

        self.btn_send_code = QPushButton("Send Reset Code")
        self.btn_send_code.clicked.connect(self.on_send_code)
        layout.addWidget(self.btn_send_code)

        self.input_token = QLineEdit()
        self.input_token.setPlaceholderText("Enter reset code")
        layout.addWidget(self.input_token)

        self.input_new_password = QLineEdit()
        self.input_new_password.setEchoMode(QLineEdit.Password)
        self.input_new_password.setPlaceholderText("Enter new password (min 8 chars)")
        layout.addWidget(self.input_new_password)

        self.btn_reset_password = QPushButton("Reset Password")
        self.btn_reset_password.clicked.connect(self.on_reset_password)
        layout.addWidget(self.btn_reset_password)

        btn_back = QPushButton("Back")
        btn_back.clicked.connect(lambda: self.back_requested.emit())
        layout.addWidget(btn_back)

        self.setLayout(layout)
        self.input_email.setFocus()

    def on_send_code(self):
        """Send password reset code email after validating the email."""
        email = self.input_email.text().strip().lower()
        if not email:
            QMessageBox.warning(self, "Error", "Please enter your email.")
            return

        user = self.db.get_user_by_username(email)
        if not user:
            QMessageBox.warning(self, "Error", "Email not found.")
            logging.warning(f"Password reset requested for non-existing email: {email}")
            return

        token = create_reset_token(self.db, user["user_id"])
        if not token:
            QMessageBox.warning(self, "Error", "Failed to create reset token.")
            return

        if send_reset_email(email, user["first_name"], token):
            QMessageBox.information(self, "Email Sent", "Reset code sent to your email.")
        else:
            QMessageBox.warning(self, "Error", "Failed to send reset email.")

    def on_reset_password(self):
        """Validate token and new password, then reset the password."""
        token = self.input_token.text().strip()
        new_password = self.input_new_password.text()

        if not token or not new_password:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return
        if len(new_password) < 8:
            QMessageBox.warning(self, "Error", "Password must be at least 8 characters.")
            return

        if not validate_reset_token(self.db, token):
            QMessageBox.warning(self, "Error", "Invalid or expired reset code.")
            return

        token_data = self.db.get_password_reset_token(token)
        user_id = token_data["user_id"]

        if reset_password(self.db, user_id, new_password):
            mark_token_used(self.db, token_data["token_id"])
            QMessageBox.information(self, "Success", "Password reset successfully.")
            self.reset_successful.emit()
            self.clear_form()
        else:
            QMessageBox.warning(self, "Error", "Failed to reset password.")

    def clear_form(self):
        """Clear input fields and reset focus."""
        self.input_email.clear()
        self.input_token.clear()
        self.input_new_password.clear()
        self.input_email.setFocus()
