"""
Controllore per le funzionalita di sistema.

Orchestra l'apertura della dashboard, il monitoraggio dei dispositivi,
la generazione di statistiche, il backup e il ripristino dei dati.
"""

from smart_home.domain.dispositivo import Dispositivo
from smart_home.domain.evento import Evento
from smart_home.service.servizio_sistema import ServizioSistema


class ControlloreSistema:
    """Orchestra le operazioni di sistema (dashboard, monitoraggio,
    backup, ripristino, statistiche)."""

    def __init__(self, servizio_sistema):
        self._servizio_sistema = servizio_sistema

    def apri_dashboard(self, id_utente):
        """Restituisce il riepilogo del sistema per la dashboard."""
        return self._servizio_sistema.carica_riepilogo(id_utente)

    def monitora_dispositivi(self):
        """Restituisce i dispositivi offline per il monitoraggio."""
        return self._servizio_sistema.monitora_dispositivi()

    def genera_statistiche(self, filtro):
        """Restituisce statistiche aggregate per un filtro."""
        return self._servizio_sistema.genera_statistiche(filtro)

    def esegui_automazioni(self):
        return self._servizio_sistema.esegui_automazioni_ora()

    # ── Backup e ripristino ───────────────────────────────────

    def salva_backup(self):
        """Crea un backup dei dati di sistema."""
        return self._servizio_sistema.salva_backup()

    def elenca_backup(self):
        """Restituisce la lista dei backup disponibili."""
        return self._servizio_sistema.elenca_backup()

    def carica_backup(self, percorso):
        """Carica un backup e ripristina il sistema."""
        return self._servizio_sistema.carica_backup(percorso)

    def elimina_backup(self, percorso):
        """Elimina un file di backup."""
        return self._servizio_sistema.elimina_backup(percorso)
