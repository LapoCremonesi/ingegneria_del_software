from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QHBoxLayout, QPushButton, QLabel

from smart_home.view.stanze_widget import WidgetStanze
from smart_home.view.dispositivi_widget import WidgetDispositivi
from smart_home.view.automazioni_widget import WidgetAutomazioni
from smart_home.view.log_widget import WidgetLog
from smart_home.view.dashboard_widget import WidgetDashboard
from smart_home.view.backup_widget import WidgetBackup


class FinestraPrincipale(QMainWindow):

    def __init__(self, controllore_stanze, controllore_dispositivi,
                 controllore_automazioni, controllore_log,
                 controllore_sistema, id_utente: str) -> None:
        super().__init__()
        self._cs = controllore_stanze
        self._cd = controllore_dispositivi
        self._ca = controllore_automazioni
        self._cl = controllore_log
        self._csi = controllore_sistema
        self._logout_richiesto = False

        self.setWindowTitle("Smart Home - Sistema di Gestione")
        self.resize(1100, 740)
        self.setMinimumSize(800, 600)

        header = QWidget()
        header.setStyleSheet(
            "background-color: #ffffff; border-bottom: 1px solid #e0e0e0;")
        header.setFixedHeight(52)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("Smart Home")
        logo.setStyleSheet(
            "font-size: 18px; font-weight: 700; color: #2563eb;")
        hl.addWidget(logo)
        hl.addStretch()
        ruolo = QLabel("")
        ruolo.setStyleSheet("color: #888888; font-size: 13px;")
        hl.addWidget(ruolo)
        self._btn_esci = QPushButton("Esci")
        self._btn_esci.setObjectName("btn_esci")
        self._btn_esci.clicked.connect(self._logout)
        hl.addWidget(self._btn_esci)

        self.setMenuWidget(header)

        self._tabs = QTabWidget()
        self._tabs.setDocumentMode(True)
        self.setCentralWidget(self._tabs)

        wd = WidgetDashboard(self._csi)
        wd.imposta_utente(id_utente)
        self._tabs.addTab(wd, "Dashboard")
        self._tabs.addTab(WidgetStanze(self._cs), "Stanze")
        self._tabs.addTab(
            WidgetDispositivi(self._cd, self._cs, self._ca), "Dispositivi")
        self._tabs.addTab(
            WidgetAutomazioni(self._ca), "Automazioni")
        self._tabs.addTab(WidgetLog(self._cl), "Log")
        self._tabs.addTab(WidgetBackup(self._csi), "Backup")

    @property
    def is_logout(self) -> bool:
        return self._logout_richiesto

    def _logout(self) -> None:
        self._logout_richiesto = True
        self.close()
