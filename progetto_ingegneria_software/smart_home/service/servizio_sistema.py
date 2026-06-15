"""
Servizio per le funzionalita di sistema.

Fornisce il riepilogo per la dashboard, il monitoraggio dei dispositivi,
la generazione di statistiche, il backup e il ripristino dei dati.
"""

from typing import List, Optional

from smart_home.domain.dispositivo import Dispositivo
from smart_home.domain.evento import Evento
from smart_home.repository.interfaces import (
    RepositoryDatiSistema,
    RepositoryDispositivi,
    RepositoryEventi,
    RepositoryStanze,
)


class ServizioSistema:
    """Business logic per dashboard, monitoraggio, statistiche, backup e ripristino."""

    def __init__(self, repository_stanze: RepositoryStanze,
                 repository_dispositivi: RepositoryDispositivi,
                 repository_eventi: RepositoryEventi,
                 repository_dati_sistema: RepositoryDatiSistema,
                 servizio_log: Optional["ServizioLog"] = None) -> None:
        self._repository_stanze = repository_stanze
        self._repository_dispositivi = repository_dispositivi
        self._repository_eventi = repository_eventi
        self._repository_dati_sistema = repository_dati_sistema
        self._servizio_log = servizio_log

    def carica_riepilogo(self, id_utente: str) -> str:
        """
        Restituisce un riepilogo testuale del sistema per la dashboard.

        Include numero di stanze, dispositivi totali, dispositivi offline
        e automazioni attive.
        """
        stanze = self._repository_stanze.trova_tutti()
        dispositivi = self._repository_dispositivi.trova_tutti()
        offline = [d for d in dispositivi if not d.online]

        return (f"Dashboard utente {id_utente}\n"
                f"Stanze: {len(stanze)}\n"
                f"Dispositivi: {len(dispositivi)} (offline: {len(offline)})\n")

    def monitora_dispositivi(self) -> List[Dispositivo]:
        """Restituisce tutti i dispositivi offline per il monitoraggio."""
        return self._repository_dispositivi.trova_offline()

    def genera_statistiche(self, filtro: str) -> List[Evento]:
        """Restituisce gli eventi aggregati in base a un filtro."""
        return self._repository_eventi.aggrega(filtro)

    # ── Backup ────────────────────────────────────────────────

    def salva_backup(self) -> str:
        """
        Crea un backup unificato di tutti i dati di sistema.

        Restituisce il percorso del file creato.
        """
        try:
            percorso = self._repository_dati_sistema.salva_backup()
            if self._servizio_log:
                self._servizio_log.registra_evento(
                    "BACKUP_COMPLETATO",
                    f"Backup creato: {percorso}",
                )
            return f"Backup creato: {percorso}"
        except Exception as e:
            if self._servizio_log:
                self._servizio_log.registra_evento(
                    "BACKUP_FALLITO",
                    f"Errore durante il backup: {e}",
                )
            return f"Backup fallito: {e}"

    def elenca_backup(self) -> List[str]:
        """Restituisce la lista dei file di backup disponibili."""
        return self._repository_dati_sistema.elenca_backup()

    def carica_backup(self, percorso: str) -> str:
        """
        Carica un file di backup e ripristina lo stato del sistema.

        Restituisce un messaggio di esito.
        """
        try:
            msg = self._repository_dati_sistema.carica_backup(percorso)
            if self._servizio_log:
                self._servizio_log.registra_evento(
                    "RIPRISTINO_COMPLETATO",
                    msg,
                )
            return msg
        except Exception as e:
            if self._servizio_log:
                self._servizio_log.registra_evento(
                    "RIPRISTINO_FALLITO",
                    f"Errore durante il ripristino: {e}",
                )
            return f"Ripristino fallito: {e}"

    # ── Metodo legacy (sostituito) ────────────────────────────

    def esegui_backup(self) -> str:
        """Alias per salva_backup. Mantenuto per compatibilita."""
        return self.salva_backup()
