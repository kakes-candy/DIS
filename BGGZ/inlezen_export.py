from classes import Patient, Pakbon, Zorgtraject, DBCTraject, Tijdschrijven, Diagnose
from collections import OrderedDict
import csv, os


bronmap = 'Test rapportages/11_52/DIS_GGZ_DBC_TEST_080_73730802_01_20190320_01'


# Submap voor ingelezen bestanden aanmaken in bronmap
try:
    os.mkdir(os.path.join(bronmap, 'ingelezen'))
except FileExistsError:
    print('Directory not created')


with open(os.path.join(bronmap, 'pakbon.txt'), 'r' ) as f_pakbon:
    p = f_pakbon.readline()
    # print(Pakbon.from_string(p).write_to_dict())

with open(os.path.join(bronmap, 'patient.txt'), 'r' ) as f_patient:

    headers_patient =  [x['Naam'] for x in Patient().format_definitions]
    with open(os.path.join(bronmap, 'ingelezen', 'patient.csv'), 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, delimiter = ';', fieldnames = headers_patient)
        writer.writeheader()
        for line in f_patient:
            patient = Patient.from_string(line)
            writer.writerow(patient.write_to_dict())


with open(os.path.join(bronmap, 'zorgtraject.txt'), 'r' ) as f_zorgtraject:

    headers_zorgtraject =  [x['Naam'] for x in Zorgtraject().format_definitions]
    with open(os.path.join(bronmap, 'ingelezen', 'zorgtraject.csv'), 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, delimiter = ';', fieldnames = headers_zorgtraject)
        writer.writeheader()
        for line in f_zorgtraject:
            zorgtraject = Zorgtraject.from_string(line)
            writer.writerow(zorgtraject.write_to_dict())


with open(os.path.join(bronmap, 'dbc_traject.txt'), 'r' ) as f_dbctraject:

    headers_dbctraject =  [x['Naam'] for x in DBCTraject().format_definitions]
    with open(os.path.join(bronmap, 'ingelezen', 'dbctraject.csv'), 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, delimiter = ';', fieldnames = headers_dbctraject)
        writer.writeheader()
        for line in f_dbctraject:
            dbctraject = DBCTraject.from_string(line)
            writer.writerow(dbctraject.write_to_dict())


with open(os.path.join(bronmap, 'geleverd_zorgprofiel_tijdschrijven.txt'), 'r' ) as f_tijdschrijven:

    headers_tijdschrijven =  [x['Naam'] for x in Tijdschrijven().format_definitions]
    with open(os.path.join(bronmap, 'ingelezen', 'tijdschrijven.csv'), 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, delimiter = ';', fieldnames = headers_tijdschrijven)
        writer.writeheader()
        for line in f_tijdschrijven:
            tijdschrijven = Tijdschrijven.from_string(line)
            writer.writerow(tijdschrijven.write_to_dict())


with open(os.path.join(bronmap, 'diagnose.txt'), 'r' ) as f_diagnose:

    headers_diagnose =  [x['Naam'] for x in Diagnose().format_definitions]
    with open(os.path.join(bronmap, 'ingelezen', 'diagnose.csv'), 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, delimiter = ';', fieldnames = headers_diagnose)
        writer.writeheader()
        for line in f_diagnose:
            diagnose = Diagnose.from_string(line)
            writer.writerow(diagnose.write_to_dict())
