
import zipfile
import shutil
from os import listdir
from os.path import isfile, join, splitext
from classes import Patient, Pakbon, Zorgtraject, DBCTraject, Tijdschrijven, Diagnose, PakbonTekst
from pathlib import Path as plib_path



"""
Configuratie van script
"""
# Map waar nieuw in te pakken bestanden staan
bronmap = 'Test rapportages/DIS aanleveringen/PROD/2019-02/DIS_GGZ_DBC_PROD_080_73730802_01_20190414_01'

# Nummer ophogen of niet (None).
nieuw_volgnummer = 20


print(plib_path(bronmap).parent)


# Pakbon uitlezen
with open(join(bronmap, 'pakbon.txt'), 'r' ) as f_pakbon:
    p = f_pakbon.readline()
    pakbonnetje = PakbonTekst.from_string(p)

print(pakbonnetje.write_to_dict())

# Gegevens uit pakbon halen
bestandsnaam = pakbonnetje._1538
bestandsnaam_algemeen = bestandsnaam[:32]
print(bestandsnaam_algemeen)
creatiedatum = pakbonnetje._1537
volgnummer = pakbonnetje._3006
extensie = '.zip'

# volgnummer ophogen
if nieuw_volgnummer:
    pakbonnetje._3006 = str(nieuw_volgnummer).zfill(2)

# bestandsnaam aanpassen met opgehoogd volgnummer
nieuwe_bestandsnaam = '_'.join([bestandsnaam_algemeen, creatiedatum, pakbonnetje._3006])

pakbonnetje._1538 = (nieuwe_bestandsnaam + extensie)


# Checken of de het aantal regels per bestand nog klopt
with open(join(bronmap, 'patient.txt'), 'r' ) as f_patient:
    N_patient = sum(1 for line in f_patient)
    print(N_patient)
    pakbonnetje._1542 = str(N_patient)

with open(join(bronmap, 'zorgtraject.txt'), 'r' ) as f_zorgtraject:
     N_zt = sum(1 for line in f_zorgtraject)
     print(N_zt)
     pakbonnetje._1543 = str(N_zt)

with open(join(bronmap, 'dbc_traject.txt'), 'r' ) as f_dbctraject:
     N_dbc = sum(1 for line in f_dbctraject)
     print(N_dbc)
     pakbonnetje._1544 = str(N_dbc)

with open(join(bronmap, 'geleverd_zorgprofiel_tijdschrijven.txt'), 'r' ) as f_tijdschrijven:
     N_tijd = sum(1 for line in f_tijdschrijven)
     print(N_tijd)
     pakbonnetje._1546 = str(N_tijd)

with open(join(bronmap, 'diagnose.txt'), 'r' ) as f_diagnose:
     N_diagnose = sum(1 for line in f_diagnose)
     print(N_diagnose)
     pakbonnetje._1545 = str(N_diagnose)


# Pakbon wegschrijven
with open(join(bronmap, 'pakbon.txt'), 'w' ) as f_pakbon:
    f_pakbon.write(pakbonnetje.write_to_string()+'\n')

# Nieuw zipbestand maken met de juiste naam
shutil.make_archive(join(plib_path(bronmap).parent, 'opnieuw_ingepakt', nieuwe_bestandsnaam), 'zip', bronmap)
