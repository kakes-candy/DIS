
from format_definitions import *
import datetime, re


"""
Klassen voor het opslaan en verwerken van DIS data
"""


# Moeder klas voor alle dis data elementen
class DISdataObject(object):

    #format_definitions is een lijst met DIS data specificaties
    format_definitions = None
    # attributen voor links met andere objecten
    child_types, parent_types = list(), list()

    def __init__(self, **kwargs):
        for definition in self.format_definitions:
            ID = '_{id}'.format(id = definition['DDID'])
            setattr(self, ID, None)

        self.children = {child_type : dict() for child_type in self.child_types}
        self.parent = None

        self.pakbon = []

    def write_to_string(self):
        result = ''
        for definition in self.format_definitions:
            dis_id = '_' + str(definition['DDID'])
            raw_value = getattr(self, dis_id)
            if not raw_value:
                raw_value = ''
            result = result + raw_value.rjust(int(definition['Lengte']), ' ')
        return(result)

    def write_to_dict(self):
        result = {}
        for definition in self.format_definitions:
            dis_id = '_' + str(definition['DDID'])
            naam = str(definition['Naam'])
            raw_value = getattr(self, dis_id)
            if not raw_value:
                raw_value = ''
            result[naam] = raw_value
        return(result)




    @classmethod
    def from_string(cls, string):
        dictionary = {}
        for item in cls.format_definitions:
            key = '_{}'.format(item.get('DDID'))
            begin, eind = int(item.get('Begin')), int(item.get('Eind'))
            dictionary[key] = string[begin-1:eind]
        return(cls(**dictionary))

    @classmethod
    def from_list(cls, lijst):
        dictionary = {}
        for i, item in enumerate(lijst):
            dis_id = '_{}'.format(cls.format_definitions[i].get('DDID'))
            dictionary[dis_id] = item
        return(cls(**dictionary))


    def add_child(self, to, obj):
        if not self.children.get(to, dict()).get(obj.__str__()):
            self.children.get(to, dict())[obj.__str__()] = obj
        # Ook bij het kind self de parent maken
        obj.add_parent(self)


    def delete_child(self, to, obj):
        try:
            del self.children.get(to)[obj.__str__()]
        except:
            pass

    def keys(self):
        return([''.join(['_',x['DDID']]) for x in self.format_definitions if 'PK' in x['Sleutel']])

    def foreign_key(self):
        # Alle id's van elementen die als FK zijn aangemeld (zou er maar 1 moeten zijn)
        keys = ['_{}'.format(x['DDID']) for x in self.format_definitions if 'FK' in x['Sleutel']]
        if keys:
            return(getattr(self, keys[0]))

    def __str__(self):
        keys = ['_{}'.format(x['DDID']) for x in self.format_definitions if 'PK' in x['Sleutel']]
        values = []
        for key in keys:
            value = getattr(self, key)
            if value:
                values.append(value)
            else:
                values.append('')

        return( '_'.join(values))

    def __repr__(self):
        return(self.__str__())

    def help(self):
        atts_of_interest = ['DDID', 'Naam', 'Lengte', 'Patroon']
        print('Dit dataobject heeft de volgende attributen:')
        for definition in self.format_definitions:
            l = ["{key}: {value}".format(key = item, value = definition[item])
                    for item in atts_of_interest]
            print(l)


    def verplichte_velden(self):
        keys = ['_{}'.format(x['DDID']) for x in self.format_definitions if x['Verplicht'] == 'V']
        values = {}
        for key in keys:
            values[key] = getattr(self, key)
        return(values)




class Patient(DISdataObject):

    format_definitions = format_patient
    child_types = ['Zorgtraject']

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def show_link(self):
        return(self._1432)


    # Methode om object te valideren
    def validate(self):
        # start assuming object is valid
        valid = True
        meldingen = []

        # Een patient hoort alleen in de export als er verwante zorgtrajecten zijn.
        for type in self.child_types:
            if len(self.children[type]) < 1:
                valid = False
                meldingen.append('PATIENT: {} heeft geen kinderen van het type {}'.format(self.__str__(), type))

        # Zijn alle verpichte velden gevuld:
        velden = self.verplichte_velden()
        for key, value in velden.items():
            if value.replace(' ', '') == '':
                meldingen.append('PATIENT: {} verplicht veld {} niet gevuld'.format(self.__str__(), key))


        # postcode controleren
        pattern = pattern = '^[1-9][0-9]{3}[A-Z][A-Z]$'
        if self._1443.replace(' ', '') == 'NL' and len(re.findall(pattern, self._1440)) == 0:
            meldingen.append('PATIENT: {} geen geldige postcode {} bij landcode NL'.format(self.__str__(), self._1440))

        if len(meldingen) > 0:
            return('   ###   '.join(meldingen))
        else:
            return()




class Zorgtraject(DISdataObject):

    format_definitions = format_zorgtraject
    child_types = ['DBCTraject']

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def show_link(self):
        return(self._1449)

    def add_parent(self, parent):
        if not self.parent:
            self.parent = parent
            self._1453 = parent._1432


    # Methode om object te valideren
    def validate(self):
        # start assuming object is valid
        valid = True
        meldingen = []

        # Een zorgtraject hoort alleen in de export als er verwante dbctrajecten zijn.
        for type in self.child_types:
            if len(self.children[type]) < 1:
                valid = False
                meldingen.append('ZORGTRAJECT: {} heeft geen kinderen van het type {}'.format(self.__str__(), type))
        # En er moet een patient als parent zijn
        if not self.parent:
            meldingen.append('ZORGTRAJECT: {} heeft geen ouder'.format(self.__str__()))

        # validatie 566, begindatum zorgtraject > Einddatum
        if datetime.datetime.strptime(self._1451, '%Y%m%d') > datetime.datetime.strptime(self._1452, '%Y%m%d'):
            meldingen.append('ZORGTRAJECT: {} startdatum > einddatum (val 566)'.format(self.__str__()))

        # validatie 1330, diagnose dsm 4 is niet leeg tenzij kinderen allemaal sluitreden 5 of 20 hebben.
        # lijst van sluitredenen
        redenen = [ x._1470.strip(' ') for x in self.children['DBCTraject'].values() if  x._1470.strip(' ') not in ('5', '20')]
        if self._1456.strip(' ') == '' and len(redenen) > 0:
            meldingen.append('ZORGTRAJECT: {} geen diagnose terwijl dbc traject niet sluitreden 5 of 20 (val 1330)'.format(self.__str__()))

        # validatie 2292, diagnose dsm 5 is niet leeg tenzij kinderen allemaal sluitreden 5 of 20 hebben.
        # lijst van sluitredenen
        redenen = [ x._1470.strip(' ') for x in self.children['DBCTraject'].values() if  x._1470.strip(' ') not in ('5', '20')]
        if self._1456.strip(' ') == '' and len(redenen) > 0:
            meldingen.append('ZORGTRAJECT: {} geen diagnose terwijl dbc traject niet sluitreden 5 of 20 (val 2292)'.format(self.__str__()))

        # validatie 2067, primaire diagnose is niet as_1 of as_2 en niet leeg
        if self._1456[:4] not in ('as1_', 'as2_', ) and self._1456.strip(' ') != '':
            meldingen.append('ZORGTRAJECT: {} diagnosecode niet as_1 of as_2 (val 2067)'.format(self.__str__()))

        if len(meldingen) > 0:
            return('   ###   '.join(meldingen))
        else:
            return()



class DBCTraject(DISdataObject):

    format_definitions = format_dbctraject
    child_types = ['Tijdschrijven', 'Diagnose']

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def show_link(self):
        return(self._1462)

    def add_parent(self, parent):
        if not self.parent:
            self.parent = parent
            self._1464 = parent._1449

    # Methode om object te valideren
    def validate(self):
        # start assuming object is valid
        valid = True
        meldingen = []

        # Een zorgtraject hoort alleen in de export als er verwante dbctrajecten zijn.
        for type in self.child_types:
            if len(self.children[type]) < 1 and type != 'Diagnose':
                valid = False
                meldingen.append('DBCTRAJECT: {} heeft geen kinderen van het type {}'.format(self.__str__(), type))

        # En er moet een patient als parent zijn
        if not self.parent:
            meldingen.append('DBCTRAJECT: {} heeft geen ouder'.format(self.__str__()))

        start_dbc = datetime.datetime.strptime(self._1465, '%Y%m%d')
        eind_dbc =  datetime.datetime.strptime(self._1466, '%Y%m%d')

        # validatie 515, begindatum  > Einddatum
        if start_dbc > eind_dbc:
            meldingen.append('DBCTRAJECT: {} startdatum > einddatum (val 515)'.format(self.__str__()))

        # validatie 1388, begindatum dbc eerder dan begindatum zorgtraject
        if self.parent and start_dbc < datetime.datetime.strptime(self.parent._1451, '%Y%m%d'):
            meldingen.append('DBCTRAJECT: {} startdatum dbc eerder dan startdatum zorgtraject (val 1388)'.format(self.__str__()))

        # validatie 2124 duur dbc langer dan 365 dagen
        if (eind_dbc - start_dbc).days >= 365:
            meldingen.append('DBCTRAJECT: {} start en einddatum meer dan 365 dagen van elkaar (val 2124)'.format(self.__str__()))

        # validatie 2083: er moet tenminste 1 hoofdbehandelaar Zijn
        if self._4091.strip(' ') == '' and self._4092.strip(' ') == '':
            meldingen.append('DBCTRAJECT: {} geen regie/hoofbehandelaars (val 2083)'.format(self.__str__()))

        # validatie 2191: Beroepcode 1e hoofdbehandelaar ontrbreekt
        if self._4091.strip(' ') != '' and self._4093.strip(' ') == '':
            meldingen.append('DBCTRAJECT: {} Beroepcode 1e hoofdbehandelaar ontrbreekt (val 2191)'.format(self.__str__()))

        # validatie 2200: Beroepcode 1e hoofdbehandelaar ontrbreekt
        if self._4092.strip(' ') != '' and self._4094.strip(' ') == '':
            meldingen.append('DBCTRAJECT: {} Beroepcode 2e hoofdbehandelaar ontrbreekt (val 2200)'.format(self.__str__()))

        # validatie 2201: 4146 Verwijzer is niet gevuld terwijl 4095 Verwijstype/code(zelf)verwijzer is 01,02,03 of 04
        if self._4146.strip(' ') == '' and self._4095 in ('01', '02', '03', '04'):
            meldingen.append('DBCTRAJECT: {}  Verwijzer is niet gevuld terwijl 4095 Verwijstype/code(zelf)verwijzer is 01,02,03 of 04 (val 2201)'.format(self.__str__()))

        # Validatie verkoopprijs
        try:
            bedrag = int(self._1471)
        except:
            meldingen.append('DBCTRAJECT: {}  verkoopprijs bevat geen geldige waarde (val 614)'.format(self.__str__()))
        else:
            if bedrag < 0:
                meldingen.append('DBCTRAJECT: {}  verkoopprijs lager dan 0 (val 1392)'.format(self.__str__()))

        # validatie 2068: 1473 Productgroepcode (positie 4 t/m 6) komt niet overeen met het productgroepcodebehandeldeel positie (10 t/m 12) in 1474 Prestatiecode Productgroepcode (positie 4 t/m 6) komt niet overeen met het productgroepcodebehandeldeel positie (10 t/m 12) in 1474 Prestatiecode
        if self._1473[-3:] != self._1474[-3:]:
            meldingen.append('DBCTRAJECT: {}  productgroepcode {} klopt niet met prestatiecode {} (val 2068)'.format(self.__str__(), self._1473[:-3], self._1474[:-3]))

        # Validatie DBC bedrag
        try:
            dbcbedrag = int(self._1476)
        except:
            meldingen.append('DBCTRAJECT: {}  DBC bedrag bevat geen geldige waarde (val 379)'.format(self.__str__()))
        else:
            if dbcbedrag < 0:
                meldingen.append('DBCTRAJECT: {}  DBC bedrag lager dan 0 (val 1396)'.format(self.__str__()))

        # Validatie verrekenbedrag
        try:
            verrekenbedrag = int(self._1477)
        except:
            meldingen.append('DBCTRAJECT: {}  verrekenbedrag bevat geen geldige waarde (val 379)'.format(self.__str__()))
        else:
            if verrekenbedrag < 0:
                meldingen.append('DBCTRAJECT: {}  verrekenbedrag lager dan 0 (val 1396)'.format(self.__str__()))

        if len(meldingen) > 0:
            return('   ###   '.join(meldingen))
        else:
            return()




class Tijdschrijven(DISdataObject):

    format_definitions = format_geleverd_zorgprofiel_tijdschrijven
    child_types = []

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_parent(self, parent):
        if not self.parent:
            self.parent = parent
            self._1488 = parent._1462

    # Methode om object te valideren
    def validate(self):
        # start assuming object is valid
        valid = True
        meldingen = []

        # En er moet een patient als parent zijn
        if not self.parent:
            meldingen.append('TIJDSCHRIJVEN: {} heeft geen ouder'.format(self.__str__()))


        # Validatie 2126: 1491 Activiteitdatum ligt niet tussen 1465 Begindatum DBC-traject en 1466 Einddatum DBC-traject
        start_dbc = datetime.datetime.strptime(self.parent._1465, '%Y%m%d')
        eind_dbc =  datetime.datetime.strptime(self.parent._1466, '%Y%m%d')
        activiteitendatum = datetime.datetime.strptime(self._1491, '%Y%m%d')
        if activiteitendatum < start_dbc or activiteitendatum > eind_dbc:
            meldingen.append('TIJDSCHRIJVEN: {} activiteitdatum ligt niet tussen begin en einddatum dbc'.format(self.__str__()))

        if len(meldingen) > 0:
            return('   ###   '.join(meldingen))
        else:
            return()



class Diagnose(DISdataObject):

    format_definitions = format_diagnose
    child_types = []

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_parent(self, parent):
        if not self.parent:
            self.parent = parent
            self._1481 = parent._1462

    # Methode om object te valideren
    def validate(self):
        # start assuming object is valid
        valid = True
        meldingen = []

        # En er moet een patient als parent zijn
        if not self.parent:
            meldingen.append('DIAGNOSE: {} heeft geen ouder'.format(self.__str__()))


        # Validatie 2133: diagnosedatum na einddatum dbcbedrag
        eind_dbc =  datetime.datetime.strptime(self.parent._1466, '%Y%m%d')
        diagnosedatum = datetime.datetime.strptime(self._1482, '%Y%m%d')
        if diagnosedatum > eind_dbc:
            meldingen.append('DIAGNOSE: {} diagnosedatum > eind DBC (val 2133)'.format(self.__str__()))

        # Validatie 2116: 1483 Diagnosecode is gelijk aan 1456 Primaire diagnosecode
        if self._1483 == self.parent.parent._1456:
            meldingen.append('DIAGNOSE: {} nevendiagnose is gelijk aan primaire diagnose'.format(self.__str__()))

        # Validatie 2308: 4167 Diagnosecode DSM-5 is niet gevuld terwijl 1483 Diagnosecode <> as1_18.02 of as1_18.03 of as2_18.02 of as2_18.03 of as4_110.
        if self._4167.strip(' ') == '' and self._1483.strip(' ') not in ('as1_18.02' 'as1_18.03', 'as2_18.02', 'as2_18.03', 'as4_110'):
            meldingen.append('DIAGNOSE: {} er had een dsm 5 code moeten staan (val 2308)'.format(self.__str__()))

        if len(meldingen) > 0:
            return('   ###   '.join(meldingen))
        else:
            return()



class PakbonTekst(DISdataObject):

    format_definitions = format_pakbon

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)




# klas om alle Disobjecten vast te houden
class Pakbon(DISdataObject):

    format_definitions = format_pakbon
    meldingen = []

    def __init__( self, **kwargs):
        super(Pakbon, self).__init__()
        # deze eigenschappen zijn constant
        self._1534 = '73730802' # agb instelling
        self._1535 = '1' # dis volgnummer
        self._1536 = '8' # versie dis aanleverstandaard
        self._1537 = datetime.date.today().strftime('%Y%m%d') # Creatiedatum
        self._1539 = 'TJIPBV' # Softwareleverancier
        self._1540 = 'WECARE' # Softwarepakket
        self._1541 = '2.0.3' # Softwareversie
        self._1542 = 0 # aantal patient
        self._1543 = 0 # aantal zorgtraject
        self._1544 = 0 # aantal dbc
        self._1545 = 0 # aantal diagnose
        self._1546 = 0 # aantal tijdschrijven
        self._1547 = 0 # aantal dagbesteding
        self._1548 = 0 # aantal verblijf
        self._1549 = 0 # aantal verrichtingen
        self._1550 = 0 # aantal overig
        self._1551 = 0 # dis gebruikersnaam
        self._1551 = 0 # kvk nummer
        self._1551 = 0 # kvk vestigingnummer


        self.patienten = dict()
        self.zorgtrajecten = dict()
        self.DBCtrajecten = dict()
        self.tijdschrijven = dict()
        self.diagnoses = dict()

    def add_patient( self, obj = None, **kwargs):
        if not obj:
            pt= Patient( **kwargs)
        else:
            pt = obj
        # Als de patient al bestaat, bestaande object teruggeven
        if pt.__str__() in self.patienten:
            meldingen.append('PATIENT: {} is niet uniek'.format(pt.__str__()))
            return(self.patienten[pt.__str__()])
        # Als de patient nog niet is ingelezen
        else:
            self.patienten[pt.__str__()] = pt
            self._1542 += 1
            return pt

    def del_patient(self, patient):
        try:
            del self.patienten[patient.__str__()]
            self._1542 -= 1
        except:
            pass


    def add_zorgtraject( self, obj = None, **kwargs):
        if not obj:
            zt= Zorgtraject(**kwargs)
        else:
            zt = obj
        # Als het zorgtraject al bestaat, bestaande object teruggeven
        if zt.__str__() in self.zorgtrajecten:
            meldingen.append('ZORGTRAJECT: {} is niet uniek'.format(zt.__str__()))
            return(self.zorgtrajecten[zt.__str__()])
        # Als het zorgtraject nog niet is ingelezen
        if zt.__str__() not in self.zorgtrajecten:
            # parent zoeken, eerste uit lijst (lijst zou 1 lang moeten zijn)
            for key, value in self.patienten.items():
                if value.show_link() == zt.foreign_key():
                    value.add_child('Zorgtraject', zt)
                    break
            # zorgtraject aan pakbon toevoegen en teller ophogen
            self.zorgtrajecten[zt.__str__()] = zt
            self._1543 += 1
            return zt

    def del_zorgtraject( self, zorgtraject):
        try:
            del self.zorgtrajecten[zorgtraject.__str__()]
            self._1543 -= 1
        except:
            pass
        self._1543 -= 1

    def add_dbctraject( self, obj = None, **kwargs):
        if not obj:
            dbc = DBCTraject(**kwargs)
        else:
            dbc = obj
        # Als het dbctraject al bestaat, bestaande object teruggeven
        if dbc.__str__() in self.DBCtrajecten:
            meldingen.append('DBCTRAJECT: {} is niet uniek'.format(dbc.__str__()))
            return(self.DBCtrajecten[dbc.__str__()])
        # Als het dbctraject nog niet is ingelezen dan toevoegen aan pakbon lijst
        if dbc.__str__() not in self.DBCtrajecten:
            # parent zoeken, eerste uit lijst (lijst zou 1 lang moeten zijn)
            for key, value in self.zorgtrajecten.items():
                if value.show_link() == dbc.foreign_key():
                    value.add_child('DBCTraject', dbc)
                    break
            self.DBCtrajecten[dbc.__str__()] = dbc
            self._1544 += 1
            return dbc

    def del_dbctraject( self, dbctraject):
        try:
            del self.DBCtrajecten[dbctraject.__str__()]
            self._1544 -= 1
        except:
            pass


    def add_diagnose( self, obj = None, **kwargs):
        if not obj:
            d = Diagnose(**kwargs)
        else:
            d = obj
        # Als de diagnose al bestaat, bestaande object teruggeven
        if d.__str__() in self.diagnoses:
            meldingen.append('DIAGNOSE: {} is niet uniek'.format(d.__str__()))
            return(self.diagnoses[d.__str__()])
        # Als de diagnose nog niet is ingelezen
        if d.__str__() not in self.diagnoses:
            # parent zoeken, eerste uit lijst (lijst zou 1 lang moeten zijn)
            for key, value in self.DBCtrajecten.items():
                if value.show_link() == d.foreign_key():
                    value.add_child('Diagnose', d)
                    break
            self.diagnoses[d.__str__()] = d
            self._1545 += 1
            return d

    def del_diagnose( self, diagnose):
        try:
            del self.diagnoses[diagnose.__str__()]
            self._1545 -= 1
        except:
            pass


    def add_tijd( self, obj = None, **kwargs):
        if not obj:
            ts = Tijdschrijven(**kwargs)
        else:
            ts = obj
        # Als de tijdrecord al bestaat, bestaande object teruggeven
        if ts.__str__() in self.tijdschrijven:
            meldingen.append('TIJDSCHRIJVEN: {} is niet uniek'.format(ts.__str__()))
            return(self.tijdschrijven[ts.__str__()])
        # Als het tijdschrijven nog niet is ingelezen
        if ts.__str__() not in self.tijdschrijven:
            # parent zoeken, eerste uit lijst (lijst zou 1 lang moeten zijn)
            for key, value in self.DBCtrajecten.items():
                if value.show_link() == ts.foreign_key():
                    value.add_child('Tijdschrijven', ts)
                    break
            self.tijdschrijven[ts.__str__()] = ts
            self._1546 += 1
        return ts

    def del_tijd( self, tijd):
        try:
            del self.tijdschrijven[tijd.__str__()]
            self._1546 -= 1
        except:
            pass
