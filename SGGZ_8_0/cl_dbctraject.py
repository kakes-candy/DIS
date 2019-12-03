from Basis.cl_DIS_dataobject import DISdataObject
from SGGZ_8_0.definitions import format_dbctraject
import datetime


class DBCTraject(DISdataObject):

    format_definitions = format_dbctraject
    child_types = ["Tijdschrijven", "Diagnose"]

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.valid = True

    def show_link(self):
        return self._1462

    def add_parent(self, parent):
        if not self.parent:
            self.parent = parent
            self._1464 = parent._1449

    # Methode om object te valideren
    def validate(self, autocorrect):
        # plek om validatiemeldingen en evt correcties in op te slaan.
        meldingen = []
        bewerkingen = []

        # Een zorgtraject hoort alleen in de export als er verwante dbctrajecten zijn.
        for type in self.child_types:
            if len(self.children[type]) < 1 and type != "Diagnose":
                valid = False
                meldingen.append(
                    "DBCTRAJECT: {} heeft geen kinderen van het type {}".format(
                        self.__str__(), type
                    )
                )

        # En er moet een patient als parent zijn
        if not self.parent:
            meldingen.append("DBCTRAJECT: {} heeft geen ouder".format(self.__str__()))

        start_dbc = datetime.datetime.strptime(self._1465, "%Y%m%d")
        eind_dbc = datetime.datetime.strptime(self._1466, "%Y%m%d")

        # validatie 515, begindatum  > Einddatum
        if start_dbc > eind_dbc:
            meldingen.append(
                "DBCTRAJECT: {} startdatum > einddatum (val 515)".format(self.__str__())
            )

        # validatie 1388, begindatum dbc eerder dan begindatum zorgtraject
        if self.parent and start_dbc < datetime.datetime.strptime(
            self.parent._1451, "%Y%m%d"
        ):
            meldingen.append(
                "DBCTRAJECT: {} startdatum dbc eerder dan startdatum zorgtraject (val 1388)".format(
                    self.__str__()
                )
            )

        # validatie 2124 duur dbc langer dan 365 dagen
        if (eind_dbc - start_dbc).days >= 365:
            meldingen.append(
                "DBCTRAJECT: {} start en einddatum meer dan 365 dagen van elkaar (val 2124)".format(
                    self.__str__()
                )
            )

        # validatie 2083: er moet tenminste 1 hoofdbehandelaar Zijn
        if self._4091.strip(" ") == "" and self._4092.strip(" ") == "":
            meldingen.append(
                "DBCTRAJECT: {} geen regie/hoofbehandelaars (val 2083)".format(
                    self.__str__()
                )
            )

        # validatie 2191: Beroepcode 1e hoofdbehandelaar ontrbreekt
        if self._4091.strip(" ") != "" and self._4093.strip(" ") == "":
            meldingen.append(
                "DBCTRAJECT: {} Beroepcode 1e hoofdbehandelaar ontrbreekt (val 2191)".format(
                    self.__str__()
                )
            )

        # validatie 2200: Beroepcode 1e hoofdbehandelaar ontrbreekt
        if self._4092.strip(" ") != "" and self._4094.strip(" ") == "":
            meldingen.append(
                "DBCTRAJECT: {} Beroepcode 2e hoofdbehandelaar ontrbreekt (val 2200)".format(
                    self.__str__()
                )
            )

        # validatie 2201: 4146 Verwijzer is niet gevuld terwijl 4095 Verwijstype/code(zelf)verwijzer is 01,02,03 of 04
        if self._4146.strip(" ") == "" and self._4095 in ("01", "02", "03", "04"):
            meldingen.append(
                "DBCTRAJECT: {}  Verwijzer is niet gevuld terwijl 4095 Verwijstype/code(zelf)verwijzer is 01,02,03 of 04 (val 2201)".format(
                    self.__str__()
                )
            )

        # Validatie verkoopprijs
        try:
            bedrag = int(self._1471)
        except:
            meldingen.append(
                "DBCTRAJECT: {}  verkoopprijs bevat geen geldige waarde (val 614)".format(
                    self.__str__()
                )
            )
        else:
            if bedrag < 0:
                meldingen.append(
                    "DBCTRAJECT: {}  verkoopprijs lager dan 0 (val 1392)".format(
                        self.__str__()
                    )
                )

        # validatie 2068: 1473 Productgroepcode (positie 4 t/m 6) komt niet overeen met het productgroepcodebehandeldeel positie (10 t/m 12) in 1474 Prestatiecode Productgroepcode (positie 4 t/m 6) komt niet overeen met het productgroepcodebehandeldeel positie (10 t/m 12) in 1474 Prestatiecode
        if self._1473[-3:] != self._1474[-3:]:
            meldingen.append(
                "DBCTRAJECT: {}  productgroepcode {} klopt niet met prestatiecode {} (val 2068)".format(
                    self.__str__(), self._1473[:-3], self._1474[:-3]
                )
            )

        # Validatie DBC bedrag
        try:
            dbcbedrag = int(self._1476)
        except:
            meldingen.append(
                "DBCTRAJECT: {}  DBC bedrag bevat geen geldige waarde (val 379)".format(
                    self.__str__()
                )
            )
        else:
            if dbcbedrag < 0:
                meldingen.append(
                    "DBCTRAJECT: {}  DBC bedrag lager dan 0 (val 1396)".format(
                        self.__str__()
                    )
                )

        # Validatie verrekenbedrag
        try:
            verrekenbedrag = int(self._1477)
        except:
            meldingen.append(
                "DBCTRAJECT: {}  verrekenbedrag bevat geen geldige waarde (val 379)".format(
                    self.__str__()
                )
            )
        else:
            if verrekenbedrag < 0:
                meldingen.append(
                    "DBCTRAJECT: {}  verrekenbedrag lager dan 0 (val 1396)".format(
                        self.__str__()
                    )
                )

        return {"bewerkingen": bewerkingen, "meldingen": meldingen}

