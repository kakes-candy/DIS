from classes import Patient, Pakbon, Zorgtraject, DBCTraject, Tijdschrijven, Diagnose, PakbonTekst
from collections import OrderedDict
import csv, os

bronmap = 'Test rapportages/16_52/DIS_GGZ_DBC_TEST_080_73730802_01_20190312_01/'

with open(os.path.join(bronmap, 'pakbon.txt'), 'r' ) as f_pakbon:
    p = f_pakbon.readline()
    print(PakbonTekst.from_string(p).write_to_dict())
