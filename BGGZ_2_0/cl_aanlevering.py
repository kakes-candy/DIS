import shutil, tempfile, os
from csv import DictWriter

from BGGZ_2_0.cl_patient import Patient
from BGGZ_2_0.cl_behandeltraject import Behandeltraject
from BGGZ_2_0.cl_zorgprofiel import GeleverdZorgprofiel
from BGGZ_2_0.cl_pakbon import PakbonTekst


# klas om alle Disobjecten vast te houden
class Aanlevering_BGGZ:

    def __init__(self, **kwargs):

        self.meldingen = []
        self.bewerkingen = []
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
            self.bewerkingen.append("PATIENT: {} niet uniek, niet geimporteerd".format(pt.__str__()))
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
            self.bewerkingen.append("PATIENT: {} verwijderd".format(patient_key))

    def add_behandeltraject(self, obj=None, **kwargs):
        if not obj:
            dbc = Behandeltraject(**kwargs)
        else:
            dbc = obj
        # Als het dbctraject al bestaat, bestaande object teruggeven
        if dbc.__str__() in self.behandeltrajecten:
            self.meldingen.append("BEHANDELTRAJECT: {} is niet uniek".format(dbc.__str__()))
            self.bewerkingen.append("BEHANDELTRAJECT: {} niet uniek, niet geimporteerd".format(dbc.__str__()))
            return self.behandeltrajecten[dbc.__str__()]
        # Als het dbctraject nog niet is ingelezen dan toevoegen aan pakbon lijst
        else:
            # parent zoeken, eerste uit lijst (lijst zou 1 lang moeten zijn)
            for value in self.patienten.values():
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
            self.bewerkingen.append("BEHANDELTRAJECT: {} verwijderd".format(traject_key))


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
            self.bewerkingen.append(
                "GELEVERD ZORGPROFIEL: {}niet uniek, niet geimporteerd".format(ts.__str__())
            )
            return self.zorgprofielen[ts.__str__()]
        # Als het tijdschrijven nog niet is ingelezen
        else:
            # parent zoeken, eerste uit lijst (lijst zou 1 lang moeten zijn)
            for value in self.behandeltrajecten.values():
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
        self.bewerkingen.append("GELEVERD ZORGPROFIEL: {} verwijderd".format(tijd_key))

    def inlezen_vanuit_map(self, pad): 
        ''' 
        Aanlevering inlezen vanuit map
        :param map: map waar de bestanden van de aanleverin staan
        :type map: str
        ''' 
                
        with open(os.path.join(pad, "PAKBON.txt"), "r") as f_pakbon:
            p = f_pakbon.readline()
            self.add_pakbon(PakbonTekst.from_string(p))

        with open(os.path.join(pad, "PATIENT.txt"), "r") as f_patient:
            for line in f_patient:
                self.add_patient(Patient.from_string(line))

        with open(os.path.join(pad, "BEHANDELTRAJECT.txt"), "r") as f_behandeltraject:
            for line in f_behandeltraject:
                self.add_behandeltraject(Behandeltraject.from_string(line))

        with open(os.path.join(pad, "GELEVERD_ZORGPROFIEL.txt"), "r") as f_zorgprofiel:
            for line in f_zorgprofiel:
                self.add_zorgprofiel(GeleverdZorgprofiel.from_string(line))

    def inlezen_vanuit_zip(self, bestand):
        '''
        Zip bestand met DIS aanlevering inlezen in aanlevering
        '''

        with tempfile.TemporaryDirectory() as tijdelijk:
            shutil.unpack_archive(bestand, tijdelijk)
            self.inlezen_vanuit_map(tijdelijk)


    def validate(self, autocorrect):
        '''
        Valideert alle elementen in de aanlevering en 
        voegt resultaten toe aan aanlevering.meldingen
        ''' 
        for patient in self.patienten.values():
            res = patient.validate(autocorrect = autocorrect)
            self.bewerkingen.extend(res['bewerkingen'])
            self.meldingen.extend(res['meldingen'])
        for traject in self.behandeltrajecten.values():
            res = traject.validate(autocorrect = autocorrect)
            self.bewerkingen.extend(res['bewerkingen'])
            self.meldingen.extend(res['meldingen'])      
        for profiel in self.zorgprofielen.values():
            res = profiel.validate(autocorrect = autocorrect)
            self.bewerkingen.extend(res['bewerkingen'])
            self.meldingen.extend(res['meldingen'])

    def exporteren_zip(self, doelmap, volgnummer = None):
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
        
        with open(os.path.join(doelmap, 'meldingen.txt'), 'w') as f_meldingen: 
            f_meldingen.writelines([x + '\n' for x in self.meldingen])
        with open(os.path.join(doelmap, 'bewerkingen.txt'), 'w') as f_bewerkingen: 
            f_bewerkingen.writelines([x + '\n' for x in self.bewerkingen])

    def exporteren_csv(self, doelmap):

        def write_objects_csv(pad, objects, headers):
            with open(pad, 'w', newline = "") as outfile:
                writer = DictWriter(outfile, delimiter=";", fieldnames=headers)
                writer.writeheader()
                for obj in objects:
                    writer.writerow(obj.write_to_dict())
  
        # Pakbon
        headers_pakbon = [x["Naam"] for x in PakbonTekst.format_definitions]
        write_objects_csv(os.path.join(doelmap, 'pakbon.csv'), [self.pakbon], headers_pakbon)
            
        # Patient
        headers_patient = [x["Naam"] for x in Patient().format_definitions]
        write_objects_csv(os.path.join(doelmap, 'patient.csv'), self.patienten.values(), headers_patient)

        # Behandeltraject
        headers_behandeltraject = [x["Naam"] for x in Behandeltraject().format_definitions]
        write_objects_csv(os.path.join(doelmap, 'behandeltrajecten.csv'), self.behandeltrajecten.values(), headers_behandeltraject)

        headers_zorgprofiel = [x["Naam"] for x in GeleverdZorgprofiel().format_definitions]
        write_objects_csv(os.path.join(doelmap, 'zorgprofielen.csv'), self.zorgprofielen.values(), headers_zorgprofiel)  