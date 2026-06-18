import uuid
from typing import Optional

from PyQt6.QtCore import QTime, Qt
from PyQt6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QPushButton,
    QVBoxLayout, QHBoxLayout, QHeaderView, QDialog,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QLabel, QFormLayout, QDialogButtonBox,
    QMessageBox, QTimeEdit,
)

from smart_home.domain.automazione import Automazione, Regola

from smart_home.controller.controllore_dispositivi import ControlloreDispositivi
from smart_home.controller.controllore_stanze import ControlloreStanze
from smart_home.domain.dispositivo import Dispositivo
from smart_home.domain.dispositivi_specifici import Luce, Termostato, Serratura


class WidgetDispositivi(QWidget):

    def __init__(self, controllore_dispositivi: ControlloreDispositivi,
                 controllore_stanze: ControlloreStanze,
                 controllore_automazioni=None, parent=None):
        super().__init__(parent)
        self._cd = controllore_dispositivi
        self._cs = controllore_stanze
        self._ca = controllore_automazioni
        self._mappa_stanze = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        titolo = QLabel("Dispositivi")
        titolo.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #222222;")
        layout.addWidget(titolo)

        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            ["Nome", "Tipo", "Stanza", "Stato", "Online", "ID"])
        self._table.setColumnHidden(5, True)
        self._table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection)
        self._table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setSortingEnabled(True)
        layout.addWidget(self._table)

        pulsanti = QHBoxLayout()
        pulsanti.setSpacing(8)

        self._btn_nuovo = QPushButton("Nuovo Dispositivo")
        self._btn_nuovo.clicked.connect(self._nuovo)
        pulsanti.addWidget(self._btn_nuovo)

        self._btn_modifica = QPushButton("Modifica")
        self._btn_modifica.clicked.connect(self._modifica)
        pulsanti.addWidget(self._btn_modifica)

        self._btn_elimina = QPushButton("Elimina")
        self._btn_elimina.setObjectName("btn_elimina")
        self._btn_elimina.clicked.connect(self._elimina)
        pulsanti.addWidget(self._btn_elimina)

        self._btn_automazione = QPushButton("Automazione")
        self._btn_automazione.clicked.connect(self._automazione)
        pulsanti.addWidget(self._btn_automazione)

        pulsanti.addStretch()
        layout.addLayout(pulsanti)

    def showEvent(self, event):
        super().showEvent(event)
        self._refresh()

    def _refresh(self):
        self._mappa_stanze.clear()
        for s in self._cs.elenca_stanze():
            self._mappa_stanze[s.id] = s.nome

        dispositivi = self._cd.elenca_dispositivi()
        self._table.setRowCount(len(dispositivi))
        for i, d in enumerate(dispositivi):
            self._table.setItem(i, 0, QTableWidgetItem(d.nome))
            self._table.setItem(
                i, 1,
                QTableWidgetItem(d.tipo.capitalize()))
            self._table.setItem(
                i, 2,
                QTableWidgetItem(
                    self._mappa_stanze.get(d.id_stanza, "-")))
            self._table.setItem(i, 3, QTableWidgetItem(d.stato))
            self._table.setItem(
                i, 4,
                QTableWidgetItem(
                    "Online" if d.online else "Offline"))
            self._table.setItem(i, 5, QTableWidgetItem(d.id))

    def _selezionato(self) -> Optional[Dispositivo]:
        r = self._table.currentRow()
        if r < 0:
            return None
        return self._cd.trova_dispositivo_per_id(
            self._table.item(r, 5).text())

    def _nuovo(self):
        d = _DialogoDispositivo(self._cs)
        if d.exec() == QDialog.DialogCode.Accepted:
            nome, tipo, id_s, kw = d.dati()
            self._cd.crea_dispositivo(nome, tipo, id_s, **kw)
            self._refresh()

    def _modifica(self):
        disp = self._selezionato()
        if not disp:
            QMessageBox.warning(
                self, "Nessuna selezione",
                "Seleziona un dispositivo.")
            return
        d = _DialogoDispositivo(self._cs, disp)
        if d.exec() != QDialog.DialogCode.Accepted:
            return
        nome, tipo, id_s, kw = d.dati()
        nuovo = self._costruisci(disp.id, nome, tipo, id_s, kw)
        nuovo.online = disp.online
        self._cd.aggiorna_dispositivo(nuovo)
        self._refresh()

    def _costruisci(self, id_d, nome, tipo, id_s, kw):
        if tipo == "luce":
            return Luce(id_d, nome, id_s, **kw)
        elif tipo == "termostato":
            return Termostato(id_d, nome, id_s, **kw)
        elif tipo == "serratura":
            return Serratura(id_d, nome, id_s, **kw)
        return Dispositivo(id_d, nome, tipo, id_s)

    def _elimina(self):
        disp = self._selezionato()
        if not disp:
            QMessageBox.warning(
                self, "Nessuna selezione",
                "Seleziona un dispositivo.")
            return
        if QMessageBox.question(
            self, "Conferma",
            f"Eliminare '{disp.nome}'?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes:
            self._cd.elimina_dispositivo(disp.id)
            self._refresh()

    def _automazione(self):
        disp = self._selezionato()
        if not disp:
            QMessageBox.warning(
                self, "Nessuna selezione",
                "Seleziona un dispositivo.")
            return
        d = _DialogoAutomazioneRapida(disp, self._ca)
        if d.exec() == QDialog.DialogCode.Accepted:
            self._refresh()


class _DialogoAutomazioneRapida(QDialog):

    def __init__(self, dispositivo, controllore_automazioni, parent=None):
        super().__init__(parent)
        self._dispositivo = dispositivo
        self._ca = controllore_automazioni
        self.setWindowTitle(f"Automazione - {dispositivo.nome}")
        self.setFixedSize(360, 260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(8)

        self._nome = QLineEdit()
        self._nome.setText(f"{dispositivo.nome}")
        form.addRow("Nome:", self._nome)

        self._orario = QTimeEdit()
        self._orario.setDisplayFormat("HH:mm")
        form.addRow("Orario:", self._orario)

        self._combo_cmd = QComboBox()
        self._combo_cmd.addItems(["accendi", "spegni"])
        t = dispositivo.tipo
        if t == "luce":
            self._combo_cmd.addItems(["attenua", "colore"])
        elif t == "termostato":
            self._combo_cmd.addItems(["imposta", "modalita"])
        elif t == "serratura":
            self._combo_cmd.addItems(
                ["blocca", "sblocca", "sicurezza on", "sicurezza off"])
        form.addRow("Comando:", self._combo_cmd)

        layout.addLayout(form)
        layout.addStretch()

        pulsanti = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel)
        pulsanti.accepted.connect(self._conferma)
        pulsanti.rejected.connect(self.reject)
        layout.addWidget(pulsanti)

    def _conferma(self):
        nome = self._nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Attenzione", "Inserisci un nome.")
            return
        t = self._orario.time()
        orario = f"{t.hour():02d}:{t.minute():02d}"
        comando = self._combo_cmd.currentText()
        a = Automazione(str(uuid.uuid4()), nome,
                        id_dispositivo=self._dispositivo.id,
                        orario=orario)
        regola = Regola("orario", orario, comando)
        a.aggiungi_regola(regola)
        a.attiva_automazione()
        self._ca.crea_regola(a)
        self.accept()


class _DialogoDispositivo(QDialog):

    def __init__(self, controllore_stanze: ControlloreStanze,
                 dispositivo: Optional[Dispositivo] = None, parent=None):
        super().__init__(parent)
        self._cs = controllore_stanze
        self._dispositivo = dispositivo
        self.setWindowTitle(
            "Modifica Dispositivo" if dispositivo
            else "Nuovo Dispositivo")
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

        self._nome = QLineEdit()
        self._nome.setPlaceholderText("Nome dispositivo")
        form.addRow("Nome:", self._nome)

        self._tipo = QComboBox()
        self._tipo.addItems(
            ["luce", "termostato", "serratura", "generico"])
        form.addRow("Tipo:", self._tipo)

        self._stanza = QComboBox()
        form.addRow("Stanza:", self._stanza)

        self._intensita_lbl = QLabel("Intensita:")
        self._intensita = QSpinBox()
        self._intensita.setRange(0, 100)
        self._intensita.setValue(50)
        form.addRow(self._intensita_lbl, self._intensita)

        self._colore_lbl = QLabel("Colore:")
        self._colore = QComboBox()
        self._colore.addItems(["bianco", "caldo", "freddo", "rgb"])
        form.addRow(self._colore_lbl, self._colore)

        self._temp_lbl = QLabel("Temperatura:")
        self._temp = QDoubleSpinBox()
        self._temp.setRange(10.0, 35.0)
        self._temp.setValue(20.0)
        form.addRow(self._temp_lbl, self._temp)

        self._modalita_lbl = QLabel("Modalita:")
        self._modalita = QComboBox()
        self._modalita.addItems(["auto", "manuale", "antigelo"])
        form.addRow(self._modalita_lbl, self._modalita)

        self._sicurezza = QCheckBox("Modalita Sicurezza")
        form.addRow(self._sicurezza)

        layout.addLayout(form)
        layout.addStretch()

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
        layout.addLayout(pulsanti)

        self._popola_stanze()
        if dispositivo:
            self._prefill()
        self._tipo.currentIndexChanged.connect(self._toggle_campi)
        self._toggle_campi()

    def _popola_stanze(self):
        self._stanza.clear()
        for s in self._cs.elenca_stanze():
            self._stanza.addItem(s.nome, s.id)

    def _prefill(self):
        d = self._dispositivo
        self._nome.setText(d.nome)
        i = self._tipo.findText(d.tipo)
        if i >= 0:
            self._tipo.setCurrentIndex(i)
        for i in range(self._stanza.count()):
            if self._stanza.itemData(i) == d.id_stanza:
                self._stanza.setCurrentIndex(i)
                break
        if isinstance(d, Luce):
            self._intensita.setValue(d.intensita)
            i = self._colore.findText(d.colore)
            if i >= 0:
                self._colore.setCurrentIndex(i)
        elif isinstance(d, Termostato):
            self._temp.setValue(d.temperatura_target)
            i = self._modalita.findText(d.modalita)
            if i >= 0:
                self._modalita.setCurrentIndex(i)
        elif isinstance(d, Serratura):
            self._sicurezza.setChecked(d.modalita_sicurezza)

    def _toggle_campi(self):
        t = self._tipo.currentText()
        l = t == "luce"
        th = t == "termostato"
        s = t == "serratura"

        self._intensita_lbl.setVisible(l)
        self._intensita.setVisible(l)
        self._colore_lbl.setVisible(l)
        self._colore.setVisible(l)

        self._temp_lbl.setVisible(th)
        self._temp.setVisible(th)
        self._modalita_lbl.setVisible(th)
        self._modalita.setVisible(th)

        self._sicurezza.setVisible(s)

    def dati(self):
        nome = self._nome.text().strip()
        tipo = self._tipo.currentText()
        id_s = self._stanza.currentData()
        kw = {}
        if tipo == "luce":
            kw = {"intensita": self._intensita.value(),
                  "colore": self._colore.currentText()}
        elif tipo == "termostato":
            kw = {"temperatura_target": self._temp.value(),
                  "modalita": self._modalita.currentText()}
        elif tipo == "serratura":
            kw = {"modalita_sicurezza": self._sicurezza.isChecked()}
        return nome, tipo, id_s, kw
