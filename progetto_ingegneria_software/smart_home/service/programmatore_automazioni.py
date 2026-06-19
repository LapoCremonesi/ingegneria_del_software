from datetime import date, datetime, time as dtime, timedelta

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from smart_home.service.servizio_automazioni import ServizioAutomazioni


class ProgrammatoreAutomazioni(QObject):

    automazioni_eseguite = pyqtSignal()

    def __init__(self, servizio_automazioni,
                 fallback_ms=60000):
        super().__init__()
        self._servizio_automazioni = servizio_automazioni
        self._timer = None
        self._fallback_ms = fallback_ms

    @property
    def timer(self):
        return self._timer

    def avvia(self):
        if self._timer is not None:
            return
        self._timer = QTimer()
        self._timer.timeout.connect(self._esegui_ciclo)
        self._programma_prossimo()

    def ferma(self):
        if self._timer is None:
            return
        self._timer.stop()
        self._timer = None

    def _esegui_ciclo(self):
        from datetime import datetime
        print(f"[ProgrammatoreAutomazioni] _esegui_ciclo scattato alle {datetime.now().strftime('%H:%M:%S.%f')}")
        risultato = self._servizio_automazioni.esegui_tutte()
        print(f"[ProgrammatoreAutomazioni] esegui_tutte restituito: {risultato}")
        self.automazioni_eseguite.emit()
        self._programma_prossimo()

    def _programma_prossimo(self):
        ora_corrente = datetime.now()
        oggi = ora_corrente.date()
        ora_oggi = ora_corrente.time()

        prossimo = None

        for auto in self._servizio_automazioni.elenca_attive():
            if not auto.orario:
                continue
            try:
                ore, minuti = map(int, auto.orario.split(":"))
            except (ValueError, IndexError):
                continue
            target = dtime(ore, minuti)
            target_dt = datetime.combine(oggi, target)

            if target >= ora_oggi:
                if prossimo is None or target_dt < prossimo:
                    prossimo = target_dt
            else:
                oggi_str = oggi.isoformat()
                if auto.ultima_esecuzione != oggi_str:
                    subito = ora_corrente + timedelta(seconds=1)
                    if prossimo is None or subito < prossimo:
                        prossimo = subito
                else:
                    domani = target_dt + timedelta(days=1)
                    if prossimo is None or domani < prossimo:
                        prossimo = domani

        if prossimo is not None:
            delay_ms = int((prossimo - ora_corrente).total_seconds() * 1000)
            delay_ms = max(1000, delay_ms)
        else:
            delay_ms = self._fallback_ms

        ora_prossima = (ora_corrente + timedelta(milliseconds=delay_ms)).strftime('%H:%M:%S')
        print(f"[ProgrammatoreAutomazioni] Prossimo scatto tra {delay_ms}ms (alle {ora_prossima})")
        self._timer.setSingleShot(True)
        self._timer.start(delay_ms)
