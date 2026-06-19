"""
Interfacce astratte per i repository.

Definisce i contratti che ogni implementazione concreta (JSON, database, ecc.)
deve rispettare, permettendo di cambiare strategia di persistenza senza
alterare il resto dell'applicazione.
"""

from smart_home.domain.utente import Utente
from smart_home.domain.stanza import Stanza
from smart_home.domain.dispositivo import Dispositivo
from smart_home.domain.automazione import Automazione
from smart_home.domain.evento import Evento


class RepositoryUtenti:
    """Interfaccia per la persistenza degli utenti."""

    def trova_per_email(self, email):
        """Cerca un utente per email. Restituisce None se non trovato."""
        pass

    def salva(self, utente):
        """Salva un utente (creazione o aggiornamento)."""
        pass

    def aggiorna(self, utente):
        """Aggiorna un utente esistente."""
        pass

    def trova_tutti(self):
        """Restituisce tutti gli utenti."""
        pass

    def elimina(self, id_utente):
        """Elimina un utente dato il suo id."""
        pass


class RepositoryStanze:
    """Interfaccia per la persistenza delle stanze."""

    def trova_tutti(self):
        """Restituisce tutte le stanze."""
        pass

    def trova_per_id(self, id_stanza):
        """Cerca una stanza per id. Restituisce None se non trovata."""
        pass

    def salva(self, stanza):
        """Salva una nuova stanza."""
        pass

    def aggiorna(self, stanza):
        """Aggiorna una stanza esistente."""
        pass

    def elimina(self, id_stanza):
        """Elimina una stanza dato il suo id."""
        pass


class RepositoryDispositivi:
    """Interfaccia per la persistenza dei dispositivi."""

    def trova_tutti(self):
        """Restituisce tutti i dispositivi."""
        pass

    def trova_per_id(self, id_dispositivo):
        """Cerca un dispositivo per id."""
        pass

    def salva(self, dispositivo):
        """Salva un nuovo dispositivo."""
        pass

    def aggiorna(self, dispositivo):
        """Aggiorna un dispositivo esistente."""
        pass

    def elimina(self, id_dispositivo):
        """Elimina un dispositivo dato il suo id."""
        pass

    def aggiorna_stanza(self, id_dispositivo, id_stanza):
        """Sposta un dispositivo in un'altra stanza."""
        pass

    def trova_offline(self):
        """Restituisce tutti i dispositivi offline."""
        pass


class RepositoryAutomazioni:
    """Interfaccia per la persistenza delle automazioni."""

    def trova_tutti(self):
        """Restituisce tutte le automazioni."""
        pass

    def trova_per_id(self, id_automazione):
        """Cerca un'automazione per id. Restituisce None se non trovata."""
        pass

    def trova_attive(self):
        """Restituisce solo le automazioni attive."""
        pass

    def salva(self, automazione):
        """Salva una nuova automazione."""
        pass

    def aggiorna(self, automazione):
        """Aggiorna un'automazione esistente."""
        pass

    def elimina(self, id_automazione):
        """Elimina un'automazione dato il suo id."""
        pass


class RepositoryEventi:
    """Interfaccia per la persistenza degli eventi di log."""

    def cerca(self, filtro):
        """Cerca eventi applicando un filtro testuale."""
        pass

    def salva(self, evento):
        """Salva un nuovo evento."""
        pass

    def aggrega(self, filtro):
        """Restituisce eventi aggregati secondo un criterio."""
        pass


class RepositoryDatiSistema:
    """Interfaccia per backup e ripristino dei dati di sistema."""

    def salva_backup(self):
        """Crea un backup unificato di tutti i dati del sistema. Restituisce il percorso."""
        pass

    def elenca_backup(self):
        """Restituisce la lista dei file di backup disponibili."""
        pass

    def carica_backup(self, percorso):
        """Carica un file di backup e ripristina tutti i dati. Restituisce un messaggio."""
        pass

    def elimina_backup(self, percorso):
        """Elimina un file di backup. Restituisce True se eliminato."""
        pass
