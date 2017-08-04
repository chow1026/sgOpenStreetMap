#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

This script is to exclude/remove the NODES and WAYS and RELATIONS that aren't Singapore SG data.
This is for second round, to dive deeper into housename, name and street.


"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
from json import dumps, loads, JSONEncoder, JSONDecoder
import pickle


NODES = defaultdict(set)
WAYS = defaultdict(set)

INPUT_OSM_FILE = "singapore_raw.osm"  # Replace this with your osm file
OUTPUT_OSM_FILE = "singapore_sg_2.osm"


odd_postcodes = ['Bukit Batok Street 25', '<different>', '135', 'S 642683', '437 437', '74', 'S120517', '05901', 'S118556', 'S 278989', '#B1-42', 'Singapore 408564', '562', '31', '2424']

MY_POSTCODES = ['80464', '88752', '81200', '81700', '80350', '80150', '81800', '80040', '81310', '81900', '81750', '80300', '81500', '81100', '80250', '80400', '79200', '81060', '80000', '80200', '80050', '81450', '80739', '8100', '81000', '79100', '80800', '81210', '81300', '80463', '2222']

ID_POSTCODES = ['29463', '29461', '29433', '24961', '29464', '29425', '29466', '29432']

NON_SG_Streets = ['110 Jalan Serampang, Taman Pelangi', '116 Jalan Serampang, Taman Pelangi', '28 Jalan Semerbak 22, Taman Bukit Dahlia, Pasir Gudang, Johor', '65 Jalan Kuning 2, Taman Pelangi', 'Anggrek Sari', 'Batam Center', 'Hotel Selesa Pasir Gudang, Main Lobby Floor, Jalan Bandar, Pasir Gudang, Johor ', 'JL. Jaksa Agung R. Soeprapto', 'Jalan Abdul Samad', 'Jalan Abdul Samad', 'Jalan Abiad', 'Jalan Abiad 1, Taman Maju Jaya', 'Jalan Anggerik', 'Jalan Api-Api 1', 'Jalan Asas', 'Jalan Austin Heights 8/8', 'Jalan Austin Heights Utama', 'Jalan Badik', 'Jalan Bahagia', 'Jalan Bayan', 'Jalan Beringin', 'Jalan Bestari 1/5', 'Jalan Bestari 12/2', 'Jalan Bestari 5/2', 'Jalan Bunga Kertas 2', 'Jalan Bunga Orkid', 'Jalan Cendera', 'Jalan Chengai', 'Jalan Dato Abdullah Tahir', 'Jalan Desaru', 'Jalan Dhoby', 'Jalan Emas 18', 'Jalan Enau 20', 'Jalan Felda Waha', 'Jalan Gelam', 'Jalan Gertak Merah', 'Jalan Glasiar', 'Jalan Hang Jebat', 'Jalan Hang Tuah 28', 'Jalan Hijrah 5', 'Jalan Hijrah Utama', 'Jalan Ibrahim', 'Jalan Ibrahim Sultan', 'Jalan Impian Emas 6', 'Jalan Indah 15', 'Jalan Indah 15/1', 'Jalan Indah 16/12', 'Jalan Indah 16/4', 'Jalan Indah 29/7', 'Jalan Inderaputra', 'Jalan Iris 1', 'Jalan Jasa', 'Jalan Jelatang 25', 'Jalan Jelita', 'Jalan Jerau 2', 'Jalan Jingga', 'Jalan Johan', 'Jalan Jurong Kechil', 'Jalan Kasa 11', 'Jalan Kasawari', 'Jalan Kebudayaan', 'Jalan Kebun Teh', 'Jalan Kemaman', 'Jalan Kempas', 'Jalan Kempas3', 'Jalan Kerambit 4', 'Jalan Keris', 'Jalan Keris 1', 'Jalan Kinabalu', 'Jalan Kota Tinggi-Kulai', 'Jalan Kuil', 'Jalan Kuning', 'Jalan Layang 16', 'Jalan Leban', 'Jalan Lencana', 'Jalan Lengkongan', 'Jalan Mahmoodiah', 'Jalan Masai Lama', 'Jalan Mastika', 'Jalan Merah', 'Jalan Meranti', 'Jalan Molek 1/12', 'Jalan Molek 1/9', 'Jalan Mulia', 'Jalan Nb2 2/2', 'Jalan Nb2 7/3', 'Jalan Nusaria', 'Jalan Orkid 1', 'Jalan Padang Dua', 'Jalan Padi Emas 1', 'Jalan Padi Huma 18', 'Jalan Pasir Pelangi', 'Jalan Pekeliling', 'Jalan Penanga', 'Jalan Permas 10', 'Jalan Permatang 5', 'Jalan Persekutuan 1', 'Jalan Persiaran Bakti 1', 'Jalan Persiaran Danga', 'Jalan Persiaran Kempas Baru', 'Jalan Persiaran Perling 1', 'Jalan Pertiwi', 'Jalan Petaling', 'Jalan Pontian', 'Jalan Pujaan','Jalan Pulai Perdana 11', 'Jalan Puteh 5', 'Jalan Raja Udang', 'Jalan Rawa', 'Jalan Resak', 'Jalan Ros Merah 1/4', 'Jalan Ros Merah 2/3', 'Jalan Ros Merah 2/8', 'Jalan Ros Merah 2/9', 'Jalan SIlat Sinding 16', 'Jalan SME 1', 'Jalan Satu', 'Jalan Sejahtera 10', 'Jalan Senang', 'Jalan Sentosa', 'Jalan Senyum', 'Jalan Serai', 'Jalan Seri Impian 1, Taman Impian Emas,', 'Jalan Seruling 2', 'Jalan Setulang', 'Jalan Siakap 10', 'Jalan Sri Pelangi', 'Jalan Stulang Darat', 'Jalan Stulang Laut', 'Jalan Sultanah Aminah', 'Jalan Sungei Sayong', 'Jalan Suria 3', 'Jalan Sutera', 'Jalan Sutera 1', 'Jalan Sutera Danga', 'Jalan Sutera Tanjung 8/3', 'Jalan Taib', 'Jalan Tanjung Kupang', 'Jalan Tarom', 'Jalan Titiwangsa 3', 'Jalan Titiwangsa 3/1', 'Jalan Trus', 'Jalan Tun Abdul Razak', 'Jalan Uda Utama 3/7',  'Jalan Ungu', 'Jalan Wong Ah Fook', 'Jalan Yahya Al-Datar', 'Jalan iKhlas', 'Jl.  Batu 13 Tanjung Pinang', 'Jl. Asoka', 'Jl. Engku Puteri', 'Jl. Raden Patah', 'Jl.Baiturrahman', 'Jl.Budi Kemuliaan', 'Jl.Hang Lekiu', 'Jl.Ir.Sutami', 'Jl.Re.Martadinata', 'Jl.Tiban I', 'Jl.Trans Barelang', 'Jln Pelatina', 'Jln Tan Hiok Nee', 'Jln. Megat Ali', 'Jln. Wr. Supratman', 'Komplek Bumi Indah Blok C No.4 (depan babinsa -nagoya) Kecamatan Lubuk Baja-Batam', 'Komplek Bumi Indah Nagoya, Depan Sari Jaya Hotel. Batam', 'Komplek Ruko Permata Komplek Ruko Permata  Niaga Blok C No.3Bukit Indah Sukajadi', 'Lebuhraya Hubungan Kedua', 'Lorong A-16', 'Meldrum', 'Mukakuning Indah 1', 'Mukakuning Indah 1 Blok U', 'Mukakuning Indah 1 Blok U No 5', 'Pantai Batu Besar', 'Persiaran Sri Putri', 'Pertokoan Seruni Indah Blok :I no.16Batam Center. Kepri-Indonesia.', 'Perumahan Graha Permata Indah, Tiban Indah', 'Perumahan nusa jaya', 'Pesona Asri Blok A17 No.15', Ruko Citra Mas Blok BNo 5', 'Taman Mediterania Tahap II Batam Center.', 'Tebrau Highway', 'Tiban Mc Dermoth', 'bandar indahpura', 'jalan cendana 10', 'jalan cendana 3', km 62', 'perum maitri garden 2', 'pondok indah ']


NON_SG_housenames = ['Allamanda', B7 Danga Walk', 'BCS Mall', 'Batamku Production', 'Batamku Production (Oleh-oleh Kaos Batam)', 'CONG JAYA', 'Gbabe Fashions', 'FELO House', 'JJ Collection', 'Jalan Imam Bonjol-Komplek Nagoya Paradise ', 'Center Blok I Indonesia', 'Jalan Imam Bonjol-Komplek Nagoya Paradise ', 'Center Blok J Indonesia', 'Jl. Teuku Umar', 'Johor Bahru City Square', 'Komp. Pertokoan Mega Junction', 'Masjid Agung Batam', 'Masjid Darussalam', 'PT. Loreynia Trading', 'Newcastle University Medicine School', 'PT. Solnet Indonesia', 'Paklah Cafe', 'Pak lah Cafe', 'Perguruan Vingtsun Batam', 'Perumahan Taman Valencia Blok B', 'Rezeki Seafood', 'Ruko Bunga Raya', 'Ruko Mega Legenda', 'Ruko Royal Sincom C11, 3rd Floors', 'Rumah 1. Suroto', 'Suksis Office', 'Aked K9 K10']

NON_SG_housenumbers = ['+60 7 663 3277', 'LPMI Batam', 'New Place Pub & Restaurant', 'Pandai Batam', 'Perguruan Vingtsun Batam', 'Salmart Batam', 'Warung Butik', 'Xamthone Herbal']

NON_SG_alt_names = ['Desaru Perdana Beach Resort', 'Jalan Kolam Ayer', 'Jalan Kongkong', 'Jalan Seelong', 'Jalan Tun Abdul Razak Interchange', 'Karang Selatan', 'Padang Golf Mount Austin', 'Pergerang Highway', 'Persiaran Perling', 'Persisran Perling']


def is_sg_by_zip(elem):
    for tag in elem.iter("tag"):
        k = tag.attrib['k']
        v = tag.attrib['v']
        if k =='addr:postcode':
            if v in MY_POSTCODES or v in ID_POSTCODES:
                return False
    return True

def is_batam_source(elem):
    for tag in elem.iter("tag"):
        k = tag.attrib['k']
        v = tag.attrib['v']
        if k =='source' and v.find("Batam Mapping Project") > -1:
            return True
    return False

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
            by_batam_source = is_batam_source(elem)
            sg_zip = is_sg_by_zip(elem)
            if in_SG and not by_batam_source and sg_zip:
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
