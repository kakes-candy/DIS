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

        # Validatie 2116: 1483 Diagnosecode is gelijk aan 1456 Primaire diagnosecode
        if self._1483 == self.parent.parent._1456:
            meldingen.append(
                "DIAGNOSE: {} nevendiagnose is gelijk aan primaire diagnose".format(
                    self.__str__()
                )
            )
            self.valid = False

        # Validatie 2308: 4167 Diagnosecode DSM-5 is niet gevuld terwijl 1483 Diagnosecode <> as1_18.02 of as1_18.03 of as2_18.02 of as2_18.03 of as4_110.
        if self._4167.strip(" ") == "" and self._1483.strip(" ") not in (
            "as1_18.02" "as1_18.03",
            "as2_18.02",
            "as2_18.03",
            "as4_110",
        ):
            meldingen.append(
                "DIAGNOSE: {} er had een dsm 5 code moeten staan (val 2308)".format(
                    self.__str__()
                )
            )
            self.valid = False

        # Validatie 2288: 4167 Diagnosecode DSM-5 komt niet voor of is niet (meer) geldig in codelijst Diagnose DSM-5.
        if self._4167.strip(" ") == "GeenDiagnose":
            meldingen.append(
                "DIAGNOSE: {} val(2288) 4167 Diagnosecode DSM-5 komt niet voor of is niet (meer) geldig in codelijst Diagnose DSM-5".format(
                    self.__str__()
                )
            )
            self.valid = False

        # Validatie 2290: 4167 Diagnosecode DSM-5 is niet gevuld terwijl 1483 Diagnosecode <> as1_18.02 of as1_18.03 of as2_18.02 of as2_18.03 of as4_110.
        if self._4167.strip(" ") == "" and self._1483.strip(" ") not in (
            "as1_18.02" "as1_18.03",
            "as2_18.02",
            "as2_18.03",
            "as4_110",
        ):
            meldingen.append(
                "DIAGNOSE: {} er had een dsm 5 code moeten staan (val 2308)".format(
                    self.__str__()
                )
            )
            self.valid = False

        return {"bewerkingen": bewerkingen, "meldingen": meldingen}

