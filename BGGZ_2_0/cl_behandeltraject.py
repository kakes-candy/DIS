from Basis.cl_DIS_dataobject import DISdataObject
from BGGZ_2_0.definitions import format_behandeltraject


class Behandeltraject(DISdataObject):

    format_definitions = format_behandeltraject
    child_types = ["GeleverdZorgprofiel"]

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.valid = True

    # Nummer van behandeltraject tonen
    def show_link(self):
        return self._3257

    def add_parent(self, parent):
        if not self.parent:
            self.parent = parent
            # Koppelnummer is gelijk aan dat van de patient (parent)
            self._3258 = parent._3340

    # Methode om object te valideren
    def validate(self, autocorrect):
        meldingen = []
        bewerkingen = []

        # Een behandeltraject hoort alleen in de export als er verwante activiteiten zijn zijn.
        for type in self.child_types:
            if len(self.children[type]) < 1:
                self.valid = False
                meldingen.append(
                    "BEHANDELTRAJECT: {} heeft geen kinderen van het type {}".format(
                        self.__str__(), type
                    )
                )
        # En er moet een patient als parent zijn
        if not self.parent:
            self.valid = False
            meldingen.append(
                "BEHANDELTRAJECT: {} heeft geen ouder".format(self.__str__())
            )

        # Validatie 2227: 3272 Reden sluiten code bevat een andere code dan 12,13,15,17,21
        # bij 3333 Prestatiecode geleverd = 180005
        if self._3333 == "180005" and self._3272.strip(" ") not in (
            "12",
            "13",
            "15",
            "17",
            "21",
        ):
            self.valid = False
            meldingen.append(
                "BEHANDELTRAJECT: {traject} val 2227 verkeerde reden sluiten bij onvolledig behandeltraject {sluitreden}".format(
                    traject=self.__str__(), sluitreden=self._3272.strip(" ")
                )
            )

        if self._3272.strip(" ") == "14" and int(self._3262[:4]) > 2014:
            self.valid = False
            meldingen.append(
                "BEHANDELTRAJECT: {} sluitreden {} is niet geldig op startdatum ".format(
                    self.__str__(), self._3272.strip(" ")
                )
            )

        return {"bewerkingen": bewerkingen, "meldingen": meldingen}

