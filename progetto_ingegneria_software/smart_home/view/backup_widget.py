from typing import List, Optional

from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QListWidget, QPushButton,
    QVBoxLayout, QWidget,
)

from smart_home.controller.controllore_sistema import ControlloreSistema


class WidgetBackup(QWidget):

    def __init__(self, controllore_sistema: ControlloreSistema,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._c = controllore_sistema
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        titolo = QLabel("Backup e Ripristino")
        titolo.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #222222;")
        layout.addWidget(titolo)

        desc = QLabel(
            "Crea backup completi del sistema o ripristina "
            "da una versione precedente.")
        desc.setStyleSheet("color: #777777; font-size: 13px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self._lista = QListWidget()
        layout.addWidget(self._lista)

        pulsanti = QHBoxLayout()
        pulsanti.setSpacing(8)

        self._btn_crea = QPushButton("Crea Backup")
        self._btn_crea.clicked.connect(self._crea)
        pulsanti.addWidget(self._btn_crea)

        self._btn_carica = QPushButton("Carica Backup")
        self._btn_carica.setObjectName("btn_annulla")
        self._btn_carica.clicked.connect(self._carica)
        pulsanti.addWidget(self._btn_carica)

        pulsanti.addStretch()
        layout.addLayout(pulsanti)

        self._status = QLabel("")
        self._status.setStyleSheet(
            "color: #2563eb; font-weight: 500; padding: 6px 0;")
        self._status.setVisible(False)
        layout.addWidget(self._status)

        self._aggiorna_lista()

    def _aggiorna_lista(self):
        self._lista.clear()
        backup = self._c.elenca_backup()
        if not backup:
            self._lista.addItem("Nessun backup disponibile")
        else:
            for b in backup:
                self._lista.addItem(b)

    def _mostra(self, msg: str, errore: bool = False):
        self._status.setText(msg)
        self._status.setStyleSheet(
            f"color: {'#dc2626' if errore else '#2563eb'}; "
            f"font-weight: 500; padding: 6px 0;")
        self._status.setVisible(True)

    def _crea(self):
        r = self._c.salva_backup()
        self._aggiorna_lista()
        self._mostra(r)

    def _carica(self):
        item = self._lista.currentItem()
        if not item or item.text() == "Nessun backup disponibile":
            self._mostra("Seleziona un backup dalla lista.", errore=True)
            return
        r = self._c.carica_backup(item.text())
        self._mostra(r)
