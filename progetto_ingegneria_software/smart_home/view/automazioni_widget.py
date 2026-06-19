import uuid

from PyQt6.QtCore import QTime
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QFormLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QMessageBox, QPushButton, QTableWidget,
    QTableWidgetItem, QTimeEdit, QVBoxLayout, QWidget,
)

from smart_home.controller.controllore_automazioni import ControlloreAutomazioni
from smart_home.domain.automazione import Automazione, Regola


class WidgetAutomazioni(QWidget):

    def __init__(self, controllore, parent=None):
        super().__init__(parent)
        self._c = controllore
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        titolo = QLabel("Automazioni")
        titolo.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #222222;")
        layout.addWidget(titolo)

        self._tabella = QTableWidget()
        self._tabella.setColumnCount(6)
        self._tabella.setHorizontalHeaderLabels(
            ["Nome", "Attiva", "Orario", "Regole", "ID", "Dispositivo"])
        self._tabella.setColumnHidden(4, True)
        self._tabella.setColumnHidden(5, True)
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

        self._btn_nuova = QPushButton("Nuova Automazione")
        self._btn_nuova.clicked.connect(self._nuova)
        pulsanti.addWidget(self._btn_nuova)

        self._btn_modifica = QPushButton("Modifica")
        self._btn_modifica.clicked.connect(self._modifica)
        pulsanti.addWidget(self._btn_modifica)

        self._btn_elimina = QPushButton("Elimina")
        self._btn_elimina.setObjectName("btn_elimina")
        self._btn_elimina.clicked.connect(self._elimina)
        pulsanti.addWidget(self._btn_elimina)

        self._btn_toggle = QPushButton("Attiva/Disattiva")
        self._btn_toggle.clicked.connect(self._toggle)
        pulsanti.addWidget(self._btn_toggle)

        pulsanti.addStretch()
        layout.addLayout(pulsanti)

        self._aggiorna()

    def showEvent(self, event):
        super().showEvent(event)
        self._aggiorna()

    def _aggiorna(self):
        automazioni = self._c.elenca_regole()
        self._tabella.setRowCount(len(automazioni))
        for r, a in enumerate(automazioni):
            self._tabella.setItem(r, 0, QTableWidgetItem(a.nome))
            self._tabella.setItem(
                r, 1,
                QTableWidgetItem("Attiva" if a.attiva else "Disattiva"))
            self._tabella.setItem(r, 2, QTableWidgetItem(a.orario or "-"))
            self._tabella.setItem(
                r, 3,
                QTableWidgetItem(str(len(a.regole))))
            self._tabella.setItem(r, 4, QTableWidgetItem(a.id))
            self._tabella.setItem(r, 5, QTableWidgetItem(a.id_dispositivo))

    def _selezionata(self):
        r = self._tabella.currentRow()
        if r < 0:
            return None
        return self._c.trova_regola_per_id(
            self._tabella.item(r, 4).text())

    def _nuova(self):
        d = _DialogoAutomazione(self)
        if d.exec() == QDialog.DialogCode.Accepted:
            nome, orario, id_dispositivo, regole = d.dati()
            a = Automazione(str(uuid.uuid4()), nome,
                            id_dispositivo=id_dispositivo,
                            orario=orario)
            for r in regole:
                a.aggiungi_regola(r)
            self._c.crea_regola(a)
            self._aggiorna()

    def _modifica(self):
        a = self._selezionata()
        if not a:
            QMessageBox.warning(
                self, "Nessuna selezione",
                "Seleziona un'automazione.")
            return
        d = _DialogoAutomazione(self, a)
        if d.exec() == QDialog.DialogCode.Accepted:
            nome, orario, id_dispositivo, regole = d.dati()
            a.nome = nome
            a.orario = orario
            a.id_dispositivo = id_dispositivo
            a._regole = regole
            self._c.aggiorna_regola(a)
            self._aggiorna()

    def _elimina(self):
        a = self._selezionata()
        if not a:
            QMessageBox.warning(
                self, "Nessuna selezione",
                "Seleziona un'automazione.")
            return
        if QMessageBox.question(
            self, "Conferma",
            f"Eliminare '{a.nome}'?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        ) == QMessageBox.StandardButton.Yes:
            self._c.elimina_regola(a.id)
            self._aggiorna()

    def _toggle(self):
        a = self._selezionata()
        if not a:
            QMessageBox.warning(
                self, "Nessuna selezione",
                "Seleziona un'automazione.")
            return
        if a.attiva:
            a.disattiva_automazione()
        else:
            a.attiva_automazione()
        self._c.aggiorna_regola(a)
        self._aggiorna()


class _DialogoAutomazione(QDialog):

    def __init__(self, parent=None, automazione=None, id_dispositivo=None):
        super().__init__(parent)
        self._a = automazione
        self._id_dispositivo_predefinito = id_dispositivo
        self.setWindowTitle(
            "Modifica Automazione" if automazione
            else "Nuova Automazione")
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)
        self._nome = QLineEdit()
        self._nome.setPlaceholderText("es. Accendi luce sera")
        form.addRow("Nome:", self._nome)

        self._id_dispositivo_input = QLineEdit()
        self._id_dispositivo_input.setPlaceholderText("ID del dispositivo target")
        form.addRow("ID Dispositivo:", self._id_dispositivo_input)

        self._orario = QTimeEdit()
        self._orario.setTime(QTime(0, 0))
        self._orario.setDisplayFormat("HH:mm")
        form.addRow("Orario:", self._orario)
        layout.addLayout(form)

        gruppo = QGroupBox("Regole")
        g_layout = QVBoxLayout(gruppo)

        self._tab_regole = QTableWidget()
        self._tab_regole.setColumnCount(3)
        self._tab_regole.setHorizontalHeaderLabels(
            ["Tipo", "Valore", "Azione"])
        self._tab_regole.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self._tab_regole.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self._tab_regole.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self._tab_regole.setAlternatingRowColors(True)
        self._tab_regole.verticalHeader().setVisible(False)
        g_layout.addWidget(self._tab_regole)

        p_reg = QHBoxLayout()
        p_reg.setSpacing(8)
        self._btn_agg = QPushButton("Aggiungi")
        self._btn_rim = QPushButton("Rimuovi")
        self._btn_rim.setObjectName("btn_elimina")
        p_reg.addWidget(self._btn_agg)
        p_reg.addWidget(self._btn_rim)
        p_reg.addStretch()
        g_layout.addLayout(p_reg)

        layout.addWidget(gruppo)

        pulsanti = QHBoxLayout()
        pulsanti.setSpacing(8)
        annulla = QPushButton("Annulla")
        annulla.setObjectName("btn_annulla")
        annulla.clicked.connect(self.reject)
        salva = QPushButton("Salva")
        salva.clicked.connect(self._conferma)
        pulsanti.addStretch()
        pulsanti.addWidget(annulla)
        pulsanti.addWidget(salva)
        layout.addLayout(pulsanti)

        self._btn_agg.clicked.connect(self._aggiungi)
        self._btn_rim.clicked.connect(self._rimuovi)

        self._regole = []
        if automazione:
            self._nome.setText(automazione.nome)
            self._id_dispositivo_input.setText(automazione.id_dispositivo)
            if automazione.orario:
                h, m = map(int, automazione.orario.split(":"))
                self._orario.setTime(QTime(h, m))
            self._regole = list(automazione.regole)
        elif id_dispositivo:
            self._id_dispositivo_input.setText(id_dispositivo)
        self._refresh_tab()

    def _refresh_tab(self):
        self._tab_regole.setRowCount(len(self._regole))
        for r, reg in enumerate(self._regole):
            self._tab_regole.setItem(
                r, 0, QTableWidgetItem(reg.tipo_condizione))
            self._tab_regole.setItem(
                r, 1, QTableWidgetItem(reg.valore_condizione))
            self._tab_regole.setItem(
                r, 2, QTableWidgetItem(reg.azione))
        self._tab_regole.resizeColumnsToContents()

    def _aggiungi(self):
        d = _DialogoRegola(self)
        if d.exec() == QDialog.DialogCode.Accepted:
            self._regole.append(Regola(*d.dati()))
            self._refresh_tab()

    def _rimuovi(self):
        righe = self._tab_regole.selectionModel().selectedRows()
        if not righe:
            return
        self._regole.pop(righe[0].row())
        self._refresh_tab()

    def _conferma(self):
        if not self._nome.text().strip():
            QMessageBox.warning(
                self, "Attenzione",
                "Inserisci un nome per l'automazione.")
            return
        self.accept()

    def dati(self):
        nome = self._nome.text().strip()
        id_dispositivo = self._id_dispositivo_input.text().strip()
        t = self._orario.time()
        orario = (
            f"{t.hour():02d}:{t.minute():02d}"
            if not (t.hour() == 0 and t.minute() == 0)
            else None
        )
        return nome, orario, id_dispositivo, self._regole


class _DialogoRegola(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuova Regola")
        self.setFixedSize(320, 180)
        layout = QFormLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self._tipo = QComboBox()
        self._tipo.addItems(["orario", "stato"])
        layout.addRow("Tipo:", self._tipo)

        self._valore = QLineEdit()
        self._valore.setPlaceholderText("es. 08:00, acceso")
        layout.addRow("Valore:", self._valore)

        self._azione = QLineEdit()
        self._azione.setPlaceholderText("es. accendi_luce")
        layout.addRow("Azione:", self._azione)

        pulsanti = QHBoxLayout()
        pulsanti.setSpacing(8)
        annulla = QPushButton("Annulla")
        annulla.setObjectName("btn_annulla")
        annulla.clicked.connect(self.reject)
        conferma = QPushButton("Conferma")
        conferma.clicked.connect(self._check)
        pulsanti.addStretch()
        pulsanti.addWidget(annulla)
        pulsanti.addWidget(conferma)
        layout.addRow(pulsanti)

    def _check(self):
        if not self._valore.text().strip():
            QMessageBox.warning(
                self, "Attenzione",
                "Inserisci un valore per la condizione.")
            return
        if not self._azione.text().strip():
            QMessageBox.warning(
                self, "Attenzione",
                "Inserisci un'azione.")
            return
        self.accept()

    def dati(self):
        return (
            self._tipo.currentText(),
            self._valore.text().strip(),
            self._azione.text().strip(),
        )
