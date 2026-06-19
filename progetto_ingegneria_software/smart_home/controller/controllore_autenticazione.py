"""
Controllore per l'autenticazione e la gestione degli utenti.

Gestisce il flusso di login, registrazione e amministrazione utenti.
"""

from smart_home.domain.utente import Utente
from smart_home.service.servizio_utenti import ServizioUtenti


class ControlloreAutenticazione:
    """Orchestra il flusso di login e gestione utenti."""

    def __init__(self, servizio_utenti):
        self._servizio_utenti = servizio_utenti

    def effettua_login(self, email, password):
        return self._servizio_utenti.autentica(email, password)

    def registra_utente(self, nome, email, password,
                        tipo="utente"):
        return self._servizio_utenti.crea_utente(nome, email, password, tipo)

    def elenca_utenti(self):
        return self._servizio_utenti.elenca_utenti()

    def elimina_utente(self, id_utente):
        return self._servizio_utenti.elimina_utente(id_utente)
