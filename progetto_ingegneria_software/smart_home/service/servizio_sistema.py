"""
Servizio per le funzionalita di sistema.

Fornisce il riepilogo per la dashboard, il monitoraggio dei dispositivi,
la generazione di statistiche, il backup e il ripristino dei dati.
"""

from smart_home.domain.dispositivo import Dispositivo
from smart_home.domain.evento import Evento
from smart_home.repository.interfaces import (
    RepositoryAutomazioni,
    RepositoryDatiSistema,
    RepositoryDispositivi,
    RepositoryEventi,
    RepositoryStanze,
)


class ServizioSistema:
    """Business logic per dashboard, monitoraggio, statistiche, backup e ripristino."""

    def __init__(self, repository_stanze,
                 repository_dispositivi,
                 repository_eventi,
                 repository_dati_sistema,
                 servizio_log=None,
                 repository_automazioni=None,
                 servizio_automazioni=None):
        self._repository_stanze = repository_stanze
        self._repository_dispositivi = repository_dispositivi
        self._repository_eventi = repository_eventi
        self._repository_dati_sistema = repository_dati_sistema
        self._servizio_log = servizio_log
        self._repository_automazioni = repository_automazioni
        self._servizio_automazioni = servizio_automazioni

    def carica_riepilogo(self, id_utente):
        """
        Restituisce un riepilogo testuale del sistema per la dashboard.

        Include numero di stanze, dispositivi totali, dispositivi offline,
        automazioni attive e lo stato dei dispositivi stanza per stanza.
        """
        stanze = self._repository_stanze.trova_tutti()
        dispositivi = self._repository_dispositivi.trova_tutti()
        offline = [d for d in dispositivi if not d.online]
        automazioni = (self._repository_automazioni.trova_tutti()
                       if self._repository_automazioni else [])
        attive = len([a for a in automazioni if a.attiva])

        stanza_map = {}
        for s in stanze:
            stanza_map[s.id] = s.nome
        disp_per_stanza = {}
        for d in dispositivi:
            stanza_id = d.id_stanza
            disp_per_stanza.setdefault(stanza_id, []).append(d)

        testo = (f"Dashboard utente {id_utente}\n"
                 f"Stanze: {len(stanze)}\n"
                 f"Dispositivi: {len(dispositivi)} (offline: {len(offline)})\n"
                 f"Automazioni: {len(automazioni)} (attive: {attive})\n\n")

        testo += "--- Stato Dispositivi ---\n"
        for stanza in stanze:
            testo += f"\n[{stanza.nome} (piano {stanza.piano})]\n"
            for d in disp_per_stanza.get(stanza.id, []):
                stato = d.stato
                if not d.online:
                    stato += " [OFFLINE]"
                testo += f"  {d.nome}: {stato}\n"

        return testo

    def monitora_dispositivi(self):
        """Restituisce tutti i dispositivi offline per il monitoraggio."""
        return self._repository_dispositivi.trova_offline()

    def genera_statistiche(self, filtro):
        """Restituisce gli eventi aggregati in base a un filtro."""
        return self._repository_eventi.aggrega(filtro)

    def esegui_automazioni_ora(self):
        if self._servizio_automazioni is None:
            return []
        return self._servizio_automazioni.esegui_tutte()

    # ── Backup ────────────────────────────────────────────────

    def salva_backup(self):
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

    def elenca_backup(self):
        """Restituisce la lista dei file di backup disponibili."""
        return self._repository_dati_sistema.elenca_backup()

    def carica_backup(self, percorso):
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

    def elimina_backup(self, percorso):
        """
        Elimina un file di backup.

        Restituisce True se il file esisteva ed e stato rimosso.
        """
        try:
            risultato = self._repository_dati_sistema.elimina_backup(percorso)
            if risultato and self._servizio_log:
                self._servizio_log.registra_evento(
                    "BACKUP_ELIMINATO",
                    f"Backup eliminato: {percorso}",
                )
            return risultato
        except Exception as e:
            if self._servizio_log:
                self._servizio_log.registra_evento(
                    "BACKUP_ELIMINAZIONE_FALLITA",
                    f"Errore durante l'eliminazione del backup: {e}",
                )
            return False

    # ── Metodo legacy (sostituito) ────────────────────────────

    def esegui_backup(self):
        """Alias per salva_backup. Mantenuto per compatibilita."""
        return self.salva_backup()
