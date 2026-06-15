import sys

from PyQt6.QtWidgets import QApplication, QDialog

from smart_home.repository.json_repository import (
    RepositoryAutomazioniJSON,
    RepositoryDatiSistemaJSON,
    RepositoryDispositiviJSON,
    RepositoryEventiJSON,
    RepositoryStanzeJSON,
    RepositoryUtentiJSON,
)
from smart_home.service.programmatore_automazioni import ProgrammatoreAutomazioni
from smart_home.service.servizio_automazioni import ServizioAutomazioni
from smart_home.service.servizio_dispositivi import ServizioDispositivi
from smart_home.service.servizio_log import ServizioLog
from smart_home.service.servizio_sistema import ServizioSistema
from smart_home.service.servizio_stanze import ServizioStanze
from smart_home.service.servizio_utenti import ServizioUtenti
from smart_home.controller.controllore_automazioni import ControlloreAutomazioni
from smart_home.controller.controllore_autenticazione import ControlloreAutenticazione
from smart_home.controller.controllore_dispositivi import ControlloreDispositivi
from smart_home.controller.controllore_log import ControlloreLog
from smart_home.controller.controllore_sistema import ControlloreSistema
from smart_home.controller.controllore_stanze import ControlloreStanze
from smart_home.view.login_dialog import LoginDialog
from smart_home.view.main_window import FinestraPrincipale
from smart_home.view.style import STILE_GLOBALE


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(STILE_GLOBALE)

    repo_utenti = RepositoryUtentiJSON()
    repo_stanze = RepositoryStanzeJSON()
    repo_dispositivi = RepositoryDispositiviJSON()
    repo_automazioni = RepositoryAutomazioniJSON()
    repo_eventi = RepositoryEventiJSON()
    repo_sistema = RepositoryDatiSistemaJSON()

    servizio_log = ServizioLog(repo_eventi)
    servizio_utenti = ServizioUtenti(repo_utenti)
    servizio_stanze = ServizioStanze(repo_stanze)
    servizio_dispositivi = ServizioDispositivi(repo_dispositivi, servizio_log)
    servizio_automazioni = ServizioAutomazioni(
        repo_automazioni, servizio_dispositivi, servizio_log)
    servizio_sistema = ServizioSistema(
        repo_stanze, repo_dispositivi, repo_eventi, repo_sistema, servizio_log)

    controllore_autenticazione = ControlloreAutenticazione(servizio_utenti)
    controllore_stanze = ControlloreStanze(servizio_stanze)
    controllore_dispositivi = ControlloreDispositivi(servizio_dispositivi)
    controllore_automazioni = ControlloreAutomazioni(servizio_automazioni)
    controllore_log = ControlloreLog(servizio_log)
    controllore_sistema = ControlloreSistema(servizio_sistema)

    programmatore = ProgrammatoreAutomazioni(servizio_automazioni)

    while True:
        login = LoginDialog(controllore_autenticazione)
        if login.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)

        utente = login.utente_autenticato
        if utente is None:
            sys.exit(0)

        finestra = FinestraPrincipale(
            controllore_stanze=controllore_stanze,
            controllore_dispositivi=controllore_dispositivi,
            controllore_automazioni=controllore_automazioni,
            controllore_log=controllore_log,
            controllore_sistema=controllore_sistema,
            id_utente=utente.id,
        )
        programmatore.avvia()
        finestra.show()
        app.exec()

        if not finestra.is_logout:
            break

    programmatore.ferma()
    sys.exit(0)


if __name__ == "__main__":
    main()
