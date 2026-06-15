"""
Modello del dominio: Stanza.

Rappresenta una stanza fisica della casa che pu contenere dispositivi.
"""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from smart_home.domain.dispositivo import Dispositivo


class Stanza:
    """Rappresenta una stanza con un identificativo, nome, piano e lista di dispositivi."""

    def __init__(self, id_stanza: str, nome: str, piano: int) -> None:
        self._id: str = id_stanza
        self._nome: str = nome
        self._piano: int = piano
        self._dispositivi: List[Dispositivo] = []

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
    def piano(self) -> int:
        return self._piano

    @piano.setter
    def piano(self, valore: int) -> None:
        self._piano = valore

    @property
    def dispositivi(self) -> List[Dispositivo]:
        return list(self._dispositivi)

    def aggiungi_dispositivo(self, dispositivo: Dispositivo) -> None:
        """Aggiunge un dispositivo alla stanza."""
        self._dispositivi.append(dispositivo)

    def rimuovi_dispositivo(self, id_dispositivo: str) -> bool:
        """Rimuove un dispositivo dalla stanza dato il suo id. Restituisce True se rimosso."""
        for d in self._dispositivi:
            if d.id == id_dispositivo:
                self._dispositivi.remove(d)
                return True
        return False

    def elenca_dispositivi(self) -> List[Dispositivo]:
        """Restituisce la lista di tutti i dispositivi presenti nella stanza."""
        return self.dispositivi

    def get_dispositivi_per_tipo(self, tipo: str) -> List[Dispositivo]:
        """Filtra i dispositivi per tipo (es. 'luce', 'termostato', 'serratura')."""
        return [d for d in self._dispositivi if d.tipo == tipo]
