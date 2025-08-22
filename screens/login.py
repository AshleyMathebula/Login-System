from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Signal, QTimer, Qt
import logging
from utils.login_helpers import validate_login_input, LoginLockoutManager, authenticate_user

class LoginScreen(QWidget):
    """
    Login screen widget for user authentication.

    Signals:
        login_successful (str): Emitted with username on successful login.
        back_requested: Emitted when user wants to return to previous screen.
        password_reset_requested: Emitted when user requests password reset.

    Args:
        parent (QWidget): Parent widget.
        db (Database): Database instance for user data access.
    """
    login_successful = Signal(str)
    back_requested = Signal()
    password_reset_requested = Signal()

    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.lockout_manager = LoginLockoutManager()
        self._is_logging_in = False

        self._setup_ui()
        self._setup_timers()

    def _setup_ui(self):
        """Initialize UI components and layout."""
        layout = QVBoxLayout(self)

        self.label = QLabel("Login to your account")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Email")
        self.input_username.setClearButtonEnabled(True)
        layout.addWidget(self.input_username)

        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText("Password")
        self.input_password.setClearButtonEnabled(True)
        layout.addWidget(self.input_password)

        self.btn_login = QPushButton("Login")
        self.btn_login.clicked.connect(self._on_login_clicked)
        layout.addWidget(self.btn_login)

        self.loading_label = QLabel("")
        self.loading_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.loading_label)

        btn_layout = QHBoxLayout()
        self.btn_forgot = QPushButton("Forgot Password?")
        self.btn_forgot.clicked.connect(lambda: self.password_reset_requested.emit())
        btn_layout.addWidget(self.btn_forgot)

        self.btn_back = QPushButton("Back")
        self.btn_back.clicked.connect(lambda: self.back_requested.emit())
        btn_layout.addWidget(self.btn_back)

        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.input_username.setFocus()

    def _setup_timers(self):
        """Set up timer to simulate login delay."""
        self._login_timer = QTimer()
        self._login_timer.setSingleShot(True)
        self._login_timer.timeout.connect(self._complete_login_attempt)

    def _on_login_clicked(self):
        """Validate input and start login process."""
        if self._is_logging_in:
            return  # Prevent multiple clicks

        username = self.input_username.text().strip().lower()
        password = self.input_password.text()

        valid, error = validate_login_input(username, password)
        if not valid:
            QMessageBox.warning(self, "Validation Error", error)
            return

        if self.lockout_manager.is_locked_out(username):
            remaining = self.lockout_manager.get_remaining_lockout_minutes(username)
            QMessageBox.warning(
                self, "Locked Out",
                f"Too many failed attempts. Try again in {remaining} minutes."
            )
            return

        self._set_login_state(True)
        self.loading_label.setText("Logging in... Please wait.")
        self._pending_username = username
        self._pending_password = password
        self._login_timer.start(1000)  # simulate delay

    def _complete_login_attempt(self):
        """Complete login attempt by authenticating credentials."""
        username = self._pending_username
        password = self._pending_password

        success, user = authenticate_user(self.db, username, password)
        if success:
            self.lockout_manager.clear_lockout(username)
            logging.info(f"User '{username}' logged in successfully.")
            self.login_successful.emit(username)
            self._clear_form()
        else:
            self.lockout_manager.increment_failed_attempts(username)
            attempts_left = 3 - self.lockout_manager.failed_attempts.get(username, 0)
            if self.lockout_manager.is_locked_out(username):
                remaining = self.lockout_manager.get_remaining_lockout_minutes(username)
                QMessageBox.warning(
                    self, "Locked Out",
                    f"Too many failed attempts. Try again in {remaining} minutes."
                )
            else:
                QMessageBox.warning(
                    self, "Login Failed",
                    f"Invalid credentials. {attempts_left} attempts left."
                )
                self.input_password.clear()
                self.input_password.setFocus()

        self._set_login_state(False)
        self.loading_label.setText("")

    def _set_login_state(self, enabled: bool):
        """Enable or disable login controls to prevent concurrent actions."""
        self._is_logging_in = enabled
        self.input_username.setDisabled(enabled)
        self.input_password.setDisabled(enabled)
        self.btn_login.setDisabled(enabled)
        self.btn_forgot.setDisabled(enabled)
        self.btn_back.setDisabled(enabled)

    def _clear_form(self):
        """Clear input fields and reset focus."""
        self.input_username.clear()
        self.input_password.clear()
        self.input_username.setFocus()
