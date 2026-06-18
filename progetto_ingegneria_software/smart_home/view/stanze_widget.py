from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMessageBox, QPushButton,
    QSpinBox, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from smart_home.controller.controllore_stanze import ControlloreStanze
from smart_home.domain.stanza import Stanza


class WidgetStanze(QWidget):

    def __init__(self, controllore_stanze: ControlloreStanze,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._controllore = controllore_stanze
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        titolo = QLabel("Stanze")
        titolo.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #222222;")
        layout.addWidget(titolo)

        self._tabella = QTableWidget()
        self._tabella.setColumnCount(3)
        self._tabella.setHorizontalHeaderLabels(["Nome", "Piano", "ID"])
        self._tabella.setColumnHidden(2, True)
        self._tabella.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self._tabella.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection)
        self._tabella.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self._tabella.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self._tabella.setAlternatingRowColors(True)
        self._tabella.verticalHeader().setVisible(False)
        self._tabella.setSortingEnabled(True)
        layout.addWidget(self._tabella)

        pulsanti = QHBoxLayout()
        pulsanti.setSpacing(8)

        self._btn_nuova = QPushButton("Nuova Stanza")
        self._btn_nuova.clicked.connect(self._nuova_stanza)
        pulsanti.addWidget(self._btn_nuova)

        self._btn_modifica = QPushButton("Modifica")
        self._btn_modifica.clicked.connect(self._modifica_stanza)
        pulsanti.addWidget(self._btn_modifica)

        self._btn_elimina = QPushButton("Elimina")
        self._btn_elimina.setObjectName("btn_elimina")
        self._btn_elimina.clicked.connect(self._elimina_stanza)
        pulsanti.addWidget(self._btn_elimina)

        pulsanti.addStretch()
        layout.addLayout(pulsanti)

        self._aggiorna_tabella()

    def _aggiorna_tabella(self) -> None:
        stanze = self._controllore.elenca_stanze()
        self._tabella.setRowCount(len(stanze))
        for r, s in enumerate(stanze):
            self._tabella.setItem(r, 0, QTableWidgetItem(s.nome))
            self._tabella.setItem(
                r, 1, QTableWidgetItem(str(s.piano)))
            self._tabella.setItem(r, 2, QTableWidgetItem(s.id))

    def _stanza_selezionata(self) -> Optional[Stanza]:
        r = self._tabella.currentRow()
        if r < 0:
            return None
        return self._controllore.trova_stanza_per_id(
            self._tabella.item(r, 2).text())

    def _nuova_stanza(self) -> None:
        d = _DialogoStanza(self)
        if d.exec() == QDialog.DialogCode.Accepted:
            nome, piano = d.dati()
            self._controllore.crea_stanza(nome, piano)
            self._aggiorna_tabella()

    def _modifica_stanza(self) -> None:
        s = self._stanza_selezionata()
        if not s:
            QMessageBox.warning(
                self, "Nessuna selezione",
                "Seleziona una stanza da modificare.")
            return
        d = _DialogoStanza(self, s)
        if d.exec() == QDialog.DialogCode.Accepted:
            s.nome, s.piano = d.dati()
            self._controllore.aggiorna_stanza(s)
            self._aggiorna_tabella()

    def _elimina_stanza(self) -> None:
        s = self._stanza_selezionata()
        if not s:
            QMessageBox.warning(
                self, "Nessuna selezione",
                "Seleziona una stanza da eliminare.")
            return
        if QMessageBox.question(
            self, "Conferma",
            f"Eliminare la stanza '{s.nome}'?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes:
            self._controllore.elimina_stanza(s.id)
            self._aggiorna_tabella()


class _DialogoStanza(QDialog):

    def __init__(self, parent: Optional[QWidget] = None,
                 stanza: Optional[Stanza] = None) -> None:
        super().__init__(parent)
        self._stanza = stanza
        self.setWindowTitle(
            "Modifica Stanza" if stanza else "Nuova Stanza")
        self.setFixedSize(340, 180)

        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self._nome = QLineEdit()
        self._nome.setPlaceholderText("es. Soggiorno")
        layout.addRow("Nome:", self._nome)

        self._piano = QSpinBox()
        self._piano.setMinimum(-5)
        self._piano.setMaximum(100)
        layout.addRow("Piano:", self._piano)

        if stanza:
            self._nome.setText(stanza.nome)
            self._piano.setValue(stanza.piano)

        pulsanti = QHBoxLayout()
        pulsanti.setSpacing(8)
        annulla = QPushButton("Annulla")
        annulla.setObjectName("btn_annulla")
        annulla.clicked.connect(self.reject)
        salva = QPushButton("Salva")
        salva.clicked.connect(self.accept)
        pulsanti.addStretch()
        pulsanti.addWidget(annulla)
        pulsanti.addWidget(salva)
        layout.addRow(pulsanti)

    def dati(self):
        return self._nome.text().strip(), self._piano.value()
