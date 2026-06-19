import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout, QHeaderView, QLabel, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from smart_home.controller.controllore_sistema import ControlloreSistema


class WidgetBackup(QWidget):

    def __init__(self, controllore_sistema, parent=None):
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

        self._tabella = QTableWidget()
        self._tabella.setColumnCount(2)
        self._tabella.setHorizontalHeaderLabels(["Backup", "Data"])
        self._tabella.horizontalHeader().setStretchLastSection(True)
        self._tabella.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch)
        self._tabella.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self._tabella.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection)
        self._tabella.setAlternatingRowColors(True)
        self._tabella.verticalHeader().setVisible(False)
        self._tabella.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self._tabella)

        pulsanti = QHBoxLayout()
        pulsanti.setSpacing(8)

        self._btn_crea = QPushButton("Crea Backup")
        self._btn_crea.clicked.connect(self._crea)
        pulsanti.addWidget(self._btn_crea)

        self._btn_carica = QPushButton("Carica Backup")
        self._btn_carica.setObjectName("btn_annulla")
        self._btn_carica.clicked.connect(self._carica)
        pulsanti.addWidget(self._btn_carica)

        self._btn_elimina = QPushButton("Elimina Backup")
        self._btn_elimina.setObjectName("btn_elimina")
        self._btn_elimina.clicked.connect(self._elimina)
        pulsanti.addWidget(self._btn_elimina)

        pulsanti.addStretch()
        layout.addLayout(pulsanti)

        self._status = QLabel("")
        self._status.setStyleSheet(
            "color: #2563eb; font-weight: 500; padding: 6px 0;")
        self._status.setVisible(False)
        layout.addWidget(self._status)

        self._aggiorna_lista()

    def _aggiorna_lista(self):
        self._tabella.setRowCount(0)
        backup = self._c.elenca_backup()
        if not backup:
            self._tabella.setRowCount(1)
            self._tabella.setItem(0, 0, QTableWidgetItem(
                "Nessun backup disponibile"))
            self._tabella.setSpan(0, 0, 1, 2)
            return
        for i, percorso in enumerate(backup):
            self._tabella.setRowCount(i + 1)
            nome = os.path.basename(percorso)
            data = nome.replace("backup_", "").replace(".json", "")
            data = data.replace("_", " ")
            item_nome = QTableWidgetItem(nome)
            item_nome.setData(Qt.ItemDataRole.UserRole, percorso)
            item_nome.setToolTip(percorso)
            self._tabella.setItem(i, 0, item_nome)
            item_data = QTableWidgetItem(data)
            item_data.setData(Qt.ItemDataRole.UserRole, percorso)
            item_data.setToolTip(percorso)
            self._tabella.setItem(i, 1, item_data)

    def _mostra(self, msg, errore=False):
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
        row = self._tabella.currentRow()
        if row < 0:
            self._mostra("Seleziona un backup dalla tabella.", errore=True)
            return
        item = self._tabella.item(row, 0)
        if not item or not item.data(Qt.ItemDataRole.UserRole):
            self._mostra("Seleziona un backup dalla tabella.", errore=True)
            return
        percorso = item.data(Qt.ItemDataRole.UserRole)
        r = self._c.carica_backup(percorso)
        self._mostra(r)

    def _elimina(self):
        row = self._tabella.currentRow()
        if row < 0:
            self._mostra("Seleziona un backup dalla tabella.", errore=True)
            return
        item = self._tabella.item(row, 0)
        if not item or not item.data(Qt.ItemDataRole.UserRole):
            self._mostra("Seleziona un backup dalla tabella.", errore=True)
            return
        percorso = item.data(Qt.ItemDataRole.UserRole)
        nome = os.path.basename(percorso)
        conferma = QMessageBox.question(
            self, "Elimina backup",
            f"Eliminare il backup '{nome}'?\nQuesta operazione non puo essere annullata.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if conferma != QMessageBox.StandardButton.Yes:
            return
        ok = self._c.elimina_backup(percorso)
        self._aggiorna_lista()
        if ok:
            self._mostra(f"Backup '{nome}' eliminato.")
        else:
            self._mostra(f"Errore nell'eliminazione del backup.", errore=True)
