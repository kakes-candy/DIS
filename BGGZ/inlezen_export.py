from classes import Patient, Pakbon, Behandeltraject, GeleverdZorgprofiel
from collections import OrderedDict
import csv, os
from pathlib import Path as plib_path


bronmap = "BGGZ/Test_rapportages/Bggz-201412-Created-20190509_135234/DIS_GBG_TRJ_TEST_020_73730802_01_20190509_01"

print(os.getcwd())

# Submap voor ingelezen bestanden aanmaken in bronmap
try:
    os.mkdir(os.path.join(plib_path(bronmap).parent, "uitgelezen"))
except FileExistsError:
    print("Directory not created")


with open(os.path.join(bronmap, "PAKBON.txt"), "r") as f_pakbon:
    p = f_pakbon.readline()
    # print(Pakbon.from_string(p).write_to_dict())

with open(os.path.join(bronmap, "PATIENT.txt"), "r") as f_patient:

    headers_patient = [x["Naam"] for x in Patient().format_definitions]
    with open(
        os.path.join(bronmap, "ingelezen", "patient.csv"), "w", newline=""
    ) as outfile:
        writer = csv.DictWriter(outfile, delimiter=";", fieldnames=headers_patient)
        writer.writeheader()
        for line in f_patient:
            patient = Patient.from_string(line)
            writer.writerow(patient.write_to_dict())


with open(os.path.join(bronmap, "BEHANDELTRAJECT.txt"), "r") as f_behandeltraject:

    headers_behandeltraject = [x["Naam"] for x in Behandeltraject().format_definitions]
    with open(
        os.path.join(bronmap, "ingelezen", "dbctraject.csv"), "w", newline=""
    ) as outfile:
        writer = csv.DictWriter(
            outfile, delimiter=";", fieldnames=headers_behandeltraject
        )
        writer.writeheader()
        for line in f_behandeltraject:
            dbctraject = Behandeltraject.from_string(line)
            writer.writerow(dbctraject.write_to_dict())


with open(os.path.join(bronmap, "GELEVERD_ZORGPROFIEL.txt"), "r") as f_tijdschrijven:

    headers_zorgprofiel = [x["Naam"] for x in GeleverdZorgprofiel().format_definitions]
    with open(
        os.path.join(bronmap, "ingelezen", "geleverd_zorgprofiel.csv"), "w", newline=""
    ) as outfile:
        writer = csv.DictWriter(outfile, delimiter=";", fieldnames=headers_zorgprofiel)
        writer.writeheader()
        for line in f_tijdschrijven:
            zorgprofiel = GeleverdZorgprofiel.from_string(line)
            writer.writerow(zorgprofiel.write_to_dict())
