from Basis.cl_DIS_dataobject import DISdataObject
from SGGZ_9_0.definitions import format_diagnose
import datetime


class Diagnose(DISdataObject):

    format_definitions = format_diagnose
    child_types = []

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.valid = True

    def add_parent(self, parent):
        if not self.parent:
            self.parent = parent
            self._1481 = parent._1462

    # Methode om object te valideren
    def validate(self, autocorrect):
        # start assuming object is valid
        meldingen = []
        bewerkingen = []

        # En er moet een patient als parent zijn
        if not self.parent:
            meldingen.append("DIAGNOSE: {} heeft geen ouder".format(self.__str__()))
            self.valid = False

        # Validatie 2133: diagnosedatum na einddatum dbcbedrag
        eind_dbc = datetime.datetime.strptime(self.parent._1466, "%Y%m%d")
        diagnosedatum = datetime.datetime.strptime(self._1482, "%Y%m%d")
        if diagnosedatum > eind_dbc:
            meldingen.append(
                "DIAGNOSE: {} diagnosedatum > eind DBC (val 2133)".format(
                    self.__str__()
                )
            )
            self.valid = False

        # 5121 Nevendiagnosehoofdgroep komt niet voor of is niet (meer) geldig in de codelijst Diagnose	2318
        if self._5121 not in (
            "001",
            "002",
            "003",
            "004",
            "005",
            "006",
            "007",
            "008",
            "009",
            "010",
            "011",
            "012",
            "013",
            "014",
            "015",
            "016",
            "017",
        ):
            meldingen.append(
                "DIAGNOSE: {} nevendiagnosehoofdgroep niet geldig (val 2318)".format(
                    self.__str__()
                )
            )
            self.valid = False

        return {"bewerkingen": bewerkingen, "meldingen": meldingen}

