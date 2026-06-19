import unittest
from datetime import date

from smart_home.domain.automazione import Automazione, Regola
from smart_home.domain.dispositivo import Dispositivo
from smart_home.domain.dispositivi_specifici import Luce, Serratura, Termostato
from smart_home.domain.evento import Evento, LogEventi
from smart_home.domain.stanza import Stanza
from smart_home.domain.utente import Amministratore, Utente


class TestUtente(unittest.TestCase):

    def setUp(self):
        self.utente = Utente("u1", "Mario", "mario@test.it", "password123")

    def test_proprieta(self):
        self.assertEqual(self.utente.id, "u1")
        self.assertEqual(self.utente.nome, "Mario")
        self.assertEqual(self.utente.email, "mario@test.it")

    def test_autentica_ok(self):
        self.assertTrue(self.utente.autentica("password123"))

    def test_autentica_fail(self):
        self.assertFalse(self.utente.autentica("sbagliata"))

    def test_cambia_password(self):
        self.utente.cambia_password("nuova456")
        self.assertTrue(self.utente.autentica("nuova456"))
        self.assertFalse(self.utente.autentica("password123"))


class TestAmministratore(unittest.TestCase):

    def setUp(self):
        self.admin = Amministratore("a1", "Admin", "admin@test.it", "admin123")
        self.utente = Utente("u1", "Mario", "mario@test.it", "pass")
        self.automazione = Automazione("auto1", "Test", "d1")

    def test_proprieta_admin(self):
        self.assertEqual(self.admin.id, "a1")
        self.assertEqual(self.admin.livello_accesso, 1)

    def test_livello_accesso_personalizzato(self):
        a = Amministratore("a2", "Super", "s@t.it", "p", livello_accesso=3)
        self.assertEqual(a.livello_accesso, 3)

    def test_gestisci_automazione_attiva(self):
        self.automazione.attiva_automazione()
        self.admin.gestisci_automazione(self.automazione)
        self.assertFalse(self.automazione.attiva)

    def test_gestisci_automazione_disattiva(self):
        self.admin.gestisci_automazione(self.automazione)
        self.assertTrue(self.automazione.attiva)

    def test_consulta_log(self):
        eventi = [Evento("e1", "TEST", "test")]
        risultato = self.admin.consulta_log(eventi)
        self.assertEqual(risultato, eventi)

    def test_crea_utente(self):
        self.assertTrue(self.admin.crea_utente(self.utente))

    def test_elimina_utente(self):
        self.assertTrue(self.admin.elimina_utente("u1"))


class TestDispositivo(unittest.TestCase):

    def setUp(self):
        self.d = Dispositivo("d1", "Luce", "luce", "s1")

    def test_proprieta(self):
        self.assertEqual(self.d.id, "d1")
        self.assertEqual(self.d.nome, "Luce")
        self.assertEqual(self.d.tipo, "luce")
        self.assertEqual(self.d.id_stanza, "s1")
        self.assertTrue(self.d.online)
        self.assertEqual(self.d.stato, "spento")

    def test_setter_nome(self):
        self.d.nome = "NuovoNome"
        self.assertEqual(self.d.nome, "NuovoNome")

    def test_setter_online(self):
        self.d.online = False
        self.assertFalse(self.d.online)

    def test_setter_id_stanza(self):
        self.d.id_stanza = "s2"
        self.assertEqual(self.d.id_stanza, "s2")

    def test_accendi(self):
        self.d.accendi()
        self.assertEqual(self.d.stato, "acceso")

    def test_spegni(self):
        self.d.accendi()
        self.d.spegni()
        self.assertEqual(self.d.stato, "spento")

    def test_cambia_stato(self):
        self.assertTrue(self.d.cambia_stato("personalizzato"))
        self.assertEqual(self.d.stato, "personalizzato")

    def test_cambia_stato_offline(self):
        self.d.online = False
        self.assertFalse(self.d.cambia_stato("test"))

    def test_invia_comando_accendi(self):
        self.assertTrue(self.d.invia_comando("accendi"))
        self.assertEqual(self.d.stato, "acceso")

    def test_invia_comando_spegni(self):
        self.d.accendi()
        self.assertTrue(self.d.invia_comando("spegni"))
        self.assertEqual(self.d.stato, "spento")

    def test_invia_comando_personalizzato(self):
        self.assertTrue(self.d.invia_comando("custom"))
        self.assertEqual(self.d.stato, "custom")

    def test_invia_comando_offline(self):
        self.d.online = False
        self.assertFalse(self.d.invia_comando("accendi"))

    def test_is_online(self):
        self.assertTrue(self.d.is_online())
        self.d.online = False
        self.assertFalse(self.d.is_online())

    def test_get_stato(self):
        self.assertEqual(self.d.get_stato(), "spento")

    def test_get_tipo(self):
        self.assertEqual(self.d.get_tipo(), "luce")

    def test_applica_comando(self):
        self.assertTrue(self.d.applica_comando("accendi"))


class TestLuce(unittest.TestCase):

    def setUp(self):
        self.luce = Luce("l1", "Luce soggiorno", "s1")

    def test_proprieta_specifiche(self):
        self.assertEqual(self.luce.intensita, 0)
        self.assertEqual(self.luce.colore, "bianco")
        self.assertEqual(self.luce.tipo, "luce")

    def test_intensita_iniziale_personalizzata(self):
        l = Luce("l2", "Test", "s1", intensita=75, colore="rosso")
        self.assertEqual(l.intensita, 75)
        self.assertEqual(l.colore, "rosso")

    def test_intensita_clamp(self):
        l = Luce("l3", "Test", "s1", intensita=150)
        self.assertEqual(l.intensita, 100)
        l2 = Luce("l4", "Test", "s1", intensita=-10)
        self.assertEqual(l2.intensita, 0)

    def test_accendi_imposta_intensita(self):
        self.luce.accendi()
        self.assertEqual(self.luce.intensita, 100)
        self.assertEqual(self.luce.stato, "acceso")

    def test_spegni_resetta_intensita(self):
        self.luce.accendi()
        self.luce.spegni()
        self.assertEqual(self.luce.intensita, 0)
        self.assertEqual(self.luce.stato, "spento")

    def test_attenua(self):
        self.assertTrue(self.luce.attenua(50))
        self.assertEqual(self.luce.intensita, 50)
        self.assertEqual(self.luce.stato, "acceso")

    def test_attenua_zero_spegne(self):
        self.luce.accendi()
        self.luce.attenua(0)
        self.assertEqual(self.luce.stato, "spento")
        self.assertEqual(self.luce.intensita, 0)

    def test_attenua_offline(self):
        self.luce.online = False
        self.assertFalse(self.luce.attenua(50))

    def test_cambia_colore(self):
        self.assertTrue(self.luce.cambia_colore("blu"))
        self.assertEqual(self.luce.colore, "blu")

    def test_cambia_colore_offline(self):
        self.luce.online = False
        self.assertFalse(self.luce.cambia_colore("blu"))

    def test_invia_comando_attenua(self):
        self.assertTrue(self.luce.invia_comando("attenua 70"))
        self.assertEqual(self.luce.intensita, 70)

    def test_invia_comando_colore(self):
        self.assertTrue(self.luce.invia_comando("colore rosso"))
        self.assertEqual(self.luce.colore, "rosso")

    def test_invia_comando_colore_offline(self):
        self.luce.online = False
        self.assertFalse(self.luce.invia_comando("accendi"))


class TestTermostato(unittest.TestCase):

    def setUp(self):
        self.t = Termostato("t1", "Termo soggiorno", "s1")

    def test_proprieta_specifiche(self):
        self.assertEqual(self.t.temperatura_target, 20.0)
        self.assertEqual(self.t.modalita, "auto")
        self.assertEqual(self.t.tipo, "termostato")
        self.assertEqual(self.t.stato, "20.0°C")

    def test_parametri_personalizzati(self):
        t = Termostato("t2", "Test", "s1", temperatura_target=22.5, modalita="caldo")
        self.assertEqual(t.temperatura_target, 22.5)
        self.assertEqual(t.modalita, "caldo")

    def test_imposta_temperatura(self):
        self.assertTrue(self.t.imposta_temperatura(25.0))
        self.assertEqual(self.t.temperatura_target, 25.0)
        self.assertEqual(self.t.stato, "25.0°C")

    def test_imposta_temperatura_offline(self):
        self.t.online = False
        self.assertFalse(self.t.imposta_temperatura(25.0))

    def test_cambia_modalita(self):
        self.assertTrue(self.t.cambia_modalita("freddo"))
        self.assertEqual(self.t.modalita, "freddo")

    def test_cambia_modalita_non_valida(self):
        self.assertFalse(self.t.cambia_modalita("invalida"))

    def test_cambia_modalita_offline(self):
        self.t.online = False
        self.assertFalse(self.t.cambia_modalita("caldo"))

    def test_invia_comando_imposta(self):
        self.assertTrue(self.t.invia_comando("imposta 21.5"))
        self.assertEqual(self.t.temperatura_target, 21.5)

    def test_invia_comando_modalita(self):
        self.assertTrue(self.t.invia_comando("modalita caldo"))
        self.assertEqual(self.t.modalita, "caldo")

    def test_invia_comando_offline(self):
        self.t.online = False
        self.assertFalse(self.t.invia_comando("accendi"))


class TestSerratura(unittest.TestCase):

    def setUp(self):
        self.s = Serratura("s1", "Serratura ingresso", "s1")

    def test_proprieta_specifiche(self):
        self.assertEqual(self.s.tipo, "serratura")
        self.assertEqual(self.s.stato, "chiusa")
        self.assertFalse(self.s.modalita_sicurezza)

    def test_blocca(self):
        self.s.sblocca()
        self.s.blocca()
        self.assertEqual(self.s.stato, "chiusa")

    def test_sblocca(self):
        self.assertTrue(self.s.sblocca())
        self.assertEqual(self.s.stato, "aperta")

    def test_sblocca_con_sicurezza(self):
        self.s.attiva_sicurezza()
        self.assertFalse(self.s.sblocca())
        self.assertEqual(self.s.stato, "chiusa")

    def test_attiva_disattiva_sicurezza(self):
        self.s.attiva_sicurezza()
        self.assertTrue(self.s.modalita_sicurezza)
        self.assertEqual(self.s.stato, "chiusa")
        self.s.disattiva_sicurezza()
        self.assertFalse(self.s.modalita_sicurezza)

    def test_invia_comando_apri(self):
        self.assertTrue(self.s.invia_comando("apri"))
        self.assertEqual(self.s.stato, "aperta")

    def test_invia_comando_sblocca(self):
        self.assertTrue(self.s.invia_comando("sblocca"))
        self.assertEqual(self.s.stato, "aperta")

    def test_invia_comando_chiudi(self):
        self.s.sblocca()
        self.assertTrue(self.s.invia_comando("chiudi"))
        self.assertEqual(self.s.stato, "chiusa")

    def test_invia_comando_blocca(self):
        self.s.sblocca()
        self.assertTrue(self.s.invia_comando("blocca"))
        self.assertEqual(self.s.stato, "chiusa")

    def test_invia_comando_sicurezza_on(self):
        self.assertTrue(self.s.invia_comando("sicurezza on"))
        self.assertTrue(self.s.modalita_sicurezza)

    def test_invia_comando_sicurezza_off(self):
        self.s.attiva_sicurezza()
        self.assertTrue(self.s.invia_comando("sicurezza off"))
        self.assertFalse(self.s.modalita_sicurezza)

    def test_invia_comando_offline(self):
        self.s.online = False
        self.assertFalse(self.s.invia_comando("apri"))


class TestStanza(unittest.TestCase):

    def setUp(self):
        self.stanza = Stanza("s1", "Soggiorno", 0)
        self.d1 = Dispositivo("d1", "Luce", "luce", "s1")
        self.d2 = Termostato("d2", "Termo", "s1")

    def test_proprieta(self):
        self.assertEqual(self.stanza.id, "s1")
        self.assertEqual(self.stanza.nome, "Soggiorno")
        self.assertEqual(self.stanza.piano, 0)

    def test_setter_nome(self):
        self.stanza.nome = "Cucina"
        self.assertEqual(self.stanza.nome, "Cucina")

    def test_setter_piano(self):
        self.stanza.piano = 1
        self.assertEqual(self.stanza.piano, 1)

    def test_aggiungi_dispositivo(self):
        self.stanza.aggiungi_dispositivo(self.d1)
        self.assertEqual(len(self.stanza.dispositivi), 1)

    def test_rimuovi_dispositivo(self):
        self.stanza.aggiungi_dispositivo(self.d1)
        self.assertTrue(self.stanza.rimuovi_dispositivo("d1"))
        self.assertEqual(len(self.stanza.dispositivi), 0)

    def test_rimuovi_dispositivo_inesistente(self):
        self.assertFalse(self.stanza.rimuovi_dispositivo("inesistente"))

    def test_elenca_dispositivi(self):
        self.stanza.aggiungi_dispositivo(self.d1)
        self.stanza.aggiungi_dispositivo(self.d2)
        self.assertEqual(len(self.stanza.elenca_dispositivi()), 2)

    def test_get_dispositivi_per_tipo(self):
        self.stanza.aggiungi_dispositivo(self.d1)
        self.stanza.aggiungi_dispositivo(self.d2)
        luci = self.stanza.get_dispositivi_per_tipo("luce")
        self.assertEqual(len(luci), 1)
        self.assertEqual(luci[0].id, "d1")

    def test_dispositivi_copia(self):
        self.stanza.aggiungi_dispositivo(self.d1)
        dispositivi = self.stanza.dispositivi
        dispositivi.append(self.d2)
        self.assertEqual(len(self.stanza.dispositivi), 1)


class TestRegola(unittest.TestCase):

    def test_creazione(self):
        r = Regola("orario", "19:00", "accendi")
        self.assertEqual(r.tipo_condizione, "orario")
        self.assertEqual(r.valore_condizione, "19:00")
        self.assertEqual(r.azione, "accendi")
        self.assertIsNotNone(r.id)

    def test_esegui_azione(self):
        r = Regola("orario", "19:00", "spegni")
        self.assertEqual(r.esegui_azione(), "spegni")


class TestAutomazione(unittest.TestCase):

    def setUp(self):
        self.auto = Automazione("a1", "Accendi luce sera", "d1", orario="19:00")

    def test_proprieta(self):
        self.assertEqual(self.auto.id, "a1")
        self.assertEqual(self.auto.nome, "Accendi luce sera")
        self.assertEqual(self.auto.id_dispositivo, "d1")
        self.assertEqual(self.auto.orario, "19:00")
        self.assertFalse(self.auto.attiva)
        self.assertIsNone(self.auto.ultima_esecuzione)

    def test_setter_nome(self):
        self.auto.nome = "Nuovo nome"
        self.assertEqual(self.auto.nome, "Nuovo nome")

    def test_setter_id_dispositivo(self):
        self.auto.id_dispositivo = "d2"
        self.assertEqual(self.auto.id_dispositivo, "d2")

    def test_setter_orario(self):
        self.auto.orario = "20:00"
        self.assertEqual(self.auto.orario, "20:00")

    def test_setter_ultima_esecuzione(self):
        self.auto.ultima_esecuzione = "2024-01-01"
        self.assertEqual(self.auto.ultima_esecuzione, "2024-01-01")

    def test_attiva_disattiva(self):
        self.auto.attiva_automazione()
        self.assertTrue(self.auto.attiva)
        self.auto.disattiva_automazione()
        self.assertFalse(self.auto.attiva)

    def test_aggiungi_rimuovi_regola(self):
        r = Regola("orario", "19:00", "accendi")
        self.auto.aggiungi_regola(r)
        self.assertEqual(len(self.auto.regole), 1)
        self.assertTrue(self.auto.rimuovi_regola(r.id))
        self.assertEqual(len(self.auto.regole), 0)

    def test_rimuovi_regola_inesistente(self):
        self.assertFalse(self.auto.rimuovi_regola("inesistente"))

    def test_deve_eseguire_non_attiva(self):
        self.assertFalse(self.auto.deve_eseguire())

    def test_deve_eseguire_senza_regole(self):
        self.auto.attiva_automazione()
        self.assertFalse(self.auto.deve_eseguire())

    def test_esegui_non_attiva(self):
        self.assertFalse(self.auto.esegui())

    def test_esegui_senza_regole(self):
        self.auto.attiva_automazione()
        self.assertFalse(self.auto.esegui())

    def test_esegui_con_regola(self):
        r = Regola("stato", "acceso", "spegni")
        self.auto.aggiungi_regola(r)
        self.auto.attiva_automazione()
        self.auto.esegui()
        oggi = date.today().isoformat()
        self.assertEqual(self.auto.ultima_esecuzione, oggi)

    def test_non_ripetizione_giornaliera(self):
        r = Regola("stato", "acceso", "spegni")
        self.auto.aggiungi_regola(r)
        self.auto.attiva_automazione()
        self.auto.esegui()
        self.assertFalse(self.auto.deve_eseguire())

    def test_regole_copia(self):
        r = Regola("orario", "19:00", "accendi")
        self.auto.aggiungi_regola(r)
        regole = self.auto.regole
        regole.append(Regola("stato", "acceso", "spegni"))
        self.assertEqual(len(self.auto.regole), 1)


class TestEvento(unittest.TestCase):

    def setUp(self):
        self.evento = Evento("e1", "LOGIN", "Utente loggato")

    def test_proprieta(self):
        self.assertEqual(self.evento.id, "e1")
        self.assertEqual(self.evento.tipo, "LOGIN")
        self.assertEqual(self.evento.descrizione, "Utente loggato")
        self.assertIsNone(self.evento.id_dispositivo)
        self.assertIsNotNone(self.evento.timestamp)

    def test_con_dispositivo(self):
        e = Evento("e2", "COMANDO", "Luce accesa", id_dispositivo="d1")
        self.assertEqual(e.id_dispositivo, "d1")

    def test_to_string(self):
        s = self.evento.to_string()
        self.assertIn("LOGIN", s)
        self.assertIn("Utente loggato", s)
        self.assertNotIn("dispositivo", s)

    def test_to_string_con_dispositivo(self):
        e = Evento("e2", "COMANDO", "Test", id_dispositivo="d1")
        s = e.to_string()
        self.assertIn("[dispositivo d1]", s)

    def test_get_timestamp(self):
        self.assertIsNotNone(self.evento.get_timestamp())

    def test_get_tipo(self):
        self.assertEqual(self.evento.get_tipo(), "LOGIN")


class TestLogEventi(unittest.TestCase):

    def setUp(self):
        self.log = LogEventi("log1")
        self.e1 = Evento("e1", "LOGIN", "Login effettuato")
        self.e2 = Evento("e2", "LOGOUT", "Logout effettuato")
        self.e3 = Evento("e3", "LOGIN", "Altro login")

    def test_aggiungi_evento(self):
        self.log.aggiungi_evento(self.e1)
        self.assertEqual(len(self.log.eventi), 1)

    def test_elimina_evento(self):
        self.log.aggiungi_evento(self.e1)
        self.assertTrue(self.log.elimina_evento("e1"))
        self.assertEqual(len(self.log.eventi), 0)

    def test_elimina_evento_inesistente(self):
        self.assertFalse(self.log.elimina_evento("inesistente"))

    def test_filtra_eventi(self):
        self.log.aggiungi_evento(self.e1)
        self.log.aggiungi_evento(self.e2)
        self.log.aggiungi_evento(self.e3)
        risultati = self.log.filtra_eventi("LOGIN")
        self.assertEqual(len(risultati), 2)

    def test_get_eventi_per_data(self):
        self.log.aggiungi_evento(self.e1)
        oggi = self.e1.timestamp
        risultati = self.log.get_eventi_per_data(oggi)
        self.assertEqual(len(risultati), 1)

    def test_esporta_log(self):
        self.log.aggiungi_evento(self.e1)
        self.log.aggiungi_evento(self.e2)
        esportato = self.log.esporta_log()
        self.assertIn("LOGIN", esportato)
        self.assertIn("LOGOUT", esportato)

    def test_eventi_copia(self):
        self.log.aggiungi_evento(self.e1)
        eventi = self.log.eventi
        eventi.append(self.e2)
        self.assertEqual(len(self.log.eventi), 1)


if __name__ == "__main__":
    unittest.main()
