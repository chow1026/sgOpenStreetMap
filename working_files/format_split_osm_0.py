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


p_addrUnit = re.compile(r"\w{1,}-\w{2,}")



GENERIC_KEYS = ['name', 'name:en', 'alt_name', 'user', 'amenity', 'landuse', 
'building', 'building:use', 
'addr:housename','addr:housenumber',  'addr:street', 'addr:unit', 'addr:city', 
'addr:country', 'addr:postcode', 'contact:email', 'contact:phone', 'contact:fax',
'contact:website', 'social:facebook', 'social:google_plus',
'social:instagram', 'social:twitter'];
# if 'amenity_1', append to 'amenity' list
# if 'landuse_1', append to 'landuse' list

NODE_KEYS = ['religion', 'denomination','cuisine', 'highway', 'exit_to'];

WAY_KEYS = ['highway', 'oneway', 'service', 'railway', 'bridge', 'place', 
'natural', 'landuse', 'leisure', 'tourism', 'school']

RELATION_KEYS = ['type', 'route', 'from', 'to']



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

# def got_name(elem):
# 	for tag in elem.iter("tag"):
# 		k = tag.attrib['k']
# 		if k =='name' or k =='alt_name' or k == 'name:en' or k == 'alt_name:en':
# 			return True
# 	return False


# def get_elem_with_name_altname(osm_file, tags=('node')):
# 	context = iter(ET.iterparse(osm_file, events=('start', 'end')))
# 	_, root = next(context)
# 	for event, elem in context:
# 		if event == 'end' and elem.tag in tags:
# 			if got_name(elem):
# 				yield elem
# 			root.clear()

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
		addr = {}
		social = {}
		contact = {}
		for child in element.findall('tag'):

			if lower_colon.search(child.get('k')) and child.get('k')[:child.get('k').find(':')+1] == "addr:":
				key = child.get('k')[(child.get('k').find(':')+1):]
				val = child.get('v')
                
				addr[key] = val
                # print(child.get('k')[(child.get('k').find(':')+1):], child.get('v'))
				node['address'] = addr
			elif lower_colon.search(child.get('k')) and child.get('k')[:child.get('k').find(':')+1] == "contact:":
				key = child.get('k')[(child.get('k').find(':')+1):]
				val = child.get('v')
                
				contact[key] = val
                # print(child.get('k')[(child.get('k').find(':')+1):], child.get('v'))
				node['contact'] = contact
			elif lower_colon.search(child.get('k')) and child.get('k')[:child.get('k').find(':')+1] == "social:":
				key = child.get('k')[(child.get('k').find(':')+1):]
				val = child.get('v')
                
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
			if elem.tag in tags and got_name(elem):
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


 
# def audit(osmfile, tags):
#     osm_file = open(osmfile, "r")
#     dict_obj = {}
#     for event, elem in ET.iterparse(osm_file, events=("start",)):
#         if elem.tag in tags and got_name(elem):
#         	dict_obj[]
#             for tag in elem.iter("tag"):
#                 k = tag.attrib['k']
#                 v = tag.attrib['v']
#                 # m1 = p_seamark.match(k)
#                 # m2 = p_turn.match(k)

#                 if k not in IRRELEVANT_keys and m1 == None and m2 == None:
#                     unique_kv[k].add(v)

#     osm_file.close()
#     return unique_kv



def test():
    # NOTE: if you are running this code on your computer, with a larger dataset,
    # call the process_map procedure with pretty=False. The pretty=True option adds
    # additional spaces to the output, making it significantly larger.
    data = process_map('singapore_fixed_10.osm', ['node', 'way', 'relation'], True)
    #pprint.pprint(data)

    # correct_first_elem = {
    #     "id": "261114295",
    #     "visible": "true",
    #     "type": "node",
    #     "pos": [41.9730791, -87.6866303],
    #     "created": {
    #         "changeset": "11129782",
    #         "user": "bbmiller",
    #         "version": "7",
    #         "uid": "451048",
    #         "timestamp": "2012-03-28T18:31:23Z"
    #     }
    # }
    # assert data[0] == correct_first_elem
    # assert data[-1]["address"] == {"street": "West Lexington St.",
    #                                 "housenumber": "1412"}
    # assert data[-1]["node_refs"] == [ "2199822281", "2199822390",  "2199822392", "2199822369",
    #                                 "2199822370", "2199822284", "2199822281"]

if __name__ == "__main__":
    test()
