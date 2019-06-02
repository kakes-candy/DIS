import sqlite3
conn = sqlite3.connect('dis_sggz_80.db')


c = conn.cursor()

# Create table
c.execute('''CREATE TABLE stocks
             (date text, trans text, symbol text, qty real, price real)''')




'cl_activiteit_begindatum'
,'cl_activiteit_einddatum'
,'cl_activiteit_code'
,'cl_activiteit_groepcode'
,'cl_activiteit_element'
,'cl_activiteit_beschrijving'	
,'cl_activiteit_aanspraak_type'
,'cl_activiteit_hierarchieniveau'
,'cl_activiteit_selecteerbaar'
,'cl_activiteit_sorteervolgorde'
,'cl_activiteit_soort'
,'cl_activiteit_mag_direct'
,'cl_activiteit_mag_indirect'
,'cl_activiteit_mag_reistijd'
,'cl_activiteit_mag_groep'
,'cl_activiteit_mutatie'
,'cl_activiteit_branche_indicatie'
