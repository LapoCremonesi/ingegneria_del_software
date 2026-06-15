"""
Servizio per la registrazione e la consultazione del log eventi.

Fornisce metodi per registrare eventi di sistema, cercarli per filtro
ed esportarli in formato testuale.
"""

import uuid
from typing import List, Optional

from smart_home.domain.evento import Evento
from smart_home.repository.interfaces import RepositoryEventi


class ServizioLog:
    """Business logic per la gestione del log eventi."""

    def __init__(self, repository_eventi: RepositoryEventi) -> None:
        self._repository_eventi = repository_eventi

    def registra_evento(self, tipo: str, messaggio: str,
                        id_dispositivo: Optional[str] = None) -> Evento:
        """
        Crea un nuovo evento e lo salva nel repository.

        Restituisce l'Evento appena creato.
        """
        evento = Evento(
            id_evento=str(uuid.uuid4()),
            tipo=tipo,
            descrizione=messaggio,
            id_dispositivo=id_dispositivo,
        )
        self._repository_eventi.salva(evento)
        return evento

    def elenca_eventi(self, filtro: str) -> List[Evento]:
        """Cerca eventi applicando un filtro testuale."""
        return self._repository_eventi.cerca(filtro)

    def esporta_eventi(self, filtro: str) -> str:
        """Cerca eventi per filtro e li restituisce come stringa formattata."""
        eventi = self.elenca_eventi(filtro)
        righe = [e.to_string() for e in eventi]
        return "\n".join(righe) if righe else "Nessun evento trovato."
