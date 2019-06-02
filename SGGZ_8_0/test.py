from classes import Patient, Pakbon, Zorgtraject, DBCTraject, Tijdschrijven, Diagnose, PakbonTekst
from collections import OrderedDict
import csv, os
from pprint import pprint



bronmap = 'Test rapportages/2017-02 11_09/DIS_GGZ_DBC_TEST_080_73730802_01_20190402_01' 

print(bronmap)

pb = Pakbon()


with open(os.path.join(bronmap, 'pakbon.txt'), 'r' ) as f_pakbon:
    p = f_pakbon.readline()
    print(PakbonTekst.from_string(p).write_to_dict())


with open(os.path.join(bronmap, 'patient.txt'), 'r' ) as f_patient:
    # patient = Patient.from_string(f_patient.readline())
    for line in f_patient:
        patient = Patient.from_string(line)
        pb.add_patient(patient)

print('patienten ingelezen')

with open(os.path.join(bronmap, 'zorgtraject.txt'), 'r' ) as f_zorgtraject:
    for line in f_zorgtraject:
        zorgtraject = Zorgtraject.from_string(line)
        pb.add_zorgtraject(zorgtraject)

print('zorgtrajecten ingelezen')

with open(os.path.join(bronmap, 'dbc_traject.txt'), 'r' ) as f_dbctraject:
    for line in f_dbctraject:
        dbctraject = DBCTraject.from_string(line)
        pb.add_dbctraject(dbctraject)

print('dbctrajecten ingelezen')

with open(os.path.join(bronmap, 'geleverd_zorgprofiel_tijdschrijven.txt'), 'r' ) as f_tijdschrijven:
    for line in f_tijdschrijven:
        tijdschrijven = Tijdschrijven.from_string(line)
        pb.add_tijd(tijdschrijven)

print('tijden ingelezen')

with open(os.path.join(bronmap, 'diagnose.txt'), 'r' ) as f_diagnose:
    for line in f_diagnose:
        diagnose = Diagnose.from_string(line)
        pb.add_diagnose(diagnose)

print('diagnoses ingelezen')


print('aantal patienten in pakbon: {}'.format(pb._1542))
print('aantal zorgtrajecten in pakbon: {}'.format(pb._1543))
print('aantal DBCs in pakbon: {}'.format(pb._1544))
print('aantal diagnoses in pakbon: {}'.format(pb._1545))
print('aantal tijdschrijven in pakbon: {}'.format(pb._1546))


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

pprint(results)

pprint(pb.meldingen)
