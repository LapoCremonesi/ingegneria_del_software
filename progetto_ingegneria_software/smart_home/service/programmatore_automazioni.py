from typing import Optional

from PyQt6.QtCore import QTimer

from smart_home.service.servizio_automazioni import ServizioAutomazioni


class ProgrammatoreAutomazioni:

    def __init__(self, servizio_automazioni: ServizioAutomazioni,
                 intervallo_ms: int = 30000) -> None:
        self._servizio_automazioni = servizio_automazioni
        self._timer: Optional[QTimer] = None
        self._intervallo_ms = intervallo_ms

    @property
    def timer(self) -> Optional[QTimer]:
        return self._timer

    def avvia(self) -> None:
        if self._timer is not None:
            return
        self._timer = QTimer()
        self._timer.timeout.connect(self._esegui_ciclo)
        self._timer.start(self._intervallo_ms)

    def ferma(self) -> None:
        if self._timer is None:
            return
        self._timer.stop()
        self._timer = None

    def _esegui_ciclo(self) -> None:
        self._servizio_automazioni.esegui_tutte()
