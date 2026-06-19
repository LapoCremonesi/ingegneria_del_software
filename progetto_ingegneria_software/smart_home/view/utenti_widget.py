from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMessageBox, QPushButton,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from smart_home.controller.controllore_autenticazione import ControlloreAutenticazione
from smart_home.domain.utente import Utente


class WidgetUtenti(QWidget):

    def __init__(self, controllore, parent=None):
        super().__init__(parent)
        self._controllore = controllore
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        titolo = QLabel("Gestione Utenti")
        titolo.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #222222;")
        layout.addWidget(titolo)

        desc = QLabel("Gestisci gli account degli utenti del sistema.")
        desc.setStyleSheet("color: #777777; font-size: 13px;")
        layout.addWidget(desc)

        self._tabella = QTableWidget()
        self._tabella.setColumnCount(4)
        self._tabella.setHorizontalHeaderLabels(["Nome", "Email", "Tipo", "ID"])
        self._tabella.setColumnHidden(3, True)
        self._tabella.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self._tabella.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection)
        self._tabella.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self._tabella.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch)
        self._tabella.setAlternatingRowColors(True)
        self._tabella.verticalHeader().setVisible(False)
        layout.addWidget(self._tabella)

        pulsanti = QHBoxLayout()
        pulsanti.setSpacing(8)

        self._btn_elimina = QPushButton("Elimina Utente")
        self._btn_elimina.setObjectName("btn_elimina")
        self._btn_elimina.clicked.connect(self._elimina_utente)
        pulsanti.addWidget(self._btn_elimina)

        pulsanti.addStretch()
        layout.addLayout(pulsanti)

        self._aggiorna()

    def _aggiorna(self):
        utenti = self._controllore.elenca_utenti()
        self._tabella.setRowCount(len(utenti))
        for r, u in enumerate(utenti):
            self._tabella.setItem(r, 0, QTableWidgetItem(u.nome))
            self._tabella.setItem(r, 1, QTableWidgetItem(u.email))
            tipo = "Amministratore" if hasattr(u, "livello_accesso") else "Utente"
            self._tabella.setItem(r, 2, QTableWidgetItem(tipo))
            self._tabella.setItem(r, 3, QTableWidgetItem(u.id))
        self._tabella.resizeColumnsToContents()

    def _utente_selezionato(self):
        r = self._tabella.currentRow()
        if r < 0:
            return None
        return self._tabella.item(r, 3).text()

    def _elimina_utente(self):
        id_utente = self._utente_selezionato()
        if not id_utente:
            QMessageBox.warning(
                self, "Nessuna selezione",
                "Seleziona un utente da eliminare.")
            return
        r = self._tabella.currentRow()
        nome = self._tabella.item(r, 0).text()
        if QMessageBox.question(
            self, "Conferma eliminazione",
            f"Eliminare l'utente '{nome}'?\nQuesta operazione è irreversibile.",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes:
            self._controllore.elimina_utente(id_utente)
            self._aggiorna()
