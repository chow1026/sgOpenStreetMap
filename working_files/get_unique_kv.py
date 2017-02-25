#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

This script is used to generate dictionaries of NODES, WAYS and RELATIONS, that consists of
the unique values of attribute k values and unique corresponding values of
attribute v, for each of the <tag> children in <node> tags and <way> tags. The
process should help identify the problems with the dataset.

p_seamark is a regex that exclude all seamark related keys, as I can't really make use of those data.
Same with p_turn, a regex that exclude all turn related keys.

Other fields I couldn't interpret or not useful at the moment, I list as ng_keys.
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint

import re

p_seamark = re.compile(r"seamark(:\w*){0,3}")
p_turn = re.compile(r"turn(:\w*)*")


IRRELEVANT_keys = ['3dr:type', 'Avg_Horz_P', 'Avg_Vert_P', 'Comment', 'Corr_Type', 'Datafile', 'DateTimeS', 'Easting', 'Elevation', 'FIXME', 'Feat_Name', 'Filt_Pos', 'FolderPath', 'GNSS_3DLen', 'GNSS_Heigh', 'GNSS_Lengt', 'GPS_Date', 'GPS_Second', 'GPS_Time', 'GPS_Week', 'Horz_Prec', 'Id', 'Line_ID', 'Max_HDOP', 'Max_PDOP', 'Northing', 'OBJECTID', 'Point_ID', 'Rcvr_Type', 'SHAPE_Leng', 'Shape_Area', 'Shape_Leng', 'Std_Dev', 'Unfilt_Pos', 'Update_Sta', 'Vert_Prec', 'Worst_Horz', 'Worst_Vert', 'asset_ref', 'building:colour', 'building:height', 'catmp-RoadID', 'description', 'description2', 'ele', 'ele:msl', 'ele:note', 'ele:source', 'fixme', 'garmin_road_class', 'garmin_type', 'gns:dsg', 'gns:uni', 'height', 'naptan:Bearing', 'note', 'ref', 'roof:colour', 'roof:direction', 'roof:height', 'route_ref', 'wikidata', 'wikipedia', 'Latitude', 'Longitude']

OSM_FILE = "singapore_fixed_10.osm"


def audit(osmfile, tags):
    osm_file = open(osmfile, "r")
    unique_kv = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag in tags:
            for tag in elem.iter("tag"):
                k = tag.attrib['k']
                v = tag.attrib['v']
                m1 = p_seamark.match(k)
                m2 = p_turn.match(k)

                if k not in IRRELEVANT_keys and m1 == None and m2 == None:
                    unique_kv[k].add(v)

    osm_file.close()
    return unique_kv

def test():
    tag_unique_kv = audit(OSM_FILE, ['node', 'way', 'relation'])
    pprint.pprint(tag_unique_kv)


if __name__ == "__main__":
    test()
