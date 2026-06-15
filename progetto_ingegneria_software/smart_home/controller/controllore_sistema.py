"""
Controllore per le funzionalita di sistema.

Orchestra l'apertura della dashboard, il monitoraggio dei dispositivi,
la generazione di statistiche, il backup e il ripristino dei dati.
"""

from typing import List

from smart_home.domain.dispositivo import Dispositivo
from smart_home.domain.evento import Evento
from smart_home.service.servizio_sistema import ServizioSistema


class ControlloreSistema:
    """Orchestra le operazioni di sistema (dashboard, monitoraggio,
    backup, ripristino, statistiche)."""

    def __init__(self, servizio_sistema: ServizioSistema) -> None:
        self._servizio_sistema = servizio_sistema

    def apri_dashboard(self, id_utente: str) -> str:
        """Restituisce il riepilogo del sistema per la dashboard."""
        return self._servizio_sistema.carica_riepilogo(id_utente)

    def monitora_dispositivi(self) -> List[Dispositivo]:
        """Restituisce i dispositivi offline per il monitoraggio."""
        return self._servizio_sistema.monitora_dispositivi()

    def genera_statistiche(self, filtro: str) -> List[Evento]:
        """Restituisce statistiche aggregate per un filtro."""
        return self._servizio_sistema.genera_statistiche(filtro)

    # ── Backup e ripristino ───────────────────────────────────

    def salva_backup(self) -> str:
        """Crea un backup dei dati di sistema."""
        return self._servizio_sistema.salva_backup()

    def elenca_backup(self) -> List[str]:
        """Restituisce la lista dei backup disponibili."""
        return self._servizio_sistema.elenca_backup()

    def carica_backup(self, percorso: str) -> str:
        """Carica un backup e ripristina il sistema."""
        return self._servizio_sistema.carica_backup(percorso)
