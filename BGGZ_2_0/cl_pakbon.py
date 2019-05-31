from Basis.cl_DIS_dataobject import DISdataObject
from BGGZ_2_0.definitions import format_pakbon


class PakbonTekst(DISdataObject):

    format_definitions = format_pakbon

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)
