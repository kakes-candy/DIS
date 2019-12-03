from Basis.cl_DIS_dataobject import DISdataObject
from SGGZ_8_0.definitions import format_geleverd_zorgprofiel_tijdschrijven
import datetime


class Tijdschrijven(DISdataObject):

    format_definitions = format_geleverd_zorgprofiel_tijdschrijven
    child_types = []

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.valid = True

    def add_parent(self, parent):
        if not self.parent:
            self.parent = parent
            self._1488 = parent._1462

    # Methode om object te valideren
    def validate(self, autocorrect):

        # start assuming object is valid
        meldingen = []
        bewerkingen = []

        # En er moet een patient als parent zijn
        if not self.parent:
            meldingen.append(
                "TIJDSCHRIJVEN: {} heeft geen ouder".format(self.__str__())
            )

        # Validatie 2126: 1491 Activiteitdatum ligt niet tussen 1465 Begindatum DBC-traject en 1466 Einddatum DBC-traject
        start_dbc = datetime.datetime.strptime(self.parent._1465, "%Y%m%d")
        eind_dbc = datetime.datetime.strptime(self.parent._1466, "%Y%m%d")
        activiteitendatum = datetime.datetime.strptime(self._1491, "%Y%m%d")
        if activiteitendatum < start_dbc or activiteitendatum > eind_dbc:
            meldingen.append(
                "TIJDSCHRIJVEN: {} activiteitdatum ligt niet tussen begin en einddatum dbc".format(
                    self.__str__()
                )
            )

        return {"bewerkingen": bewerkingen, "meldingen": meldingen}

