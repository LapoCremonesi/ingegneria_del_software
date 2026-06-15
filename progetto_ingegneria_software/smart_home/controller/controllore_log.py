"""
Controllore per la consultazione del log eventi.

Orchestra il flusso di ricerca ed esportazione degli eventi di sistema.
"""

from typing import List

from smart_home.domain.evento import Evento
from smart_home.service.servizio_log import ServizioLog


class ControlloreLog:
    """Orchestra il flusso di consultazione ed esportazione del log."""

    def __init__(self, servizio_log: ServizioLog) -> None:
        self._servizio_log = servizio_log

    def elenca_eventi(self, filtro: str) -> List[Evento]:
        """Cerca eventi applicando un filtro testuale."""
        return self._servizio_log.elenca_eventi(filtro)

    def esporta_eventi(self, filtro: str) -> str:
        """Cerca eventi e li restituisce come stringa esportabile."""
        return self._servizio_log.esporta_eventi(filtro)
