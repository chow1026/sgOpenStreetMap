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
and/or 'facebook', 'contact:fax' and/or 'fax', 'social:google_plus', 
'social:instagram', 'contact:phone' and/or 'phone', 'social:twitter', 
'contact:website' and/or 'website', 'exit_to', 'highway', 'religion', 'cuisine', 'demonition'
3) Consolidate repeated keys and values (such as 'contact:email' & 'email', 'amenity' & 'amenity_1') 
4) Clean up data format for phone/fax numbers, website urls and emails.  
5) Extract cleaned, meaningful node data from OSM to JSON file.

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

def shape_element(element):
	node = {}

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
				if child.get('k')[:child.get('k').find(':')+1] != "addr:":
					node[child.get('k')] = child.get('v')
	if len(element.findall('nd')) > 0:
		node_refs = []
		for child in element.findall('nd'):
			node_refs.append(child.get('ref'))
		node['node_refs'] = node_refs
		return node
	else:
		return None

def process_map(file_in, tags, pretty = False):
    # You do not need to change this file
	file_out = "{0}.json".format(file_in)
	data = []
	NODES = []
	WAYS = []
	RELATIONS = []
	with codecs.open(file_out, "w") as fo:
		for _, elem in ET.iterparse(file_in):
			if elem.tag in tags:
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
	return data



def test():
    # NOTE: if you are running this code on your computer, with a larger dataset,
    # call the process_map procedure with pretty=False. The pretty=True option adds
    # additional spaces to the output, making it significantly larger.
    data = process_map('singapore_fixed_10.osm', ['node', 'way', 'relation'], True)
    #pprint.pprint(data)

if __name__ == "__main__":
    test()
