#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script is used to generate list of keys by node, way, relation for initial examination
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint

OSM_FILE = "singapore_fixed_10.osm"


def audit(osmfile, tags):
    osm_file = open(osmfile, "r")
    unique_keys = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag in tags:
            for tag in elem.iter("tag"):
                k = tag.attrib['k']
                unique_keys[elem.tag].add(k)

    osm_file.close()
    return unique_keys

def test():
    unique_keys = audit(OSM_FILE, ['node', 'way', 'relation'])
    pprint.pprint(unique_keys)


if __name__ == "__main__":
    test()
