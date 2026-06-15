"""
Servizio per la gestione degli utenti.

Fornisce i metodi di autenticazione e gestione del profilo utente.
"""

from typing import Optional

from smart_home.domain.utente import Utente, Amministratore
from smart_home.repository.interfaces import RepositoryUtenti


class ServizioUtenti:
    """Business logic per l'autenticazione e la gestione degli utenti."""

    def __init__(self, repository_utenti: RepositoryUtenti) -> None:
        self._repository_utenti = repository_utenti

    def autentica(self, email: str, password: str) -> Optional[Utente]:
        """
        Cerca un utente per email e verifica la password.

        Restituisce l'oggetto Utente se l'autenticazione riesce,
        None altrimenti.
        """
        utente = self._repository_utenti.trova_per_email(email)
        if utente is None:
            return None
        if utente.autentica(password):
            return utente
        return None
