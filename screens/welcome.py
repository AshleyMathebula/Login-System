from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal

class WelcomeScreen(QWidget):
    """
    Initial welcome screen allowing navigation to login, signup, or exit.

    Signals:
        login_requested: Emitted when user clicks login.
        signup_requested: Emitted when user clicks signup.
        exit_requested: Emitted when user clicks exit.

    Args:
        parent (QWidget): Parent widget.
        db (optional): Database connection object, default is None.
    """
    login_requested = Signal()
    signup_requested = Signal()
    exit_requested = Signal()

    WELCOME_TEXT = "Welcome to Thebu Tech Solutions"

    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db  # Store database connection if needed in future
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        welcome_label = QLabel(self.WELCOME_TEXT)
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)

        btn_login = QPushButton("Login")
        btn_login.clicked.connect(lambda: self.login_requested.emit())
        btn_login.setShortcut("Ctrl+L")
        btn_login.setToolTip("Login to your account")
        layout.addWidget(btn_login)

        btn_signup = QPushButton("Sign Up")
        btn_signup.clicked.connect(lambda: self.signup_requested.emit())
        btn_signup.setShortcut("Ctrl+S")
        btn_signup.setToolTip("Create a new account")
        layout.addWidget(btn_signup)

        btn_exit = QPushButton("Exit")
        btn_exit.clicked.connect(lambda: self.exit_requested.emit())
        btn_exit.setShortcut("Ctrl+Q")
        btn_exit.setToolTip("Exit the application")
        layout.addWidget(btn_exit)
