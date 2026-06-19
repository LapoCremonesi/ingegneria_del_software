"""
Controllore per la gestione e il controllo dei dispositivi.

Orchestra le operazioni CRUD e l'invio di comandi ai dispositivi.
Supporta la creazione tipizzata: Luce, Termostato, Serratura.
"""

import uuid

from smart_home.domain.dispositivo import Dispositivo
from smart_home.domain.dispositivi_specifici import Luce, Serratura, Termostato
from smart_home.service.servizio_dispositivi import ServizioDispositivi


class ControlloreDispositivi:
    """Orchestra il flusso di CRUD e controllo dei dispositivi."""

    def __init__(self, servizio_dispositivi):
        self._servizio_dispositivi = servizio_dispositivi

    def crea_dispositivo(self, nome, tipo, id_stanza,
                         **kwargs):
        """
        Crea un dispositivo del tipo specificato.

        ``tipo`` puo essere 'luce', 'termostato', 'serratura' o un tipo generico.
        Parametri aggiuntivi in ``kwargs`` vengono passati al costruttore
        della classe specifica.
        """
        nuovo_id = str(uuid.uuid4())
        tipo_normalizzato = tipo.strip().lower()
        if tipo_normalizzato == "luce":
            dispositivo = Luce(
                id_dispositivo=nuovo_id,
                nome=nome,
                id_stanza=id_stanza,
                intensita=kwargs.get("intensita", 0),
                colore=kwargs.get("colore", "bianco"),
            )
        elif tipo_normalizzato == "termostato":
            dispositivo = Termostato(
                id_dispositivo=nuovo_id,
                nome=nome,
                id_stanza=id_stanza,
                temperatura_target=kwargs.get("temperatura_target", 20.0),
                modalita=kwargs.get("modalita", "auto"),
            )
        elif tipo_normalizzato == "serratura":
            dispositivo = Serratura(
                id_dispositivo=nuovo_id,
                nome=nome,
                id_stanza=id_stanza,
                modalita_sicurezza=kwargs.get("modalita_sicurezza", False),
            )
        else:
            dispositivo = Dispositivo(
                id_dispositivo=nuovo_id,
                nome=nome,
                tipo=tipo_normalizzato,
                id_stanza=id_stanza,
            )
        return self._servizio_dispositivi.crea(dispositivo)

    def aggiorna_dispositivo(self, dispositivo):
        """Aggiorna un dispositivo esistente."""
        return self._servizio_dispositivi.aggiorna(dispositivo)

    def elimina_dispositivo(self, id_dispositivo):
        """Elimina un dispositivo dato il suo id."""
        return self._servizio_dispositivi.elimina(id_dispositivo)

    def elenca_dispositivi(self):
        """Restituisce l'elenco di tutti i dispositivi."""
        return self._servizio_dispositivi.elenca()

    def trova_dispositivo_per_id(self, id_dispositivo):
        """Restituisce un dispositivo per id."""
        return self._servizio_dispositivi.trova_per_id(id_dispositivo)

    def invia_comando(self, id_dispositivo, comando):
        """
        Invia un comando a un dispositivo.

        Restituisce il Dispositivo aggiornato se il comando ha avuto successo,
        None altrimenti.
        """
        return self._servizio_dispositivi.invia_comando(id_dispositivo, comando)
