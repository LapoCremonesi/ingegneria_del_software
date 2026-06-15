"""
Interfacce astratte per i repository.

Definisce i contratti che ogni implementazione concreta (JSON, database, ecc.)
deve rispettare, permettendo di cambiare strategia di persistenza senza
alterare il resto dell'applicazione.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from smart_home.domain.utente import Utente
from smart_home.domain.stanza import Stanza
from smart_home.domain.dispositivo import Dispositivo
from smart_home.domain.automazione import Automazione
from smart_home.domain.evento import Evento


class RepositoryUtenti(ABC):
    """Interfaccia per la persistenza degli utenti."""

    @abstractmethod
    def trova_per_email(self, email: str) -> Optional[Utente]:
        """Cerca un utente per email. Restituisce None se non trovato."""
        pass

    @abstractmethod
    def salva(self, utente: Utente) -> None:
        """Salva un utente (creazione o aggiornamento)."""
        pass

    @abstractmethod
    def aggiorna(self, utente: Utente) -> None:
        """Aggiorna un utente esistente."""
        pass


class RepositoryStanze(ABC):
    """Interfaccia per la persistenza delle stanze."""

    @abstractmethod
    def trova_tutti(self) -> List[Stanza]:
        """Restituisce tutte le stanze."""
        pass

    @abstractmethod
    def trova_per_id(self, id_stanza: str) -> Optional[Stanza]:
        """Cerca una stanza per id. Restituisce None se non trovata."""
        pass

    @abstractmethod
    def salva(self, stanza: Stanza) -> None:
        """Salva una nuova stanza."""
        pass

    @abstractmethod
    def aggiorna(self, stanza: Stanza) -> None:
        """Aggiorna una stanza esistente."""
        pass

    @abstractmethod
    def elimina(self, id_stanza: str) -> bool:
        """Elimina una stanza dato il suo id."""
        pass


class RepositoryDispositivi(ABC):
    """Interfaccia per la persistenza dei dispositivi."""

    @abstractmethod
    def trova_tutti(self) -> List[Dispositivo]:
        """Restituisce tutti i dispositivi."""
        pass

    @abstractmethod
    def trova_per_id(self, id_dispositivo: str) -> Optional[Dispositivo]:
        """Cerca un dispositivo per id."""
        pass

    @abstractmethod
    def salva(self, dispositivo: Dispositivo) -> None:
        """Salva un nuovo dispositivo."""
        pass

    @abstractmethod
    def aggiorna(self, dispositivo: Dispositivo) -> None:
        """Aggiorna un dispositivo esistente."""
        pass

    @abstractmethod
    def elimina(self, id_dispositivo: str) -> bool:
        """Elimina un dispositivo dato il suo id."""
        pass

    @abstractmethod
    def aggiorna_stanza(self, id_dispositivo: str, id_stanza: str) -> bool:
        """Sposta un dispositivo in un'altra stanza."""
        pass

    @abstractmethod
    def trova_offline(self) -> List[Dispositivo]:
        """Restituisce tutti i dispositivi offline."""
        pass


class RepositoryAutomazioni(ABC):
    """Interfaccia per la persistenza delle automazioni."""

    @abstractmethod
    def trova_tutti(self) -> List[Automazione]:
        """Restituisce tutte le automazioni."""
        pass

    @abstractmethod
    def trova_per_id(self, id_automazione: str) -> Optional[Automazione]:
        """Cerca un'automazione per id. Restituisce None se non trovata."""
        pass

    @abstractmethod
    def trova_attive(self) -> List[Automazione]:
        """Restituisce solo le automazioni attive."""
        pass

    @abstractmethod
    def salva(self, automazione: Automazione) -> None:
        """Salva una nuova automazione."""
        pass

    @abstractmethod
    def aggiorna(self, automazione: Automazione) -> None:
        """Aggiorna un'automazione esistente."""
        pass

    @abstractmethod
    def elimina(self, id_automazione: str) -> bool:
        """Elimina un'automazione dato il suo id."""
        pass


class RepositoryEventi(ABC):
    """Interfaccia per la persistenza degli eventi di log."""

    @abstractmethod
    def cerca(self, filtro: str) -> List[Evento]:
        """Cerca eventi applicando un filtro testuale."""
        pass

    @abstractmethod
    def salva(self, evento: Evento) -> None:
        """Salva un nuovo evento."""
        pass

    @abstractmethod
    def aggrega(self, filtro: str) -> List[Evento]:
        """Restituisce eventi aggregati secondo un criterio."""
        pass


class RepositoryDatiSistema(ABC):
    """Interfaccia per backup e ripristino dei dati di sistema."""

    @abstractmethod
    def salva_backup(self) -> str:
        """Crea un backup unificato di tutti i dati del sistema. Restituisce il percorso."""
        pass

    @abstractmethod
    def elenca_backup(self) -> List[str]:
        """Restituisce la lista dei file di backup disponibili."""
        pass

    @abstractmethod
    def carica_backup(self, percorso: str) -> str:
        """Carica un file di backup e ripristina tutti i dati. Restituisce un messaggio."""
        pass
