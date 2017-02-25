#!, usr, bin, env python
# -*- coding: utf-8 -*-

"""

This script is to 
1) Filter and include ONLY node elements that have 'name' or
'alt_name'.  Use 'alt_name' when 'name' not available, Include 'alt_name' if
'name' available.   
2) Get data for meaningful keys such as: 'user', 
'name' and/or 'alt_name', 'amentity' and/or 'amenity_1',  'addr:unit', 
'addr:housename', 'addr:housenumber', 'addr:postcode', 'addr:street', 'contact:email' and/or 'email', 'contact:facebook' 
and/or 'facebook', 'contact:fax' and/or 'fax', 'contact:google_plus', 
'contact:instagram', 'contact:phone' and/or 'phone', 'contact:twitter', 
'contact:website' and/or 'website', 'exit_to', 'highway', 'religion', 'cuisine', 'demonition'
3) Consolidate repeated keys and values (such as 'contact:email' & 'email', 'amenity' & 'amenity_1') 
4) Clean up data format for phone/fax numbers, website urls and emails.  
5) Extract cleaned, meaningful node data from OSM to JSON file.

"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import json
import io
import re
import pprint

p_addrUnit = re.complie(r"\w{1,}-\w{2,}")

def format_cuisine(str_value):
	return str_value.replace('_', ' ').strip().title()

def split_value_to_list(str_value):
	split_chars = [';', ',', '/', 'or']
	lst_value = []
	for char in split_chars: 
		if str_value.find(char) > -1:
			lst_value = str_value.split(char)
		else: 
			lst_value.append(str_value)
	return lst_value

def format_addrunit(str_unit):
	if !str_unit.startswith('#'):
		return '#' + str_unit
	return str_unit

def format_url(str_url):
	if !str_url.startswith('http'):
		return 'http://' + str_url
	return str_url

def format_phonefax(str_phonefax):
	rm_chars = ['(', ')', ' ', '-']
	for char in rm_chars: 
		str_phonefax.replace(char, '')
	if len(str_phonefax) == 10 and str_phonefax.startswith('65'):
		str_phonefax = '+' + str_phonefax
	elif len(str_phonefax) == 8:
		str_phonefax = '+65' + str_phonefax
	elif str_phonefax.find('1800') > -1:
		str_phonefax = str_phonefax[str_phonefax.find('1800'):]
	return str_phonefax

def fix_phonefax(val_phonefax):


def fix_cuisine(val_cuisine):
	lst_cuisine = split_value_to_list(str_cuisine)
	for c in lst_cuisine:
		format_cuisine(c)
	return lst_cuisine


def got_name(elem):
	for tag in elem.iter("tag"):
        k = tag.attrib['k']
        if k =='name' or k =='alt_name':
        	return True
	return False


def get_node_with_name_altname(osm_file, tags=('node')):
	context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            if got_name(elem):
                yield elem
            root.clear()
 
def audit(osmfile, tags):
    osm_file = open(osmfile, "r")
    unique_kv = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag in tags:

            for tag in elem.iter("tag"):
                k = tag.attrib['k']
                v = tag.attrib['v']
                # m1 = p_seamark.match(k)
                # m2 = p_turn.match(k)

                if k not in IRRELEVANT_keys and m1 == None and m2 == None:
                    unique_kv[k].add(v)

    osm_file.close()
    return unique_kv

def test():
    tag_unique_kv = audit(OSM_FILE, ['node'])
    # odd_postcode(tag_unique_kv)
    # print(odd_postcodes)
    pprint.pprint(tag_unique_kv)

if __name__ == "__main__":
    test()