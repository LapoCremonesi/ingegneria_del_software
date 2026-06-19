import uuid
from datetime import date, datetime, time


class Regola:

    def __init__(self, tipo_condizione, valore_condizione, azione):
        self._id = str(uuid.uuid4())
        self._tipo_condizione = tipo_condizione
        self._valore_condizione = valore_condizione
        self._azione = azione

    @property
    def id(self):
        return self._id

    @property
    def tipo_condizione(self):
        return self._tipo_condizione

    @property
    def valore_condizione(self):
        return self._valore_condizione

    @property
    def azione(self):
        return self._azione

    def valuta_condizione(self):
        if self._tipo_condizione == "orario":
            ora_corrente = datetime.now().time()
            ore, minuti = map(int, self._valore_condizione.split(":"))
            ora_target = time(ore, minuti)
            return ora_corrente >= ora_target
        return True

    def esegui_azione(self):
        return self._azione


class Automazione:

    def __init__(self, id_automazione, nome, id_dispositivo, orario=None):
        self._id = id_automazione
        self._nome = nome
        self._id_dispositivo = id_dispositivo
        self._attiva = False
        self._orario = orario
        self._ultima_esecuzione = None
        self._regole = []

    @property
    def id(self):
        return self._id

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valore):
        self._nome = valore

    @property
    def id_dispositivo(self):
        return self._id_dispositivo

    @id_dispositivo.setter
    def id_dispositivo(self, valore):
        self._id_dispositivo = valore

    @property
    def attiva(self):
        return self._attiva

    @property
    def orario(self):
        return self._orario

    @orario.setter
    def orario(self, valore):
        self._orario = valore

    @property
    def ultima_esecuzione(self):
        return self._ultima_esecuzione

    @ultima_esecuzione.setter
    def ultima_esecuzione(self, valore):
        self._ultima_esecuzione = valore

    @property
    def regole(self):
        return list(self._regole)

    def attiva_automazione(self):
        self._attiva = True

    def disattiva_automazione(self):
        self._attiva = False

    def aggiungi_regola(self, regola):
        self._regole.append(regola)

    def rimuovi_regola(self, id_regola):
        for r in self._regole:
            if r.id == id_regola:
                self._regole.remove(r)
                return True
        return False

    def valuta_regole(self):
        return [r for r in self._regole if r.valuta_condizione()]

    def deve_eseguire(self):
        if not self._attiva or not self._orario or not self._regole:
            return False
        oggi = date.today().isoformat()
        if self._ultima_esecuzione == oggi:
            return False
        regole_soddisfatte = self.valuta_regole()
        return len(regole_soddisfatte) > 0

    def esegui(self):
        if not self._attiva:
            return False
        regole_soddisfatte = self.valuta_regole()
        if not regole_soddisfatte:
            return False
        for regola in regole_soddisfatte:
            regola.esegui_azione()
        self._ultima_esecuzione = date.today().isoformat()
        return True
