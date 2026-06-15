from __future__ import annotations

import uuid
from datetime import date, datetime, time
from typing import List, Optional


class Regola:

    def __init__(self, tipo_condizione: str, valore_condizione: str,
                 azione: str) -> None:
        self._id: str = str(uuid.uuid4())
        self._tipo_condizione: str = tipo_condizione
        self._valore_condizione: str = valore_condizione
        self._azione: str = azione

    @property
    def id(self) -> str:
        return self._id

    @property
    def tipo_condizione(self) -> str:
        return self._tipo_condizione

    @property
    def valore_condizione(self) -> str:
        return self._valore_condizione

    @property
    def azione(self) -> str:
        return self._azione

    def valuta_condizione(self) -> bool:
        if self._tipo_condizione == "orario":
            ora_corrente = datetime.now().time()
            ore, minuti = map(int, self._valore_condizione.split(":"))
            ora_target = time(ore, minuti)
            return ora_corrente >= ora_target
        return True

    def esegui_azione(self) -> str:
        return self._azione


class Automazione:

    def __init__(self, id_automazione: str, nome: str,
                 id_dispositivo: str,
                 orario: Optional[str] = None) -> None:
        self._id: str = id_automazione
        self._nome: str = nome
        self._id_dispositivo: str = id_dispositivo
        self._attiva: bool = False
        self._orario: Optional[str] = orario
        self._ultima_esecuzione: Optional[str] = None
        self._regole: List[Regola] = []

    @property
    def id(self) -> str:
        return self._id

    @property
    def nome(self) -> str:
        return self._nome

    @nome.setter
    def nome(self, valore: str) -> None:
        self._nome = valore

    @property
    def id_dispositivo(self) -> str:
        return self._id_dispositivo

    @id_dispositivo.setter
    def id_dispositivo(self, valore: str) -> None:
        self._id_dispositivo = valore

    @property
    def attiva(self) -> bool:
        return self._attiva

    @property
    def orario(self) -> Optional[str]:
        return self._orario

    @orario.setter
    def orario(self, valore: Optional[str]) -> None:
        self._orario = valore

    @property
    def ultima_esecuzione(self) -> Optional[str]:
        return self._ultima_esecuzione

    @ultima_esecuzione.setter
    def ultima_esecuzione(self, valore: Optional[str]) -> None:
        self._ultima_esecuzione = valore

    @property
    def regole(self) -> List[Regola]:
        return list(self._regole)

    def attiva_automazione(self) -> None:
        self._attiva = True

    def disattiva_automazione(self) -> None:
        self._attiva = False

    def aggiungi_regola(self, regola: Regola) -> None:
        self._regole.append(regola)

    def rimuovi_regola(self, id_regola: str) -> bool:
        for r in self._regole:
            if r.id == id_regola:
                self._regole.remove(r)
                return True
        return False

    def valuta_regole(self) -> List[Regola]:
        return [r for r in self._regole if r.valuta_condizione()]

    def deve_eseguire(self) -> bool:
        if not self._attiva or not self._orario or not self._regole:
            return False
        oggi = date.today().isoformat()
        if self._ultima_esecuzione == oggi:
            return False
        regole_soddisfatte = self.valuta_regole()
        return len(regole_soddisfatte) > 0

    def esegui(self) -> bool:
        if not self._attiva:
            return False
        regole_soddisfatte = self.valuta_regole()
        if not regole_soddisfatte:
            return False
        for regola in regole_soddisfatte:
            regola.esegui_azione()
        self._ultima_esecuzione = date.today().isoformat()
        return True
