"""
Servizio per la gestione delle stanze.

Fornisce le operazioni CRUD sulle stanze della casa.
"""

from typing import List, Optional

from smart_home.domain.stanza import Stanza
from smart_home.repository.interfaces import RepositoryStanze


class ServizioStanze:
    """Business logic per le operazioni CRUD sulle stanze."""

    def __init__(self, repository_stanze: RepositoryStanze) -> None:
        self._repository_stanze = repository_stanze

    def crea(self, stanza: Stanza) -> Stanza:
        """Crea una nuova stanza e la salva nel repository."""
        self._repository_stanze.salva(stanza)
        return stanza

    def aggiorna(self, stanza: Stanza) -> Stanza:
        """Aggiorna una stanza esistente."""
        self._repository_stanze.aggiorna(stanza)
        return stanza

    def elimina(self, id_stanza: str) -> bool:
        """Elimina una stanza dato il suo id."""
        return self._repository_stanze.elimina(id_stanza)

    def elenca(self) -> List[Stanza]:
        """Restituisce l'elenco di tutte le stanze."""
        return self._repository_stanze.trova_tutti()

    def trova_per_id(self, id_stanza: str) -> Optional[Stanza]:
        """Restituisce una stanza per id."""
        return self._repository_stanze.trova_per_id(id_stanza)
