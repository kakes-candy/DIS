from Basis.cl_DIS_dataobject import DISdataObject
from BGGZ_2_0.definitions import format_zorgprofiel


class GeleverdZorgprofiel(DISdataObject):

    format_definitions = format_zorgprofiel
    child_types = []

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_parent(self, parent):
        if not self.parent:
            self.parent = parent
            self._3309 = parent._3257

    # Methode om object te valideren
    def validate(self, autocorrect):

        meldingen = []
        bewerkingen = []

        # En er moet een patient als parent zijn
        if not self.parent:
            meldingen.append(
                "TIJDSCHRIJVEN: {} heeft geen ouder".format(self.__str__())
            )

        # # Validatie 2126: 1491 Activiteitdatum ligt niet tussen 1465 Begindatum DBC-traject en 1466 Einddatum DBC-traject
        # start_dbc = datetime.datetime.strptime(self.parent._1465, '%Y%m%d')
        # eind_dbc =  datetime.datetime.strptime(self.parent._1466, '%Y%m%d')
        # activiteitendatum = datetime.datetime.strptime(self._1491, '%Y%m%d')
        # if activiteitendatum < start_dbc or activiteitendatum > eind_dbc:
        #     meldingen.append('TIJDSCHRIJVEN: {} activiteitdatum ligt niet tussen begin en einddatum dbc'.format(self.__str__()))

        # Gevonden meldingen en bewerkingen teruggeven
        return {"bewerkingen": bewerkingen, "meldingen": meldingen}

