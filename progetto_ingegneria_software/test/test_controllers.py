import unittest

from smart_home.controller.controllore_autenticazione import ControlloreAutenticazione
from smart_home.controller.controllore_automazioni import ControlloreAutomazioni
from smart_home.controller.controllore_dispositivi import ControlloreDispositivi
from smart_home.controller.controllore_log import ControlloreLog
from smart_home.controller.controllore_sistema import ControlloreSistema
from smart_home.controller.controllore_stanze import ControlloreStanze
from smart_home.domain.automazione import Automazione
from smart_home.domain.dispositivo import Dispositivo
from smart_home.domain.evento import Evento
from smart_home.domain.stanza import Stanza
from smart_home.domain.utente import Amministratore, Utente
from smart_home.repository.interfaces import (
    RepositoryAutomazioni, RepositoryDatiSistema, RepositoryDispositivi,
    RepositoryEventi, RepositoryStanze, RepositoryUtenti,
)
from smart_home.service.servizio_automazioni import ServizioAutomazioni
from smart_home.service.servizio_dispositivi import ServizioDispositivi
from smart_home.service.servizio_log import ServizioLog
from smart_home.service.servizio_stanze import ServizioStanze
from smart_home.service.servizio_sistema import ServizioSistema
from smart_home.service.servizio_utenti import ServizioUtenti


# --- Mock repositories (same as in test_services.py) ---

class MockRepoUtenti(RepositoryUtenti):
    def __init__(self):
        self.utenti = {}
    def trova_per_email(self, email):
        for u in self.utenti.values():
            if u.email == email:
                return u
        return None
    def salva(self, utente):
        self.utenti[utente.id] = utente
    def aggiorna(self, utente):
        self.utenti[utente.id] = utente
    def trova_tutti(self):
        return list(self.utenti.values())
    def elimina(self, id_utente):
        return self.utenti.pop(id_utente, None) is not None


class MockRepoStanze(RepositoryStanze):
    def __init__(self):
        self.stanze = {}
    def trova_tutti(self):
        return list(self.stanze.values())
    def trova_per_id(self, id_stanza):
        return self.stanze.get(id_stanza)
    def salva(self, stanza):
        self.stanze[stanza.id] = stanza
    def aggiorna(self, stanza):
        self.stanze[stanza.id] = stanza
    def elimina(self, id_stanza):
        return self.stanze.pop(id_stanza, None) is not None


class MockRepoDispositivi(RepositoryDispositivi):
    def __init__(self):
        self.dispositivi = {}
    def trova_tutti(self):
        return list(self.dispositivi.values())
    def trova_per_id(self, id_dispositivo):
        return self.dispositivi.get(id_dispositivo)
    def salva(self, dispositivo):
        self.dispositivi[dispositivo.id] = dispositivo
    def aggiorna(self, dispositivo):
        self.dispositivi[dispositivo.id] = dispositivo
    def elimina(self, id_dispositivo):
        return self.dispositivi.pop(id_dispositivo, None) is not None
    def aggiorna_stanza(self, id_dispositivo, id_stanza):
        d = self.dispositivi.get(id_dispositivo)
        if d is None:
            return False
        d.id_stanza = id_stanza
        return True
    def trova_offline(self):
        return [d for d in self.dispositivi.values() if not d.online]


class MockRepoAutomazioni(RepositoryAutomazioni):
    def __init__(self):
        self.automazioni = {}
    def trova_tutti(self):
        return list(self.automazioni.values())
    def trova_per_id(self, id_automazione):
        return self.automazioni.get(id_automazione)
    def trova_attive(self):
        return [a for a in self.automazioni.values() if a.attiva]
    def salva(self, automazione):
        self.automazioni[automazione.id] = automazione
    def aggiorna(self, automazione):
        self.automazioni[automazione.id] = automazione
    def elimina(self, id_automazione):
        return self.automazioni.pop(id_automazione, None) is not None


class MockRepoEventi(RepositoryEventi):
    def __init__(self):
        self.eventi = []
    def cerca(self, filtro):
        if not filtro:
            return list(self.eventi)
        f = filtro.lower()
        return [e for e in self.eventi
                if f in e.tipo.lower() or f in e.descrizione.lower()]
    def salva(self, evento):
        self.eventi.append(evento)
    def aggrega(self, filtro):
        f = filtro.lower()
        return [e for e in self.eventi if f in e.tipo.lower()]


class MockRepoDatiSistema(RepositoryDatiSistema):
    def __init__(self):
        self.backups = []
    def salva_backup(self):
        path = f"/mock/backup_{len(self.backups)}.json"
        self.backups.append(path)
        return path
    def elenca_backup(self):
        return list(self.backups)
    def carica_backup(self, percorso):
        if percorso not in self.backups:
            raise FileNotFoundError(percorso)
        return f"Ripristino completato da: {percorso}"

    def elimina_backup(self, percorso):
        if percorso not in self.backups:
            return False
        self.backups.remove(percorso)
        return True


class TestControlloreAutenticazione(unittest.TestCase):

    def setUp(self):
        repo = MockRepoUtenti()
        servizio = ServizioUtenti(repo)
        self.controllore = ControlloreAutenticazione(servizio)

    def test_effettua_login_ok(self):
        self.controllore.registra_utente("Mario", "m@t.it", "pass")
        utente = self.controllore.effettua_login("m@t.it", "pass")
        self.assertIsNotNone(utente)
        self.assertEqual(utente.nome, "Mario")

    def test_effettua_login_fail(self):
        self.assertIsNone(self.controllore.effettua_login("no@t.it", "pass"))

    def test_registra_utente(self):
        utente = self.controllore.registra_utente("Mario", "m@t.it", "pass")
        self.assertIsNotNone(utente)
        self.assertEqual(utente.email, "m@t.it")

    def test_registra_duplicato(self):
        self.controllore.registra_utente("Mario", "m@t.it", "pass")
        self.assertIsNone(self.controllore.registra_utente("Mario2", "m@t.it", "pass2"))

    def test_registra_admin(self):
        admin = self.controllore.registra_utente("Admin", "a@t.it", "pass", tipo="amministratore")
        self.assertIsInstance(admin, Amministratore)

    def test_elenca_utenti(self):
        self.controllore.registra_utente("A", "a@t.it", "p")
        self.controllore.registra_utente("B", "b@t.it", "p")
        self.assertEqual(len(self.controllore.elenca_utenti()), 2)

    def test_elimina_utente(self):
        u = self.controllore.registra_utente("Mario", "m@t.it", "pass")
        self.assertTrue(self.controllore.elimina_utente(u.id))
        self.assertEqual(len(self.controllore.elenca_utenti()), 0)


class TestControlloreStanze(unittest.TestCase):

    def setUp(self):
        repo = MockRepoStanze()
        servizio = ServizioStanze(repo)
        self.controllore = ControlloreStanze(servizio)

    def test_crea_stanza(self):
        stanza = self.controllore.crea_stanza("Salotto", 0)
        self.assertEqual(stanza.nome, "Salotto")
        self.assertEqual(stanza.piano, 0)

    def test_elenca_stanze(self):
        self.controllore.crea_stanza("Salotto", 0)
        self.controllore.crea_stanza("Cucina", 0)
        self.assertEqual(len(self.controllore.elenca_stanze()), 2)

    def test_trova_stanza_per_id(self):
        stanza = self.controllore.crea_stanza("Salotto", 0)
        trovata = self.controllore.trova_stanza_per_id(stanza.id)
        self.assertEqual(trovata.nome, "Salotto")

    def test_aggiorna_stanza(self):
        stanza = self.controllore.crea_stanza("Salotto", 0)
        stanza.nome = "Salotto Modificato"
        self.controllore.aggiorna_stanza(stanza)
        trovata = self.controllore.trova_stanza_per_id(stanza.id)
        self.assertEqual(trovata.nome, "Salotto Modificato")

    def test_elimina_stanza(self):
        stanza = self.controllore.crea_stanza("Salotto", 0)
        self.assertTrue(self.controllore.elimina_stanza(stanza.id))


class TestControlloreDispositivi(unittest.TestCase):

    def setUp(self):
        repo = MockRepoDispositivi()
        servizio = ServizioDispositivi(repo)
        self.controllore = ControlloreDispositivi(servizio)
        self.repo_stanze = MockRepoStanze()
        self.repo_stanze.salva(Stanza("s1", "Salotto", 0))

    def test_crea_dispositivo(self):
        d = self.controllore.crea_dispositivo("Luce", "luce", "s1")
        self.assertEqual(d.nome, "Luce")
        self.assertEqual(d.tipo, "luce")

    def test_crea_luce(self):
        d = self.controllore.crea_dispositivo("Luce", "luce", "s1",
                                              intensita=50, colore="rosso")
        self.assertEqual(d.intensita, 50)
        self.assertEqual(d.colore, "rosso")

    def test_crea_termostato(self):
        d = self.controllore.crea_dispositivo("Termo", "termostato", "s1",
                                              temperatura_target=22.5, modalita="caldo")
        self.assertEqual(d.temperatura_target, 22.5)
        self.assertEqual(d.modalita, "caldo")

    def test_crea_serratura(self):
        d = self.controllore.crea_dispositivo("Serratura", "serratura", "s1",
                                              modalita_sicurezza=True)
        self.assertTrue(d.modalita_sicurezza)

    def test_crea_tipo_generico(self):
        d = self.controllore.crea_dispositivo("Generico", "altro", "s1")
        self.assertEqual(d.tipo, "altro")

    def test_elenca_dispositivi(self):
        self.controllore.crea_dispositivo("Luce", "luce", "s1")
        self.controllore.crea_dispositivo("Termo", "termostato", "s1")
        self.assertEqual(len(self.controllore.elenca_dispositivi()), 2)

    def test_invia_comando(self):
        d = self.controllore.crea_dispositivo("Luce", "luce", "s1")
        risultato = self.controllore.invia_comando(d.id, "accendi")
        self.assertIsNotNone(risultato)
        self.assertEqual(risultato.stato, "acceso")

    def test_invia_comando_dispositivo_inesistente(self):
        self.assertIsNone(self.controllore.invia_comando("inesistente", "accendi"))

    def test_aggiorna_dispositivo(self):
        d = self.controllore.crea_dispositivo("Luce", "luce", "s1")
        d.nome = "Luce Modificata"
        self.controllore.aggiorna_dispositivo(d)
        trovato = self.controllore.trova_dispositivo_per_id(d.id)
        self.assertEqual(trovato.nome, "Luce Modificata")

    def test_elimina_dispositivo(self):
        d = self.controllore.crea_dispositivo("Luce", "luce", "s1")
        self.assertTrue(self.controllore.elimina_dispositivo(d.id))


class TestControlloreAutomazioni(unittest.TestCase):

    def setUp(self):
        repo = MockRepoAutomazioni()
        servizio = ServizioAutomazioni(repo)
        self.controllore = ControlloreAutomazioni(servizio)

    def test_crea_regola(self):
        a = Automazione("a1", "Accendi sera", "d1")
        risultato = self.controllore.crea_regola(a)
        self.assertEqual(risultato.nome, "Accendi sera")

    def test_elenca_regole(self):
        self.controllore.crea_regola(Automazione("a1", "A", "d1"))
        self.controllore.crea_regola(Automazione("a2", "B", "d2"))
        self.assertEqual(len(self.controllore.elenca_regole()), 2)

    def test_trova_regola_per_id(self):
        self.controllore.crea_regola(Automazione("a1", "Test", "d1"))
        trovata = self.controllore.trova_regola_per_id("a1")
        self.assertEqual(trovata.nome, "Test")

    def test_aggiorna_regola(self):
        a = Automazione("a1", "Vecchio", "d1")
        self.controllore.crea_regola(a)
        a.nome = "Nuovo"
        self.controllore.aggiorna_regola(a)
        trovata = self.controllore.trova_regola_per_id("a1")
        self.assertEqual(trovata.nome, "Nuovo")

    def test_elimina_regola(self):
        self.controllore.crea_regola(Automazione("a1", "Test", "d1"))
        self.assertTrue(self.controllore.elimina_regola("a1"))


class TestControlloreLog(unittest.TestCase):

    def setUp(self):
        repo = MockRepoEventi()
        servizio = ServizioLog(repo)
        self.controllore = ControlloreLog(servizio)

    def test_elenca_eventi(self):
        repo = self.controllore._servizio_log._repository_eventi
        repo.salva(Evento("e1", "LOGIN", "Login effettuato"))
        eventi = self.controllore.elenca_eventi("LOGIN")
        self.assertEqual(len(eventi), 1)

    def test_esporta_eventi(self):
        repo = self.controllore._servizio_log._repository_eventi
        repo.salva(Evento("e1", "LOGIN", "Login ok"))
        testo = self.controllore.esporta_eventi("LOGIN")
        self.assertIn("Login ok", testo)


class TestControlloreSistema(unittest.TestCase):

    def setUp(self):
        self.repo_sistema = MockRepoDatiSistema()
        repo_stanze = MockRepoStanze()
        repo_dispositivi = MockRepoDispositivi()
        repo_eventi = MockRepoEventi()
        repo_automazioni = MockRepoAutomazioni()
        servizio = ServizioSistema(
            repo_stanze, repo_dispositivi, repo_eventi,
            self.repo_sistema, repository_automazioni=repo_automazioni,
        )
        self.controllore = ControlloreSistema(servizio)

    def test_salva_backup(self):
        msg = self.controllore.salva_backup()
        self.assertIn("Backup creato", msg)

    def test_elenca_backup(self):
        self.repo_sistema.salva_backup()
        self.assertEqual(len(self.controllore.elenca_backup()), 1)

    def test_carica_backup(self):
        percorso = self.repo_sistema.salva_backup()
        msg = self.controllore.carica_backup(percorso)
        self.assertIn("Ripristino completato", msg)

    def test_elimina_backup(self):
        percorso = self.repo_sistema.salva_backup()
        self.assertTrue(self.controllore.elimina_backup(percorso))

    def test_elimina_backup_inesistente(self):
        self.assertFalse(self.controllore.elimina_backup("inesistente"))

    def test_apri_dashboard(self):
        msg = self.controllore.apri_dashboard("u1")
        self.assertIn("u1", msg)

    def test_monitora_dispositivi(self):
        self.assertEqual(len(self.controllore.monitora_dispositivi()), 0)

    def test_genera_statistiche(self):
        self.assertEqual(len(self.controllore.genera_statistiche("TEST")), 0)


if __name__ == "__main__":
    unittest.main()
