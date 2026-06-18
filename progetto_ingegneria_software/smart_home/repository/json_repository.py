"""
Implementazione concreta dei repository basata su file JSON.

Ogni repository gestisce un file JSON nella cartella ``data/``.
I metodi serializzano e deserializzano gli oggetti del dominio
per renderli persistenti su disco.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from smart_home.domain.automazione import Automazione, Regola
from smart_home.domain.dispositivo import Dispositivo
from smart_home.domain.dispositivi_specifici import Luce, Serratura, Termostato
from smart_home.domain.evento import Evento
from smart_home.domain.stanza import Stanza
from smart_home.domain.utente import Amministratore, Utente
from smart_home.repository.interfaces import (
    RepositoryAutomazioni,
    RepositoryDatiSistema,
    RepositoryDispositivi,
    RepositoryEventi,
    RepositoryStanze,
    RepositoryUtenti,
)

# ── Percorsi base ─────────────────────────────────────────────

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "..", "backup")


def _data_path(filename: str) -> str:
    return os.path.normpath(os.path.join(DATA_DIR, filename))


# ── Helper di serializzazione ──────────────────────────────────

def _to_dict(obj: Any) -> Dict[str, Any]:
    """Converte un oggetto del dominio in dizionario serializzabile."""
    if isinstance(obj, Utente):
        d: Dict[str, Any] = {
            "id": str(obj.id),
            "nome": obj.nome,
            "email": obj.email,
            "password": obj._password_hash,
        }
        if isinstance(obj, Amministratore):
            d["tipo"] = "amministratore"
            d["livello_accesso"] = obj.livello_accesso
        else:
            d["tipo"] = "utente"
        return d

    if isinstance(obj, Stanza):
        return {
            "id": str(obj.id),
            "nome": obj.nome,
            "piano": obj.piano,
        }

    if isinstance(obj, Dispositivo):
        base: Dict[str, Any] = {
            "id": str(obj.id),
            "nome": obj.nome,
            "tipo": obj.tipo,
            "stato": obj.stato,
            "online": obj.online,
            "id_stanza": str(obj.id_stanza),
        }
        if isinstance(obj, Luce):
            base["intensita"] = obj.intensita
            base["colore"] = obj.colore
        elif isinstance(obj, Termostato):
            base["temperatura_target"] = obj.temperatura_target
            base["modalita"] = obj.modalita
        elif isinstance(obj, Serratura):
            base["modalita_sicurezza"] = obj.modalita_sicurezza
        return base

    if isinstance(obj, Regola):
        return {
            "id": str(obj.id),
            "tipo_condizione": obj.tipo_condizione,
            "valore_condizione": obj.valore_condizione,
            "azione": obj.azione,
        }

    if isinstance(obj, Automazione):
        return {
            "id": str(obj.id),
            "nome": obj.nome,
            "attiva": obj.attiva,
            "orario": obj.orario,
            "id_dispositivo": str(obj.id_dispositivo),
            "ultima_esecuzione": obj.ultima_esecuzione,
            "regole": [_to_dict(r) for r in obj.regole],
        }

    if isinstance(obj, Evento):
        return {
            "id": str(obj.id),
            "timestamp": obj.timestamp.isoformat(),
            "tipo": obj.tipo,
            "descrizione": obj.descrizione,
            "id_dispositivo": str(obj.id_dispositivo) if obj.id_dispositivo else None,
        }

    raise TypeError(f"Tipo non supportato: {type(obj)}")


def _from_dict(cls: type, data: Dict[str, Any]) -> Any:
    """Ricostruisce un oggetto del dominio da un dizionario."""
    if cls == Utente or cls == Amministratore:
        if data.get("tipo") == "amministratore":
            u = Amministratore(
                id_utente=str(data["id"]),
                nome=data["nome"],
                email=data["email"],
                password="",
                livello_accesso=data.get("livello_accesso", 1),
            )
        else:
            u = Utente(
                id_utente=str(data["id"]),
                nome=data["nome"],
                email=data["email"],
                password="",
            )
        password_hash = data.get("password", "")
        if password_hash:
            u._password_hash = password_hash
        return u

    if cls == Stanza:
        s = Stanza(id_stanza=str(data["id"]), nome=data["nome"], piano=data["piano"])
        return s

    if cls == Dispositivo or issubclass(cls, Dispositivo):
        tipo = data.get("tipo", "")
        id_stanza = str(data.get("id_stanza", ""))
        if tipo == "luce":
            d: Dispositivo = Luce(
                id_dispositivo=str(data["id"]),
                nome=data["nome"],
                id_stanza=id_stanza,
                intensita=data.get("intensita", 0),
                colore=data.get("colore", "bianco"),
            )
        elif tipo == "termostato":
            d = Termostato(
                id_dispositivo=str(data["id"]),
                nome=data["nome"],
                id_stanza=id_stanza,
                temperatura_target=data.get("temperatura_target", 20.0),
                modalita=data.get("modalita", "auto"),
            )
        elif tipo == "serratura":
            d = Serratura(
                id_dispositivo=str(data["id"]),
                nome=data["nome"],
                id_stanza=id_stanza,
                modalita_sicurezza=data.get("modalita_sicurezza", False),
            )
        else:
            d = Dispositivo(
                id_dispositivo=str(data["id"]),
                nome=data["nome"],
                tipo=tipo,
                id_stanza=id_stanza,
            )
        d._stato = data.get("stato", "spento")
        d._online = data.get("online", True)
        return d

    if cls == Regola:
        return Regola(
            tipo_condizione=data["tipo_condizione"],
            valore_condizione=data["valore_condizione"],
            azione=data["azione"],
        )

    if cls == Automazione:
        a = Automazione(
            id_automazione=str(data["id"]),
            nome=data["nome"],
            id_dispositivo=str(data.get("id_dispositivo", "")),
            orario=data.get("orario"),
        )
        if data.get("attiva", False):
            a.attiva_automazione()
        a.ultima_esecuzione = data.get("ultima_esecuzione")
        for r_data in data.get("regole", []):
            a.aggiungi_regola(_from_dict(Regola, r_data))
        return a

    if cls == Evento:
        id_dispositivo = data.get("id_dispositivo")
        e = Evento(
            id_evento=str(data["id"]),
            tipo=data["tipo"],
            descrizione=data["descrizione"],
            id_dispositivo=str(id_dispositivo) if id_dispositivo is not None else None,
        )
        if "timestamp" in data:
            e._timestamp = datetime.fromisoformat(data["timestamp"])
        return e

    raise TypeError(f"Tipo non supportato: {cls}")


# ── Classe base per repository JSON ───────────────────────────

class _BaseJSONRepository:
    """Fornisce caricamento e salvataggio generico su file JSON."""

    def __init__(self, filename: str) -> None:
        self._filepath = _data_path(filename)

    def _carica(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self._filepath):
            return []
        with open(self._filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _salva(self, dati: List[Dict[str, Any]]) -> None:
        os.makedirs(os.path.dirname(self._filepath), exist_ok=True)
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(dati, f, indent=2, ensure_ascii=False)

    def _trova_indice(self, dati: List[Dict[str, Any]], id_ricerca: str) -> int:
        for i, d in enumerate(dati):
            if str(d.get("id")) == str(id_ricerca):
                return i
        return -1


# ── Implementazioni concrete ──────────────────────────────────

class RepositoryUtentiJSON(_BaseJSONRepository, RepositoryUtenti):
    """Repository utenti persistente su file JSON."""

    def __init__(self) -> None:
        super().__init__("utenti.json")

    def trova_per_email(self, email: str) -> Optional[Utente]:
        for d in self._carica():
            if d.get("email") == email:
                return _from_dict(Utente, d)
        return None

    def salva(self, utente: Utente) -> None:
        dati = self._carica()
        idx = self._trova_indice(dati, utente.id)
        entry = _to_dict(utente)
        if idx >= 0:
            dati[idx] = entry
        else:
            dati.append(entry)
        self._salva(dati)

    def aggiorna(self, utente: Utente) -> None:
        self.salva(utente)


class RepositoryStanzeJSON(_BaseJSONRepository, RepositoryStanze):
    """Repository stanze persistente su file JSON."""

    def __init__(self) -> None:
        super().__init__("stanze.json")

    def trova_tutti(self) -> List[Stanza]:
        return [_from_dict(Stanza, d) for d in self._carica()]

    def trova_per_id(self, id_stanza: str) -> Optional[Stanza]:
        for d in self._carica():
            if str(d.get("id")) == id_stanza:
                return _from_dict(Stanza, d)
        return None

    def salva(self, stanza: Stanza) -> None:
        dati = self._carica()
        idx = self._trova_indice(dati, stanza.id)
        entry = _to_dict(stanza)
        if idx >= 0:
            dati[idx] = entry
        else:
            dati.append(entry)
        self._salva(dati)

    def aggiorna(self, stanza: Stanza) -> None:
        self.salva(stanza)

    def elimina(self, id_stanza: str) -> bool:
        dati = self._carica()
        idx = self._trova_indice(dati, id_stanza)
        if idx < 0:
            return False
        dati.pop(idx)
        self._salva(dati)
        return True


class RepositoryDispositiviJSON(_BaseJSONRepository, RepositoryDispositivi):
    """Repository dispositivi persistente su file JSON."""

    def __init__(self) -> None:
        super().__init__("dispositivi.json")

    def trova_tutti(self) -> List[Dispositivo]:
        return [_from_dict(Dispositivo, d) for d in self._carica()]

    def trova_per_id(self, id_dispositivo: str) -> Optional[Dispositivo]:
        for d in self._carica():
            if str(d.get("id")) == id_dispositivo:
                return _from_dict(Dispositivo, d)
        return None

    def salva(self, dispositivo: Dispositivo) -> None:
        dati = self._carica()
        idx = self._trova_indice(dati, dispositivo.id)
        entry = _to_dict(dispositivo)
        if idx >= 0:
            dati[idx] = entry
        else:
            dati.append(entry)
        self._salva(dati)

    def aggiorna(self, dispositivo: Dispositivo) -> None:
        self.salva(dispositivo)

    def elimina(self, id_dispositivo: str) -> bool:
        dati = self._carica()
        idx = self._trova_indice(dati, id_dispositivo)
        if idx < 0:
            return False
        dati.pop(idx)
        self._salva(dati)
        return True

    def aggiorna_stanza(self, id_dispositivo: str, id_stanza: str) -> bool:
        dati = self._carica()
        idx = self._trova_indice(dati, id_dispositivo)
        if idx < 0:
            return False
        dati[idx]["id_stanza"] = id_stanza
        self._salva(dati)
        return True

    def trova_offline(self) -> List[Dispositivo]:
        return [
            _from_dict(Dispositivo, d) for d in self._carica() if not d.get("online", True)
        ]


class RepositoryAutomazioniJSON(_BaseJSONRepository, RepositoryAutomazioni):
    """Repository automazioni persistente su file JSON."""

    def __init__(self) -> None:
        super().__init__("automazioni.json")

    def trova_tutti(self) -> List[Automazione]:
        return [_from_dict(Automazione, d) for d in self._carica()]

    def trova_per_id(self, id_automazione: str) -> Optional[Automazione]:
        for d in self._carica():
            if str(d.get("id")) == id_automazione:
                return _from_dict(Automazione, d)
        return None

    def trova_attive(self) -> List[Automazione]:
        return [
            _from_dict(Automazione, d) for d in self._carica() if d.get("attiva", False)
        ]

    def salva(self, automazione: Automazione) -> None:
        dati = self._carica()
        idx = self._trova_indice(dati, automazione.id)
        entry = _to_dict(automazione)
        if idx >= 0:
            dati[idx] = entry
        else:
            dati.append(entry)
        self._salva(dati)

    def aggiorna(self, automazione: Automazione) -> None:
        self.salva(automazione)

    def elimina(self, id_automazione: str) -> bool:
        dati = self._carica()
        idx = self._trova_indice(dati, id_automazione)
        if idx < 0:
            return False
        dati.pop(idx)
        self._salva(dati)
        return True


class RepositoryEventiJSON(_BaseJSONRepository, RepositoryEventi):
    """Repository eventi persistente su file JSON."""

    def __init__(self) -> None:
        super().__init__("eventi.json")

    def cerca(self, filtro: str) -> List[Evento]:
        risultati: List[Evento] = []
        filtro_lower = filtro.lower()
        for d in self._carica():
            if filtro_lower in d.get("tipo", "").lower() \
               or filtro_lower in d.get("descrizione", "").lower():
                risultati.append(_from_dict(Evento, d))
        return risultati

    def salva(self, evento: Evento) -> None:
        dati = self._carica()
        dati.append(_to_dict(evento))
        self._salva(dati)

    def aggrega(self, filtro: str) -> List[Evento]:
        """Restituisce eventi aggregati per tipo."""
        return [
            _from_dict(Evento, d) for d in self._carica()
            if filtro.lower() in d.get("tipo", "").lower()
        ]


class RepositoryDatiSistemaJSON(_BaseJSONRepository, RepositoryDatiSistema):
    """Repository per backup e ripristino su file JSON unificati."""

    _FONTI: List[str] = ["utenti.json", "stanze.json", "dispositivi.json",
                         "automazioni.json", "eventi.json"]

    def __init__(self) -> None:
        super().__init__("backup.json")

    # ── Backup ────────────────────────────────────────────────

    def salva_backup(self) -> str:
        """
        Crea un backup unificato con timestamp.

        Legge tutti i file JSON e li raggruppa in un unico file
        nella cartella ``backup/``.
        """
        now = datetime.now()
        nome_file = f"backup_{now.strftime('%Y-%m-%d_%H%M%S')}.json"
        dir_backup = _backup_path()
        os.makedirs(dir_backup, exist_ok=True)
        percorso = os.path.join(dir_backup, nome_file)

        dati_backup: Dict[str, Any] = {
            "data_creazione": now.isoformat(),
        }
        for nome_fonte in self._FONTI:
            path = _data_path(nome_fonte)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    dati_backup[nome_fonte.replace(".json", "")] = json.load(f)
            else:
                dati_backup[nome_fonte.replace(".json", "")] = []

        with open(percorso, "w", encoding="utf-8") as f:
            json.dump(dati_backup, f, indent=2, ensure_ascii=False)

        return percorso

    # ── Elenco backup ─────────────────────────────────────────

    def elenca_backup(self) -> List[str]:
        """Restituisce la lista dei backup disponibili ordinati dal piu recente."""
        dir_backup = _backup_path()
        if not os.path.isdir(dir_backup):
            return []
        files = [f for f in os.listdir(dir_backup)
                 if f.startswith("backup_") and f.endswith(".json")]
        files.sort(reverse=True)
        return [os.path.join(dir_backup, f) for f in files]

    # ── Ripristino ────────────────────────────────────────────

    def carica_backup(self, percorso: str) -> str:
        """
        Carica un file di backup e ripristina i dati sovrascrivendo
        i file JSON originali.
        """
        if not os.path.exists(percorso):
            raise FileNotFoundError(f"File backup non trovato: {percorso}")

        with open(percorso, "r", encoding="utf-8") as f:
            dati_backup = json.load(f)

        chiave_fonte = {
            "utenti": "utenti.json",
            "stanze": "stanze.json",
            "dispositivi": "dispositivi.json",
            "automazioni": "automazioni.json",
            "eventi": "eventi.json",
        }

        for chiave, nome_file in chiave_fonte.items():
            dati = dati_backup.get(chiave, [])
            path = _data_path(nome_file)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(dati, f, indent=2, ensure_ascii=False)

        return f"Ripristino completato da: {os.path.basename(percorso)}"


def _backup_path() -> str:
    """Restituisce il percorso assoluto della cartella backup, creandola se necessario."""
    p = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "backup"))
    os.makedirs(p, exist_ok=True)
    return p
