import json
import os
import shutil
import tempfile
import time
import unittest

from smart_home.domain.automazione import Automazione, Regola
from smart_home.domain.dispositivo import Dispositivo
from smart_home.domain.dispositivi_specifici import Luce, Serratura, Termostato
from smart_home.domain.evento import Evento
from smart_home.domain.stanza import Stanza
from smart_home.domain.utente import Amministratore, Utente
from smart_home.repository import json_repository as repo_module


def _setup_temp_repo(module, temp_dir):
    """Sostituisce percorsi e funzione _backup_path con percorsi temporanei."""
    old_data = repo_module.DATA_DIR
    old_backup = repo_module.BACKUP_DIR
    old_backup_path = repo_module._backup_path
    data_dir = os.path.join(temp_dir, "data")
    backup_dir = os.path.join(temp_dir, "backup")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)
    repo_module.DATA_DIR = data_dir
    repo_module.BACKUP_DIR = backup_dir
    repo_module._backup_path = lambda: backup_dir
    return old_data, old_backup, old_backup_path


def _restore_repo(module, old_data, old_backup, old_backup_path):
    module.DATA_DIR = old_data
    module.BACKUP_DIR = old_backup
    module._backup_path = old_backup_path


class TestRepositoryUtentiJSON(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.old_data, self.old_backup, self.old_backup_path = _setup_temp_repo(repo_module, self.temp_dir)
        self.repo = repo_module.RepositoryUtentiJSON()
        self.utente = Utente("u1", "Mario", "mario@test.it", "pass123")
        self.admin = Amministratore("a1", "Admin", "admin@test.it", "admin123")

    def tearDown(self):
        _restore_repo(repo_module, self.old_data, self.old_backup, self.old_backup_path)
        shutil.rmtree(self.temp_dir)

    def test_salva_e_trova_per_email(self):
        self.repo.salva(self.utente)
        trovato = self.repo.trova_per_email("mario@test.it")
        self.assertIsNotNone(trovato)
        self.assertEqual(trovato.nome, "Mario")

    def test_trova_per_email_inesistente(self):
        self.assertIsNone(self.repo.trova_per_email("nessuno@test.it"))

    def test_salva_admin(self):
        self.repo.salva(self.admin)
        trovato = self.repo.trova_per_email("admin@test.it")
        self.assertIsInstance(trovato, Amministratore)

    def test_aggiorna(self):
        self.repo.salva(self.utente)
        self.utente._nome = "Mario Rossi"
        self.repo.aggiorna(self.utente)
        trovato = self.repo.trova_per_email("mario@test.it")
        self.assertEqual(trovato.nome, "Mario Rossi")

    def test_trova_tutti(self):
        self.repo.salva(self.utente)
        self.repo.salva(self.admin)
        tutti = self.repo.trova_tutti()
        self.assertEqual(len(tutti), 2)

    def test_elimina(self):
        self.repo.salva(self.utente)
        self.assertTrue(self.repo.elimina("u1"))
        self.assertIsNone(self.repo.trova_per_email("mario@test.it"))

    def test_elimina_inesistente(self):
        self.assertFalse(self.repo.elimina("inesistente"))


class TestRepositoryStanzeJSON(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.old_data, self.old_backup, self.old_backup_path = _setup_temp_repo(repo_module, self.temp_dir)
        self.repo = repo_module.RepositoryStanzeJSON()
        self.stanza = Stanza("s1", "Soggiorno", 0)

    def tearDown(self):
        _restore_repo(repo_module, self.old_data, self.old_backup, self.old_backup_path)
        shutil.rmtree(self.temp_dir)

    def test_salva_e_trova_per_id(self):
        self.repo.salva(self.stanza)
        trovata = self.repo.trova_per_id("s1")
        self.assertIsNotNone(trovata)
        self.assertEqual(trovata.nome, "Soggiorno")

    def test_trova_per_id_inesistente(self):
        self.assertIsNone(self.repo.trova_per_id("inesistente"))

    def test_trova_tutti(self):
        self.repo.salva(self.stanza)
        s2 = Stanza("s2", "Cucina", 0)
        self.repo.salva(s2)
        self.assertEqual(len(self.repo.trova_tutti()), 2)

    def test_aggiorna(self):
        self.repo.salva(self.stanza)
        self.stanza.nome = "Salotto"
        self.repo.aggiorna(self.stanza)
        trovata = self.repo.trova_per_id("s1")
        self.assertEqual(trovata.nome, "Salotto")

    def test_elimina(self):
        self.repo.salva(self.stanza)
        self.assertTrue(self.repo.elimina("s1"))
        self.assertEqual(len(self.repo.trova_tutti()), 0)

    def test_elimina_inesistente(self):
        self.assertFalse(self.repo.elimina("inesistente"))


class TestRepositoryDispositiviJSON(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.old_data, self.old_backup, self.old_backup_path = _setup_temp_repo(repo_module, self.temp_dir)
        self.repo = repo_module.RepositoryDispositiviJSON()
        self.d1 = Dispositivo("d1", "Luce base", "luce", "s1")
        self.luce = Luce("d2", "Luce smart", "s1", intensita=50, colore="blu")
        self.termo = Termostato("d3", "Termo", "s1", temperatura_target=22.0)
        self.serratura = Serratura("d4", "Serratura", "s1")

    def tearDown(self):
        _restore_repo(repo_module, self.old_data, self.old_backup, self.old_backup_path)
        shutil.rmtree(self.temp_dir)

    def test_salva_e_trova_per_id(self):
        self.repo.salva(self.d1)
        trovato = self.repo.trova_per_id("d1")
        self.assertIsNotNone(trovato)
        self.assertEqual(trovato.nome, "Luce base")

    def test_salva_e_ricarica_luce(self):
        self.repo.salva(self.luce)
        trovato = self.repo.trova_per_id("d2")
        self.assertIsInstance(trovato, Luce)
        self.assertEqual(trovato.intensita, 50)
        self.assertEqual(trovato.colore, "blu")

    def test_salva_e_ricarica_termostato(self):
        self.repo.salva(self.termo)
        trovato = self.repo.trova_per_id("d3")
        self.assertIsInstance(trovato, Termostato)
        self.assertEqual(trovato.temperatura_target, 22.0)

    def test_salva_e_ricarica_serratura(self):
        self.repo.salva(self.serratura)
        trovato = self.repo.trova_per_id("d4")
        self.assertIsInstance(trovato, Serratura)

    def test_trova_tutti(self):
        self.repo.salva(self.d1)
        self.repo.salva(self.luce)
        self.assertEqual(len(self.repo.trova_tutti()), 2)

    def test_aggiorna(self):
        self.repo.salva(self.d1)
        self.d1.nome = "Luce modificata"
        self.repo.aggiorna(self.d1)
        trovato = self.repo.trova_per_id("d1")
        self.assertEqual(trovato.nome, "Luce modificata")

    def test_elimina(self):
        self.repo.salva(self.d1)
        self.assertTrue(self.repo.elimina("d1"))
        self.assertIsNone(self.repo.trova_per_id("d1"))

    def test_elimina_inesistente(self):
        self.assertFalse(self.repo.elimina("inesistente"))

    def test_aggiorna_stanza(self):
        self.repo.salva(self.d1)
        self.assertTrue(self.repo.aggiorna_stanza("d1", "s2"))
        trovato = self.repo.trova_per_id("d1")
        self.assertEqual(trovato.id_stanza, "s2")

    def test_aggiorna_stanza_inesistente(self):
        self.assertFalse(self.repo.aggiorna_stanza("inesistente", "s2"))

    def test_trova_offline(self):
        self.repo.salva(self.d1)
        self.d1.online = False
        self.repo.aggiorna(self.d1)
        offline = self.repo.trova_offline()
        self.assertEqual(len(offline), 1)
        self.assertEqual(offline[0].id, "d1")


class TestRepositoryAutomazioniJSON(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.old_data, self.old_backup, self.old_backup_path = _setup_temp_repo(repo_module, self.temp_dir)
        self.repo = repo_module.RepositoryAutomazioniJSON()
        self.auto = Automazione("a1", "Accendi sera", "d1", orario="19:00")
        self.regola = Regola("orario", "19:00", "accendi")

    def tearDown(self):
        _restore_repo(repo_module, self.old_data, self.old_backup, self.old_backup_path)
        shutil.rmtree(self.temp_dir)

    def test_salva_e_trova_per_id(self):
        self.repo.salva(self.auto)
        trovata = self.repo.trova_per_id("a1")
        self.assertIsNotNone(trovata)
        self.assertEqual(trovata.nome, "Accendi sera")

    def test_salva_con_regole(self):
        self.auto.aggiungi_regola(self.regola)
        self.auto.attiva_automazione()
        self.repo.salva(self.auto)
        trovata = self.repo.trova_per_id("a1")
        self.assertTrue(trovata.attiva)
        self.assertEqual(len(trovata.regole), 1)

    def test_trova_attive(self):
        self.auto.attiva_automazione()
        self.repo.salva(self.auto)
        auto2 = Automazione("a2", "Spenta", "d2")
        self.repo.salva(auto2)
        attive = self.repo.trova_attive()
        self.assertEqual(len(attive), 1)
        self.assertEqual(attive[0].id, "a1")

    def test_aggiorna(self):
        self.repo.salva(self.auto)
        self.auto.nome = "Modificata"
        self.repo.aggiorna(self.auto)
        trovata = self.repo.trova_per_id("a1")
        self.assertEqual(trovata.nome, "Modificata")

    def test_elimina(self):
        self.repo.salva(self.auto)
        self.assertTrue(self.repo.elimina("a1"))
        self.assertIsNone(self.repo.trova_per_id("a1"))

    def test_elimina_inesistente(self):
        self.assertFalse(self.repo.elimina("inesistente"))


class TestRepositoryEventiJSON(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.old_data, self.old_backup, self.old_backup_path = _setup_temp_repo(repo_module, self.temp_dir)
        self.repo = repo_module.RepositoryEventiJSON()
        self.e1 = Evento("e1", "LOGIN", "Login utente")
        self.e2 = Evento("e2", "COMANDO", "Luce accesa", id_dispositivo="d1")
        self.e3 = Evento("e3", "LOGOUT", "Logout utente")

    def tearDown(self):
        _restore_repo(repo_module, self.old_data, self.old_backup, self.old_backup_path)
        shutil.rmtree(self.temp_dir)

    def test_salva_e_cerca(self):
        self.repo.salva(self.e1)
        risultati = self.repo.cerca("LOGIN")
        self.assertEqual(len(risultati), 1)

    def test_cerca_per_descrizione(self):
        self.repo.salva(self.e1)
        self.repo.salva(self.e2)
        risultati = self.repo.cerca("Luce")
        self.assertEqual(len(risultati), 1)

    def test_cerca_case_insensitive(self):
        self.repo.salva(self.e1)
        risultati = self.repo.cerca("login")
        self.assertEqual(len(risultati), 1)

    def test_cerca_nessun_risultato(self):
        self.repo.salva(self.e1)
        risultati = self.repo.cerca("INESISTENTE")
        self.assertEqual(len(risultati), 0)

    def test_aggrega(self):
        self.repo.salva(self.e1)
        self.repo.salva(self.e2)
        self.repo.salva(self.e3)
        risultati = self.repo.aggrega("LOGIN")
        self.assertEqual(len(risultati), 1)

    def test_salva_multipli(self):
        self.repo.salva(self.e1)
        self.repo.salva(self.e2)
        self.repo.salva(self.e3)
        self.assertEqual(len(self.repo.cerca("")), 3)


class TestRepositoryDatiSistemaJSON(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.old_data, self.old_backup, self.old_backup_path = _setup_temp_repo(repo_module, self.temp_dir)
        self.repo = repo_module.RepositoryDatiSistemaJSON()

        repo_utenti = repo_module.RepositoryUtentiJSON()
        repo_stanze = repo_module.RepositoryStanzeJSON()
        repo_utenti.salva(Utente("u1", "Test", "test@test.it", "pass"))
        repo_stanze.salva(Stanza("s1", "Stanza test", 0))

    def tearDown(self):
        _restore_repo(repo_module, self.old_data, self.old_backup, self.old_backup_path)
        shutil.rmtree(self.temp_dir)

    def test_salva_backup(self):
        percorso = self.repo.salva_backup()
        self.assertTrue(os.path.exists(percorso))
        self.assertIn("backup_", os.path.basename(percorso))

    def test_elenca_backup(self):
        self.repo.salva_backup()
        time.sleep(1.1)
        self.repo.salva_backup()
        backup = self.repo.elenca_backup()
        self.assertEqual(len(backup), 2)

    def test_elenca_backup_ordinati(self):
        self.repo.salva_backup()
        time.sleep(1.1)
        self.repo.salva_backup()
        backup = self.repo.elenca_backup()
        self.assertEqual(len(backup), 2)

    def test_carica_backup(self):
        percorso = self.repo.salva_backup()
        msg = self.repo.carica_backup(percorso)
        self.assertIn("Ripristino completato", msg)

    def test_carica_backup_inesistente(self):
        with self.assertRaises(FileNotFoundError):
            self.repo.carica_backup("non_esiste.json")

    def test_elimina_backup(self):
        percorso = self.repo.salva_backup()
        self.assertTrue(os.path.exists(percorso))
        self.assertTrue(self.repo.elimina_backup(percorso))
        self.assertFalse(os.path.exists(percorso))

    def test_elimina_backup_inesistente(self):
        self.assertFalse(self.repo.elimina_backup("non_esiste.json"))


class TestSerializzazione(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.old_data, self.old_backup, self.old_backup_path = _setup_temp_repo(repo_module, self.temp_dir)

    def tearDown(self):
        _restore_repo(repo_module, self.old_data, self.old_backup, self.old_backup_path)
        shutil.rmtree(self.temp_dir)

    def test_to_dict_utente(self):
        u = Utente("u1", "Mario", "m@t.it", "pass")
        d = repo_module._to_dict(u)
        self.assertEqual(d["id"], "u1")
        self.assertEqual(d["tipo"], "utente")
        self.assertIn("password", d)

    def test_to_dict_admin(self):
        a = Amministratore("a1", "Admin", "a@t.it", "pass", livello_accesso=2)
        d = repo_module._to_dict(a)
        self.assertEqual(d["tipo"], "amministratore")
        self.assertEqual(d["livello_accesso"], 2)

    def test_to_dict_stanza(self):
        s = Stanza("s1", "Salotto", 1)
        d = repo_module._to_dict(s)
        self.assertEqual(d["piano"], 1)

    def test_to_dict_luce(self):
        l = Luce("l1", "Luce", "s1", intensita=70, colore="rosso")
        d = repo_module._to_dict(l)
        self.assertEqual(d["intensita"], 70)
        self.assertEqual(d["colore"], "rosso")
        self.assertEqual(d["tipo"], "luce")

    def test_to_dict_termostato(self):
        t = Termostato("t1", "Termo", "s1", temperatura_target=22.5)
        d = repo_module._to_dict(t)
        self.assertEqual(d["temperatura_target"], 22.5)

    def test_to_dict_serratura(self):
        s = Serratura("s1", "Serratura", "s1", modalita_sicurezza=True)
        d = repo_module._to_dict(s)
        self.assertTrue(d["modalita_sicurezza"])

    def test_to_dict_regola(self):
        r = Regola("orario", "19:00", "accendi")
        d = repo_module._to_dict(r)
        self.assertEqual(d["tipo_condizione"], "orario")

    def test_to_dict_automazione(self):
        a = Automazione("a1", "Auto", "d1")
        d = repo_module._to_dict(a)
        self.assertEqual(d["nome"], "Auto")

    def test_to_dict_evento(self):
        e = Evento("e1", "TEST", "test event")
        d = repo_module._to_dict(e)
        self.assertIn("timestamp", d)

    def test_from_dict_utente(self):
        data = {"id": "u1", "nome": "Mario", "email": "m@t.it",
                "password": "hash", "tipo": "utente"}
        u = repo_module._from_dict(Utente, data)
        self.assertEqual(u.nome, "Mario")
        self.assertEqual(u._password_hash, "hash")

    def test_from_dict_admin(self):
        data = {"id": "a1", "nome": "Admin", "email": "a@t.it",
                "password": "hash", "tipo": "amministratore", "livello_accesso": 2}
        a = repo_module._from_dict(Amministratore, data)
        self.assertIsInstance(a, Amministratore)
        self.assertEqual(a.livello_accesso, 2)

    def test_from_dict_stanza(self):
        data = {"id": "s1", "nome": "Salotto", "piano": 1}
        s = repo_module._from_dict(Stanza, data)
        self.assertEqual(s.piano, 1)

    def test_from_dict_luce(self):
        data = {"id": "l1", "nome": "Luce", "tipo": "luce", "id_stanza": "s1",
                "intensita": 70, "colore": "rosso", "stato": "acceso", "online": True}
        l = repo_module._from_dict(Dispositivo, data)
        self.assertIsInstance(l, Luce)
        self.assertEqual(l.intensita, 70)
        self.assertEqual(l.colore, "rosso")

    def test_from_dict_termostato(self):
        data = {"id": "t1", "nome": "Termo", "tipo": "termostato", "id_stanza": "s1",
                "temperatura_target": 22.5, "modalita": "caldo", "stato": "22.5°C", "online": True}
        t = repo_module._from_dict(Dispositivo, data)
        self.assertIsInstance(t, Termostato)
        self.assertEqual(t.temperatura_target, 22.5)

    def test_from_dict_serratura(self):
        data = {"id": "s1", "nome": "Serratura", "tipo": "serratura", "id_stanza": "s1",
                "modalita_sicurezza": True, "stato": "chiusa", "online": True}
        s = repo_module._from_dict(Dispositivo, data)
        self.assertIsInstance(s, Serratura)
        self.assertTrue(s.modalita_sicurezza)

    def test_from_dict_automazione(self):
        data = {"id": "a1", "nome": "Auto", "attiva": True, "orario": "19:00",
                "id_dispositivo": "d1", "ultima_esecuzione": None, "regole": []}
        a = repo_module._from_dict(Automazione, data)
        self.assertTrue(a.attiva)
        self.assertEqual(a.orario, "19:00")


if __name__ == "__main__":
    unittest.main()
