import shutil, tempfile, os
from csv import DictWriter


from SGGZ_9_0.cl_pakbon import PakbonTekst
from SGGZ_9_0.cl_patient import Patient
from SGGZ_9_0.cl_zorgtraject import Zorgtraject
from SGGZ_9_0.cl_dbctraject import DBCTraject
from SGGZ_9_0.cl_tijdschrijven import Tijdschrijven
from SGGZ_9_0.cl_diagnose import Diagnose


# klas om alle Disobjecten vast te houden
class Aanlevering_SGGZ:

    def __init__(self, **kwargs):

        self.meldingen = []
        self.bewerkingen = []
        self.pakbon = None
        self.patienten = dict()
        self.zorgtrajecten = dict()
        self.dbctrajecten = dict()
        self.diagnoses =dict()
        self.tijdschrijven = dict()



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
            kinderen = self.patienten[patient_key].children.get('Zorgtraject')
            if kinderen:
                for kind in list(kinderen.values()):
                    kind.parent = None
                    self.del_dbctraject(kind.__str__())
            # dan de patient verwijderen 
            del self.patienten[patient_key]
            self.bewerkingen.append("PATIENT: {} verwijderd".format(patient_key))


    def add_zorgtraject(self, obj=None, **kwargs):
        if not obj:
            zt= Zorgtraject(**kwargs)
        else:
            zt = obj
        # Als het zorgtraject al bestaat, bestaande object teruggeven
        if zt.__str__() in self.zorgtrajecten:
            self.meldingen.append('ZORGTRAJECT: {} is niet uniek'.format(zt.__str__()))
            self.bewerkingen.append("ZORGTRAJECT: {} niet uniek, niet geimporteerd".format(zt.__str__()))
            return(self.zorgtrajecten[zt.__str__()])
        # Als de patient nog niet is ingelezen
        else:
            # parent zoeken, eerste uit lijst (lijst zou 1 lang moeten zijn)
            for value in self.patienten.values():
                if value.show_link() == zt.foreign_key():
                    value.add_child('Zorgtraject', zt)
                    break
            # zorgtraject aan pakbon toevoegen en teller ophogen
            self.zorgtrajecten[zt.__str__()] = zt
            return zt

    def del_zorgtraject(self, zorgtraject_key):
            zt = self.zorgtrajecten[zorgtraject_key]
            # De kinderen (dbc trajecten) van de instantie moeten worden verwijderd
            kinderen = zt.children.get('DBCTraject')
            if kinderen:
                for kind in list(kinderen.values()):
                    kind.parent = None
                    self.del_dbctraject(kind.__str__())
            # Heeft het zorgtraject nog ouders?
            if zt.parent:
                # Als dit het enige kind is van de ouder, dan verwijderen
                if len(zt.parent.children.get('Zorgtraject', {})) == 1:
                    # voorkomen dat verwijderen patient ook weer gaat proberen dit zorgtraject te verwijderen
                    zt.parent.delete_child('Zorgtraject', zorgtraject_key)
                    self.del_patient(zt.parent.__str__())
            #  als laatste het zorgtraject zelf verwijderen
            del self.zorgtrajecten[zorgtraject_key]
            self.bewerkingen.append("ZORGTRAJECT: {} verwijderd".format(zorgtraject_key))


    def add_dbctraject(self, obj=None, **kwargs):
        if not obj:
            dbc = DBCTraject(**kwargs)
        else:
            dbc = obj
        # Als het dbctraject al bestaat, bestaande object teruggeven
        if dbc.__str__() in self.dbctrajecten:
            self.meldingen.append("DBCTRAJECT: {} is niet uniek".format(dbc.__str__()))
            self.bewerkingen.append("DBCTRAJECT: {} niet uniek, niet geimporteerd".format(dbc.__str__()))
            return self.dbctrajecten[dbc.__str__()]
        # Als het dbctraject nog niet is ingelezen dan toevoegen aan pakbon lijst
        else:
            # parent zoeken, eerste uit lijst (lijst zou 1 lang moeten zijn)
            for value in self.zorgtrajecten.values():
                if value.show_link() == dbc.foreign_key():
                    value.add_child("DBCTraject", dbc)
                    break
            self.dbctrajecten[dbc.__str__()] = dbc
            return dbc

    def del_dbctraject(self, traject_key):
            dbc = self.dbctrajecten[traject_key]
            # De kinderen (diagnoses en tijdschrijven) van de patient instantie moeten worden verwijderd
            kinderen_tijd = dbc.children.get('Tijdschrijven')
            if kinderen_tijd:
                for kind in list(kinderen_tijd.values()):
                    kind.parent = None
                    self.del_tijdschrijven(kind.__str__())
            kinderen_diagnose = dbc.children.get('Diagnose')
            if kinderen_diagnose:
                for kind in list(kinderen_diagnose.values()):
                    kind.parent = None
                    self.del_diagnose(kind.__str__())                    
            # Heeft het behandeltraject nog ouders?
            if dbc.parent:
                # Als dit het enige kind is van de ouder, dan verwijderen
                if len(dbc.parent.children.get('DBCTraject', {})) == 1:
                    # voorkomen dat verwijderen patient ook weer gaat proberen dit behandeltraject te verwijderen
                    dbc.parent.delete_child('DBCTraject', traject_key)
                    self.del_zorgtraject(dbc.parent.__str__())
            #  als laatste het behandeltraject zelf verwijderen
            del self.dbctrajecten[traject_key]
            self.bewerkingen.append("BEHANDELTRAJECT: {} verwijderd".format(traject_key))


    def add_tijdschrijven(self, obj=None, **kwargs):
        if not obj:
            ts = Tijdschrijven(**kwargs)
        else:
            ts = obj
        # Als de tijdrecord al bestaat, bestaande object teruggeven
        if ts.__str__() in self.tijdschrijven:
            self.meldingen.append(
                "TIJDSCHRIJVEN: {} is niet uniek".format(ts.__str__())
            )
            self.bewerkingen.append(
                "TIJDSCHRIJVEN: {} niet uniek, niet geimporteerd".format(ts.__str__())
            )
            return self.tijdschrijven[ts.__str__()]
        # Als het tijdschrijven nog niet is ingelezen
        else:
            # parent zoeken, eerste uit lijst (lijst zou 1 lang moeten zijn)
            for value in self.dbctrajecten.values():
                if value.show_link() == ts.foreign_key():
                    value.add_child("Tijdschrijven", ts)
                    break
            self.tijdschrijven[ts.__str__()] = ts
        return ts

    def del_tijdschrijven(self, tijd_key):
        ts = self.tijdschrijven[tijd_key]
        # Heeft het zorgprofiel nog een ouder?
        if ts.parent:
        # Als dit het laatste kind is van een ouder, dan verwijderen
            if len(ts.parent.children.get('Tijdschrijven', {})) == 1:
                # voorkomen dat verwijderen patient ook weer gaat proberen dit behandeltraject te verwijderen
                ts.parent.delete_child('Tijdschrijven', tijd_key)
                self.del_dbctraject(ts.parent.__str__())
        #  als laatste het behandeltraject zelf verwijderen
        del self.tijdschrijven[tijd_key]
        self.bewerkingen.append("TIJDSCHRIJVEN: {} verwijderd".format(tijd_key))


    def add_diagnose(self, obj=None, **kwargs):
        if not obj:
            diagnose = Diagnose(**kwargs)
        else:
            diagnose = obj
        # Als de tijdrecord al bestaat, bestaande object teruggeven
        if diagnose.__str__() in self.diagnoses:
            self.meldingen.append(
                "DIAGNOSE: {} is niet uniek".format(diagnose.__str__())
            )
            self.bewerkingen.append(
                "DIAGNOSE: {}niet uniek, niet geimporteerd".format(diagnose.__str__())
            )
            return self.diagnoses[diagnose.__str__()]
        # Als het tijdschrijven nog niet is ingelezen
        else:
            # parent zoeken, eerste uit lijst (lijst zou 1 lang moeten zijn)
            for value in self.dbctrajecten.values():
                if value.show_link() == diagnose.foreign_key():
                    value.add_child("Diagnose", diagnose)
                    break
            self.diagnoses[diagnose.__str__()] = diagnose
        return diagnose

    def del_diagnose(self, diagnose_key):
        diagnose = self.diagnoses[diagnose_key]
        # DBC trajecten zonder nevendiagnoses kunnen, dus check of dit het laatste kind is niet nodig 
        del self.diagnoses[diagnose_key]
        self.bewerkingen.append("DIAGNOSE: {} verwijderd".format(diagnose_key))



    def inlezen_vanuit_map(self, pad): 
        ''' 
        Aanlevering inlezen vanuit map
        :param map: map waar de bestanden van de aanleverin staan
        :type map: str
        ''' 
                
        with open(os.path.join(pad, "pakbon.txt"), "r") as f_pakbon:
            p = f_pakbon.readline()
            self.add_pakbon(PakbonTekst.from_string(p))

        with open(os.path.join(pad, "patient.txt"), "r") as f_patient:
            for line in f_patient:
                self.add_patient(Patient.from_string(line))

        with open(os.path.join(pad, "zorgtraject.txt"), "r") as f_zorgtraject:
            for line in f_zorgtraject:
                self.add_zorgtraject(Zorgtraject.from_string(line))

        with open(os.path.join(pad, "dbc_traject.txt"), "r") as f_dbctraject:
            for line in f_dbctraject:
                self.add_dbctraject(DBCTraject.from_string(line))

        with open(os.path.join(pad, "geleverd_zorgprofiel_tijdschrijven.txt"), "r") as f_tijdschrijven:
            for line in f_tijdschrijven:
                self.add_tijdschrijven(Tijdschrijven.from_string(line))

        with open(os.path.join(pad, "diagnose.txt"), "r") as f_diagnose:
            for line in f_diagnose:
                self.add_diagnose(Diagnose.from_string(line))

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
        # TODO: onnodige herhaling verwijderen door alle te valideren objecten aan lijst toe te 
        # voegen en dan in 1 keer valideren
        for patient in self.patienten.values():
            res = patient.validate(autocorrect = autocorrect)
            self.bewerkingen.extend(res['bewerkingen'])
            self.meldingen.extend(res['meldingen'])
        for zt in self.zorgtrajecten.values():
            res = zt.validate(autocorrect = autocorrect)
            self.bewerkingen.extend(res['bewerkingen'])
            self.meldingen.extend(res['meldingen'])  
        for traject in self.dbctrajecten.values():
            res = traject.validate(autocorrect = autocorrect)
            self.bewerkingen.extend(res['bewerkingen'])
            self.meldingen.extend(res['meldingen'])      
        for tijd in self.tijdschrijven.values():
            res = tijd.validate(autocorrect = autocorrect)
            self.bewerkingen.extend(res['bewerkingen'])
            self.meldingen.extend(res['meldingen'])
        for diagnose in self.diagnoses.values():
            res = diagnose.validate(autocorrect = autocorrect)
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

        bestandsnaam = self.pakbon._1538
        bestandsnaam_algemeen = bestandsnaam[:32]
        creatiedatum = self.pakbon._1537
        extensie = ".zip"

        # volgnummer ophogen
        if volgnummer:
            self.pakbon._3006 = str(volgnummer).zfill(2)

        # bestandsnaam aanpassen met opgehoogd volgnummer
        nieuwe_bestandsnaam = "_".join([bestandsnaam_algemeen, creatiedatum, self.pakbon._3006])
        self.pakbon._1538 = nieuwe_bestandsnaam + extensie


        # Aantal clienten, behandeltrajecten etc bijwerken
        self.pakbon._1542 = str(len(self.patienten))
        self.pakbon._1543 = str(len(self.zorgtrajecten))
        self.pakbon._1544 = str(len(self.dbctrajecten))
        self.pakbon._1546 = str(len(self.tijdschrijven))
        self.pakbon._1545 = str(len(self.diagnoses))


        with tempfile.TemporaryDirectory() as tijdelijk:
            # patientgegevens wegschrijven
            with open(os.path.join(tijdelijk, 'patient.txt'), 'w') as f_pat:
                for patient in self.patienten.values():
                    f_pat.write(patient.write_to_string() + '\n')

            # zorgtrajecten wegschrijven
            with open(os.path.join(tijdelijk, 'zorgtraject.txt'), 'w') as f_zorgtraject:
                for zt in self.zorgtrajecten.values():
                    f_zorgtraject.write(zt.write_to_string() + '\n')    

            # dbc's wegschrijven
            with open(os.path.join(tijdelijk, 'dbc_traject.txt'), 'w') as f_beh:
                for dbc in self.dbctrajecten.values():
                    f_beh.write(dbc.write_to_string() + '\n')            

            # Zorgprofiel wegschrijven
            with open(os.path.join(tijdelijk, 'geleverd_zorgprofiel_tijdschrijven.txt'), 'w') as f_profiel:
                for tijd in self.tijdschrijven.values():
                    f_profiel.write(tijd.write_to_string() + '\n')     

            # diagnoses wegschrijven
            with open(os.path.join(tijdelijk, 'diagnose.txt'), 'w') as f_diagnose:
                for diagnose in self.diagnoses.values():
                    f_diagnose.write(diagnose.write_to_string() + '\n')            

            # pakbon wegschrijven
            with open(os.path.join(tijdelijk, 'pakbon.txt'), 'w') as f_pakbon:
                f_pakbon.write(self.pakbon.write_to_string() + '\n')
       
            # Bestanden die we niet gebruiken
            lege_bestanden = [
             'geleverd_zorgprofiel_dagbesteding.txt'   
            ,'geleverd_zorgprofiel_verblijfsdagen.txt'
            ,'geleverd_zorgprofiel_verrichtingen.txt'
            ,'overige_verrichting.txt']

            for bestand in lege_bestanden:
                    f = open(os.path.join(tijdelijk,bestand), 'w')
                    f.close()

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

        # Zorgtraject
        headers_zt = [x["Naam"] for x in Zorgtraject.format_definitions]
        write_objects_csv(os.path.join(doelmap, 'zorgtraject.csv'), self.zorgtrajecten.values(), headers_zt)

        # DBC
        headers_dbctraject = [x["Naam"] for x in DBCTraject().format_definitions]
        write_objects_csv(os.path.join(doelmap, 'dbc_traject.csv'), self.dbctrajecten.values(), headers_dbctraject)

        # Tijdschrijven
        headers_zorgprofiel = [x["Naam"] for x in Tijdschrijven().format_definitions]
        write_objects_csv(os.path.join(doelmap, 'geleverd_zorgprofiel_tijdschrijven.csv'), self.tijdschrijven.values(), headers_zorgprofiel)  
        
        # Diagnose
        headers_diagnose = [x["Naam"] for x in Diagnose().format_definitions]
        write_objects_csv(os.path.join(doelmap, 'diagnose.csv'), self.diagnoses.values(), headers_diagnose) 