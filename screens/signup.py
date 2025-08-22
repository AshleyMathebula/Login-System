from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)

from utils.signup_helpers import validate_signup_input, create_user


class SignUpScreen(QWidget):
    """
    Sign Up screen widget for creating new user accounts.

    Signals:
        signup_successful (str): Emitted with email on successful signup.
        back_requested: Emitted when user wants to return to previous screen.

    Args:
        parent (QWidget): Parent widget.
        db (Database): Database instance for user data access.
    """
    signup_successful = Signal(str)
    back_requested = Signal()

    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db

        self._setup_ui()

    def _setup_ui(self):
        """Initialize UI components and layout."""
        layout = QVBoxLayout(self)

        title_label = QLabel("Create a New Account")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.input_first_name = QLineEdit()
        self.input_first_name.setPlaceholderText("First Name")
        layout.addWidget(self.input_first_name)

        self.input_last_name = QLineEdit()
        self.input_last_name.setPlaceholderText("Last Name")
        layout.addWidget(self.input_last_name)

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Email")
        layout.addWidget(self.input_email)

        self.input_phone = QLineEdit()
        self.input_phone.setPlaceholderText("Phone Number")
        layout.addWidget(self.input_phone)

        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("Password")
        layout.addWidget(self.input_password)

        self.input_confirm_password = QLineEdit()
        self.input_confirm_password.setEchoMode(QLineEdit.Password)
        self.input_confirm_password.setPlaceholderText("Confirm Password")
        layout.addWidget(self.input_confirm_password)

        self.btn_signup = QPushButton("Sign Up")
        self.btn_signup.clicked.connect(self.on_signup_clicked)
        layout.addWidget(self.btn_signup)

        btn_back = QPushButton("Back")
        btn_back.clicked.connect(lambda: self.back_requested.emit())
        layout.addWidget(btn_back)

        self.setLayout(layout)
        self.input_first_name.setFocus()

    def on_signup_clicked(self):
        """
        Handle signup button click event.

        Validates input fields, creates a user in the database,
        and emits signup_successful signal on success.
        """
        first_name = self.input_first_name.text().strip()
        last_name = self.input_last_name.text().strip()
        email = self.input_email.text().strip().lower()
        phone = self.input_phone.text().strip()
        password = self.input_password.text()
        confirm_password = self.input_confirm_password.text()

        valid, error = validate_signup_input(
            first_name, last_name, email, phone, password, confirm_password
        )
        if not valid:
            QMessageBox.warning(self, "Validation Error", error)
            return

        success, err_msg = create_user(self.db, first_name, last_name, email, phone, password)
        if success:
            QMessageBox.information(self, "Success", "Account created successfully! Please log in.")
            self.signup_successful.emit(email)
            self.clear_form()
        else:
            QMessageBox.warning(self, "Error", err_msg)

    def clear_form(self):
        """Clear all input fields and reset focus."""
        self.input_first_name.clear()
        self.input_last_name.clear()
        self.input_email.clear()
        self.input_phone.clear()
        self.input_password.clear()
        self.input_confirm_password.clear()
        self.input_first_name.setFocus()
