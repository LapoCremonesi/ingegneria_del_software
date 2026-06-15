"""
Controllore per l'autenticazione.

Gestisce il flusso di login: riceve le credenziali, le passa al servizio
e restituisce l'esito alla vista.
"""

from typing import Optional

from smart_home.domain.utente import Utente
from smart_home.service.servizio_utenti import ServizioUtenti


class ControlloreAutenticazione:
    """Orchestra il flusso di login."""

    def __init__(self, servizio_utenti: ServizioUtenti) -> None:
        self._servizio_utenti = servizio_utenti

    def effettua_login(self, email: str, password: str) -> Optional[Utente]:
        """
        Tenta l'autenticazione con le credenziali fornite.

        Restituisce l'oggetto Utente in caso di successo, None altrimenti.
        """
        return self._servizio_utenti.autentica(email, password)
