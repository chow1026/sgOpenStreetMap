"""
Your task is to check the "productionStartYear" of the DBPedia autos datafile for valid values.
The following things should be done:
- check if the field "productionStartYear" contains a year
- check if the year is in range 1886-2014
- convert the value of the field to be just a year (not full datetime)
- the rest of the fields and values should stay the same
- if the value of the field is a valid year in the range as described above,
  write that line to the output_good file
- if the value of the field is not a valid year as described above,
  write that line to the output_bad file
- discard rows (neither write to good nor bad) if the URI is not from dbpedia.org
- you should use the provided way of reading and writing data (DictReader and DictWriter)
  They will take care of dealing with the header.

You can write helper functions for checking the data and writing the files, but we will call only the
'process_file' with 3 arguments (inputfile, output_good, output_bad).
"""
import csv
import pprint
from datetime import date

INPUT_FILE = 'autos.csv'
OUTPUT_GOOD = 'autos-valid.csv'
OUTPUT_BAD = 'FIXME-autos.csv'
OUTPUT_DISCARD = 'autos-invalid.csv'

def sourced_from_dbpedia(row):
    print(row['URI'])
    if row['URI'].find("dbpedia.org") == -1:
        return False
    else:
        return True

def datetime_to_year(datetime):
    if datetime.find('01-01') == -1:
        return datetime
    else:
        return datetime[:4]


def within_range(start_year, end_year, year):
    if year >= start_year and year <=end_year:
        return True
    else:
        return False

def process_file(input_file, output_good, output_bad):

    data_bad = []
    data_good = []
    with open(input_file, "r") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames

        for row in reader:
            print(sourced_from_dbpedia(row))
            if sourced_from_dbpedia(row):
                productionStartYear = datetime_to_year(row['productionStartYear'])
                # row['productionStartYear'] = productionStartYear
                # if productionStartYear != 'NULL' and productionStartYear.isdigit() and within_range(1886, 2014, int(productionStartYear)):
                #     data_good.append(row)
                # else:
                #     data_bad.append(row)
                try: # use try/except to filter valid items
                    productionStartYear = int(productionStartYear)
                    row['productionStartYear'] = productionStartYear
                    if (productionStartYear >= 1886) and (productionStartYear <= 2014):
                        data_good.append(row)
                    else:
                        data_bad.append(row)
                except ValueError: # non-numeric strings caught by exception
                    if ps_year == 'NULL':
                        data_bad.append(row)

    with open(output_good, "w") as g:
            writer = csv.DictWriter(g, delimiter=",", fieldnames= header)
            writer.writeheader()
            for row in data_good:
                writer.writerow(row)

    with open(output_bad, "w") as b:
            writer = csv.DictWriter(b, delimiter=",", fieldnames= header)
            writer.writeheader()
            for row in data_bad:
                writer.writerow(row)


def test():

    process_file(INPUT_FILE, OUTPUT_GOOD, OUTPUT_BAD)


if __name__ == "__main__":
    test()
