#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
In this problem set you work with cities infobox data, audit it, come up with a
cleaning idea and then clean it up.

In the previous quiz you recognized that the "name" value can be an array (or
list in Python terms). It would make it easier to process and query the data
later if all values for the name are in a Python list, instead of being
just a string separated with special characters, like now.

Finish the function fix_name(). It will recieve a string as an input, and it
will return a list of all the names. If there is only one name, the list will
have only one item in it; if the name is "NULL", the list should be empty.
The rest of the code is just an example on how this function can be used.
"""
import codecs
import csv
import pprint
import os

    # {"elevation" : 1855,
    # "name" : "Kud",
    # "country" : "India",
    # "lon" : 75.28,
    # "lat" : 33.08,
    # "isPartOf" : [
    #     "Jammu and Kashmir",
    #     "Udhampur district"
    # ],
    # "timeZone" : [
    #     "Indian Standard Time"
    # ],
    # "population" : 1140}





CITIES = 'cities.csv'
MYCITIES = 'mycities.csv'
# FIELDS = {'name': 'name',
#         'nick': 'nick',
#         'city_label': 'city',
#         'country_label': 'country',
#         'anthem_label': 'anthem',
#         'motto': 'motto',
#         'code': 'code',
#         'synonym': 'synonym',
#         'twinCity_label': 'twinCity',
#         'twinCountry_label': 'twinCountry',
#         'foundingDate': 'foundingDate',
#         'foundingPerson_label': 'foundingPerson',
#         'foundingYear': 'foundingYear',
#         'governingBody_label': 'governingBody',
#         'government_label': 'government',
#         'governmentType_label': 'governmentType',
#         'administrativeDistrict_label': 'administrativeDistrict',
#         'federalState_label': 'federalState',
#         'leader_label': 'leader',
#         'leaderName_label': 'leaderName',
#         'leaderParty_label': 'leaderParty',
#         'leaderTitle': 'leaderTitle',
#         'mayor_label': 'mayor',
#         'daylightSavingTimeZone_label': 'daylightSavingTimeZone',
#         'timeZone_label': 'timeZone',
#         'utcOffset': 'utcOffset',
#         'district_label': 'district',
#         'division_label': 'division',
#         'region_label': 'region',
#         'state_label': 'state',
#         'municipality_label': 'municipality',
#         'postalCode': 'postalCode',
#         'areaCode' : 'areaCode',
#         'point': 'point',
#         'wgs84_pos#lat': 'lat',
#         'wgs84_pos#long': 'lon',
#         'isPartOf_label': 'isPartOf',
#         'isoCodeRegion_label': 'isoCodeRegion',
#         'area': 'area',
#         'areaLand': 'areaLand',
#         'areaWater': 'areaWater',
#         'percentageOfAreaWater': 'percentageOfAreaWater',
#         'areaMetro': 'areaMetro',
#         'areaRural': 'areaRural',
#         'areaUrban': 'areaUrban',
#         'elevation': 'elevation',
#         'maximumElevation': 'maximumElevation',
#         'minimumElevation': 'minimumElevation',
#         'populationMetro': 'populationMetro',
#         'populationMetroDensity': 'populationMetroDensity',
#         'populationUrban': 'populationUrban',
#         'populationUrbanDensity': 'populationUrbanDensity',
#         'populationRural': 'populationRural',
#         'populationTotal': 'population',
#         'populationTotalRanking': 'populationTotalRanking',
#         'populationAsOf': 'populationAsOf',
#         'populationDensity': 'populationDensity'
#          }
FIELDS = {'elevation': 'elevation',
         'rdf-schema#label': 'name',
         'country_label': 'country',
         'wgs84_pos#lat': 'lat',
         'wgs84_pos#long': 'lon',
         'isPartOf_label': 'isPartOf',
         'timeZone_label': 'timeZone',
         'populationTotal': 'population'}



def fix_datatype(s):
    try:
        s = float(s)
        if s.is_integer():
            return int(s)
        else:
            return s
    except (TypeError, ValueError):
        return s


def parse_array(v):
    if (v[0] == "{") and (v[-1] == "}"):
        v = v.lstrip("{")
        v = v.rstrip("}")
        v_array = v.split("|")
        v_array = [ fix_datatype(i.strip()) for i in v_array]
        return v_array
    return [v]

def process_file(filename, fields):
    data = []
    with open(filename, "r", encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        # skipping the extra metadata
        for i in range(3):
            # l = reader.next()
            l = next(reader)

        # processing file
        for line in reader:

            data_point = {}

            for key, value in fields.items():
                line[key] = fix_datatype(line[key])

                if str(line[key]) == 'NULL':
                    line[key] = None
                elif (str(line[key]).find("{") > -1 and str(line[key]).find("}") > -1):
                    line[key] = parse_array(str(line[key]))

                # print("{0} :: {1} :: {2}".format(key, line[key], type(line[key])))
                data_point[value] = line[key]
            # print(data_point)
            data.append(data_point)
    return data

# def WriteDictToCSV(csv_file,csv_columns,dict_data):
# 	try:
# 		with open(csv_file, 'w') as csvfile:
# 		    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
# 		    writer.writeheader()
# 		    for data in dict_data:
# 		    	writer.writerow(data)
# 	except IOError
# 	        print("I/O error({0}): {1}".format(errno, strerror))
# 	return

def write_csv_file(filename, csv_columns, data):
    try:
        with open(filename, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=csv_columns)
            writer.writeheader()
            for l in data:
                writer.writerow(l)
    except IOError:
        print("I/O error()")
    return

def insert_mongodb(data):
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017")
    db = client.examples

    collection = db.mycities
    for item in data:
        print(item)
        collection.insert(item)

def test():
    data = process_file(CITIES, FIELDS)

    # insert_mongodb(data)

    csv_columns = FIELDS.values()
    # print(csv_columns)
    write_csv_file(MYCITIES, csv_columns, data)

    # print("Printing 20 results:")
    # for n in range(20):
    #     pprint.pprint(data[n]["name"])
    #
    # assert data[14]["name"] == ['Negtemiut', 'Nightmute']
    # assert data[9]["name"] == ['Pell City Alabama']
    # assert data[3]["name"] == ['Kumhari']

if __name__ == "__main__":
    test()
