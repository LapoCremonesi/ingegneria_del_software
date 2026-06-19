"""
Dispositivi specifici: Luce, Termostato, Serratura.

Estendono la classe base Dispositivo con attributi e comportamenti
specifici per ogni tipologia di device.
"""

from smart_home.domain.dispositivo import Dispositivo


class Luce(Dispositivo):
    """Luce smart con controllo di intensita e colore."""

    def __init__(self, id_dispositivo, nome, id_stanza, intensita=0, colore="bianco"):
        super().__init__(id_dispositivo, nome, "luce", id_stanza)
        self._intensita = max(0, min(100, intensita))
        self._colore = colore

    @property
    def intensita(self):
        return self._intensita

    @property
    def colore(self):
        return self._colore

    def accendi(self):
        super().accendi()
        if self._intensita == 0:
            self._intensita = 100

    def spegni(self):
        super().spegni()
        self._intensita = 0

    def attenua(self, valore):
        """Imposta l'intensita luminosa (0-100)."""
        if not self._online:
            return False
        self._intensita = max(0, min(100, valore))
        if valore > 0:
            self._stato = "acceso"
        else:
            self._stato = "spento"
        return True

    def cambia_colore(self, colore):
        """Cambia il colore della luce."""
        if not self._online:
            return False
        self._colore = colore
        return True

    def invia_comando(self, comando):
        if not self._online:
            return False
        cmd = comando.strip().lower()
        if cmd.startswith("attenua "):
            try:
                valore = int(cmd.split()[1])
                return self.attenua(valore)
            except (IndexError, ValueError):
                return False
        if cmd.startswith("colore "):
            return self.cambia_colore(cmd.split(maxsplit=1)[1])
        return super().invia_comando(comando)


class Termostato(Dispositivo):
    """Termostato smart con controllo di temperatura e modalita."""

    def __init__(self, id_dispositivo, nome, id_stanza, temperatura_target=20.0, modalita="auto"):
        super().__init__(id_dispositivo, nome, "termostato", id_stanza)
        self._temperatura_target = temperatura_target
        self._modalita = modalita
        self._stato = f"{temperatura_target}°C"

    @property
    def temperatura_target(self):
        return self._temperatura_target

    @property
    def modalita(self):
        return self._modalita

    def imposta_temperatura(self, temp):
        """Imposta la temperatura target."""
        if not self._online:
            return False
        self._temperatura_target = temp
        self._stato = f"{temp}°C"
        return True

    def cambia_modalita(self, modalita):
        """Cambia la modalita di funzionamento (caldo/freddo/auto)."""
        if not self._online:
            return False
        if modalita not in ("caldo", "freddo", "auto"):
            return False
        self._modalita = modalita
        return True

    def invia_comando(self, comando):
        if not self._online:
            return False
        cmd = comando.strip().lower()
        if cmd.startswith("imposta "):
            try:
                temp = float(cmd.split()[1])
                return self.imposta_temperatura(temp)
            except (IndexError, ValueError):
                return False
        if cmd.startswith("modalita "):
            return self.cambia_modalita(cmd.split(maxsplit=1)[1])
        return super().invia_comando(comando)


class Serratura(Dispositivo):
    """Serratura smart con blocco/sblocco e modalita sicurezza."""

    def __init__(self, id_dispositivo, nome, id_stanza, modalita_sicurezza=False):
        super().__init__(id_dispositivo, nome, "serratura", id_stanza)
        self._stato = "chiusa"
        self._modalita_sicurezza = modalita_sicurezza

    @property
    def modalita_sicurezza(self):
        return self._modalita_sicurezza

    def blocca(self):
        """Blocca la serratura."""
        self._stato = "chiusa"

    def sblocca(self):
        """Sblocca la serratura. Se in modalita sicurezza, richiede override."""
        if self._modalita_sicurezza:
            return False
        self._stato = "aperta"
        return True

    def attiva_sicurezza(self):
        """Attiva la modalita sicurezza (blocco totale)."""
        self._modalita_sicurezza = True
        self._stato = "chiusa"

    def disattiva_sicurezza(self):
        """Disattiva la modalita sicurezza."""
        self._modalita_sicurezza = False

    def invia_comando(self, comando):
        if not self._online:
            return False
        cmd = comando.strip().lower()
        if cmd == "apri" or cmd == "sblocca":
            return self.sblocca()
        if cmd == "chiudi" or cmd == "blocca":
            self.blocca()
            return True
        if cmd == "sicurezza on":
            self.attiva_sicurezza()
            return True
        if cmd == "sicurezza off":
            self.disattiva_sicurezza()
            return True
        return super().invia_comando(comando)
