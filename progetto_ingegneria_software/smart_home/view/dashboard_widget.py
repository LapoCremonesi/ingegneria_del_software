from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QVBoxLayout, QWidget,
)

from smart_home.controller.controllore_sistema import ControlloreSistema
from smart_home.domain.dispositivo import Dispositivo
from smart_home.domain.evento import Evento


class WidgetDashboard(QWidget):

    def __init__(self, controllore_sistema, parent=None):
        super().__init__(parent)
        self._c = controllore_sistema
        self._id_utente = ""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        titolo = QLabel("Dashboard")
        titolo.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #222222;")
        layout.addWidget(titolo)

        self._area = QTextEdit()
        self._area.setReadOnly(True)
        layout.addWidget(self._area)

        pulsanti = QHBoxLayout()
        pulsanti.setSpacing(8)

        self._btn_aggiorna = QPushButton("Aggiorna")
        self._btn_aggiorna.clicked.connect(self.aggiorna)
        pulsanti.addWidget(self._btn_aggiorna)

        self._filtro = QLineEdit()
        self._filtro.setPlaceholderText("Filtro statistiche...")
        pulsanti.addWidget(self._filtro)

        self._btn_stat = QPushButton("Statistiche")
        self._btn_stat.setObjectName("btn_annulla")
        self._btn_stat.clicked.connect(self._statistiche)
        pulsanti.addWidget(self._btn_stat)

        layout.addLayout(pulsanti)

    def imposta_utente(self, id_utente):
        self._id_utente = id_utente
        self.aggiorna()

    def aggiorna(self):
        eseguite = self._c.esegui_automazioni()
        testo = self._c.apri_dashboard(self._id_utente) + "\n"
        if eseguite:
            testo += "Automazioni eseguite:\n"
            for msg in eseguite:
                testo += f"  - {msg}\n"
            testo += "\n"
        offline = self._c.monitora_dispositivi()
        if offline:
            testo += "\nDispositivi Offline:\n"
            for d in offline:
                testo += f"  - {d.nome} ({d.tipo})\n"
        self._area.setPlainText(testo)

    def showEvent(self, event):
        super().showEvent(event)
        self.aggiorna()

    def _statistiche(self):
        filtro = self._filtro.text()
        eventi = self._c.genera_statistiche(filtro)
        testo = f"Statistiche (filtro: '{filtro}')\n"
        testo += "-" * 30 + "\n"
        if not eventi:
            testo += "Nessun evento trovato.\n"
        else:
            for e in eventi:
                testo += e.to_string() + "\n"
        self._area.setPlainText(testo)
