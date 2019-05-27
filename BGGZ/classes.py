from format_definitions import *
import datetime, re
import shutil, tempfile, os

"""
Klassen voor het opslaan en verwerken van DIS data
"""


# Moeder klas voor alle dis data elementen
class DISdataObject(object):

    # format_definitions is een lijst met DIS data specificaties
    format_definitions = None
    # attributen voor links met andere objecten
    child_types, parent_types = list(), list()

    def __init__(self, **kwargs):
        for definition in self.format_definitions:
            ID = "_{id}".format(id=definition["DDID"])
            setattr(self, ID, None)

        self.children = {child_type: dict() for child_type in self.child_types}
        self.parent = None

    def write_to_string(self):
        result = ""
        for definition in self.format_definitions:
            dis_id = "_" + str(definition["DDID"])
            raw_value = getattr(self, dis_id)
            if not raw_value:
                raw_value = ""
            result = result + raw_value.rjust(int(definition["Lengte"]), " ")
        return result

    def write_to_dict(self):
        result = {}
        for definition in self.format_definitions:
            dis_id = "_" + str(definition["DDID"])
            naam = str(definition["Naam"])
            raw_value = getattr(self, dis_id)
            if not raw_value:
                raw_value = ""
            result[naam] = raw_value
        return result

    @classmethod
    def from_string(cls, string):
        dictionary = {}
        for item in cls.format_definitions:
            key = "_{}".format(item.get("DDID"))
            begin, eind = int(item.get("Begin")), int(item.get("Eind"))
            dictionary[key] = string[begin - 1 : eind]
        return cls(**dictionary)

    @classmethod
    def from_list(cls, lijst):
        dictionary = {}
        for i, item in enumerate(lijst):
            dis_id = "_{}".format(cls.format_definitions[i].get("DDID"))
            dictionary[dis_id] = item
        return cls(**dictionary)

    def add_child(self, to, obj):
        if not self.children.get(to, dict()).get(obj.__str__()):
            self.children.get(to, dict())[obj.__str__()] = obj
        # Ook bij het kind self de parent maken
        obj.add_parent(self)

    def delete_child(self, to, object_key):
        try:
            del self.children.get(to)[object_key]
        except:
            pass

    def keys(self):
        return [
            "".join(["_", x["DDID"]])
            for x in self.format_definitions
            if "PK" in x["Sleutel"]
        ]

    def foreign_key(self):
        # Alle id's van elementen die als FK zijn aangemeld (zou er maar 1 moeten zijn)
        keys = [
            "_{}".format(x["DDID"])
            for x in self.format_definitions
            if "FK" in x["Sleutel"]
        ]
        if keys:
            return getattr(self, keys[0])

    def __str__(self):
        keys = [
            "_{}".format(x["DDID"])
            for x in self.format_definitions
            if "PK" in x["Sleutel"]
        ]
        values = []
        for key in keys:
            value = getattr(self, key)
            if value:
                values.append(value)
            else:
                values.append("")

        return "_".join(values)

    def __repr__(self):
        return self.__str__()

    def help(self):
        atts_of_interest = ["DDID", "Naam", "Lengte", "Patroon"]
        print("Dit dataobject heeft de volgende attributen:")
        for definition in self.format_definitions:
            l = [
                "{key}: {value}".format(key=item, value=definition[item])
                for item in atts_of_interest
            ]
            print(l)

    def verplichte_velden(self):
        keys = [
            "_{}".format(x["DDID"])
            for x in self.format_definitions
            if x["Verplicht"] == "V"
        ]
        values = {}
        for key in keys:
            values[key] = getattr(self, key)
        return values


class Patient(DISdataObject):

    format_definitions = format_patient
    child_types = ["Behandeltraject"]

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    # Koppelnummer tonen
    def show_link(self):
        return self._3340

    # Methode om object te valideren
    def validate(self):
        # start assuming object is valid
        valid = True
        meldingen = []

        # Een patient hoort alleen in de export als er verwante zorgtrajecten zijn.
        for type in self.child_types:
            if len(self.children[type]) < 1:
                valid = False
                meldingen.append(
                    "PATIENT: {} heeft geen kinderen van het type {}".format(
                        self.__str__(), type
                    )
                )

        # Zijn alle verpichte velden gevuld:
        velden = self.verplichte_velden()
        for key, value in velden.items():
            if value.replace(" ", "") == "":
                meldingen.append(
                    "PATIENT: {} verplicht veld {} niet gevuld".format(
                        self.__str__(), key
                    )
                )

        # postcode controleren
        pattern = pattern = "^[1-9][0-9]{3}[A-Z][A-Z]$"
        landcode = self._3338
        postcode = self._3242

        if (
            landcode.replace(" ", "") == "NL"
            and len(re.findall(pattern, postcode)) == 0
        ):
            meldingen.append(
                "PATIENT: {} geen geldige postcode {} bij landcode NL".format(
                    self.__str__(), postcode
                )
            )

        if len(meldingen) > 0:
            return "   ###   ".join(meldingen)
        else:
            return ()


class Behandeltraject(DISdataObject):

    format_definitions = format_behandeltraject
    child_types = ["GeleverdZorgprofiel"]

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    # Nummer van behandeltraject tonen
    def show_link(self):
        return self._3257

    def add_parent(self, parent):
        if not self.parent:
            self.parent = parent
            # Koppelnummer is gelijk aan dat van de patient (parent)
            self._3258 = parent._3340

    # Methode om object te valideren
    def validate(self):
        # start assuming object is valid
        valid = True
        meldingen = []

        # Een zorgtraject hoort alleen in de export als er verwante dbctrajecten zijn.
        for type in self.child_types:
            if len(self.children[type]) < 1:
                valid = False
                meldingen.append(
                    "BEHANDELTRAJECT: {} heeft geen kinderen van het type {}".format(
                        self.__str__(), type
                    )
                )
        # # En er moet een patient als parent zijn
        # if not self.parent:
        #     meldingen.append('BEHANDELTRAJECT: {} heeft geen ouder'.format(self.__str__()))

        # # validatie 566, begindatum zorgtraject > Einddatum
        # if datetime.datetime.strptime(self._1451, '%Y%m%d') > datetime.datetime.strptime(self._1452, '%Y%m%d'):
        #     meldingen.append('BEHANDELTRAJECT: {} startdatum > einddatum (val 566)'.format(self.__str__()))

        # # validatie 1330, diagnose dsm 4 is niet leeg tenzij kinderen allemaal sluitreden 5 of 20 hebben.
        # # lijst van sluitredenen
        # redenen = [ x._1470.strip(' ') for x in self.children['DBCTraject'].values() if  x._1470.strip(' ') not in ('5', '20')]
        # if self._1456.strip(' ') == '' and len(redenen) > 0:
        #     meldingen.append('ZORGTRAJECT: {} geen diagnose terwijl dbc traject niet sluitreden 5 of 20 (val 1330)'.format(self.__str__()))

        # # validatie 2292, diagnose dsm 5 is niet leeg tenzij kinderen allemaal sluitreden 5 of 20 hebben.
        # # lijst van sluitredenen
        # redenen = [ x._1470.strip(' ') for x in self.children['DBCTraject'].values() if  x._1470.strip(' ') not in ('5', '20')]
        # if self._1456.strip(' ') == '' and len(redenen) > 0:
        #     meldingen.append('ZORGTRAJECT: {} geen diagnose terwijl dbc traject niet sluitreden 5 of 20 (val 2292)'.format(self.__str__()))

        # # validatie 2067, primaire diagnose is niet as_1 of as_2 en niet leeg
        # if self._1456[:4] not in ('as1_', 'as2_', ) and self._1456.strip(' ') != '':
        #     meldingen.append('ZORGTRAJECT: {} diagnosecode niet as_1 of as_2 (val 2067)'.format(self.__str__()))

        if len(meldingen) > 0:
            return "   ###   ".join(meldingen)
        else:
            return ()


# class DBCTraject(DISdataObject):

#     format_definitions = format_dbctraject
#     child_types = ["Tijdschrijven", "Diagnose"]

#     def __init__(self, **kwargs):
#         super().__init__()
#         for key, value in kwargs.items():
#             setattr(self, key, value)

#     def show_link(self):
#         return self._1462

#     def add_parent(self, parent):
#         if not self.parent:
#             self.parent = parent
#             self._1464 = parent._1449

#     # Methode om object te valideren
#     def validate(self):
#         # start assuming object is valid
#         valid = True
#         meldingen = []


#         # Een zorgtraject hoort alleen in de export als er verwante dbctrajecten zijn.
#         for type in self.child_types:
#             if len(self.children[type]) < 1 and type != 'Diagnose':
#                 valid = False
#                 meldingen.append('DBCTRAJECT: {} heeft geen kinderen van het type {}'.format(self.__str__(), type))

#         # En er moet een patient als parent zijn
#         if not self.parent:
#             meldingen.append('DBCTRAJECT: {} heeft geen ouder'.format(self.__str__()))

#         start_dbc = datetime.datetime.strptime(self._1465, '%Y%m%d')
#         eind_dbc =  datetime.datetime.strptime(self._1466, '%Y%m%d')

#         # validatie 515, begindatum  > Einddatum
#         if start_dbc > eind_dbc:
#             meldingen.append('DBCTRAJECT: {} startdatum > einddatum (val 515)'.format(self.__str__()))

#         # validatie 1388, begindatum dbc eerder dan begindatum zorgtraject
#         if self.parent and start_dbc < datetime.datetime.strptime(self.parent._1451, '%Y%m%d'):
#             meldingen.append('DBCTRAJECT: {} startdatum dbc eerder dan startdatum zorgtraject (val 1388)'.format(self.__str__()))

#         # validatie 2124 duur dbc langer dan 365 dagen
#         if (eind_dbc - start_dbc).days >= 365:
#             meldingen.append('DBCTRAJECT: {} start en einddatum meer dan 365 dagen van elkaar (val 2124)'.format(self.__str__()))

#         # validatie 2083: er moet tenminste 1 hoofdbehandelaar Zijn
#         if self._4091.strip(' ') == '' and self._4092.strip(' ') == '':
#             meldingen.append('DBCTRAJECT: {} geen regie/hoofbehandelaars (val 2083)'.format(self.__str__()))

#         # validatie 2191: Beroepcode 1e hoofdbehandelaar ontrbreekt
#         if self._4091.strip(' ') != '' and self._4093.strip(' ') == '':
#             meldingen.append('DBCTRAJECT: {} Beroepcode 1e hoofdbehandelaar ontrbreekt (val 2191)'.format(self.__str__()))

#         # validatie 2200: Beroepcode 1e hoofdbehandelaar ontrbreekt
#         if self._4092.strip(' ') != '' and self._4094.strip(' ') == '':
#             meldingen.append('DBCTRAJECT: {} Beroepcode 2e hoofdbehandelaar ontrbreekt (val 2200)'.format(self.__str__()))

#         # validatie 2201: 4146 Verwijzer is niet gevuld terwijl 4095 Verwijstype/code(zelf)verwijzer is 01,02,03 of 04
#         if self._4146.strip(' ') == '' and self._4095 in ('01', '02', '03', '04'):
#             meldingen.append('DBCTRAJECT: {}  Verwijzer is niet gevuld terwijl 4095 Verwijstype/code(zelf)verwijzer is 01,02,03 of 04 (val 2201)'.format(self.__str__()))

#         # Validatie verkoopprijs
#         try:
#             bedrag = int(self._1471)
#         except:
#             meldingen.append('DBCTRAJECT: {}  verkoopprijs bevat geen geldige waarde (val 614)'.format(self.__str__()))
#         else:
#             if bedrag < 0:
#                 meldingen.append('DBCTRAJECT: {}  verkoopprijs lager dan 0 (val 1392)'.format(self.__str__()))

#         # validatie 2068: 1473 Productgroepcode (positie 4 t/m 6) komt niet overeen met het productgroepcodebehandeldeel positie (10 t/m 12) in 1474 Prestatiecode Productgroepcode (positie 4 t/m 6) komt niet overeen met het productgroepcodebehandeldeel positie (10 t/m 12) in 1474 Prestatiecode
#         if self._1473[-3:] != self._1474[-3:]:
#             meldingen.append('DBCTRAJECT: {}  productgroepcode {} klopt niet met prestatiecode {} (val 2068)'.format(self.__str__(), self._1473[:-3], self._1474[:-3]))

#         # Validatie DBC bedrag
#         try:
#             dbcbedrag = int(self._1476)
#         except:
#             meldingen.append('DBCTRAJECT: {}  DBC bedrag bevat geen geldige waarde (val 379)'.format(self.__str__()))
#         else:
#             if dbcbedrag < 0:
#                 meldingen.append('DBCTRAJECT: {}  DBC bedrag lager dan 0 (val 1396)'.format(self.__str__()))

#         # Validatie verrekenbedrag
#         try:
#             verrekenbedrag = int(self._1477)
#         except:
#             meldingen.append('DBCTRAJECT: {}  verrekenbedrag bevat geen geldige waarde (val 379)'.format(self.__str__()))
#         else:
#             if verrekenbedrag < 0:
#                 meldingen.append('DBCTRAJECT: {}  verrekenbedrag lager dan 0 (val 1396)'.format(self.__str__()))

#         if len(meldingen) > 0:
#             return('   ###   '.join(meldingen))
#         else:
#             return()


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
    def validate(self):
        # start assuming object is valid
        valid = True
        meldingen = []

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

        if len(meldingen) > 0:
            return "   ###   ".join(meldingen)
        else:
            return ()


class PakbonTekst(DISdataObject):

    format_definitions = format_pakbon

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)


# klas om alle Disobjecten vast te houden
class Aanlevering_BGGZ:

    def __init__(self, **kwargs):

        self.meldingen = []
        self.pakbon = None
        self.patienten = dict()
        self.behandeltrajecten = dict()
        self.zorgprofielen = dict()


    def add_pakbon(self, obj=None, **kwargs):
        if not obj:
            pb = PakbonTekst(**kwargs)
            self.pakbon = pb
        else: 
            self.pakbon = obj

    def add_patient(self, obj=None, **kwargs):
        if not obj:
            pt = Patient(**kwargs)
        else:
            pt = obj
        # Als de patient al bestaat, bestaande object teruggeven
        if pt.__str__() in self.patienten:
            self.meldingen.append("PATIENT: {} is niet uniek".format(pt.__str__()))
            return self.patienten[pt.__str__()]
        # Als de patient nog niet is ingelezen
        else:
            self.patienten[pt.__str__()] = pt
            return pt

    # Patient instantie verwijderen uit aanlevering
    def del_patient(self, patient_key):
            # De kinderen (behandeltrajecten) van de patient instantie moeten worden verwijderd
            kinderen = self.patienten[patient_key].children.get('Behandeltraject')
            if kinderen:
                for kind in list(kinderen.values()):
                    kind.parent = None
                    self.del_behandeltraject(kind.__str__())
            # dan de patient verwijderen 
            del self.patienten[patient_key]

    def add_behandeltraject(self, obj=None, **kwargs):
        if not obj:
            dbc = Behandeltraject(**kwargs)
        else:
            dbc = obj
        # Als het dbctraject al bestaat, bestaande object teruggeven
        if dbc.__str__() in self.behandeltrajecten:
            self.meldingen.append("BEHANDELTRAJECT: {} is niet uniek".format(dbc.__str__()))
            return self.behandeltrajecten[dbc.__str__()]
        # Als het dbctraject nog niet is ingelezen dan toevoegen aan pakbon lijst
        else:
            # parent zoeken, eerste uit lijst (lijst zou 1 lang moeten zijn)
            for key, value in self.patienten.items():
                if value.show_link() == dbc.foreign_key():
                    value.add_child("Behandeltraject", dbc)
                    break
            self.behandeltrajecten[dbc.__str__()] = dbc
            return dbc

    def del_behandeltraject(self, traject_key):
            traject = self.behandeltrajecten[traject_key]
            # De kinderen (behandeltrajecten) van de patient instantie moeten worden verwijderd
            kinderen = traject.children.get('GeleverdZorgprofiel')
            if kinderen:
                for kind in list(kinderen.values()):
                    kind.parent = None
                    self.del_zorgprofiel(kind.__str__())
            # Heeft het behandeltraject nog ouders?
            if traject.parent:
                # Als dit het enige kind is van de ouder, dan verwijderen
                if len(traject.parent.children.get('Behandeltraject', {})) == 1:
                    # voorkomen dat verwijderen patient ook weer gaat proberen dit behandeltraject te verwijderen
                    traject.parent.delete_child('Behandeltraject', traject_key)
                    self.del_patient(traject.parent.__str__())
            #  als laatste het behandeltraject zelf verwijderen
            del self.behandeltrajecten[traject_key]


    def add_zorgprofiel(self, obj=None, **kwargs):
        if not obj:
            ts = GeleverdZorgprofiel(**kwargs)
        else:
            ts = obj
        # Als de tijdrecord al bestaat, bestaande object teruggeven
        if ts.__str__() in self.zorgprofielen:
            self.meldingen.append(
                "GELEVERD ZORGPROFIEL: {} is niet uniek".format(ts.__str__())
            )
            return self.zorgprofielen[ts.__str__()]
        # Als het tijdschrijven nog niet is ingelezen
        else:
            # parent zoeken, eerste uit lijst (lijst zou 1 lang moeten zijn)
            for key, value in self.behandeltrajecten.items():
                if value.show_link() == ts.foreign_key():
                    value.add_child("GeleverdZorgprofiel", ts)
                    break
            self.zorgprofielen[ts.__str__()] = ts
        return ts

    def del_zorgprofiel(self, tijd_key):
        zorgprofiel = self.zorgprofielen[tijd_key]
        # Heeft het zorgprofiel nog een ouder?
        if zorgprofiel.parent:
        # Als dit het laatste kind is van een ouder, dan verwijderen
            if len(zorgprofiel.parent.children.get('GeleverdZorgprofiel', {})) == 1:
                # voorkomen dat verwijderen patient ook weer gaat proberen dit behandeltraject te verwijderen
                zorgprofiel.parent.delete_child('GeleverdZorgprofiel', tijd_key)
                self.del_behandeltraject(zorgprofiel.parent.__str__())
        #  als laatste het behandeltraject zelf verwijderen
        del self.zorgprofielen[tijd_key]

    def validate(self):
        '''
        Valideert alle elementen in de aanlevering
        ''' 
        results = []
        for patient in self.patienten.values():
            res = patient.validate()
            if res:
                results.append(res)
        for traject in self.behandeltrajecten.values():
            res = traject.validate()
            if res:
                results.append(res)        
        for profiel in self.zorgprofielen.values():
            res = profiel.validate()
            if res:
                results.append(res)  

    def aanlevering_exporteren(self, doelmap, volgnummer = None):
        """   
        exporteert een aanlevering naar een DIS geformatteerd zip bestand

        :param doelmap: map waar het zipbestand wordt opgeslagen
        :type doelmap: str
        :param volgnummer: volgnummer dat gewenst is voor de aanlevering
        :type volgnummer: str
        """

        bestandsnaam = self.pakbon._3344
        bestandsnaam_algemeen = bestandsnaam[:32]
        creatiedatum = self.pakbon._3233
        volgnummer_origineel = self.pakbon._3234
        extensie = ".zip"

        # volgnummer ophogen
        if volgnummer:
            self.pakbon._3234 = str(volgnummer).zfill(2)

        # bestandsnaam aanpassen met opgehoogd volgnummer
        nieuwe_bestandsnaam = "_".join([bestandsnaam_algemeen, creatiedatum, self.pakbon._3234])
        self.pakbon._3344 = nieuwe_bestandsnaam + extensie


        # Aantal clienten, behandeltrajecten etc bijwerken
        self.pakbon._3239 = str(len(self.patienten))
        self.pakbon._3345 = str(len(self.behandeltrajecten))
        self.pakbon._3245 = str(len(self.zorgprofielen))


        with tempfile.TemporaryDirectory() as tijdelijk:
            # patientgegevens wegschrijven
            with open(os.path.join(tijdelijk, 'PATIENT.txt'), 'w') as f_pat:
                for patient in self.patienten.values():
                    f_pat.write(patient.write_to_string() + '\n')
            
            # Behandeltraject wegschrijven
            with open(os.path.join(tijdelijk, 'BEHANDELTRAJECT.txt'), 'w') as f_beh:
                for behandel in self.behandeltrajecten.values():
                    f_beh.write(behandel.write_to_string() + '\n')            

            # Zorgprofiel wegschrijven
            with open(os.path.join(tijdelijk, 'GELEVERD_ZORGPROFIEL.txt'), 'w') as f_profiel:
                for profiel in self.zorgprofielen.values():
                    f_profiel.write(profiel.write_to_string() + '\n')     

            # Zorgprofiel wegschrijven
            with open(os.path.join(tijdelijk, 'PAKBON.txt'), 'w') as f_pakbon:
                f_pakbon.write(self.pakbon.write_to_string() + '\n')

            # Zorgprofiel wegschrijven
            with open(os.path.join(tijdelijk, 'OVERIGE_VERRICHTING.txt'), 'w') as f_profiel:
                pass         

            # Nieuw zipbestand maken met de juiste naam
            shutil.make_archive(os.path.join(doelmap, nieuwe_bestandsnaam),
                "zip",
                tijdelijk)