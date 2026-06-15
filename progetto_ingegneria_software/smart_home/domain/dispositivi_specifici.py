"""
Dispositivi specifici: Luce, Termostato, Serratura.

Estendono la classe base Dispositivo con attributi e comportamenti
specifici per ogni tipologia di device.
"""

from __future__ import annotations

from smart_home.domain.dispositivo import Dispositivo


class Luce(Dispositivo):
    """Luce smart con controllo di intensita e colore."""

    def __init__(self, id_dispositivo: str, nome: str,
                 id_stanza: str, intensita: int = 0,
                 colore: str = "bianco") -> None:
        super().__init__(id_dispositivo, nome, "luce", id_stanza)
        self._intensita: int = max(0, min(100, intensita))
        self._colore: str = colore

    @property
    def intensita(self) -> int:
        return self._intensita

    @property
    def colore(self) -> str:
        return self._colore

    def accendi(self) -> None:
        super().accendi()
        if self._intensita == 0:
            self._intensita = 100

    def spegni(self) -> None:
        super().spegni()
        self._intensita = 0

    def attenua(self, valore: int) -> bool:
        """Imposta l'intensita luminosa (0-100)."""
        if not self._online:
            return False
        self._intensita = max(0, min(100, valore))
        if valore > 0:
            self._stato = "acceso"
        else:
            self._stato = "spento"
        return True

    def cambia_colore(self, colore: str) -> bool:
        """Cambia il colore della luce."""
        if not self._online:
            return False
        self._colore = colore
        return True

    def invia_comando(self, comando: str) -> bool:
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

    def __init__(self, id_dispositivo: str, nome: str,
                 id_stanza: str,
                 temperatura_target: float = 20.0,
                 modalita: str = "auto") -> None:
        super().__init__(id_dispositivo, nome, "termostato", id_stanza)
        self._temperatura_target: float = temperatura_target
        self._modalita: str = modalita
        self._stato = f"{temperatura_target}°C"

    @property
    def temperatura_target(self) -> float:
        return self._temperatura_target

    @property
    def modalita(self) -> str:
        return self._modalita

    def imposta_temperatura(self, temp: float) -> bool:
        """Imposta la temperatura target."""
        if not self._online:
            return False
        self._temperatura_target = temp
        self._stato = f"{temp}°C"
        return True

    def cambia_modalita(self, modalita: str) -> bool:
        """Cambia la modalita di funzionamento (caldo/freddo/auto)."""
        if not self._online:
            return False
        if modalita not in ("caldo", "freddo", "auto"):
            return False
        self._modalita = modalita
        return True

    def invia_comando(self, comando: str) -> bool:
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

    def __init__(self, id_dispositivo: str, nome: str,
                 id_stanza: str,
                 modalita_sicurezza: bool = False) -> None:
        super().__init__(id_dispositivo, nome, "serratura", id_stanza)
        self._stato = "chiusa"
        self._modalita_sicurezza: bool = modalita_sicurezza

    @property
    def modalita_sicurezza(self) -> bool:
        return self._modalita_sicurezza

    def blocca(self) -> None:
        """Blocca la serratura."""
        self._stato = "chiusa"

    def sblocca(self) -> bool:
        """Sblocca la serratura. Se in modalita sicurezza, richiede override."""
        if self._modalita_sicurezza:
            return False
        self._stato = "aperta"
        return True

    def attiva_sicurezza(self) -> None:
        """Attiva la modalita sicurezza (blocco totale)."""
        self._modalita_sicurezza = True
        self._stato = "chiusa"

    def disattiva_sicurezza(self) -> None:
        """Disattiva la modalita sicurezza."""
        self._modalita_sicurezza = False

    def invia_comando(self, comando: str) -> bool:
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
