


from DIS_SGGZ_80.format_definitions import *

"""
Klassen voor het opslaan en verwerken van DIS data
"""

class DISdataObject(object):

    format_definitions = None
    # attributen voor links met andere objecten
    children = []
    parents = []

    def __init__(self, **kwargs):
        # Check of attributen uit definitie al gezet zijn
        self.init_definitions()
        for link in self.children:
            setattr(self, link, [])
        for link in self.parents:
            setattr(self, link, [])
        self.set_attributes_from_kwargs(kwargs)

    def init_definitions(self):
        # definities gebruiken om klasattributen te zetten
        for definition in self.format_definitions:
            ID = '_{}'.format(definition['DDID'])
            setattr(self, ID, None)

    def __setattr__(self, name, value):
        allowed_attributes = ['_{}'.format(item['DDID']) for item in self.format_definitions]
        allowed_attributes = allowed_attributes + self.children
        if not name in allowed_attributes:
            raise AttributeError('{classname} has no attribute named {attr_name}'
                                    .format(classname = self.__class__.__name__,
                                            attr_name = name))
        else:
            super(DISdataObject, self).__setattr__(name, value)


    def set_attributes_from_kwargs(self, kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def write_to_string(self):
        result = ''
        for definition in self.format_definitions:
            # type = definition.type
            ddid = '_' + str(definition['DDID'])
            raw_value = getattr(self, ddid)
            if not raw_value:
                raw_value = ''
            # Nog afhankelijk maken van type
            result = result + raw_value.rjust(int(definition['Lengte']), ' ')
        return(result)

    def add_child(self, to, obj):
        old_links = getattr(self, to)
        new_links =  old_links + [obj]
        setattr(self, to, new_links)

    def help(self):
        atts_of_interest = ['DDID', 'Naam', 'Lengte', 'Patroon']
        print('Dit dataobject heeft de volgende attributen:')
        for definition in self.format_definitions:
            l = ["{key}: {value}".format(key = item, value = definition[item])
                    for item in atts_of_interest]
            print(l)



class Patient(DISdataObject):

    format_definitions = format_patient
    # attributen voor links met andere objecten
    children = ['Zorgtraject']
    parents = []

    def __init__(self, **kwargs):
        super(Patient, self).__init__()


class Zorgtraject(DISdataObject):

    format_definitions = format_zorgtraject
    # attributen voor links met andere objecten
    children = ['DBCTraject']
    parents = ['Patient']

    def __init__(self, **kwargs):
        super(Zorgtraject, self).__init__()


class DBCTraject(DISdataObject):
    format_definitions = format_dbctraject

    children = ['GeleverdZorgprofielTijdschrijven', 'Diagnose']
    parents = ['Zorgtraject']

    def __init__(self, **kwargs):
        super(DBCTraject, self).__init__()


class GeleverdZorgprofielTijdschrijven(DISdataObject):
    format_definitions = format_geleverd_zorgprofiel_tijdschrijven

    children = []
    parents = ['DBCTraject']

    def __init__(self, **kwargs):
        super(GeleverdZorgprofielTijdschrijven, self).__init__()


class Diagnose(DISdataObject):
    format_definitions = format_diagnose

    children = []
    parents = ['DBCTraject']

    def __init__(self, **kwargs):
        super(Diagnose, self).__init__()



# Eerste tests

p1 = Patient()
# print(p1.help())
#

print(p1.format_definitions)

print(sorted(p1.format_definitions, key = lambda x:int(x['Begin']), reverse = True))



zt = Zorgtraject()
# print(zt.help())
dbc = DBCTraject()
# print(dbc.help())
tijd = GeleverdZorgprofielTijdschrijven()
# print(tijd.help())
diagnose = Diagnose()
# print(diagnose.help())
