"""
Controllore per la gestione delle stanze.

Orchestra le operazioni CRUD sulle stanze tra vista e servizio.
"""

import uuid

from smart_home.domain.stanza import Stanza
from smart_home.service.servizio_stanze import ServizioStanze


class ControlloreStanze:
    """Orchestra il flusso di creazione, modifica, eliminazione e lettura delle stanze."""

    def __init__(self, servizio_stanze):
        self._servizio_stanze = servizio_stanze

    def crea_stanza(self, nome, piano):
        """Crea una nuova stanza e la restituisce."""
        stanza = Stanza(id_stanza=str(uuid.uuid4()), nome=nome, piano=piano)
        return self._servizio_stanze.crea(stanza)

    def aggiorna_stanza(self, stanza):
        """Aggiorna una stanza esistente."""
        return self._servizio_stanze.aggiorna(stanza)

    def elimina_stanza(self, id_stanza):
        """Elimina una stanza dato il suo id."""
        return self._servizio_stanze.elimina(id_stanza)

    def elenca_stanze(self):
        """Restituisce l'elenco di tutte le stanze."""
        return self._servizio_stanze.elenca()

    def trova_stanza_per_id(self, id_stanza):
        """Restituisce una stanza per id."""
        return self._servizio_stanze.trova_per_id(id_stanza)
