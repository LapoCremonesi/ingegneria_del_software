"""
Modello del dominio: Dispositivo.

Rappresenta un dispositivo smart (luce, termostato, serratura, ecc.)
collegato al sistema.
"""


class Dispositivo:
    """Dispositivo intelligente con stato, tipo e connessione."""

    def __init__(self, id_dispositivo, nome, tipo, id_stanza):
        self._id = id_dispositivo
        self._nome = nome
        self._tipo = tipo
        self._stato = "spento"
        self._online = True
        self._id_stanza = id_stanza

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
    def tipo(self):
        return self._tipo

    @property
    def stato(self):
        return self._stato

    @property
    def online(self):
        return self._online

    @online.setter
    def online(self, valore):
        self._online = valore

    @property
    def id_stanza(self):
        return self._id_stanza

    @id_stanza.setter
    def id_stanza(self, valore):
        self._id_stanza = valore

    def accendi(self):
        """Accende il dispositivo e ne aggiorna lo stato."""
        self._stato = "acceso"

    def spegni(self):
        """Spegne il dispositivo e ne aggiorna lo stato."""
        self._stato = "spento"

    def cambia_stato(self, nuovo_stato):
        """Imposta un nuovo stato personalizzato. Restituisce False se il dispositivo offline."""
        if not self._online:
            return False
        self._stato = nuovo_stato
        return True

    def invia_comando(self, comando):
        """
        Elabora un comando testuale sul dispositivo.

        Comandi riconosciuti: 'accendi', 'spegni', oppure un valore personalizzato.
        """
        if not self._online:
            return False
        comando_normalizzato = comando.strip().lower()
        if comando_normalizzato == "accendi":
            self.accendi()
        elif comando_normalizzato == "spegni":
            self.spegni()
        else:
            self._stato = comando
        return True

    def is_online(self):
        """Verifica se il dispositivo connesso alla rete."""
        return self._online

    def get_stato(self):
        """Restituisce lo stato corrente del dispositivo."""
        return self._stato

    def get_tipo(self):
        """Restituisce il tipo del dispositivo."""
        return self._tipo

    def applica_comando(self, comando):
        """Alias per invia_comando, usato nei diagrammi di sequenza."""
        return self.invia_comando(comando)
