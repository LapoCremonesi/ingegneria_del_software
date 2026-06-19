import unittest

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


class MockRepositoryUtenti(RepositoryUtenti):
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


class MockRepositoryStanze(RepositoryStanze):
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


class MockRepositoryDispositivi(RepositoryDispositivi):
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


class MockRepositoryAutomazioni(RepositoryAutomazioni):
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


class MockRepositoryEventi(RepositoryEventi):
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


class MockRepositoryDatiSistema(RepositoryDatiSistema):
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


class TestServizioUtenti(unittest.TestCase):

    def setUp(self):
        self.repo = MockRepositoryUtenti()
        self.servizio = ServizioUtenti(self.repo)

    def test_autentica_ok(self):
        self.repo.salva(Utente("u1", "Mario", "m@t.it", "pass123"))
        utente = self.servizio.autentica("m@t.it", "pass123")
        self.assertIsNotNone(utente)
        self.assertEqual(utente.nome, "Mario")

    def test_autentica_password_errata(self):
        self.repo.salva(Utente("u1", "Mario", "m@t.it", "pass123"))
        self.assertIsNone(self.servizio.autentica("m@t.it", "sbagliata"))

    def test_autentica_email_inesistente(self):
        self.assertIsNone(self.servizio.autentica("no@t.it", "pass"))

    def test_crea_utente(self):
        utente = self.servizio.crea_utente("Mario", "m@t.it", "pass123")
        self.assertIsNotNone(utente)
        self.assertEqual(utente.nome, "Mario")
        self.assertIsInstance(utente, Utente)

    def test_crea_amministratore(self):
        admin = self.servizio.crea_utente("Admin", "a@t.it", "pass", tipo="amministratore")
        self.assertIsInstance(admin, Amministratore)

    def test_crea_utente_email_duplicata(self):
        self.servizio.crea_utente("Mario", "m@t.it", "pass")
        self.assertIsNone(self.servizio.crea_utente("Mario2", "m@t.it", "pass2"))

    def test_elenca_utenti(self):
        self.servizio.crea_utente("A", "a@t.it", "p")
        self.servizio.crea_utente("B", "b@t.it", "p")
        self.assertEqual(len(self.servizio.elenca_utenti()), 2)

    def test_elimina_utente(self):
        u = self.servizio.crea_utente("Mario", "m@t.it", "pass")
        self.assertTrue(self.servizio.elimina_utente(u.id))
        self.assertEqual(len(self.servizio.elenca_utenti()), 0)

    def test_elimina_utente_inesistente(self):
        self.assertFalse(self.servizio.elimina_utente("inesistente"))


class TestServizioStanze(unittest.TestCase):

    def setUp(self):
        self.repo = MockRepositoryStanze()
        self.servizio = ServizioStanze(self.repo)

    def test_crea(self):
        s = Stanza("s1", "Salotto", 0)
        risultato = self.servizio.crea(s)
        self.assertEqual(risultato.nome, "Salotto")
        self.assertEqual(len(self.servizio.elenca()), 1)

    def test_elenca(self):
        self.servizio.crea(Stanza("s1", "A", 0))
        self.servizio.crea(Stanza("s2", "B", 1))
        self.assertEqual(len(self.servizio.elenca()), 2)

    def test_trova_per_id(self):
        self.servizio.crea(Stanza("s1", "Salotto", 0))
        trovata = self.servizio.trova_per_id("s1")
        self.assertEqual(trovata.nome, "Salotto")

    def test_trova_per_id_inesistente(self):
        self.assertIsNone(self.servizio.trova_per_id("inesistente"))

    def test_aggiorna(self):
        s = Stanza("s1", "Salotto", 0)
        self.servizio.crea(s)
        s.nome = "Salotto Modificato"
        self.servizio.aggiorna(s)
        self.assertEqual(self.servizio.trova_per_id("s1").nome, "Salotto Modificato")

    def test_elimina(self):
        self.servizio.crea(Stanza("s1", "Salotto", 0))
        self.assertTrue(self.servizio.elimina("s1"))
        self.assertEqual(len(self.servizio.elenca()), 0)

    def test_elimina_inesistente(self):
        self.assertFalse(self.servizio.elimina("inesistente"))


class TestServizioDispositivi(unittest.TestCase):

    def setUp(self):
        self.repo = MockRepositoryDispositivi()
        self.servizio = ServizioDispositivi(self.repo)

    def test_crea(self):
        d = Dispositivo("d1", "Luce", "luce", "s1")
        risultato = self.servizio.crea(d)
        self.assertEqual(risultato.nome, "Luce")
        self.assertEqual(len(self.servizio.elenca()), 1)

    def test_elenca(self):
        self.servizio.crea(Dispositivo("d1", "A", "luce", "s1"))
        self.servizio.crea(Dispositivo("d2", "B", "termostato", "s1"))
        self.assertEqual(len(self.servizio.elenca()), 2)

    def test_trova_per_id(self):
        self.servizio.crea(Dispositivo("d1", "Luce", "luce", "s1"))
        trovato = self.servizio.trova_per_id("d1")
        self.assertEqual(trovato.nome, "Luce")

    def test_aggiorna(self):
        d = Dispositivo("d1", "Luce", "luce", "s1")
        self.servizio.crea(d)
        d.nome = "Luce Modificata"
        self.servizio.aggiorna(d)
        self.assertEqual(self.servizio.trova_per_id("d1").nome, "Luce Modificata")

    def test_elimina(self):
        self.servizio.crea(Dispositivo("d1", "Luce", "luce", "s1"))
        self.assertTrue(self.servizio.elimina("d1"))
        self.assertEqual(len(self.servizio.elenca()), 0)

    def test_elimina_inesistente(self):
        self.assertFalse(self.servizio.elimina("inesistente"))

    def test_invia_comando_ok(self):
        d = Dispositivo("d1", "Luce", "luce", "s1")
        self.servizio.crea(d)
        risultato = self.servizio.invia_comando("d1", "accendi")
        self.assertIsNotNone(risultato)
        self.assertEqual(risultato.stato, "acceso")

    def test_invia_comando_dispositivo_inesistente(self):
        self.assertIsNone(self.servizio.invia_comando("inesistente", "accendi"))

    def test_invia_comando_offline(self):
        d = Dispositivo("d1", "Luce", "luce", "s1")
        d.online = False
        self.servizio.crea(d)
        self.assertIsNone(self.servizio.invia_comando("d1", "accendi"))


class TestServizioAutomazioni(unittest.TestCase):

    def setUp(self):
        self.repo_auto = MockRepositoryAutomazioni()
        self.repo_disp = MockRepositoryDispositivi()
        self.servizio_disp = ServizioDispositivi(self.repo_disp)
        self.servizio = ServizioAutomazioni(self.repo_auto, self.servizio_disp)

        self.dispositivo = Dispositivo("d1", "Luce", "luce", "s1")
        self.servizio_disp.crea(self.dispositivo)
        self.automazione = Automazione("a1", "Accendi sera", "d1", orario="19:00")

    def test_crea(self):
        self.servizio.crea(self.automazione)
        self.assertEqual(len(self.servizio.elenca()), 1)

    def test_elenca(self):
        self.servizio.crea(self.automazione)
        self.servizio.crea(Automazione("a2", "Spegni", "d1"))
        self.assertEqual(len(self.servizio.elenca()), 2)

    def test_trova_per_id(self):
        self.servizio.crea(self.automazione)
        trovata = self.servizio.trova_per_id("a1")
        self.assertEqual(trovata.nome, "Accendi sera")

    def test_elenca_attive(self):
        self.automazione.attiva_automazione()
        self.servizio.crea(self.automazione)
        self.servizio.crea(Automazione("a2", "Spenta", "d1"))
        self.assertEqual(len(self.servizio.elenca_attive()), 1)

    def test_elenca_per_dispositivo(self):
        self.servizio.crea(self.automazione)
        self.servizio.crea(Automazione("a2", "Altra", "d2"))
        lista = self.servizio.elenca_per_dispositivo("d1")
        self.assertEqual(len(lista), 1)

    def test_elimina(self):
        self.servizio.crea(self.automazione)
        self.assertTrue(self.servizio.elimina("a1"))

    def test_aggiorna(self):
        self.servizio.crea(self.automazione)
        self.automazione.nome = "Modificata"
        self.servizio.aggiorna(self.automazione)
        self.assertEqual(self.servizio.trova_per_id("a1").nome, "Modificata")

    def test_esegui_automazione_no_dispositivo(self):
        serv = ServizioAutomazioni(self.repo_auto)
        self.assertFalse(serv.esegui_automazione(self.automazione))

    def test_esegui_tutte(self):
        self.automazione.attiva_automazione()
        self.servizio.crea(self.automazione)
        messaggi = self.servizio.esegui_tutte()
        self.assertEqual(len(messaggi), 0)


class TestServizioLog(unittest.TestCase):

    def setUp(self):
        self.repo = MockRepositoryEventi()
        self.servizio = ServizioLog(self.repo)

    def test_registra_evento(self):
        evento = self.servizio.registra_evento("LOGIN", "Utente loggato")
        self.assertEqual(evento.tipo, "LOGIN")
        self.assertEqual(len(self.servizio.elenca_eventi("")), 1)

    def test_registra_evento_con_dispositivo(self):
        evento = self.servizio.registra_evento("COMANDO", "Luce accesa", id_dispositivo="d1")
        self.assertEqual(evento.id_dispositivo, "d1")

    def test_elenca_eventi_filtro(self):
        self.servizio.registra_evento("LOGIN", "Login effettuato")
        self.servizio.registra_evento("LOGOUT", "Logout effettuato")
        self.assertEqual(len(self.servizio.elenca_eventi("LOGIN")), 1)

    def test_elenca_eventi_tutti(self):
        self.servizio.registra_evento("A", "Evento A")
        self.servizio.registra_evento("B", "Evento B")
        self.assertEqual(len(self.servizio.elenca_eventi("")), 2)

    def test_esporta_eventi(self):
        self.servizio.registra_evento("LOGIN", "Login ok")
        testo = self.servizio.esporta_eventi("LOGIN")
        self.assertIn("Login ok", testo)
        self.assertIn("LOGIN", testo)

    def test_esporta_eventi_vuoto(self):
        testo = self.servizio.esporta_eventi("NESSUNA")
        self.assertEqual(testo, "Nessun evento trovato.")


class TestServizioSistema(unittest.TestCase):

    def setUp(self):
        self.repo_stanze = MockRepositoryStanze()
        self.repo_dispositivi = MockRepositoryDispositivi()
        self.repo_eventi = MockRepositoryEventi()
        self.repo_sistema = MockRepositoryDatiSistema()
        self.repo_automazioni = MockRepositoryAutomazioni()
        self.servizio = ServizioSistema(
            self.repo_stanze, self.repo_dispositivi, self.repo_eventi,
            self.repo_sistema, repository_automazioni=self.repo_automazioni,
        )

    def test_carica_riepilogo(self):
        self.repo_stanze.salva(Stanza("s1", "Salotto", 0))
        self.repo_dispositivi.salva(Dispositivo("d1", "Luce", "luce", "s1"))
        riepilogo = self.servizio.carica_riepilogo("u1")
        self.assertIn("Stanze: 1", riepilogo)
        self.assertIn("Dispositivi: 1", riepilogo)

    def test_monitora_dispositivi(self):
        d = Dispositivo("d1", "Offline", "luce", "s1")
        d.online = False
        self.repo_dispositivi.salva(d)
        offline = self.servizio.monitora_dispositivi()
        self.assertEqual(len(offline), 1)

    def test_genera_statistiche(self):
        self.repo_eventi.salva(Evento("e1", "LOGIN", "Login"))
        self.repo_eventi.salva(Evento("e2", "COMANDO", "Comando"))
        self.assertEqual(len(self.servizio.genera_statistiche("LOGIN")), 1)

    def test_salva_backup(self):
        msg = self.servizio.salva_backup()
        self.assertIn("Backup creato", msg)

    def test_elenca_backup(self):
        self.repo_sistema.salva_backup()
        self.assertEqual(len(self.servizio.elenca_backup()), 1)

    def test_carica_backup(self):
        percorso = self.repo_sistema.salva_backup()
        msg = self.servizio.carica_backup(percorso)
        self.assertIn("Ripristino completato", msg)

    def test_carica_backup_inesistente(self):
        msg = self.servizio.carica_backup("inesistente")
        self.assertIn("Ripristino fallito", msg)

    def test_esegui_backup_alias(self):
        msg = self.servizio.esegui_backup()
        self.assertIn("Backup creato", msg)

    def test_elimina_backup(self):
        percorso = self.repo_sistema.salva_backup()
        self.assertTrue(self.servizio.elimina_backup(percorso))

    def test_elimina_backup_inesistente(self):
        self.assertFalse(self.servizio.elimina_backup("inesistente"))


if __name__ == "__main__":
    unittest.main()
