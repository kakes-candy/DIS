from SGGZ_8_0.cl_aanlevering import Aanlevering_SGGZ
from collections import OrderedDict
import csv, os
from pprint import pprint
from pathlib import Path as plib_path


bronmap = r"SGGZ_8_0\Test_rapportages\2017-03"
doelmap = os.path.join(bronmap, "opnieuw_ingepakt")
doelmap_csv = os.path.join(bronmap, "uitgelezen")
dis_zip = r"DIS_GGZ_DBC_PROD_080_73730802_01_20190410_01.zip"


# Submap voor ingelezen bestanden aanmaken in bronmap
try:
    os.mkdir(doelmap_csv)
except FileExistsError:
    print("Directory not created")


aanlevering = Aanlevering_SGGZ()

aanlevering.inlezen_vanuit_zip(os.path.join(bronmap, dis_zip))

# aanlevering.inlezen_vanuit_map(bronmap)

print(len(aanlevering.patienten))
print(len(aanlevering.zorgtrajecten))
print(len(aanlevering.dbctrajecten))
print(len(aanlevering.tijdschrijven))
print(len(aanlevering.diagnoses))


aanlevering.validate(autocorrect=True)

# Patienten valideren en verwijderen
for invalid_patient in [
    x.__str__() for x in aanlevering.patienten.values() if x.valid == False
]:
    aanlevering.del_patient(invalid_patient)

# Zorgtrajecten valideren en verwijderen
for invalid_traject in [
    x.__str__() for x in aanlevering.zorgtrajecten.values() if x.valid == False
]:
    aanlevering.del_zorgtraject(invalid_traject)

# dbc valideren en verwijderen
for invalid_dbc in [
    x.__str__() for x in aanlevering.dbctrajecten.values() if x.valid == False
]:
    aanlevering.del_dbctraject(invalid_dbc)

# tijdschrijven valideren en verwijderen
for invalid_tijd in [
    x.__str__() for x in aanlevering.tijdschrijven.values() if x.valid == False
]:
    aanlevering.del_tijdschrijven(invalid_tijd)

# diagnoses valideren en verwijderen
for invalid_diagnoses in [
    x.__str__() for x in aanlevering.diagnoses.values() if x.valid == False
]:
    aanlevering.del_diagnose(invalid_diagnoses)

# Even laten zien wat er uit de validatie kwam
print(aanlevering.meldingen)
print(aanlevering.bewerkingen)

# opgeschoonde data wegschrijven.
# aanlevering.exporteren_zip(doelmap=doelmap, volgnummer=2)
# aanlevering.exporteren_csv(doelmap_csv)

