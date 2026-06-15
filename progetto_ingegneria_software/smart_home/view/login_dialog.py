from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QMessageBox,
    QPushButton, QVBoxLayout, QWidget,
)

from smart_home.controller.controllore_autenticazione import ControlloreAutenticazione
from smart_home.domain.utente import Utente


class LoginDialog(QDialog):

    def __init__(self, controllore: ControlloreAutenticazione,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._controllore = controllore
        self._utente: Optional[Utente] = None
        self.setWindowTitle("Smart Home - Accesso")
        self.setFixedSize(380, 340)
        self._setup_ui()

    @property
    def utente_autenticato(self) -> Optional[Utente]:
        return self._utente

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 36, 28, 28)
        layout.setSpacing(0)

        titolo = QLabel("Smart Home")
        titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titolo.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #2563eb; "
            "margin-bottom: 4px;")
        layout.addWidget(titolo)

        sottotitolo = QLabel("Accedi al sistema di gestione")
        sottotitolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sottotitolo.setStyleSheet(
            "font-size: 13px; color: #888888; margin-bottom: 28px;")
        layout.addWidget(sottotitolo)

        label_email = QLabel("Email")
        label_email.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #555555; "
            "margin-bottom: 4px;")
        layout.addWidget(label_email)

        self._email_input = QLineEdit()
        self._email_input.setPlaceholderText("nome@esempio.com")
        layout.addWidget(self._email_input)

        layout.addSpacing(14)

        label_password = QLabel("Password")
        label_password.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #555555; "
            "margin-bottom: 4px;")
        layout.addWidget(label_password)

        self._password_input = QLineEdit()
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._password_input.setPlaceholderText("Inserisci la password")
        layout.addWidget(self._password_input)

        layout.addStretch()

        login_button = QPushButton("Accedi")
        login_button.clicked.connect(self._tenta_login)
        layout.addWidget(login_button)

        layout.addSpacing(8)

        annulla_button = QPushButton("Annulla")
        annulla_button.setObjectName("btn_annulla")
        annulla_button.clicked.connect(self.reject)
        layout.addWidget(annulla_button)

        self._password_input.returnPressed.connect(login_button.click)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

    def _tenta_login(self) -> None:
        email = self._email_input.text().strip()
        password = self._password_input.text().strip()
        utente = self._controllore.effettua_login(email, password)
        if utente is not None:
            self._utente = utente
            self.accept()
        else:
            QMessageBox.warning(
                self, "Errore di accesso",
                "Email o password non validi.")
