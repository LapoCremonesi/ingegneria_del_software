"""
Modello del dominio: Evento e LogEventi.

Registra ogni operazione rilevante (accesione, spegnimento, errore, automazione, backup)
per la consultazione e l'esportazione dello storico.
"""

from datetime import datetime


class Evento:
    """Evento di sistema con timestamp, tipo e descrizione."""

    def __init__(self, id_evento, tipo, descrizione, id_dispositivo=None):
        self._id = id_evento
        self._timestamp = datetime.now()
        self._tipo = tipo
        self._descrizione = descrizione
        self._id_dispositivo = id_dispositivo

    @property
    def id(self):
        return self._id

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def tipo(self):
        return self._tipo

    @property
    def descrizione(self):
        return self._descrizione

    @property
    def id_dispositivo(self):
        return self._id_dispositivo

    def to_string(self):
        """Restituisce una rappresentazione testuale dell'evento."""
        disp = f" [dispositivo {self._id_dispositivo}]" if self._id_dispositivo else ""
        return f"[{self._timestamp.strftime('%Y-%m-%d %H:%M:%S')}] " \
               f"{self._tipo}: {self._descrizione}{disp}"

    def get_timestamp(self):
        return self._timestamp

    def get_tipo(self):
        return self._tipo


class LogEventi:
    """Collezione di eventi con metodi di filtro ed esportazione."""

    def __init__(self, id_log):
        self._id = id_log
        self._eventi = []

    @property
    def id(self):
        return self._id

    @property
    def eventi(self):
        return list(self._eventi)

    def aggiungi_evento(self, evento):
        """Aggiunge un evento al log."""
        self._eventi.append(evento)

    def elimina_evento(self, id_evento):
        """Rimuove un evento dal log dato il suo id."""
        for e in self._eventi:
            if e.id == id_evento:
                self._eventi.remove(e)
                return True
        return False

    def filtra_eventi(self, tipo):
        """Filtra gli eventi per tipo."""
        return [e for e in self._eventi if e.tipo == tipo]

    def get_eventi_per_data(self, data):
        """Restituisce gli eventi che corrispondono alla data specificata."""
        return [e for e in self._eventi
                if e.timestamp.date() == data.date()]

    def esporta_log(self):
        """Esporta l'intero log come stringa testuale."""
        righe = [e.to_string() for e in self._eventi]
        return "\n".join(righe)
