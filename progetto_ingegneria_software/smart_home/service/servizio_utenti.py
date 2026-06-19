"""
Servizio per la gestione degli utenti.

Fornisce i metodi di autenticazione e gestione del profilo utente.
"""

import uuid

from smart_home.domain.utente import Amministratore, Utente
from smart_home.repository.interfaces import RepositoryUtenti


class ServizioUtenti:
    """Business logic per l'autenticazione e la gestione degli utenti."""

    def __init__(self, repository_utenti):
        self._repository_utenti = repository_utenti

    def autentica(self, email, password):
        utente = self._repository_utenti.trova_per_email(email)
        if utente is None:
            return None
        if utente.autentica(password):
            return utente
        return None

    def crea_utente(self, nome, email, password, tipo="utente"):
        esistente = self._repository_utenti.trova_per_email(email)
        if esistente is not None:
            return None
        nuovo_id = str(uuid.uuid4())
        if tipo == "amministratore":
            utente = Amministratore(nuovo_id, nome, email, password)
        else:
            utente = Utente(nuovo_id, nome, email, password)
        self._repository_utenti.salva(utente)
        return utente

    def elenca_utenti(self):
        return self._repository_utenti.trova_tutti()

    def elimina_utente(self, id_utente):
        return self._repository_utenti.elimina(id_utente)
