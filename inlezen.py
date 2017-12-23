import csv, pprint


pp = pprint.PrettyPrinter(indent=4)

with open('format_patient.csv') as format_file:
    format_dict = [{key: value for key, value in row.items()}
                    for row in csv.DictReader(format_file)]


pp.pprint(format_dict)
