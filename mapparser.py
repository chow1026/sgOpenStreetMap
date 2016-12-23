#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Your task is to use the iterative parsing to process the map file and
find out not only what tags are there, but also how many, to get the
feeling on how much of which data you can expect to have in the map.
Fill out the count_tags function. It should return a dictionary with the
tag name as the key and number of times this tag can be encountered in
the map as value.

Note that your code will be tested with a different data file than the 'example.osm'
"""
import xml.etree.cElementTree as ET
import pprint

def loop_tags():
    pass

def count_tags(filename):

    tags = {}

    tree = ET.parse(filename)
    root = tree.getroot()
    tag_elems = list(root.iter())

    tag_list = []
    for i in tag_elems:
        tag_list.append(i.tag)
    # print(tag_list, len(tag_list))

    for j in tag_list:
        tags[j] = tag_list.count(j)

    return tags


def test():

    tags = count_tags('example.osm')
    pprint.pprint(tags)
    assert tags == {'bounds': 1,
                     'member': 3,
                     'nd': 4,
                     'node': 20,
                     'osm': 1,
                     'relation': 1,
                     'tag': 7,
                     'way': 1}



if __name__ == "__main__":
    test()
