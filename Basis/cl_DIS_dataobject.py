# Moeder klas voor alle dis data elementen
class DISdataObject(object):

    # format_definitions is een lijst met DIS data specificaties
    format_definitions = {}
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
            value = getattr(self, key).strip(" ")
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
