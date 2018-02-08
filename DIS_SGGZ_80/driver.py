



from classes import Patient
from collections import OrderedDict
import csv, os

# kolomnamen mappen naar dis data ids
mapping = {
'Patient': OrderedDict(
    [('AGBCode', '_1430')
    ,('dis_volgnummer', '_1431')
    ,('client_id', '_1432')
    ,('client_achternaam', '_1433')
    ,('client_tussenvoegsels', '_1434')
    ,('dis_naamcode', '_1435')
    ,('client_partnernaam', '_1436')
    ,('client_partnernaam_tussenvoegsels', '_1437')
    ,('dis_naamcode_2', '_1438')
    ,('client_voorletters', '_1439')
    ,('client_postcode', '_1440')
    ,('client_huisnummer', '_1441')
    ,('Toevoeging', '_1442')
    ,('dis_landcode', '_1443')
    ,('client_geboortedatum', '_1444')
    ,('client_geslacht', '_1445')
    ,('client_bsn', '_1446')
    ,('datum_eerste_inschrijving', '_3182')
    ,('datum_laatste_uitschrijving', '_3183')
    ]
    )
}

dis_data_objecten = {
'Patienten': {}
,'Zorgtrajecten': {}
,'DBCtrajecten': {}
,'Diagnoses': {}
,'Tijdschrijven': {}
}

with open('../data/DIS_test.csv', newline = '', encoding = 'latin-1') as f:
    dreader = csv.DictReader(f=f, delimiter = ';')
    p_previous = str()
    for row in dreader:
        # check of deze patient ook in de vorige rij stond
        p_current = '_'.join([row['AGBCode'], row['dis_volgnummer'], row['client_id']])
        if p_previous == p_current:
            continue

        # patientgegevens in dictionary met items gemapt naar dis_ids
        dis_data_objecten['Patienten'][p_current] = Patient( **{
                v:row[k] for k, v in mapping['Patient'].items()
        })

        # Vorige rij nu overschrijven door deze rij
        p_previous = p_current

print(len(dis_data_objecten['Patienten'].keys()))
