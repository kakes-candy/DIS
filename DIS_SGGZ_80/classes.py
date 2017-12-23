


from DIS_SGGZ_80.format_definitions import format_patient, format_dbctraject


# from format_definitions import format_patient


"""
Klassen voor het opslaan en verwerken van DIS data
"""

class Patient(object):

    format_definitions = format_patient
    # attributen voor links met andere objecten
    children = ['DBCtrajecten']
    parents = []

    def __init__(self, **kwargs):
        # Check of attributen uit definitie al gezet zijn
        self.init_definitions()
        for link in self.children:
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
            super(Patient, self).__setattr__(name, value)


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
            l = ["{n} {key}: {value}".format(n =n, key = item, value = definition[item])
                    for item in atts_of_interest]
            print(l)


class DBCTraject(Patient):
    format_definitions = format_dbctraject


    children = []
    parents = ['Zorgtraject']

    def __init__(self, **kwargs):
        super(DBCTraject, self).__init__()


# Eerste tests

p1 = Patient()
print(p1.help())
#
# p1._1433 = 'Harry'
# p1._1444 = '19761020'


# dbc1 = DBCTraject()
# print(dbc1.help())

# dbc1._4091 = 'testendoet'
# dbc1._1465 = '20170101'


# p1.add_child('DBCtrajecten', dbc1)
