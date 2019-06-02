
from classes import Patient, Pakbon, Zorgtraject
from classes import DBCTraject, Tijdschrijven, Diagnose
from collections import OrderedDict
import csv, os

# kolomnamen mappen naar dis data ids
mapping = {
'Patient': OrderedDict(
[
('patient_declarerende_instelling', '_1430'),
('patient_intselling_volgnummer', '_1431'),
('patient_koppelnummer', '_1432'),
('patient_naam_1', '_1433'),
('patient_voorvoegsel_1', '_1434'),
('patient_naamcode_1', '_1435'),
('patient_naam_2', '_1436'),
('patient_voorvoegsel_2', '_1437'),
('patient_naamcode_2', '_1438'),
('patient_voorletters', '_1439'),
('patient_postcode', '_1440'),
('patient_huisnummer', '_1441'),
# TODO: huisnummer toevoeging
('patient_landcode', '_1443'),
('patient_geboortedatum', '_1444'),
('patient_geslacht', '_1445'),
('patient_bsn', '_1446'),
('datum_eerste_inschrijving', '_3182'),
('datum_laatste_uitschrijving', '_3183')
]
),
'Zorgtraject': OrderedDict(
[
('dbctraject_zorgtraject', '_1449'),
# TODO:Begindatum Zorgtraject
# TODO:Einddatum zorgtraject
# TODO:client_id is een FK, moet uit ouder klasse komen, niet uit data
# ('zorgtraject_client_id', '_1453'),
('zorgtraject_verwijzende_instelling', '_1454'),
('zorgtraject_verwijzer', '_1455'),
('zorgtraject_primaire_diagnose', '_1456'),
('zorgtraject_primaire_diagnose_trekken_van', '_1457'),
('zorgtraject_primaire_diagnose_dsm5', '_4168'),
('zorgtraject_verwijsdatum', '_1458')
]
),
'DBCtraject': OrderedDict(
[
('dbctraject_nummer', '_1462'),
 # TODO:zorgtraject id is een FK, moet uit ouder klasse komen, niet uit data
# ('dbctraject_zorgtraject', '_1464'),
('dbctraject_begindatum', '_1465'),
('dbctraject_einddatum', '_1466'),
('dbctraject_eerste_hoofdbehandelaar', '_4091'),
('dbctraject_eerste_hoofdbehandelaar_beroep', '_4093'),
('dbctraject_tweede_hoofdbehandelaar', '_4092'),
('dbctraject_tweede_hoofdbehandelaar_beroep', '_4094'),
('dbctraject_type_verwijzer', '_4095'),
('dbctraject_verwijzer', '_4146'),
('dbctraject_circuit', '_1496'),
('uzovi', '_1467'),
('dbctraject_zorgtype', '_1468'),
('dbctraject_sluitreden', '_1470'),
('dbctraject_verkoopprijs', '_1471'),
('dbctraject_productgroepcode', '_1473'),
('dbctraject_prestatiecocde', '_1474'),
('dbctraject_declaratiecode', '_1475'),
('dbctraject_tarief', '_1476'),
('dbctraject_verrekenbedrag', '_1477'),
('dbctraject_declaratiedatum', '_2144'),
('dbctraject_nhcbehandel', '_3217'),
('dbctraject_nhcverblijf', '_3218')
]),
# 'dossier_id',
'Tijdschrijven': OrderedDict(
[
# TODO:dbc traject id is een FK, moet uit ouder klasse komen, niet uit data
('dbctraject_nummer', '_1488'),
('tijd_activiteit_nummer', '_1489'),
('tijd_activiteit_code', '_1490'),
('tijd_activiteit_datum', '_1491'),
('tijd_activiteit_beroepcode', '_1492'),
('tijd_activiteit_hoofdbehandelaar', '_4136'),
('tijd_activiteit_direct', '_1493'),
('tijd_activiteit_indirect', '_1495'),
('tijd_activiteit_reis', '_1494')
]),
'Diagnose': OrderedDict(
[
# TODO:dbc traject id is een FK, moet uit ouder klasse komen, niet uit data
('dbctraject_nummer', '_1481'),
('diagnose_datum', '_1482'),
('diagnose_code', '_1483'),
('diagnose_trekken_van', '_1484'),
('diagnose_code_dsm5', '_4167')
])
}


pb = Pakbon()

with open('../data/DIS_test_2.csv', newline = '', encoding = 'latin-1') as f:

    dreader = csv.DictReader(f=f, delimiter = ';')
    for i, row in enumerate(dreader):
        if i > 100:
            break
        # Objecten aanmaken. Worden alleen vastgelegd als ze nieuw zijn.
        patient = pb.add_patient(**{v:row[k] for k, v in mapping['Patient'].items()})
        zorgtraject = pb.add_zorgtraject(**{v:row[k] for k, v in mapping['Zorgtraject'].items()})
        patient.add_child('Zorgtraject', zorgtraject)
        dbctraject = pb.add_dbctraject(**{v:row[k] for k, v in mapping['DBCtraject'].items()})
        zorgtraject.add_child('DBCTraject', dbctraject)
        tijd = pb.add_tijd(**{v:row[k] for k, v in mapping['Tijdschrijven'].items()})
        dbctraject.add_child('Tijdschrijven', tijd)
        diagnose = pb.add_diagnose(**{v:row[k] for k, v in mapping['Diagnose'].items()})
        dbctraject.add_child('Diagnose', diagnose)


print('aantal patienten in pakbon: {}'.format(pb._1542))
print('aantal zorgtrajecten in pakbon: {}'.format(pb._1543))
print('aantal DBCs in pakbon: {}'.format(pb._1544))
print('aantal diagnoses in pakbon: {}'.format(pb._1545))
print('aantal tijdschrijven in pakbon: {}'.format(pb._1546))


for key, patient in pb.patienten.items():
    for key, value in patient.children['Zorgtraject'].items():
        print(value.parent._1432)

print(50*'*')
print('DBCtrajecten')

for key, ztraject in pb.zorgtrajecten.items():
    for key, value in ztraject.children['DBCTraject'].items():
        print(value)

print(50*'*')
print('Diagnoses')

for key, dbc in pb.DBCtrajecten.items():
    for key, value in dbc.children['Diagnose'].items():
        print(value)

print(50*'*')
print('Tijdschrijven')

for key, dbc in pb.DBCtrajecten.items():
    print(len(dbc.children['Tijdschrijven']))
    for key, value in dbc.children['Tijdschrijven'].items():
        print(value.keys())
