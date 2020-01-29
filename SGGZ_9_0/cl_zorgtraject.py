from Basis.cl_DIS_dataobject import DISdataObject
from SGGZ_9_0.definitions import format_zorgtraject
import datetime


class Zorgtraject(DISdataObject):

    format_definitions = format_zorgtraject
    child_types = ["DBCTraject"]

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.valid = True

    def show_link(self):
        return self._1449

    def add_parent(self, parent):
        if not self.parent:
            self.parent = parent
            self._1453 = parent._1432

    # Methode om object te valideren
    def validate(self, autocorrect):

        meldingen = []
        bewerkingen = []

        # Een zorgtraject hoort alleen in de export als er verwante dbctrajecten zijn.
        for type in self.child_types:
            if len(self.children[type]) < 1:
                self.valid = False
                meldingen.append(
                    "ZORGTRAJECT: {} heeft geen kinderen van het type {}".format(
                        self.__str__(), type
                    )
                )
        # En er moet een patient als parent zijn
        if not self.parent:
            meldingen.append("ZORGTRAJECT: {} heeft geen ouder".format(self.__str__()))
            self.valid = False

        # validatie 566, begindatum zorgtraject > Einddatum
        if datetime.datetime.strptime(
            self._1451, "%Y%m%d"
        ) > datetime.datetime.strptime(self._1452, "%Y%m%d"):
            self.valid = False
            meldingen.append(
                "ZORGTRAJECT: {} startdatum > einddatum (val 566)".format(
                    self.__str__()
                )
            )

        # validatie 2313, diagnose dsm 4 is niet leeg tenzij kinderen allemaal sluitreden 5 of 20 hebben.
        # lijst van sluitredenen
        redenen = [
            x._1470.strip(" ")
            for x in self.children["DBCTraject"].values()
            if x._1470.strip(" ") not in ("5", "20")
        ]
        if self._5119.strip(" ") == "" and len(redenen) > 0:
            self.valid = False
            meldingen.append(
                "ZORGTRAJECT: {} geen diagnose terwijl dbc traject niet sluitreden 5 of 20 (val 2313)".format(
                    self.__str__()
                )
            )

        # 5119 Diagnosehoofdgroep komt niet voor of is niet (meer) geldig in codelijst Diagnose	(2314)
        if (self._5119.strip(" ") != "") and self._5119 not in (
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
            self.valid = False
            meldingen.append(
                "ZORGTRAJECT: {} nevendiagnosehoofdgroep niet geldig (val 2314)".format(
                    self.__str__()
                )
            )

        # Gevonden meldingen en bewerkingen teruggeven
        return {"bewerkingen": bewerkingen, "meldingen": meldingen}
