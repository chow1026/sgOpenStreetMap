#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

This script is used to examine use regex to filter out postcodes that are non Singapore
postcode format.
The odd postcode list were then used to manually google to determine if the 
node/way/relation is singapore data. 
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import re


p_odd_postcode = re.compile(r"\d{6}")
p_MY_postcode = re.compile(r"(8|7)\d{4}")

OSM_FILE = "singapore.osm"


def audit_postcode(osmfile, tags):
    osm_file = open(osmfile, "r")
    non_sg_postcodes = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag in tags:
            for tag in elem.iter("tag"):
                k = tag.attrib['k']
                v = tag.attrib['v']
                if k == 'addr:postcode':
                	if not p_MY_postcode.match(v) == None and len(v) == 5:
			            non_sg_postcodes['MY'].add(v)
			        elif p_odd_postcode.match(v) == None:
			            non_sg_postcodes['odd'].add(v)
                
    osm_file.close()
    return non_sg_postcodes

def test():
    non_sg_postcodes = audit_postcode(OSM_FILE, ['node', 'way', 'relation'])
    pprint.pprint(non_sg_postcodes)

if __name__ == "__main__":
    test()





