#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

This script is to exclude/remove the NODES and WAYS and RELATIONS that aren't Singapore SG data.
This is for first round - Filter by most obvious values: Country, State, City, Town, Suburb, Region etc.

"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
from json import dumps, loads, JSONEncoder, JSONDecoder
import pickle


NODES = defaultdict(set)
WAYS = defaultdict(set)

INPUT_OSM_FILE = "singapore_raw.osm"  # Replace this with your osm file
OUTPUT_OSM_FILE = "singapore_sg_0.osm"


def is_SG(elem):

    # keys = ['addr:country', 'is_in', 'is_in:country', 'is_in:country_code']
    # values = ['SG', 'Singapore', 'Sentosa']
    keys = ['addr:city', 'addr:complex', 'addr:country', 'addr:full', 'addr:place', 'addr:postcode', 'addr:state', 'addr:subdistrict', 'addr:suburb', 'addr:town', 'alt_name:ms', 'destination', 'is_in', 'is_in:city', 'is_in:country', 'is_in:country_code', 'is_in:county', 'is_in:region', 'is_in:state', 'is_in:town']

    Non_SG_Values = ['Bandar Baru Permas Jaya', 'Batam', 'Batam Centre', 'Batam Kep.Riau', 'Batam Kota', 'Bintan', 'Danga Bay', 'Gelang Patah', 'JB', 'Johor Bahru', 'Karimun', 'Kota Tinggi', 'Kulai', 'Masai', 'Nusajaya', 'Pasir Gudang, Johor', 'Permas Jaya', 'Pulai Johor', 'SKUDAI', 'Sekupang', 'Skudai', 'Sungai Rengit', 'Taman Century', 'Taman Johor Jaya', 'Taman Ponderosa, Johor Bahru', 'Tanjung Puteri', 'Ulu Tiram', 'batam Kota', 'johor Bahru', 'Perumahan Taman Valencia', 'Perumahan Tering Raya', 'ID', 'MY', 'Jalan Raya Pelabuhan Kabil . Kampung Baru Kabil. ', 'Nongsa Batam', 'Masjid Al-Hidayah. Perumahan Taman Valencia Kel. ', 'Belian. Kec. Batam Kota', 'Skudai', 'Taman Bukit Indah', 'Johor Bahru', 'Kepulauan Riau', 'Johor', 'Bandar Medini', 'Nusajaya', 'Jalan Johor', 'Jambatan Sungai Johor', 'Lebuhraya Johor Bahru-Kota Tinggi', 'Lebuhraya Senai', 'Taman Istana', 'Jalan Wangi', 'Kawasan Perindustrian Senai', 'Pandan-Tebrau', 'Senai Selatan', 'Senai Utara', 'Sungai Besi', 'Taman Perling', 'Tanjung Kupang', 'Ulu Pulai', 'Batam Kota', 'Batu Aji', 'Batu Pahat, Johor, Malaysia', 'Bengkong', 'Bintan, Riau Islands', 'Galang', 'Johor', 'Johor Bahru, Johor, Malaysia', 'Kota Tinggi, Johor, Malaysia', 'Kukup', 'Kukup Laut', 'Kulai, Johor, Malaysia', 'Layang-Layang, Kulai, Johor', 'Layang-Layang, Kulai, Johor, Malaysia', 'Leisure Farm', 'Malaysia', 'Murni Jaya, Layang-Layang, Kulai, Johor', 'Pontian, Johor, Malaysia', 'Tanjung Balai Karimun', 'Tanjung Piai, Pontian, Johor, Malaysia', 'Batam', 'Kota Madya Batam', 'Malaysia', 'Indonesia', 'ID', 'MY', 'Batu Ampar', 'Belakang Padang', 'Bintan Timur', 'Bintan Utara', 'Bukit Bestari', 'Bulang', 'Buru', 'Galang', 'Karimun', 'Kundur Barat', 'Kundur Utara', 'Lubuk Baja', 'Meral', 'Moro', 'Nongsa', 'Rangsang', 'Sei Beduk', 'Sekupang', 'Tanjung Pinang Barat', 'Tanjung Pinang Timur', 'Tanjungpinang Kota', 'Tebing', 'Teluk Bintan', 'Teluk Sebung', 'Bengkalis', 'Karimun', 'Kepulauan Riau', 'Kota Batam', 'Kota Tanjung Pinang', 'Jawa Timur', 'Johor', 'Kepulauan Riau', 'Province of Kepulauan Riau', 'Province of Riau Islands', 'Riau', 'Batam Kota','Batu Ampar', 'Bengkong', 'Nongsa', 'Sungai Beduk']


    for tag in elem.iter("tag"):
        k = tag.attrib['k']
        v = tag.attrib['v']
        if k in keys and v in Non_SG_Values:
            # print(k, v)
            return False
    return True

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)

    for event, elem in context:

        if event == 'end' and elem.tag in tags:
            in_SG = is_SG(elem)
            if in_SG:
                # print(elem.attrib['id'])
                yield elem
            root.clear()


with open(OUTPUT_OSM_FILE, 'wb') as output:
    output.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write(b'<osm>\n')

    # Write every kth top level element
    for i, element in enumerate(get_element(INPUT_OSM_FILE)):
        # if i % k == 0:
        output.write(ET.tostring(element, encoding='utf-8'))

    output.write(b'</osm>')

#
# def test():
#
#     node_unique_kv = audit(OSM_FILE, "node")
#     way_unique_kv = audit(OSM_FILE, "way")
#     # j = dump(node_unique_kv, open("nodes.json",'w'), cls=PythonObjectEncoder)
#     # with open('nodes.json', 'wb') as outfile:
#         # pickle.dump(node_unique_kv, outfile)
#     pprint.pprint(node_unique_kv)
#     # pprint.pprint(way_unique_kv)
#
#
#
#
#
# if __name__ == "__main__":
#     test()
