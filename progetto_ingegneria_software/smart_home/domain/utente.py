"""
Modello del dominio: Utente e Amministratore.

Gestisce l'autenticazione e la gestione degli utenti del sistema.
"""

import hashlib
import uuid


class Utente:
    """Rappresenta un utente generico del sistema Smart Home."""

    def __init__(self, id_utente, nome, email, password):
        self._id = id_utente
        self._nome = nome
        self._email = email
        self._password_hash = self._hash_password(password)

    @property
    def id(self):
        return self._id

    @property
    def nome(self):
        return self._nome

    @property
    def email(self):
        return self._email

    def autentica(self, password):
        """Verifica se la password fornata corrisponde a quella memorizzata."""
        return self._password_hash == self._hash_password(password)

    def cambia_password(self, nuova_password):
        """Aggiorna la password dell'utente."""
        self._password_hash = self._hash_password(nuova_password)

    @staticmethod
    def _hash_password(password):
        """Restituisce l'hash SHA-256 della password."""
        return hashlib.sha256(password.encode()).hexdigest()


class Amministratore(Utente):
    """Amministratore del sistema. Estende Utente con permessi aggiuntivi."""

    def __init__(self, id_utente, nome, email, password, livello_accesso=1):
        super().__init__(id_utente, nome, email, password)
        self._livello_accesso = livello_accesso

    @property
    def livello_accesso(self):
        return self._livello_accesso

    def gestisci_automazione(self, automazione):
        """Attiva o disattiva un'automazione."""
        if automazione.attiva:
            automazione.disattiva_automazione()
        else:
            automazione.attiva_automazione()

    def consulta_log(self, eventi):
        """Restituisce l'elenco completo degli eventi (filtro opzionale)."""
        return eventi

    def crea_utente(self, utente):
        return True

    def elimina_utente(self, id_utente):
        return True
