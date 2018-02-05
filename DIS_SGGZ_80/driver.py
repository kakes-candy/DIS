



from classes import Patient
import csv, os


with open('../data/DIS_test.csv', newline = '', encoding = 'latin-1') as f:
    next(f)
    reader = csv.reader(f, delimiter = ';')
    lijst = []
    for index, row in enumerate(reader):
        if index > 10:
            break
        else:
            lijst.append(Patient().from_list(row))
