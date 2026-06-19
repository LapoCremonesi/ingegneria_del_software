from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget,
)

from smart_home.controller.controllore_autenticazione import ControlloreAutenticazione
from smart_home.domain.utente import Utente


class LoginDialog(QDialog):

    def __init__(self, controllore, parent=None):
        super().__init__(parent)
        self._controllore = controllore
        self._utente = None
        self.setWindowTitle("Smart Home - Accesso")
        self.setFixedSize(380, 460)
        self._setup_ui()

    @property
    def utente_autenticato(self):
        return self._utente

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 32, 28, 28)
        layout.setSpacing(0)

        titolo = QLabel("Smart Home")
        titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titolo.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #2563eb;")
        layout.addWidget(titolo)

        layout.addSpacing(6)

        sottotitolo = QLabel("Accedi al sistema di gestione")
        sottotitolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sottotitolo.setStyleSheet(
            "font-size: 13px; color: #888888;")
        layout.addWidget(sottotitolo)

        layout.addSpacing(24)

        tab_bar = QHBoxLayout()
        tab_bar.setSpacing(0)

        self._btn_accedi = QPushButton("Accedi")
        self._btn_accedi.setObjectName("tab_active")
        self._btn_accedi.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_accedi.clicked.connect(lambda: self._mostra_pagina(0))

        self._btn_registrati = QPushButton("Registrati")
        self._btn_registrati.setObjectName("tab_inactive")
        self._btn_registrati.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_registrati.clicked.connect(lambda: self._mostra_pagina(1))

        tab_bar.addWidget(self._btn_accedi)
        tab_bar.addWidget(self._btn_registrati)
        layout.addLayout(tab_bar)

        layout.addSpacing(16)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._pagina_login())
        self._stack.addWidget(self._pagina_registrazione())
        layout.addWidget(self._stack)

    def _mostra_pagina(self, index):
        self._stack.setCurrentIndex(index)
        if index == 0:
            self._btn_accedi.setObjectName("tab_active")
            self._btn_registrati.setObjectName("tab_inactive")
        else:
            self._btn_accedi.setObjectName("tab_inactive")
            self._btn_registrati.setObjectName("tab_active")
        self._btn_accedi.style().unpolish(self._btn_accedi)
        self._btn_accedi.style().polish(self._btn_accedi)
        self._btn_registrati.style().unpolish(self._btn_registrati)
        self._btn_registrati.style().polish(self._btn_registrati)

    def _pagina_login(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        label_email = QLabel("Email")
        label_email.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #555555;")
        layout.addWidget(label_email)

        layout.addSpacing(4)

        self._email_input = QLineEdit()
        self._email_input.setPlaceholderText("nome@esempio.com")
        layout.addWidget(self._email_input)

        layout.addSpacing(14)

        label_password = QLabel("Password")
        label_password.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #555555;")
        layout.addWidget(label_password)

        layout.addSpacing(4)

        self._password_input = QLineEdit()
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._password_input.setPlaceholderText("Inserisci la password")
        layout.addWidget(self._password_input)

        layout.addSpacing(20)

        login_button = QPushButton("Accedi")
        login_button.clicked.connect(self._tenta_login)
        layout.addWidget(login_button)

        layout.addStretch()

        self._password_input.returnPressed.connect(login_button.click)

        return page

    def _pagina_registrazione(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        label_nome = QLabel("Nome")
        label_nome.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #555555;")
        layout.addWidget(label_nome)

        layout.addSpacing(4)

        self._reg_nome_input = QLineEdit()
        self._reg_nome_input.setPlaceholderText("Il tuo nome")
        layout.addWidget(self._reg_nome_input)

        layout.addSpacing(14)

        label_email = QLabel("Email")
        label_email.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #555555;")
        layout.addWidget(label_email)

        layout.addSpacing(4)

        self._reg_email_input = QLineEdit()
        self._reg_email_input.setPlaceholderText("nome@esempio.com")
        layout.addWidget(self._reg_email_input)

        layout.addSpacing(14)

        label_password = QLabel("Password")
        label_password.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #555555;")
        layout.addWidget(label_password)

        layout.addSpacing(4)

        self._reg_password_input = QLineEdit()
        self._reg_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._reg_password_input.setPlaceholderText("Minimo 6 caratteri")
        layout.addWidget(self._reg_password_input)

        layout.addSpacing(14)

        label_conferma = QLabel("Conferma password")
        label_conferma.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #555555;")
        layout.addWidget(label_conferma)

        layout.addSpacing(4)

        self._reg_conferma_input = QLineEdit()
        self._reg_conferma_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._reg_conferma_input.setPlaceholderText("Ripeti password")
        layout.addWidget(self._reg_conferma_input)

        layout.addSpacing(20)

        registra_button = QPushButton("Registrati")
        registra_button.clicked.connect(self._tenta_registrazione)
        layout.addWidget(registra_button)

        layout.addStretch()

        self._reg_conferma_input.returnPressed.connect(registra_button.click)

        return page

    def showEvent(self, event):
        super().showEvent(event)
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2,
        )

    def _tenta_login(self):
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

    def _tenta_registrazione(self):
        nome = self._reg_nome_input.text().strip()
        email = self._reg_email_input.text().strip()
        password = self._reg_password_input.text()
        conferma = self._reg_conferma_input.text()

        if not nome or not email or not password:
            QMessageBox.warning(self, "Campi obbligatori",
                                "Compila tutti i campi.")
            return

        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Email non valida",
                                "Inserisci un indirizzo email valido.")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "Password debole",
                                "La password deve avere almeno 6 caratteri.")
            return

        if password != conferma:
            QMessageBox.warning(self, "Password non corrispondenti",
                                "Le password non coincidono.")
            return

        utente = self._controllore.registra_utente(nome, email, password)
        if utente is None:
            QMessageBox.warning(self, "Email già registrata",
                                "Esiste già un account con questa email.")
            return

        self._utente = utente
        self.accept()
