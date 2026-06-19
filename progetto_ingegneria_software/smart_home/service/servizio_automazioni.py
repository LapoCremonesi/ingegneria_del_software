from datetime import date

from smart_home.domain.automazione import Automazione, Regola
from smart_home.repository.interfaces import RepositoryAutomazioni


class ServizioAutomazioni:

    def __init__(self, repository_automazioni,
                 servizio_dispositivi=None,
                 servizio_log=None):
        self._repository_automazioni = repository_automazioni
        self._servizio_dispositivi = servizio_dispositivi
        self._servizio_log = servizio_log

    @property
    def servizio_dispositivi(self):
        return self._servizio_dispositivi

    @servizio_dispositivi.setter
    def servizio_dispositivi(self, valore):
        self._servizio_dispositivi = valore

    @property
    def servizio_log(self):
        return self._servizio_log

    @servizio_log.setter
    def servizio_log(self, valore):
        self._servizio_log = valore

    def crea(self, automazione):
        self._repository_automazioni.salva(automazione)
        if self._servizio_log:
            self._servizio_log.registra_evento(
                "AUTOMAZIONE_CREATA",
                f"Automazione '{automazione.nome}' creata",
            )
        return automazione

    def aggiorna(self, automazione):
        self._repository_automazioni.aggiorna(automazione)
        if self._servizio_log:
            self._servizio_log.registra_evento(
                "AUTOMAZIONE_AGGIORNATA",
                f"Automazione '{automazione.nome}' aggiornata",
            )
        return automazione

    def elimina(self, id_automazione):
        risultato = self._repository_automazioni.elimina(id_automazione)
        if risultato and self._servizio_log:
            self._servizio_log.registra_evento(
                "AUTOMAZIONE_ELIMINATA",
                f"Automazione con ID '{id_automazione}' eliminata",
            )
        return risultato

    def elenca(self):
        return self._repository_automazioni.trova_tutti()

    def trova_per_id(self, id_automazione):
        return self._repository_automazioni.trova_per_id(id_automazione)

    def elenca_attive(self):
        return self._repository_automazioni.trova_attive()

    def elenca_per_dispositivo(self, id_dispositivo):
        return [a for a in self.elenca()
                if a.id_dispositivo == id_dispositivo]

    def esegui_automazione(self, automazione):
        if not automazione.deve_eseguire():
            return False
        if not self._servizio_dispositivi:
            return False
        for regola in automazione.valuta_regole():
            risultato = self._servizio_dispositivi.invia_comando(
                automazione.id_dispositivo, regola.azione)
            if risultato:
                automazione.esegui()
                self._repository_automazioni.aggiorna(automazione)
                msg = f"Automazione '{automazione.nome}' eseguita su dispositivo '{risultato.nome}'"
                if self._servizio_log:
                    self._servizio_log.registra_evento(
                        "AUTOMAZIONE_ESEGUITA", msg)
                return True
        return False

    def esegui_tutte(self):
        messaggi = []
        for automazione in self.elenca_attive():
            if self.esegui_automazione(automazione):
                messaggi.append(
                    f"Automazione '{automazione.nome}' eseguita")
        return messaggi
