


from format_definitions import *

"""
Klassen voor het opslaan en verwerken van DIS data
"""

class DISdataObject(object):

    #format_definitions is een lijst met DIS data specificaties
    format_definitions = None
    # attributen voor links met andere objecten
    child_types, parent_types = list(), list()

    def __init__(self, **kwargs):
        for definition in self.format_definitions:
            ID = '_{id}'.format(id = definition['DDID'])
            setattr(self, ID, None)

        self.children = {child_type : set() for child_type in self.child_types}
        self.parents = {parent_type : set() for parent_type in self.parent_types}


    def write_to_string(self):
        result = ''
        for definition in self.format_definitions:
            dis_id = '_' + str(definition['DDID'])
            raw_value = getattr(self, dis_id)
            if not raw_value:
                raw_value = ''
            result = result + raw_value.rjust(int(definition['Lengte']), ' ')
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




    def add_member(self, to, obj):
        self.children.get(to, set()).add(obj)

    def delete_member(self, to, obj):
        self.children.get(to, set()).discard(obj)


    def help(self):
        atts_of_interest = ['DDID', 'Naam', 'Lengte', 'Patroon']
        print('Dit dataobject heeft de volgende attributen:')
        for definition in self.format_definitions:
            l = ["{key}: {value}".format(key = item, value = definition[item])
                    for item in atts_of_interest]
            print(l)



class Patient(DISdataObject):

    format_definitions = format_patient
    child_types = ['Zorgtraject']
    parent_types = []

    def __init__(self, **kwargs):
        super(Patient, self).__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    # Methode om object te valideren
    def validate(self):
        # start assuming object is valid
        valid = True

        # check if object has children if defined in class
        for child in self.children:
            if len(child) == 0:
                valid = False
            else:
                for child_instance in child:
                    pass

        # Also check for parents
        for parent in self.parents:
            if len(parent) == 0:
                valid = False




class Zorgtraject(DISdataObject):

    format_definitions = format_zorgtraject
    child_types = ['DBCTraject']
    parent_types = ['Patient']

    def __init__(self, **kwargs):
        super(Zorgtraject, self).__init__()


class DBCTraject(DISdataObject):

    format_definitions = format_dbctraject
    child_types = ['Tijdschrijven', 'Diagnose']
    parent_types = ['Zorgtraject']

    def __init__(self, **kwargs):
        super(DBCTraject, self).__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)


class Tijdschrijven(DISdataObject):

    format_definitions = format_geleverd_zorgprofiel_tijdschrijven
    child_types = []
    parent_types = ['DBCTraject']

    def __init__(self, **kwargs):
        super(Tijdschrijven, self).__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

class Diagnose(DISdataObject):

    format_definitions = format_diagnose
    child_types = []
    parent_types = ['DBCTraject']

    def __init__(self, **kwargs):
        super(Diagnose, self).__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)
