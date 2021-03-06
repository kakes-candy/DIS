from Basis.cl_DIS_dataobject import DISdataObject
from BGGZ_2_0.definitions import format_patient
import re


class Patient(DISdataObject):

    format_definitions = format_patient
    child_types = ["Behandeltraject"]

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.valid = True

    # Koppelnummer tonen
    def show_link(self):
        return self._3340

    # Methode om object te valideren
    def validate(self, autocorrect):

        meldingen = []
        bewerkingen = []

        # Een patient hoort alleen in de export als er verwante zorgtrajecten zijn.
        for type in self.child_types:
            if len(self.children[type]) < 1:
                meldingen.append(
                    "PATIENT: {} heeft geen kinderen van het type {}".format(
                        self.__str__(), type
                    )
                )
                self.valid = False

        # Zijn alle verpichte velden gevuld:
        velden = self.verplichte_velden()
        for key, value in velden.items():
            if value.replace(" ", "") == "":
                meldingen.append(
                    "PATIENT: {} verplicht veld {} niet gevuld".format(
                        self.__str__(), key
                    )
                )
                self.valid = False

        # postcode controleren
        pattern_NL = "^[1-9][0-9]{3}[A-Z][A-Z]$"
        pattern_DE = "^[1-9][0-9]{4}$"
        pattern_BE = "^[1-9][0-9]{3}$"
        landcode = self._3338
        postcode = self._3242.replace(" ", "")

        if (
            landcode.replace(" ", "") == "NL"
            and len(re.findall(pattern_NL, postcode)) == 0
        ):
            melding = "PATIENT: {} geen geldige postcode {} bij landcode NL".format(
                self.__str__(), postcode
            )
            self.valid = False

            # Kijken of we het patroon van Duitse of Belgische postcodes herkennen en eventueel
            # automatisch de landcode corrigeren
            if autocorrect == True:
                if len(re.findall(pattern_DE, postcode)) == 1:
                    self._3338 = "DE"
                    bewerkingen.append(
                        "PATIENT: {} landcode naar DE gezet voor postcode {}".format(
                            self.__str__(), postcode
                        )
                    )
                    self.valid = True
                elif len(re.findall(pattern_BE, postcode)) == 1:
                    self._3338 = "BE"
                    bewerkingen.append(
                        "PATIENT: {} landcode naar BE gezet voor postcode {}".format(
                            self.__str__(), postcode
                        )
                    )
                    self.valid = True
                else:
                    meldingen.append(melding)
            else:
                meldingen.append(melding)

        # Gevonden meldingen en bewerkingen teruggeven
        return {"bewerkingen": bewerkingen, "meldingen": meldingen}
