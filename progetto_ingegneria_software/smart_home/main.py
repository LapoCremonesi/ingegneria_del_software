#!/usr/bin/env python3
"""
Punto di ingresso del sistema Smart Home.

Inizializza tutti i componenti (repository, servizi, controller)
con dependency injection e avvia il menu interattivo da terminale.
"""

import json
import os

from smart_home.controller.controllore_autenticazione import ControlloreAutenticazione
from smart_home.controller.controllore_automazioni import ControlloreAutomazioni
from smart_home.controller.controllore_dispositivi import ControlloreDispositivi
from smart_home.controller.controllore_log import ControlloreLog
from smart_home.controller.controllore_sistema import ControlloreSistema
from smart_home.controller.controllore_stanze import ControlloreStanze
from smart_home.domain.automazione import Automazione, Regola
from smart_home.repository.json_repository import (
    RepositoryAutomazioniJSON,
    RepositoryDatiSistemaJSON,
    RepositoryDispositiviJSON,
    RepositoryEventiJSON,
    RepositoryStanzeJSON,
    RepositoryUtentiJSON,
)
from smart_home.service.servizio_automazioni import ServizioAutomazioni
from smart_home.service.servizio_dispositivi import ServizioDispositivi
from smart_home.service.servizio_log import ServizioLog
from smart_home.service.servizio_sistema import ServizioSistema
from smart_home.service.servizio_stanze import ServizioStanze
from smart_home.service.servizio_utenti import ServizioUtenti


class SmartHomeApplication:
    """
    Applicazione Smart Home.

    Assembla tutti i componenti del sistema tramite dependency injection
    e fornisce un menu testuale per interagire con le funzionalit.
    """

    def __init__(self) -> None:
        # ── Repository ────────────────────────────────────────
        self._repo_utenti = RepositoryUtentiJSON()
        self._repo_stanze = RepositoryStanzeJSON()
        self._repo_dispositivi = RepositoryDispositiviJSON()
        self._repo_automazioni = RepositoryAutomazioniJSON()
        self._repo_eventi = RepositoryEventiJSON()
        self._repo_dati_sistema = RepositoryDatiSistemaJSON()

        percorso_eventi = os.path.join(
            os.path.dirname(__file__), "data", "eventi.json")
        with open(percorso_eventi, "w", encoding="utf-8") as f:
            json.dump([], f)

        # ── Servizi ───────────────────────────────────────────
        self._servizio_utenti = ServizioUtenti(repository_utenti=self._repo_utenti)
        self._servizio_stanze = ServizioStanze(
            repository_stanze=self._repo_stanze,
            servizio_log=self._servizio_log,
        )
        self._servizio_log = ServizioLog(repository_eventi=self._repo_eventi)
        self._servizio_dispositivi = ServizioDispositivi(
            repository_dispositivi=self._repo_dispositivi,
            servizio_log=self._servizio_log,
        )
        self._servizio_automazioni = ServizioAutomazioni(
            repository_automazioni=self._repo_automazioni,
            servizio_dispositivi=self._servizio_dispositivi,
            servizio_log=self._servizio_log,
        )
        self._servizio_sistema = ServizioSistema(
            repository_stanze=self._repo_stanze,
            repository_dispositivi=self._repo_dispositivi,
            repository_eventi=self._repo_eventi,
            repository_dati_sistema=self._repo_dati_sistema,
            servizio_log=self._servizio_log,
            repository_automazioni=self._repo_automazioni,
        )

        # ── Controller ────────────────────────────────────────
        self._ctrl_autenticazione = ControlloreAutenticazione(
            servizio_utenti=self._servizio_utenti,
        )
        self._ctrl_stanze = ControlloreStanze(servizio_stanze=self._servizio_stanze)
        self._ctrl_dispositivi = ControlloreDispositivi(
            servizio_dispositivi=self._servizio_dispositivi,
        )
        self._ctrl_automazioni = ControlloreAutomazioni(
            servizio_automazioni=self._servizio_automazioni,
        )
        self._ctrl_log = ControlloreLog(servizio_log=self._servizio_log)
        self._ctrl_sistema = ControlloreSistema(
            servizio_sistema=self._servizio_sistema,
        )

    # ── Menu interattivo ──────────────────────────────────────

    def avvia(self) -> None:
        """Avvia il menu principale del sistema."""
        print("=" * 50)
        print("  BENVENUTO NEL SISTEMA SMART HOME")
        print("=" * 50)

        while True:
            self._mostra_menu()
            scelta = input("\nScegli un'opzione: ").strip()
            if scelta == "0":
                print("Arrivederci!")
                break
            self._esegui_scelta(scelta)

    def _mostra_menu(self) -> None:
        print("\n--- MENU PRINCIPALE ---")
        print("1. Autenticazione")
        print("2. Gestione stanze (CRUD)")
        print("3. Gestione dispositivi (CRUD)")
        print("4. Controllo dispositivo")
        print("5. Gestione automazioni (CRUD)")
        print("6. Log eventi")
        print("7. Dashboard / Monitoraggio")
        print("8. Backup / Ripristino")
        print("0. Esci")

    def _esegui_scelta(self, scelta: str) -> None:
        if scelta == "1":
            self._menu_autenticazione()
        elif scelta == "2":
            self._menu_stanze()
        elif scelta == "3":
            self._menu_dispositivi()
        elif scelta == "4":
            self._menu_controllo_dispositivo()
        elif scelta == "5":
            self._menu_automazioni()
        elif scelta == "6":
            self._menu_log()
        elif scelta == "7":
            self._menu_dashboard()
        elif scelta == "8":
            self._menu_backup()
        else:
            print("Opzione non valida.")

    # ── Sottomenu: Autenticazione ────────────────────────────

    def _menu_autenticazione(self) -> None:
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        utente = self._ctrl_autenticazione.effettua_login(email, password)
        if utente:
            print(f"Login riuscito! Benvenuto {utente.nome} (ID: {utente.id})")
        else:
            print("Credenziali non valide.")

    # ── Sottomenu: Stanze (CRUD) ─────────────────────────────

    def _menu_stanze(self) -> None:
        while True:
            print("\n--- GESTIONE STANZE ---")
            print("1. Elenca stanze")
            print("2. Crea stanza")
            print("3. Modifica stanza")
            print("4. Elimina stanza")
            print("0. Indietro")
            s = input("Scelta: ").strip()

            if s == "1":
                self._elenca_stanze()
            elif s == "2":
                self._crea_stanza()
            elif s == "3":
                self._modifica_stanza()
            elif s == "4":
                self._elimina_stanza()
            elif s == "0":
                break

    def _elenca_stanze(self) -> None:
        stanze = self._ctrl_stanze.elenca_stanze()
        if not stanze:
            print("Nessuna stanza trovata.")
        else:
            for st in stanze:
                print(f"  [{st.id}] {st.nome} (piano {st.piano})")

    def _crea_stanza(self) -> None:
        nome = input("Nome stanza: ").strip()
        try:
            piano = int(input("Piano: ").strip())
        except ValueError:
            print("Piano non valido.")
            return
        stanza = self._ctrl_stanze.crea_stanza(nome, piano)
        print(f"Stanza creata: [ID {stanza.id}] {stanza.nome}")

    def _modifica_stanza(self) -> None:
        self._elenca_stanze()
        try:
            id_s = int(input("ID stanza da modificare: ").strip())
        except ValueError:
            print("ID non valido.")
            return
        stanza = self._ctrl_stanze.trova_stanza_per_id(id_s)
        if not stanza:
            print("Stanza non trovata.")
            return
        nuovo_nome = input(f"Nome [{stanza.nome}]: ").strip() or stanza.nome
        try:
            nuovo_piano = input(f"Piano [{stanza.piano}]: ").strip()
            nuovo_piano = int(nuovo_piano) if nuovo_piano else stanza.piano
        except ValueError:
            print("Piano non valido.")
            return
        stanza._nome = nuovo_nome
        stanza._piano = nuovo_piano
        self._ctrl_stanze.aggiorna_stanza(stanza)
        print("Stanza aggiornata.")

    def _elimina_stanza(self) -> None:
        self._elenca_stanze()
        try:
            id_s = int(input("ID stanza da eliminare: ").strip())
        except ValueError:
            print("ID non valido.")
            return
        if self._ctrl_stanze.elimina_stanza(id_s):
            print("Stanza eliminata.")
        else:
            print("Stanza non trovata.")

    # ── Sottomenu: Dispositivi (CRUD) ────────────────────────

    def _menu_dispositivi(self) -> None:
        while True:
            print("\n--- GESTIONE DISPOSITIVI ---")
            print("1. Elenca dispositivi")
            print("2. Crea dispositivo")
            print("3. Modifica dispositivo")
            print("4. Elimina dispositivo")
            print("0. Indietro")
            s = input("Scelta: ").strip()

            if s == "1":
                self._elenca_dispositivi()
            elif s == "2":
                self._crea_dispositivo()
            elif s == "3":
                self._modifica_dispositivo()
            elif s == "4":
                self._elimina_dispositivo()
            elif s == "0":
                break

    def _elenca_dispositivi(self) -> None:
        dispositivi = self._ctrl_dispositivi.elenca_dispositivi()
        if not dispositivi:
            print("Nessun dispositivo trovato.")
        else:
            for d in dispositivi:
                online = "online" if d.online else "offline"
                info_extra = ""
                if hasattr(d, "intensita"):
                    info_extra = f" | intensita={d.intensita} colore={d.colore}"
                elif hasattr(d, "temperatura_target"):
                    info_extra = f" | target={d.temperatura_target}°C modalita={d.modalita}"
                elif hasattr(d, "modalita_sicurezza"):
                    sic = "sicurezza ON" if d.modalita_sicurezza else ""
                    info_extra = f" | {sic}"
                print(f"  [{d.id}] {d.nome} ({d.tipo}) - {d.stato} - {online}{info_extra}")

    def _crea_dispositivo(self) -> None:
        # Mostra stanze disponibili
        stanze = self._ctrl_stanze.elenca_stanze()
        if not stanze:
            print("Nessuna stanza disponibile. Creane una prima.")
            return
        for st in stanze:
            print(f"  Stanza [{st.id}] {st.nome}")

        nome = input("Nome dispositivo: ").strip()
        print("Tipo: 1. Luce  2. Termostato  3. Serratura  4. Altro")
        t = input("Scelta [1]: ").strip() or "1"
        try:
            id_stanza = int(input("ID stanza: ").strip())
        except ValueError:
            print("ID stanza non valido.")
            return

        tipo_map = {"1": "luce", "2": "termostato", "3": "serratura", "4": "altro"}
        tipo = tipo_map.get(t, "luce")

        kwargs = {}
        if tipo == "luce":
            try:
                kwargs["intensita"] = int(input("Intensita iniziale (0-100) [0]: ").strip() or "0")
            except ValueError:
                pass
            kwargs["colore"] = input("Colore [bianco]: ").strip() or "bianco"
        elif tipo == "termostato":
            try:
                kwargs["temperatura_target"] = float(
                    input("Temperatura target [20.0]: ").strip() or "20.0")
            except ValueError:
                pass
            kwargs["modalita"] = input("Modalita (caldo/freddo/auto) [auto]: ").strip() or "auto"

        dispositivo = self._ctrl_dispositivi.crea_dispositivo(nome, tipo, id_stanza, **kwargs)
        print(f"Dispositivo creato: [ID {dispositivo.id}] {dispositivo.nome} ({tipo})")

    def _modifica_dispositivo(self) -> None:
        self._elenca_dispositivi()
        try:
            id_d = int(input("ID dispositivo da modificare: ").strip())
        except ValueError:
            print("ID non valido.")
            return
        disp = self._ctrl_dispositivi.trova_dispositivo_per_id(id_d)
        if not disp:
            print("Dispositivo non trovato.")
            return

        nuovo_nome = input(f"Nome [{disp.nome}]: ").strip() or disp.nome
        try:
            nuova_stanza = input(f"ID stanza [{disp.id_stanza}]: ").strip()
            nuova_stanza = int(nuova_stanza) if nuova_stanza else disp.id_stanza
        except ValueError:
            print("ID stanza non valido.")
            return
        disp._nome = nuovo_nome
        disp._id_stanza = nuova_stanza
        self._ctrl_dispositivi.aggiorna_dispositivo(disp)
        print("Dispositivo aggiornato.")

    def _elimina_dispositivo(self) -> None:
        self._elenca_dispositivi()
        try:
            id_d = int(input("ID dispositivo da eliminare: ").strip())
        except ValueError:
            print("ID non valido.")
            return
        if self._ctrl_dispositivi.elimina_dispositivo(id_d):
            print("Dispositivo eliminato.")
        else:
            print("Dispositivo non trovato.")

    # ── Sottomenu: Controllo dispositivo ─────────────────────

    def _menu_controllo_dispositivo(self) -> None:
        self._elenca_dispositivi()
        try:
            id_d = int(input("ID dispositivo: ").strip())
        except ValueError:
            print("ID non valido.")
            return
        disp = self._ctrl_dispositivi.trova_dispositivo_per_id(id_d)
        if not disp:
            print("Dispositivo non trovato.")
            return

        print(f"\nComandi disponibili per {disp.nome} ({disp.tipo}):")
        if disp.tipo == "luce":
            print("  accendi, spegni, attenua <0-100>, colore <nome>")
        elif disp.tipo == "termostato":
            print("  accendi, spegni, imposta <temperatura>, modalita <caldo/freddo/auto>")
        elif disp.tipo == "serratura":
            print("  blocca, sblocca, sicurezza on, sicurezza off")
        else:
            print("  accendi, spegni, <comando personalizzato>")

        comando = input("Comando: ").strip()
        risultato = self._ctrl_dispositivi.invia_comando(id_d, comando)
        if risultato:
            info = ""
            if hasattr(risultato, "intensita"):
                info = f" | intensita={risultato.intensita}"
            elif hasattr(risultato, "temperatura_target"):
                info = f" | target={risultato.temperatura_target}°C"
            print(f"Comando eseguito. Nuovo stato: {risultato.stato}{info}")
        else:
            print("Comando fallito (dispositivo offline o comando non valido).")

    # ── Sottomenu: Automazioni (CRUD) ────────────────────────

    def _menu_automazioni(self) -> None:
        while True:
            print("\n--- GESTIONE AUTOMAZIONI ---")
            print("1. Elenca automazioni")
            print("2. Crea automazione")
            print("3. Attiva / disattiva")
            print("4. Elimina automazione")
            print("5. Esegui tutte le automazioni attive")
            print("0. Indietro")
            s = input("Scelta: ").strip()

            if s == "1":
                self._elenca_automazioni()
            elif s == "2":
                self._crea_automazione()
            elif s == "3":
                self._toggle_automazione()
            elif s == "4":
                self._elimina_automazione()
            elif s == "5":
                risultati = self._servizio_automazioni.esegui_tutte()
                if risultati:
                    for r in risultati:
                        print(f"  {r}")
                else:
                    print("Nessuna automazione attiva da eseguire.")
            elif s == "0":
                break

    def _elenca_automazioni(self) -> None:
        automazioni = self._ctrl_automazioni.elenca_regole()
        if not automazioni:
            print("Nessuna automazione trovata.")
        else:
            for a in automazioni:
                stato = "attiva" if a.attiva else "disattiva"
                regole_cnt = len(a.regole)
                print(f"  [{a.id}] {a.nome} - {stato} (orario: {a.orario}, regole: {regole_cnt})")

    def _crea_automazione(self) -> None:
        nome = input("Nome automazione: ").strip()
        orario = input("Orario (HH:MM, opzionale): ").strip() or None
        automazione = Automazione(id_automazione=self._prossimo_id_auto(),
                                  nome=nome, orario=orario)

        # Aggiungi regole
        while True:
            aggiungi = input("Aggiungere una regola? (s/n) [n]: ").strip().lower()
            if aggiungi != "s":
                break
            tipo_cond = input("Tipo condizione (orario/stato) [orario]: ").strip() or "orario"
            valore_cond = input("Valore condizione (es. 19:00): ").strip()
            azione = input("Azione (es. accendi): ").strip()
            regola = Regola(tipo_cond, valore_cond, azione)
            automazione.aggiungi_regola(regola)

        automazione.attiva_automazione()
        self._ctrl_automazioni.crea_regola(automazione)
        print(f"Automazione creata: [ID {automazione.id}] {automazione.nome}")

    def _toggle_automazione(self) -> None:
        self._elenca_automazioni()
        try:
            id_a = int(input("ID automazione: ").strip())
        except ValueError:
            print("ID non valido.")
            return
        auto = self._ctrl_automazioni.trova_regola_per_id(id_a)
        if not auto:
            print("Automazione non trovata.")
            return
        if auto.attiva:
            auto.disattiva_automazione()
            print("Automazione disattivata.")
        else:
            auto.attiva_automazione()
            print("Automazione attivata.")
        self._ctrl_automazioni.aggiorna_regola(auto)

    def _elimina_automazione(self) -> None:
        self._elenca_automazioni()
        try:
            id_a = int(input("ID automazione da eliminare: ").strip())
        except ValueError:
            print("ID non valido.")
            return
        if self._ctrl_automazioni.elimina_regola(id_a):
            print("Automazione eliminata.")
        else:
            print("Automazione non trovata.")

    def _prossimo_id_auto(self) -> int:
        """Genera un id numerico per le nuove automazioni."""
        import random
        return random.randint(1000, 9999)

    # ── Sottomenu: Log eventi ─────────────────────────────────

    def _menu_log(self) -> None:
        filtro = input("Filtro (lascia vuoto per tutti): ").strip()
        eventi = self._ctrl_log.elenca_eventi(filtro if filtro else "")
        if not eventi:
            print("Nessun evento trovato.")
        else:
            print(f"\n--- EVENTI ({len(eventi)}) ---")
            for e in eventi:
                print(f"  {e.to_string()}")

    # ── Sottomenu: Dashboard / Monitoraggio ──────────────────

    def _menu_dashboard(self) -> None:
        print("\n--- DASHBOARD ---")
        print(self._ctrl_sistema.apri_dashboard(1))
        offline = self._ctrl_sistema.monitora_dispositivi()
        if offline:
            print("Dispositivi offline:")
            for d in offline:
                print(f"  - {d.nome} ({d.tipo})")
        else:
            print("Tutti i dispositivi sono online.")

    # ── Sottomenu: Backup / Ripristino ────────────────────────

    def _menu_backup(self) -> None:
        while True:
            print("\n--- BACKUP / RIPRISTINO ---")
            print("1. Crea backup")
            print("2. Elenca backup disponibili")
            print("3. Carica backup (ripristina)")
            print("0. Indietro")
            s = input("Scelta: ").strip()

            if s == "1":
                print(self._ctrl_sistema.salva_backup())
            elif s == "2":
                self._elenca_backup()
            elif s == "3":
                self._carica_backup()
            elif s == "0":
                break

    def _elenca_backup(self) -> None:
        backup_list = self._ctrl_sistema.elenca_backup()
        if not backup_list:
            print("Nessun backup disponibile.")
        else:
            print(f"\nBackup disponibili ({len(backup_list)}):")
            for i, path in enumerate(backup_list, 1):
                nome = os.path.basename(path)
                try:
                    size = os.path.getsize(path)
                    print(f"  {i}. {nome} ({size} byte)")
                except OSError:
                    print(f"  {i}. {nome}")

    def _carica_backup(self) -> None:
        backup_list = self._ctrl_sistema.elenca_backup()
        if not backup_list:
            print("Nessun backup disponibile.")
            return
        self._elenca_backup()
        try:
            idx = int(input("\nNumero backup da ripristinare: ").strip())
            if idx < 1 or idx > len(backup_list):
                print("Numero non valido.")
                return
            percorso = backup_list[idx - 1]
            conferma = input(f"Ripristinare '{os.path.basename(percorso)}'? "
                             f"I dati correnti verranno sovrascritti (s/N): ").strip().lower()
            if conferma == "s":
                print(self._ctrl_sistema.carica_backup(percorso))
        except ValueError:
            print("Numero non valido.")


if __name__ == "__main__":
    app = SmartHomeApplication()
    app.avvia()
