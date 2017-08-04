#!, usr, bin, env python
# -*- coding: utf-8 -*-

"""

This script is to extract cleaned data from OSM to JSON file.

"""

import xml.etree.cElementTree as ET
import json
import io
import re
import pprint
import codecs


CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
NODES = []
WAYS = []
RELATIONS = []

def split_value_to_list(str_value):
    split_chars = [';', ',', '/']
    lst_value = list()
    for char in split_chars: 
        if str_value.find(char) > -1:
            lst_value = str_value.split(char)
    if len(lst_value) == 0:
        lst_value.append(str_value)
    print('str_to_list :: str_value: {0}, lst_value: {1}'.format(str_value, lst_value))
    return lst_value

def got_name(elem):
	for tag in elem.iter("tag"):
		k = tag.attrib['k']
		if k =='name' or k =='alt_name' or k == 'name:en' or k == 'alt_name:en':
			return True
	return False

def shape_element(element):
	node = {}

	if (element.tag == "node" or element.tag == "way"):
		node['id'] = element.get("id")

		node['type'] = element.tag
		node['visible'] = element.get("visible")

		created = {}
		for c in CREATED:
			created[c] = element.get(c)
		node['created'] = created

		if element.get("lat") and element.get("lon"):
			node['pos'] = [float(element.get("lat")), float(element.get("lon"))]

		if len(element.findall('tag')) > 0:
			
			for child in element.findall('tag'):

				if lower_colon.search(child.get('k')):
					key = child.get('k')[(child.get('k').find(':')+1):]
					val = child.get('v')
					if child.get('k')[:child.get('k').find(':')+1] == "addr:":
						addr = {}
						addr[key] = val
		                # print(child.get('k')[(child.get('k').find(':')+1):], child.get('v'))
						node['address'] = addr
					elif child.get('k')[:child.get('k').find(':')+1] == "contact:":
						contact = {}
						contact[key] = val
		                # print(child.get('k')[(child.get('k').find(':')+1):], child.get('v'))
						node['contact'] = contact
					elif child.get('k')[:child.get('k').find(':')+1] == "social:":
						social = {}
						social[key] = val
		                # print(child.get('k')[(child.get('k').find(':')+1):], child.get('v'))
						node['social'] = social
				else:
					# print(child.get('k')[:child.get('k').find(':')+1])
					node[child.get('k')] = child.get('v')
		if len(element.findall('nd')) > 0:
			node_refs = []
			for child in element.findall('nd'):
				node_refs.append(child.get('ref'))
			node['node_refs'] = node_refs
		return node
	else:
		return None

def process_map(file_in, pretty = False):
    # You do not need to change this file
	file_out = "{0}_all.json".format(file_in[:-3])
	data = []
	NODES = []
	WAYS = []
	RELATIONS = []
	with codecs.open(file_out, "w") as fo:
		for _, elem in ET.iterparse(file_in):	
			el = shape_element(elem)

			if el:
				pprint.pprint(el)
				data.append(el)
				if el['type'] == 'node':
					NODES.append(el)
				elif el['type'] == 'way':
					WAYS.append(el)
				elif el['type'] == 'relation':
					RELATIONS.append(el)

				if pretty:
					fo.write(json.dumps(el, indent=2)+"\n")
				else:
					fo.write(json.dumps(el) + "\n")
	pprint.pprint('len(WAYS): {0}'.format(len(WAYS)))
	pprint.pprint('len(NODES): {0}'.format(len(NODES)))
	pprint.pprint('len(RELATIONS): {0}'.format(len(RELATIONS)))

	return data



def test():
    # NOTE: if you are running this code on your computer, with a larger dataset,
    # call the process_map procedure with pretty=False. The pretty=True option adds
    # additional spaces to the output, making it significantly larger.
    data = process_map('singapore_fixed_10.osm', True)
    
if __name__ == "__main__":
    test()
