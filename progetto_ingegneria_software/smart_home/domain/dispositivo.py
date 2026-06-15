"""
Modello del dominio: Dispositivo.

Rappresenta un dispositivo smart (luce, termostato, serratura, ecc.)
collegato al sistema.
"""

from __future__ import annotations

from typing import Optional


class Dispositivo:
    """Dispositivo intelligente con stato, tipo e connessione."""

    def __init__(self, id_dispositivo: str, nome: str, tipo: str,
                 id_stanza: str) -> None:
        self._id: str = id_dispositivo
        self._nome: str = nome
        self._tipo: str = tipo
        self._stato: str = "spento"
        self._online: bool = True
        self._id_stanza: str = id_stanza

    @property
    def id(self) -> str:
        return self._id

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    def nome(self, valore: str) -> None:
        self._nome = valore

    @property
    def tipo(self) -> str:
        return self._tipo

    @property
    def stato(self) -> str:
        return self._stato

    @property
    def online(self) -> bool:
        return self._online

    @online.setter
    def online(self, valore: bool) -> None:
        self._online = valore

    @property
    def id_stanza(self) -> str:
        return self._id_stanza

    @id_stanza.setter
    def id_stanza(self, valore: str) -> None:
        self._id_stanza = valore

    def accendi(self) -> None:
        """Accende il dispositivo e ne aggiorna lo stato."""
        self._stato = "acceso"

    def spegni(self) -> None:
        """Spegne il dispositivo e ne aggiorna lo stato."""
        self._stato = "spento"

    def cambia_stato(self, nuovo_stato: str) -> bool:
        """Imposta un nuovo stato personalizzato. Restituisce False se il dispositivo offline."""
        if not self._online:
            return False
        self._stato = nuovo_stato
        return True

    def invia_comando(self, comando: str) -> bool:
        """
        Elabora un comando testuale sul dispositivo.

        Comandi riconosciuti: 'accendi', 'spegni', oppure un valore personalizzato.
        """
        if not self._online:
            return False
        comando_normalizzato = comando.strip().lower()
        if comando_normalizzato == "accendi":
            self.accendi()
        elif comando_normalizzato == "spegni":
            self.spegni()
        else:
            self._stato = comando
        return True

    def is_online(self) -> bool:
        """Verifica se il dispositivo connesso alla rete."""
        return self._online

    def get_stato(self) -> str:
        """Restituisce lo stato corrente del dispositivo."""
        return self._stato

    def get_tipo(self) -> str:
        """Restituisce il tipo del dispositivo."""
        return self._tipo

    def applica_comando(self, comando: str) -> bool:
        """Alias per invia_comando, usato nei diagrammi di sequenza."""
        return self.invia_comando(comando)
