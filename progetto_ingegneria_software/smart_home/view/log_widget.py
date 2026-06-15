from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox,
)

from smart_home.controller.controllore_log import ControlloreLog


class WidgetLog(QWidget):

    def __init__(self, controllore_log: ControlloreLog,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._c = controllore_log
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        titolo = QLabel("Log Eventi")
        titolo.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #222222;")
        layout.addWidget(titolo)

        filtro = QHBoxLayout()
        filtro.setSpacing(8)

        self._filtro = QLineEdit()
        self._filtro.setPlaceholderText("Cerca per tipo o descrizione...")
        filtro.addWidget(self._filtro)

        self._btn_cerca = QPushButton("Cerca")
        self._btn_cerca.clicked.connect(self._refresh)
        filtro.addWidget(self._btn_cerca)

        self._btn_esporta = QPushButton("Esporta")
        self._btn_esporta.setObjectName("btn_annulla")
        self._btn_esporta.clicked.connect(self._esporta)
        filtro.addWidget(self._btn_esporta)

        layout.addLayout(filtro)

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(
            ["Timestamp", "Tipo", "Descrizione", "Dispositivo", "ID"])
        self._table.setColumnHidden(4, True)
        self._table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

        self._filtro.returnPressed.connect(self._btn_cerca.click)

    def _refresh(self):
        filtro = self._filtro.text()
        eventi = self._c.elenca_eventi(filtro)
        self._table.setRowCount(len(eventi))
        for r, e in enumerate(eventi):
            self._table.setItem(
                r, 0, QTableWidgetItem(str(e.timestamp)))
            self._table.setItem(r, 1, QTableWidgetItem(e.tipo))
            self._table.setItem(r, 2, QTableWidgetItem(e.descrizione))
            self._table.setItem(
                r, 3,
                QTableWidgetItem(e.id_dispositivo or ""))
            self._table.setItem(r, 4, QTableWidgetItem(e.id))
        self._table.resizeColumnsToContents()

    def _esporta(self):
        filtro = self._filtro.text()
        QMessageBox.information(
            self, "Esportazione",
            self._c.esporta_eventi(filtro))
