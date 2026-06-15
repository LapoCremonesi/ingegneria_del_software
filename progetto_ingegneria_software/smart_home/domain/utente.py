"""
Modello del dominio: Utente e Amministratore.

Gestisce l'autenticazione e la gestione degli utenti del sistema.
"""

from __future__ import annotations

import hashlib
import uuid
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from smart_home.domain.automazione import Automazione
    from smart_home.domain.evento import Evento


class Utente:
    """Rappresenta un utente generico del sistema Smart Home."""

    def __init__(self, id_utente: str, nome: str, email: str, password: str) -> None:
        self._id: str = id_utente
        self._nome: str = nome
        self._email: str = email
        self._password_hash: str = self._hash_password(password)

    @property
    def id(self) -> str:
        return self._id

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def email(self) -> str:
        return self._email

    def autentica(self, password: str) -> bool:
        """Verifica se la password fornata corrisponde a quella memorizzata."""
        return self._password_hash == self._hash_password(password)

    def cambia_password(self, nuova_password: str) -> None:
        """Aggiorna la password dell'utente."""
        self._password_hash = self._hash_password(nuova_password)

    @staticmethod
    def _hash_password(password: str) -> str:
        """Restituisce l'hash SHA-256 della password."""
        return hashlib.sha256(password.encode()).hexdigest()


class Amministratore(Utente):
    """Amministratore del sistema. Estende Utente con permessi aggiuntivi."""

    def __init__(self, id_utente: str, nome: str, email: str,
                 password: str, livello_accesso: int = 1) -> None:
        super().__init__(id_utente, nome, email, password)
        self._livello_accesso: int = livello_accesso

    @property
    def livello_accesso(self) -> int:
        return self._livello_accesso

    def gestisci_automazione(self, automazione: Automazione) -> None:
        """Attiva o disattiva un'automazione."""
        if automazione.attiva:
            automazione.disattiva_automazione()
        else:
            automazione.attiva_automazione()

    def consulta_log(self, eventi: List[Evento]) -> List[Evento]:
        """Restituisce l'elenco completo degli eventi (filtro opzionale)."""
        return eventi

    def crea_utente(self, utente: Utente) -> bool:
        return True

    def elimina_utente(self, id_utente: str) -> bool:
        return True
