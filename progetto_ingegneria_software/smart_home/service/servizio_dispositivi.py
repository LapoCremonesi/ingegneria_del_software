"""
Servizio per la gestione e il controllo dei dispositivi.

Fornisce operazioni CRUD sui dispositivi e l'invio di comandi,
registrando automaticamente gli eventi nel log di sistema.
"""

from smart_home.domain.dispositivo import Dispositivo
from smart_home.repository.interfaces import RepositoryDispositivi


class ServizioDispositivi:
    """Business logic per CRUD e controllo dei dispositivi smart."""

    def __init__(self, repository_dispositivi,
                 servizio_log=None):
        self._repository_dispositivi = repository_dispositivi
        self._servizio_log = servizio_log

    @property
    def servizio_log(self):
        return self._servizio_log

    @servizio_log.setter
    def servizio_log(self, valore):
        self._servizio_log = valore

    def crea(self, dispositivo):
        """Crea un nuovo dispositivo."""
        self._repository_dispositivi.salva(dispositivo)
        if self._servizio_log:
            self._servizio_log.registra_evento(
                "DISPOSITIVO_CREATO",
                f"Dispositivo '{dispositivo.nome}' creato",
            )
        return dispositivo

    def aggiorna(self, dispositivo):
        """Aggiorna un dispositivo esistente."""
        self._repository_dispositivi.aggiorna(dispositivo)
        return dispositivo

    def elimina(self, id_dispositivo):
        """Elimina un dispositivo dato il suo id."""
        dispositivo = self._repository_dispositivi.trova_per_id(id_dispositivo)
        nome = dispositivo.nome if dispositivo else id_dispositivo
        risultato = self._repository_dispositivi.elimina(id_dispositivo)
        if risultato and self._servizio_log:
            self._servizio_log.registra_evento(
                "DISPOSITIVO_ELIMINATO",
                f"Dispositivo '{nome}' eliminato",
            )
        return risultato

    def elenca(self):
        """Restituisce l'elenco di tutti i dispositivi."""
        return self._repository_dispositivi.trova_tutti()

    def trova_per_id(self, id_dispositivo):
        """Restituisce un dispositivo per id."""
        return self._repository_dispositivi.trova_per_id(id_dispositivo)

    def invia_comando(self, id_dispositivo, comando):
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
