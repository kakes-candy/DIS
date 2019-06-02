
import zipfile
from os import listdir
from os.path import isfile, join, splitext
from classes import Patient, Pakbon, Zorgtraject, DBCTraject, Tijdschrijven, Diagnose, PakbonTekst

bronmap = 'Test rapportages/2017-02 11_09'

# Bestanden in bronmap
dir = listdir(bronmap)

# DIS aanleverbestand
filename =  [f for f in listdir(bronmap) if isfile(join(bronmap, f)) and splitext(f)[1] == '.zip'][0]

# Naam map om uit te pakken is zelfde als bestandsnaam zonder extensie
targetdir = join(bronmap, splitext(filename)[0])


# De bestandsnaam bevat gegevens, splitsen in het algemene deel, de aanleverdatum en het volgnummer
algemeen = filename[:33]
aanleverdatum = filename[33:41]
volgnummer = filename[42:44]


PakbonTekst().help()


# Bestanden uitpakken in bronmap
with zipfile.ZipFile(join(bronmap, filename), "r") as zip_ref:
    zip_ref.extractall(targetdir)

# Pakbon uitlezen
with open(join(targetdir, 'pakbon.txt'), 'r' ) as f_pakbon:
    p = f_pakbon.readline()
    pakbonnetje = PakbonTekst.from_string(p)

print(pakbonnetje.write_to_dict())

# Gegevens uit pakbon halen
bestandsnaam = pakbonnetje._1538
bestandsnaam_algemeen = filename[:32]
creatiedatum = pakbonnetje._1537
volgnummer = pakbonnetje._3006
extensie = '.zip'

# volgnummer ophogen
pakbonnetje._3006 = str(int(volgnummer) + 1).zfill(2)

# bestandsnaam aanpassen met opgehoogd volgnummer
pakbonnetje._1538 = ('_'.join([bestandsnaam_algemeen, creatiedatum, pakbonnetje._3006]) + extensie)


# Checken of de het aantal regels per bestand nog klopt
with open(join(targetdir, 'patient.txt'), 'r' ) as f_patient:
    N_patient = sum(1 for line in f_patient)
    print(N_patient)
    pakbonnetje._1542 = str(N_patient)

with open(join(targetdir, 'zorgtraject.txt'), 'r' ) as f_zorgtraject:
     N_zt = sum(1 for line in f_zorgtraject)
     print(N_zt)
     pakbonnetje._1543 = str(N_zt)

with open(join(targetdir, 'dbc_traject.txt'), 'r' ) as f_dbctraject:
     N_dbc = sum(1 for line in f_dbctraject)
     print(N_dbc)
     pakbonnetje._1544 = str(N_dbc)

with open(join(targetdir, 'geleverd_zorgprofiel_tijdschrijven.txt'), 'r' ) as f_tijdschrijven:
     N_tijd = sum(1 for line in f_tijdschrijven)
     print(N_tijd)
     pakbonnetje._1546 = str(N_tijd)

with open(join(targetdir, 'diagnose.txt'), 'r' ) as f_diagnose:
     N_diagnose = sum(1 for line in f_diagnose)
     print(N_diagnose)
     pakbonnetje._1545 = str(N_diagnose)


# Pakbon wegschrijven
with open(join(targetdir, 'pakbon.txt'), 'w' ) as f_pakbon:
    f_pakbon.write(pakbonnetje.write_to_string())



# Pakbon opnieuw uitlezen
with open(join(targetdir, 'pakbon.txt'), 'r' ) as f_pakbon:
    p = f_pakbon.readline()
    pakbonnetje = PakbonTekst.from_string(p)


print(pakbonnetje.write_to_dict())
