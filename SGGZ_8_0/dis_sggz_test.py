from classes import Patient, Pakbon, Zorgtraject, DBCTraject, Tijdschrijven, Diagnose, PakbonTekst
from collections import OrderedDict
import csv, zipfile, logging
from pprint import pprint
from os import path, listdir, mkdir
from datetime import time


bronmap = 'Test rapportages/DIS aanleveringen/PROD/2019-02'

# Bestanden in bronmap
dir = listdir(bronmap)

# DIS aanleverbestand
filename =  [f for f in listdir(bronmap) if path.isfile(path.join(bronmap, f)) and path.splitext(f)[1] == '.zip'][0]

# Naam map om uit te pakken is zelfde als bestandsnaam zonder extensie
targetdir = path.join(bronmap, path.splitext(filename)[0])


# Bestanden uitpakken in bronmap
with zipfile.ZipFile(path.join(bronmap, filename), "r") as zip_ref:
    zip_ref.extractall(targetdir)

# Submap voor ingelezen bestanden aanmaken in bronmap
try:
    mkdir(path.join(bronmap, 'ingelezen'))
except FileExistsError:
    print('Directory not created')




"""
Logging configuratie
"""
logfilename = "dis_sggz_test.log"
logpath = path.join(bronmap, 'ingelezen', logfilename)

# root logger
logging.basicConfig(filemode = 'w')
rootlogger = logging.getLogger()
# loglevel instellen voor deze logger, zet op debug om meer logs te krijgen, INFO is standaard
# NB: als je het loglevel wil aanpassen, doe dit dan bij 1 van de handlers
rootlogger.setLevel(logging.DEBUG)

# file handler maken
fh = logging.FileHandler(logpath)
# Voor tests altijd debug als loglevel, anders kiezen
fh.setLevel(logging.DEBUG)
# console handler markeren
# formatter maken en toevoegen aan de handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s %(message)s')
fh.setFormatter(formatter)
# handler toewijzen aan de logger
rootlogger.addHandler(fh)
# logger openen, de logger zou al geconfigureerd moeten zijn
filelogger = logging.getLogger(__name__)



filelogger.debug(targetdir)

# Pakbon object om alle dis data te bevatten
pb = Pakbon()

with open(path.join(targetdir, 'pakbon.txt'), 'r' ) as f_pakbon:
    p = f_pakbon.readline()
    print(PakbonTekst.from_string(p).write_to_dict())


# export bestanden openen en uitlezen in objecten + wegschrijven in csv
with open(path.join(targetdir, 'patient.txt'), 'r' ) as f_patient:
    headers_patient =  [x['Naam'] for x in Patient().format_definitions]
    with open(path.join(bronmap, 'ingelezen', 'patient.csv'), 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, delimiter = ';', fieldnames = headers_patient)
        writer.writeheader()
        for line in f_patient:
            patient = Patient.from_string(line)
            pb.add_patient(patient)
            writer.writerow(patient.write_to_dict())

filelogger.debug('patienten ingelezen')



with open(path.join(targetdir, 'zorgtraject.txt'), 'r' ) as f_zorgtraject:
    headers_zorgtraject =  [x['Naam'] for x in Zorgtraject().format_definitions]
    with open(path.join(bronmap, 'ingelezen', 'zorgtraject.csv'), 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, delimiter = ';', fieldnames = headers_zorgtraject)
        writer.writeheader()
        for line in f_zorgtraject:
            zorgtraject = Zorgtraject.from_string(line)
            pb.add_zorgtraject(zorgtraject)
            writer.writerow(zorgtraject.write_to_dict())

filelogger.debug('zorgtrajecten ingelezen')




with open(path.join(targetdir, 'dbc_traject.txt'), 'r' ) as f_dbctraject:
    headers_dbctraject =  [x['Naam'] for x in DBCTraject().format_definitions]
    with open(path.join(bronmap, 'ingelezen', 'dbctraject.csv'), 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, delimiter = ';', fieldnames = headers_dbctraject)
        writer.writeheader()
        for line in f_dbctraject:
            dbctraject = DBCTraject.from_string(line)
            pb.add_dbctraject(dbctraject)
            writer.writerow(dbctraject.write_to_dict())

filelogger.debug('dbctrajecten ingelezen')



with open(path.join(targetdir, 'geleverd_zorgprofiel_tijdschrijven.txt'), 'r' ) as f_tijdschrijven:
    headers_tijdschrijven =  [x['Naam'] for x in Tijdschrijven().format_definitions]
    with open(path.join(bronmap, 'ingelezen', 'tijdschrijven.csv'), 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, delimiter = ';', fieldnames = headers_tijdschrijven)
        writer.writeheader()
        for line in f_tijdschrijven:
            tijdschrijven = Tijdschrijven.from_string(line)
            pb.add_tijd(tijdschrijven)
            writer.writerow(tijdschrijven.write_to_dict())

filelogger.debug('tijden ingelezen')

with open(path.join(targetdir, 'diagnose.txt'), 'r' ) as f_diagnose:
    headers_diagnose =  [x['Naam'] for x in Diagnose().format_definitions]
    with open(path.join(bronmap, 'ingelezen', 'diagnose.csv'), 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, delimiter = ';', fieldnames = headers_diagnose)
        writer.writeheader()
        for line in f_diagnose:
            diagnose = Diagnose.from_string(line)
            pb.add_diagnose(diagnose)
            writer.writerow(diagnose.write_to_dict())

filelogger.debug('diagnoses ingelezen')



filelogger.debug('aantal patienten in pakbon: {}'.format(pb._1542))
filelogger.debug('aantal zorgtrajecten in pakbon: {}'.format(pb._1543))
filelogger.debug('aantal DBCs in pakbon: {}'.format(pb._1544))
filelogger.debug('aantal diagnoses in pakbon: {}'.format(pb._1545))
filelogger.debug('aantal tijdschrijven in pakbon: {}'.format(pb._1546))

# voer validaties uit
results = []
for ingelezen_patient in pb.patienten.values():
    result = ingelezen_patient.validate()
    if result:
        results.append(result)

for ingelezen_zorgtraject in pb.zorgtrajecten.values():
    result = ingelezen_zorgtraject.validate()
    if result:
        results.append(result)

for ingelezen_dbctraject in pb.DBCtrajecten.values():
    result = ingelezen_dbctraject.validate()
    if result:
        results.append(result)

for ingelezen_tijd in pb.tijdschrijven.values():
    result = ingelezen_tijd.validate()
    if result:
        results.append(result)

for ingelezen_diagnose in pb.diagnoses.values():
    result = ingelezen_diagnose.validate()
    if result:
        results.append(result)


for result in results:
    filelogger.debug(result)

for melding in pb.meldingen:
    filelogger.debug(melding)
