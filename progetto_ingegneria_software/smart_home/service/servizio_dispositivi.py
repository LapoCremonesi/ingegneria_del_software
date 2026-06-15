"""
Servizio per la gestione e il controllo dei dispositivi.

Fornisce operazioni CRUD sui dispositivi e l'invio di comandi,
registrando automaticamente gli eventi nel log di sistema.
"""

from typing import List, Optional

from smart_home.domain.dispositivo import Dispositivo
from smart_home.repository.interfaces import RepositoryDispositivi


class ServizioDispositivi:
    """Business logic per CRUD e controllo dei dispositivi smart."""

    def __init__(self, repository_dispositivi: RepositoryDispositivi,
                 servizio_log: Optional["ServizioLog"] = None) -> None:
        self._repository_dispositivi = repository_dispositivi
        self._servizio_log = servizio_log

    @property
    def servizio_log(self) -> Optional["ServizioLog"]:
        return self._servizio_log

    @servizio_log.setter
    def servizio_log(self, valore: "ServizioLog") -> None:
        self._servizio_log = valore

    def crea(self, dispositivo: Dispositivo) -> Dispositivo:
        """Crea un nuovo dispositivo."""
        self._repository_dispositivi.salva(dispositivo)
        if self._servizio_log:
            self._servizio_log.registra_evento(
                "DISPOSITIVO_CREATO",
                f"Dispositivo '{dispositivo.nome}' creato",
            )
        return dispositivo

    def aggiorna(self, dispositivo: Dispositivo) -> Dispositivo:
        """Aggiorna un dispositivo esistente."""
        self._repository_dispositivi.aggiorna(dispositivo)
        return dispositivo

    def elimina(self, id_dispositivo: str) -> bool:
        """Elimina un dispositivo dato il suo id."""
        return self._repository_dispositivi.elimina(id_dispositivo)

    def elenca(self) -> List[Dispositivo]:
        """Restituisce l'elenco di tutti i dispositivi."""
        return self._repository_dispositivi.trova_tutti()

    def trova_per_id(self, id_dispositivo: str) -> Optional[Dispositivo]:
        """Restituisce un dispositivo per id."""
        return self._repository_dispositivi.trova_per_id(id_dispositivo)

    def invia_comando(self, id_dispositivo: str, comando: str) -> Optional[Dispositivo]:
        """
        Invia un comando a un dispositivo.

        Se il comando viene eseguito correttamente restituisce il Dispositivo
        aggiornato, altrimenti None.
        """
        dispositivo = self._repository_dispositivi.trova_per_id(id_dispositivo)
        if dispositivo is None:
            return None

        esito = dispositivo.applica_comando(comando)
        if esito:
            self._repository_dispositivi.aggiorna(dispositivo)
            if self._servizio_log:
                self._servizio_log.registra_evento(
                    "COMANDO_ESEGUITO",
                    f"Comando '{comando}' eseguito su '{dispositivo.nome}'",
                    id_dispositivo=id_dispositivo,
                )
        else:
            if self._servizio_log:
                self._servizio_log.registra_evento(
                    "COMANDO_FALLITO",
                    f"Comando '{comando}' fallito su '{dispositivo.nome}'",
                    id_dispositivo=id_dispositivo,
                )
            return None

        return dispositivo
