
import zipfile
from os import listdir
from os.path import isfile, join, splitext

bronmap = 'Test rapportages/2017-02 11_09'

# Bestanden in bronmap
dir = listdir(bronmap)

# DIS aanleverbestand
filename =  [f for f in listdir(bronmap) if isfile(join(bronmap, f)) and splitext(f)[1] == '.zip'][0]

# Naam map om uit te pakken is zelfde als bestandsnaam zonder extensie
targetdir = join(bronmap, splitext(filename)[0])


# Bestanden uitpakken in bronmap
with zipfile.ZipFile(join(bronmap, filename), "r") as zip_ref:
    zip_ref.extractall(targetdir)
