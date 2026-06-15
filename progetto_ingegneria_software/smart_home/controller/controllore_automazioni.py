"""
Controllore per la gestione delle automazioni.

Orchestra le operazioni CRUD delle automazioni e l'esecuzione
delle regole automatiche.
"""

from typing import List, Optional

from smart_home.domain.automazione import Automazione
from smart_home.service.servizio_automazioni import ServizioAutomazioni


class ControlloreAutomazioni:
    """Orchestra il flusso di CRUD e attivazione delle automazioni."""

    def __init__(self, servizio_automazioni: ServizioAutomazioni) -> None:
        self._servizio_automazioni = servizio_automazioni

    def crea_regola(self, automazione: Automazione) -> Automazione:
        """Crea una nuova automazione."""
        return self._servizio_automazioni.crea(automazione)

    def aggiorna_regola(self, automazione: Automazione) -> Automazione:
        """Aggiorna un'automazione esistente."""
        return self._servizio_automazioni.aggiorna(automazione)

    def elimina_regola(self, id_automazione: str) -> bool:
        """Elimina un'automazione dato il suo id."""
        return self._servizio_automazioni.elimina(id_automazione)

    def elenca_regole(self) -> List[Automazione]:
        """Restituisce l'elenco di tutte le automazioni."""
        return self._servizio_automazioni.elenca()

    def trova_regola_per_id(self, id_automazione: str) -> Optional[Automazione]:
        """Restituisce un'automazione per id."""
        return self._servizio_automazioni.trova_per_id(id_automazione)
