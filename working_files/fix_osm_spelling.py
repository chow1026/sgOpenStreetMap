#!, usr, bin, env python
# -*- coding: utf-8 -*-

"""

This script is to
1) Change abbreviations and hyphenation of streets and housenames to full names.
2) Correct Spelling Errors for housenames, streets.

"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint


INPUT_OSM_FILE = "singapore_fixed_data_9.osm"  # Replace this with your osm file
OUTPUT_OSM_FILE = "singapore_fixed_9.osm"

ABBREV_KEYS = {'Ave': 'Avenue',
'ave': 'Avenue',
'avenue': 'Avenue',
'Blvd': 'Boulevard',
'Rd': 'Road',
'rd': 'Road',
'road': 'Road',
'St': 'Street',
'st': 'Street',
'Dr': 'Drive',
'dr': 'Drive',
'Ind': 'Industrial',
'terrace': 'Terrace',
'Cresent': 'Crescent',
'Lor': 'Lorong',
'lor': 'Lorong',
'Ind': 'Industrial',
'Upp': 'Upper',
'Bt': 'Bukit',
'Jln': 'Jalan',
'jln': 'Jalan',
'Bkt': 'Bukit',
'Ctr': 'Centre',
'ctr': 'Centre',
'Nth': 'North',
'Bldg': 'Building',
'bldg': 'Building',
'Water Venture': 'Water-Venture'}

TYPO_FIXES = {'Hongkong Street': 'Hong Kong Street',
'Bayfront Avebue': 'Bayfront Avenue',
'Mackenzie Road': 'MacKenzie Road',
'King Albet Park': 'King Albert Park',
'Macpherson Road': 'MacPherson Road',
'Maragaret Drive': 'Margaret Drive',
'Serangoon Aenue 1': 'Serangoon Avenue 1',
'Sin Min Ave': 'Sin Ming Avenue',
'Marind Drive': 'Marine Drive',
"St Andrew's Road": "St. Andrew's Road",
"St Michael's Road": "St. Michael's Road",
"St Patrick's Road": "St. Patrick's Road",
'St Wilfred Road': "St. Wilfred's Road",
"St. George's Lane": "St Michael's Road",
'Tiban Mc Dermoth': 'Jalan Tiban McDermoth',
'Jalan Yayang Layang': 'Jalan Layang Layang',
'Botania Garden': 'Botanic Garden',
'Gutrie House': 'Guthrie House',
'Heleconia': 'Heliconia',
'I12 Katong': '112 Katong',
'Odeo Tower': 'Odeon Tower',
'Pinnacle@Duxton': 'The Pinnacle@Duxton',
'ThePeak@Balmeg': 'The Peak@Balmeg',
'Twr 3': 'The Bayshore Tower 3',
'Ubi Techpark': 'Ubi TechPark',
'Yio Chu Kang Sport Hall': 'Yio Chu Kang Sports Hall',
'Water Venture Bedok Reservoir': 'Water-Venture Bedok Reservoir',
'Water Venture East Coast': 'Water-Venture East Coast',
'Bah Soon Pah Rd': 'Bah Soon Pah Rd',
'singapore': 'Singapore',
'+6667021031': '+6567021031'}

# 1. correct
# 2. make is title
# 3. fix abbrev


def replace_abbreviate(str_value):
    lst_str = str_value.split()
    new_lst_str = [ABBREV_KEYS[w] if w in ABBREV_KEYS.keys() else w for w in lst_str]
    return ' '.join(new_lst_str)
  

def fix_spelling_case(elem):
    keys = ['addr:street', 'addr:housename', 'addr:city', 'contact:phone', 'phone']
    for tag in elem.iter("tag"):
        k = tag.attrib['k']
        v = tag.attrib['v']
        new_v = ""

        if k in keys :
            print('v: {0}'.format(v))
            if v in TYPO_FIXES.keys():
                v = TYPO_FIXES[v]
            v = replace_abbreviate(v)
            tag.set('v', v)
    return elem


def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http:, , stackoverflow.com, questions, 3095434, inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)

    for event, elem in context:

        if event == 'end' and elem.tag in tags:

            yield fix_spelling_case(elem)
            root.clear()


with open(OUTPUT_OSM_FILE, 'wb') as output:
    output.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write(b'<osm>\n')

    # Write every kth top level element
    for i, element in enumerate(get_element(INPUT_OSM_FILE)):
        # if i % k == 0:
        output.write(ET.tostring(element, encoding='utf-8'))

    output.write(b'</osm>')
