"""
Modello del dominio: Stanza.

Rappresenta una stanza fisica della casa che pu contenere dispositivi.
"""


class Stanza:
    """Rappresenta una stanza con un identificativo, nome, piano e lista di dispositivi."""

    def __init__(self, id_stanza, nome, piano):
        self._id = id_stanza
        self._nome = nome
        self._piano = piano
        self._dispositivi = []

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
    def piano(self):
        return self._piano

    @piano.setter
    def piano(self, valore):
        self._piano = valore

    @property
    def dispositivi(self):
        return list(self._dispositivi)

    def aggiungi_dispositivo(self, dispositivo):
        """Aggiunge un dispositivo alla stanza."""
        self._dispositivi.append(dispositivo)

    def rimuovi_dispositivo(self, id_dispositivo):
        """Rimuove un dispositivo dalla stanza dato il suo id. Restituisce True se rimosso."""
        for d in self._dispositivi:
            if d.id == id_dispositivo:
                self._dispositivi.remove(d)
                return True
        return False

    def elenca_dispositivi(self):
        """Restituisce la lista di tutti i dispositivi presenti nella stanza."""
        return self.dispositivi

    def get_dispositivi_per_tipo(self, tipo):
        """Filtra i dispositivi per tipo (es. 'luce', 'termostato', 'serratura')."""
        return [d for d in self._dispositivi if d.tipo == tipo]
