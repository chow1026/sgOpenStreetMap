#!, usr, bin, env python
# -*- coding: utf-8 -*-

"""

This script is to
1) consolidate address keys into
    - 'addr:housenumber'
    - 'addr:housename'
    - 'addr:street'
    - 'addr:unit'
    - 'addr:postcode'
    - 'addr:floor'
    - 'addr:city'
    - 'addr:country'
2) fix, clean address data in each field that aren't valid
3) fix spelling errors and abbreviations

"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint


KEY_SWAPS = {}
KEY_SWAPS['addr:housenumber_1'] = {'#01-01': 'addr:unit'}

KEY_SWAPS['addr:door'] = {'#02-201': 'addr:unit'}

KEY_SWAPS['addr:floor'] = {'05-01': {'addr:unit': '#05-01'}}

KEY_SWAPS['addr:flats'] = {'#03-3585': 'addr:unit', '#04-3565': 'addr:unit'}

KEY_SWAPS['addr:street'] = {'Tanjong Pagar Plaza': 'addr:housename'}

KEY_SWAPS['addr:place'] = {'Buangkok Crescent': 'addr:street', 'Buangkok Link': 'addr:street', 'Dairy Farm Estate': 'addr:housename', 'Tanjong Pagar Road': 'addr:street'}

KEY_SWAPS['addr:name'] = {'Dahlia': {'addr:housename': 'Dahlia Park'}}

KEY_SWAPS['addr:unit'] = {
    '12/14/16': {'addr:housenumber': '12, 14, 16'},
    '357A/359A': {'addr:housenumber': '357A, 359A'},
    '471-A/B/C & 473-A/B/C': {'addr:housenumber': '471A, 471B, 471C, 473A, 473B, 473C'},
    '549A/B': {'addr:housenumber': '549A, 549B'},
    '97/99': {'addr:housenumber': '97, 99'},
    'Marina Bay Sands North Tower': 'addr:housename',
    'XFrontiers Block': 'addr:housename',
    '#02-01, #02-02 and #02-03': {'addr:unit': '#02-01/#02-02/#02-03'},
    '#03-01, #04-01 & #05-01': {'addr:unit': '#03-01/#04-01/#05-01'},
    '01-13/14': {'addr:unit':'#01-13/#01-14'},
    '01/14-15': {'addr:unit': '#01-14/#01-15'},
    '#01-38/#01-40,#01-42': {'addr:unit': '#01-38/#01-40/#01-42'},
    '3': {'addr:unit': '#00-03'},
    '9F 36': {'addr:unit': '#09-36'}}

KEY_SWAPS['addr:city'] = {
'#01-05': 'addr:unit', 
'#01-06': 'addr:unit', 
'#01-33': 'addr:unit', 
'#01-38/40/42': {'addr:unit': '#01-38/#01-40,#01-42'}, 
'#01-44': 'addr:unit', 
'#01-46': 'addr:unit', 
'#01-50': 'addr:unit', 
'#01-58/60': {'addr:unit': '#01-58/#01-60'}, 
'#01-62': 'addr:unit', 
'Ang Mo Kio': 'addr:suburb', 
'Changi Village': 'addr:suburb', 
'Holland Village': 'addr:suburb', 
'Punggol': 'addr:suburb', 
'Sembawang': 'addr:suburb', 
'Woodlands Spectrum II': 'addr:housename', 
'01-169 Singapore': {'addr:unit': '#01-169', 'addr:city': 'Singapore'}
}

KEY_SWAPS['addr:postcode'] = {
    'Bukit Batok Street 25': 'addr:street',
    '135': 'addr:housenumber',
    '74': 'addr:housenumber',
    '<different>': {'addr:postcode': '670454'},
    '#B1-42': {'addr:unit': '#B1-42', 'addr:postcode': '588174'},
    'Singapore 408564': {'addr:city': 'Singapore', 'addr:postcode': '408564'},
    '31': {'addr:street': 'Woodlands Street 31', 'addr:housenumber': '1', 'addr:postcode': '738581'},
    '05901': {'addr:postcode': '059016'},
    'S 642683': {'addr:postcode': '642683'},
    '437 437': {'addr:postcode': '437437'},
    'S120517': {'addr:postcode': '120517'},
    'S118556': {'addr:postcode': '118556'},
    'S 278989': {'addr:postcode': '278989'},
    '562': {'addr:postcode': '530562'},
    '2424': 'rm'}

KEY_SWAPS['addr:street'] = {
    '公司65': 'rm',
    '1 Pasir Ris Close': {'addr:housenumber': '1', 'addr:street': 'Pasir Ris Close'},
    '1013 Geylang East Ave 3': {'addr:housenumber': '1013', 'addr:street': 'Geylang East Avenue 3'},
    '140 Maxwell Road': {'addr:housenumber': '140', 'addr:street': 'Maxwell Road'},
    '169-A/B/D and 171-A/B/C/D Bencoolen Street': {'addr:housenumber': '169A, 169B, 169D, 171A, 171B, 171C, 171D', 'addr:street': 'Bencoolen Street'},
    '2 Cox Terrace Fort Canning Park': {'addr:housename': 'Fort Canning Park', 'addr:housenumber': '2', 'addr:street': 'Cox Terrace'},
    '180 Ang Mo Kio Avenue 8': {'addr:housenumber': '180', 'addr:street': 'Ang Mo Kio Avenue 8'},
    '2': 'addr:housenumber',
    '2 Jurong East Central 1': {'addr:housenumber': '2', 'addr:street': 'Jurong East Central 1'},
    '220 Turf Club Road': {'addr:housenumber': '220', 'addr:street': 'Turf Club Road'}, '24, 26 & 28 Dunlop Street': {'addr:housenumber': '24, 26, 28', 'addr:street': 'Dunlop Street'},
    '252 North Bridge Road': {'addr:housenumber': '252', 'addr:street': 'North Bridge Road'},
    '31 Lower Kent Ridge Rd': {'addr:housenumber': '31', 'addr:street': 'Lower Kent Ridge Road'},
    '310074': 'addr:postcode',
    '37 Mimosa Park Mimosa Road': {'addr:housename': 'Mimosa Park', 'addr:housenumber': '37', 'addr:street': 'Mimosa Road'},
    '38 Draycott Drive': {'addr:housenumber': '38', 'addr:street': 'Draycott Drive'},
    '43A, 43B, 43C Jalan Besar': {'addr:housenumber': '43A, 43B, 43C', 'addr:street': 'Jalan Besar'},
    '5 Draycott Drive': {'addr:housenumber': '5', 'addr:street': 'Draycott Drive'},
    '520 Lorong 6 Toa Payoh': {'addr:housenumber': '520', 'addr:street': 'Lorong 6 Toa Payoh'},
    '535 Clementi Road': {'addr:housenumber': '535', 'addr:street': 'Clementi Road'},
    '535 Upper Changi Road': {'addr:housenumber': '535', 'addr:street': 'Upper Changi Road'},
    '61A/B & 63A/B Pagoda Street': {'addr:housenumber': '61A, 61B, 63A, 63B', 'addr:street': 'Pagoda Street'},
    '656289': {'addr:postcode': '656289', 'addr:housenumber': '288G', 'addr:street': 'Bukit Batok Street 25'},
    '67, Ubi road 1, Oxley Biz Hub 1, #07-08': {'addr:housenumber': '67', 'addr:street': 'Ubi road 1', 'addr:housename': 'Oxley Biz Hub 1', 'addr:unit': '#07-08'},
    '699 Hougang Street 52': {'addr:housenumber': '699', 'addr:street': 'Hougang Street 52'},
    '7 Draycott Drive': {'addr:housenumber': '7', 'addr:street': 'Draycott Drive'},
    '70 Woodlands Ave 7': {'addr:housenumber': '70', 'addr:street': 'Woodlands Ave 7'},
    '769, 771, 773 & 775 North Bridge Road': {'addr:housenumber': '769, 771, 773, 775', 'addr:street': 'North Bridge Road'},
    'Blk 10 Ubi Crescent': {'addr:housenumber': '10', 'addr:street': 'Ubi Crescent'},
    'East Coast Road #03-09': {'addr:unit': '#03-09', 'addr:street': 'East Coast Road'},
    'East Coast Road #03-14': {'addr:unit': '#03-14', 'addr:street': 'East Coast Road'},
    'Jalan Rajah, #01-01, Zhong Shan Park,': {'addr:suburb': 'ZhongShan Park', 'addr:unit': '#01-01', 'addr:street': 'Jalan Rajah'},
    'Jalan Rajah, #01-02 Zhongshan Park': {'addr:suburb': 'ZhongShan Park', 'addr:unit': '#01-02', 'addr:street': 'Jalan Rajah'},
    'Orchard Road, #B1-12/13': {'addr:unit': '#B1-12/#B1-13', 'addr:street': 'Orchard Road'},
    'Orchard Road, #K-02/03': {'addr:unit': '#K-02/#K-03', 'addr:street': 'Orchard Road'},
    'Rangoon Road #01-02': {'addr:unit': '#01-02', 'addr:street': 'Rangoon Road'},
    'Rochor Canal Road #02-85': {'addr:unit': '#02-85', 'addr:street': 'Rochor Canal Road'},
    'Sims Drive #05-12B': {'addr:unit': '#05-12B', 'addr:street': 'Sims Drive'},
    'Ubi Road 1 #01-23': {'addr:unit': '#01-23', 'addr:street': 'Ubi Road 1'},
    'Unit : #05-464,  Hougang Street 51': {'addr:unit': '#05-464', 'addr:street': 'Hougang Street 51'},
    'Worchester Road\n': {'addr:street': 'Worchester Road'},
    'Street Michael\'s Road': {'addr:street': 'St. Michael\'s Road'},
    'مسجد السلطان': {'addr:housenumber': '3', 'addr:street': 'Muscat Street', 'addr:postcode': '198833'}}

KEY_SWAPS['addr:housename'] = {
    '#01-02': 'addr:unit',
    '#01-11': 'addr:unit',
    '#08-01A Far East Finance Building': {'addr:unit': '#08-01A', 'addr:housename': 'Far East Finance Building'},
    '#19-3329': 'addr:unit',
    '119': 'addr:housenumber',
    '392': 'addr:housenumber',
    '1': 'addr:housenumber',
    '1 Pandan Crescent':  {'addr:housenumber': '1', 'addr:street': 'Pandan Crescent'},
    '10 Chapel Road': {'addr:housenumber': '10', 'addr:street': 'Chapel Road'},
    '10A Chapel Road':  {'addr:housenumber': '10A', 'addr:street': 'Chapel Road'},
    '11 Chapel Road': {'addr:housenumber': '11', 'addr:street': 'Chapel Road'},
    '11B Chapel Road': {'addr:housenumber': '11B', 'addr:street': 'Chapel Road'},
    '12 Chapel Road': {'addr:housenumber': '12', 'addr:street': 'Chapel Road'},
    '12A Chapel Road': {'addr:housenumber': '12A', 'addr:street': 'Chapel Road'},
    '13 Chapel Road': {'addr:housenumber': '13', 'addr:street': 'Chapel Road'},
    '15 Chapel Road': {'addr:housenumber': '15', 'addr:street': 'Chapel Road'},
    '2': 'addr:housenumber',
    '21': 'addr:housenumber',
    '24': 'addr:housenumber',
    '26': 'addr:housenumber',
    '3': 'addr:housenumber',
    '3 Chapel Road': {'addr:housenumber': '3', 'addr:street': 'Chapel Road'},
    '3 Pandan Crescent': {'addr:housenumber': '3', 'addr:street': 'Pandan Crescent'},
    '31': 'addr:housenumber',
    '31 Lower Kent Ridge Rd, Singapore': {'addr:housenumber': '31', 'addr:street': 'Lower Kent Ridge Road', 'addr:city': 'Singapore'},
    '325': 'addr:housenumber',
    '33': 'addr:housenumber',
    '334': 'addr:housenumber',
    '341': 'addr:housenumber',
    '343': 'addr:housenumber',
    '35': 'addr:housenumber',
    '357': 'addr:housenumber',
    '358': 'addr:housenumber',
    '37': 'addr:housenumber',
    '383': 'addr:housenumber',
    '383A': 'addr:housenumber',
    '384': 'addr:housenumber',
    '385': 'addr:housenumber',
    '387': 'addr:housenumber',
    '388': 'addr:housenumber',
    '388A': 'addr:housenumber',
    '389': 'addr:housenumber',
    '38th Draycott Drive': {'addr:housenumber': '38', 'addr:street': 'Draycott Drive'},
    '39 Chapel Road': {'addr:housenumber': '39', 'addr:street': 'Chapel Road'},
    '390': 'addr:housenumber',
    '391': 'addr:housenumber',
    '393': 'addr:housenumber',
    '394': 'addr:housenumber',
    '395': 'addr:housenumber',
    '395A': 'addr:housenumber',
    '3A Chapel Road': {'addr:housenumber': '3A', 'addr:street': 'Chapel Road'},
    '3B Chapel Road': {'addr:housenumber': '3B', 'addr:street': 'Chapel Road'},
    '3C Chapel Road': {'addr:housenumber': '3C', 'addr:street': 'Chapel Road'},
    '3D Chapel Road': {'addr:housenumber': '3D', 'addr:street': 'Chapel Road'},
    '3E Chapel Road': {'addr:housenumber': '3E', 'addr:street': 'Chapel Road'},
    '405': 'addr:housenumber',
    '406': 'addr:housenumber',
    '41': 'addr:housenumber',
    '411': 'addr:housenumber',
    '413': 'addr:housenumber',
    '414': 'addr:housenumber',
    '415': 'addr:housenumber',
    '417': 'addr:housenumber',
    '43': 'addr:housenumber',
    '448': 'addr:housenumber',
    '449': 'addr:housenumber',
    '45': 'addr:housenumber',
    '450': 'addr:housenumber',
    '505A': 'addr:housenumber',
    '7': 'addr:housenumber',
    '7 Draycott Drive': {'addr:housenumber': '7', 'addr:street': 'Draycott Drive'},
    '8': 'addr:housenumber',
    '8 Chapel Road': {'addr:housenumber': '8', 'addr:street': 'Chapel Road'},
    '8 East Wing': {'addr:housenumber': '8', 'addr:housename': 'East Wing'},
    '8 West Wing': {'addr:housenumber': '8', 'addr:housename': 'West Wing'},
    '8A Chapel Road': {'addr:housenumber': '8A', 'addr:street': 'Chapel Road'},
    '8B Chapel Road': {'addr:housenumber': '8B', 'addr:street': 'Chapel Road'},
    '8C Chapel Road': {'addr:housenumber': '8C', 'addr:street': 'Chapel Road'},
    '8D': 'addr:housenumber',
    '9': 'addr:housenumber',
    '91': 'addr:housenumber',
    '93': 'addr:housenumber',
    'Blk 116': {'addr:housenumber': '116'},
    'Blk 233': {'addr:housenumber': '233'},
    'Blk 410': {'addr:housenumber': '410'},
    'Blk 412': {'addr:housenumber': '412'},
    'Blk 416': {'addr:housenumber': '416'},
    'Blk 45': {'addr:housenumber': '45'},
    'Blk 46 Sims Place': {'addr:housenumber': '46', 'addr:street': 'Sims Place'},
    'Blk 47': {'addr:housenumber': '47'},
    'Blk 49': {'addr:housenumber': '49'},
    'Blk 51': {'addr:housenumber': '51'},
    'Blk 53': {'addr:housenumber': '53'},
    'Block 11': {'addr:housenumber': '11'},
    'Block 13': {'addr:housenumber': '13'},
    'Block 14': {'addr:housenumber': '14'},
    'Block 15': {'addr:housenumber': '15'},
    'Block 424': {'addr:housenumber': '424'},
    'Block 7': {'addr:housenumber': '7'},
    'E': 'rm',
    'Gold, Diamond and Jewllery Employees': 'rm',
    'Jalan Sendudok': 'addr:street',
    'Level 1': {'addr:floor': '1'},
    'blk 155': {'addr:housenumber': '155'},
    'blk 159': {'addr:housenumber': '159'},
    'blk 164': {'addr:housenumber': '164'},
    'blk 166': {'addr:housenumber': '166'},
    'blk 168 bedok south ave 3': {'addr:housenumber': '168', 'addr:street': 'Bedok South Avenue 3'},
    'blk 169': {'addr:housenumber': '169'}}

KEY_SWAPS['addr:housenumber'] = {
    '111H/N': {'addr:housenumber': '111H, 111N'},
    '111J/P': {'addr:housenumber': '111J, 111P'},
    '117-135': {'addr:housenumber': '117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135'},
    '13-474': {'addr:housenumber': '260D', 'addr:unit': '13-474'},
    '#01-43': {'addr:unit':'#01-43'},
    '#01-04, Marina Bay Financial Centre Tower 2, 10': {'addr:housenumber': '10', 'addr:housename': 'Marina Bay Financial Centre Tower 2', 'addr:unit': '#01-04'},
    '#01-04/05, Asia Square Tower 2, 12': {'addr:housenumber': '12', 'addr:housename': 'Asia Square Tower 2', 'addr:unit': '#01-04/#01-05'},
    '#01-08, 9': {'addr:housenumber': '9', 'addr:unit': '#01-08'},
    '#01-43': {'addr:unit':'#01-43'},
    '01': {'addr:floor': '1', 'addr:street': 'Jurong West Street 92'},
    '01-09/10': {'addr:unit': '#01-09/#01-10'},
    '01-19': {'addr:unit': '#01-19'},
    '03-207': {'addr:unit': '#03-207'},
    '08/09--02': {'addr:unit': '#02-08/#02-09', 'addr:housenumber': '1', 'addr:housename': 'Changi Village Hotel'},
    '1 Blok C': 'rm',
    '1-15': {'addr:housenumber': '1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15'},
    '10-12': {'addr:housenumber': '10, 11, 12'},
    '12A/B & 14A/B': {'addr:housenumber': '12A, 12B, 14A, 14B'},
    '131 #03-04': {'addr:housenumber': '131', 'addr:unit': '#03-04'},
    '117-135': {'addr:housenumber': '117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135'},
    '128A MSCP': {'addr:housename': '128A MSCP', 'addr:housenumber': '128A'},
    '140, #05-02,': {'addr:housenumber': '140', 'addr:unit': '#05-02'},
    '143-145': {'addr:housenumber': '143, 144, 145'},
    '153A, 153B & 155B': {'addr:housenumber': '153A, 153B, 155B'},
    '16 & 18': {'addr:housenumber': '16, 18'},
    '16-20': {'addr:housenumber': '16, 17, 18, 19, 20'},
    '17-29': {'addr:housenumber': '17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29'},
    '18/18A/18B/18C': {'addr:housenumber': '18, 18A, 18B, 18C'},
    '21 / 21A': {'addr:housenumber': '21, 21A'},
    '211A, 213A, 215A & 217A': {'addr:housenumber': '211A, 213A, 215A, 217A'},
    '263 & 265': {'addr:housenumber': '263, 265'},
    '259A-D': {'addr:housenumber': '259A, 259B, 259C, 259D'},
    '3 & 5': {'addr:housenumber': '3, 5'},
    '3 & 7': {'addr:housenumber': '3, 7'},
    '3 - 7': {'addr:housenumber': '3, 4, 5, 6, 7'},
    '3, 5, 7 & 9': {'addr:housenumber': '3, 5, 7, 9'},
    '30-38': {'addr:housenumber': '30, 31, 32, 33, 34, 35, 36, 37, 38'},
    '31-37': {'addr:housenumber': '31, 32, 33, 34, 35, 36, 37'},
    '31A/33': {'addr:housenumber': '31A, 33'},
    '33A. 33B, 33C, 35A,35B,35C,37A,37B & 37C': {'addr:housenumber': '33A, 33B, 33C, 35A, 35B, 35C, 37A, 37B, 37C'},
    '347A MSCP': {'addr:housename': '347A MSCP', 'addr:housenumber': '347A'},
    '361 - 369': {'addr:housenumber': '361, 362, 363, 364, 365, 366, 367, 368, 369'},
    '39-44': {'addr:housenumber': '39, 40, 41, 42, 43, 44'},
    '40-42': {'addr:housenumber': '40, 41, 42'},
    '44 & 44A': {'addr:housenumber': '44, 44A'},
    '46-50': {'addr:housenumber': '46, 47, 48, 49, 50'},
    '47-63': {'addr:housenumber': '47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63'},
    '490 & 492': {'addr:housenumber': '490, 492'},
    '50 & 51': {'addr:housenumber': '50, 51'},
    '51 - 65': {'addr:housenumber': '51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65'},
    '54-62': {'addr:housenumber': '54, 55, 56, 57, 58, 59, 60, 61, 62'},
    '6 & 7': {'addr:housenumber': '6, 7'},
    '60,60B, 62A/B/C & 64A/B/C': {'addr:housenumber': '60, 60B, 62A, 62B, 62C, 64A, 64B, 64C'},
    '64-A/B, 66-A/B & 68-A/B': {'addr:housenumber': '64A, 64B, 66A, 66B, 68A, 68B'},
    '65 ': {'addr:housenumber': '65'},
    '65-81': {'addr:housenumber': '65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81'},
    '71-83': {'addr:housenumber': '71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83'},
    '73-76': {'addr:housenumber': '73, 74, 75, 76'},
    '76A/B & 78A/B': {'addr:housenumber': '76A, 76B, 78A, 78B'},
    '77A & 79A': {'addr:housenumber': '77A, 79A'},
    '8, 10 & 12': {'addr:housenumber': '8, 10, 12'},
    '81 - 81C': {'addr:housenumber': '81, 81A, 81B, 81C'},
    '83-95': {'addr:housenumber': '83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95'},
    '87 & 89': {'addr:housenumber': '87, 89'},
    '8A, 9A & 9B': {'addr:housenumber': '8A, 9A, 9B'},
    '91A, 93A & 95A': {'addr:housenumber': '91A, 93A, 95A'},
    '31-45': {'addr:housenumber': '31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45'},
    '328-332': {'addr:housenumber': '328, 329, 330, 331, 332'},
    '30A, B & C': {'addr:housenumber': '30A, 30B, 30C'},
    '894A - Ricky': {'addr:housenumber': '894A'},
    '97-115': {'addr:housenumber': '97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115'},
    'B1-18': {'addr:unit': '#B1-18'},
    'BLK 205': {'addr:housenumber': '205'},
    'Blk 114': {'addr:housenumber': '114'},
    'Blk 115': {'addr:housenumber': '115'},
    'Blk 116': {'addr:housenumber': '116'},
    'Blk 117': {'addr:housenumber': '117'},
    'Blk 120': {'addr:housenumber': '120'},
    'Blk 129': {'addr:housenumber': '129'},
    'Blk 161': {'addr:housenumber': '161'},
    'Blk 183': {'addr:housenumber': '183'},
    'Blk 229': {'addr:housenumber': '229'},
    'Blk 233': {'addr:housenumber': '233'},
    'Blk 24 ': {'addr:housenumber': '24'},
    'Blk 257': {'addr:housenumber': '257'},
    'Blk 260': {'addr:housenumber': '260'},
    'Blk 318': {'addr:housenumber': '318'},
    'Blk 573': {'addr:housenumber': '573'},
    'Blk 60 #05-01': {'addr:housenumber': '60', 'addr:unit': '#05-01'},
    'Blk 710': {'addr:housenumber': '710'},
    'Blk 801': {'addr:housenumber': '801'},
    'Blk x': {'addr:housenumber': '6'},
    'Blk167': {'addr:housenumber': '167'},
    'Block 107': {'addr:housenumber': '107'},
    'Block 108': {'addr:housenumber': '108'},
    'Block 11': {'addr:housenumber': '11'},
    'Block 163': {'addr:housenumber': '163'},
    'Block 21': {'addr:housenumber': '21'},
    'Block 3 ': {'addr:housenumber': '3'},
    'Block 73': {'addr:housenumber': '73'},
    'Block 94': {'addr:housenumber': '94'},
    'Block 95': {'addr:housenumber': '95'},
    'Block 96': {'addr:housenumber': '96'},
    'Block 97': {'addr:housenumber': '97'},
    'Off upper Thomson': {'addr:unit': '#01-34', 'addr:housename': 'SEMBAWANG HILL FOOD CENTRE', 'addr:housenumber': '590', 'addr:street': 'UPPER THOMSON ROAD', 'addr:postcode': '574419'},
    'S2S': 'rm',
    'Singapore Home': {'addr:housenumber': '606'},
    'blk 162': {'addr:housenumber': '162'},
    'blk 163': {'addr:housenumber': '163'},
    'blk 165': {'addr:housenumber': '165'},
    'blok a, 6': 'rm',
    'q': 'rm',
    '19 / 19A': {'addr:housenumber': '19, 19A'},
    '19B / 19C': {'addr:housenumber': '19B, 19C'},
    '19D / 19E': {'addr:housenumber': '19D, 19E'},
    '19F / 19G': {'addr:housenumber': '19F, 19G'},
    '19H / 19J': {'addr:housenumber': '19H, 19J'},
    '19K / 19L': {'addr:housenumber': '19K, 19L'},
    '19M / 19N': {'addr:housenumber': '19M, 19N'},
    '21B / 21C': {'addr:housenumber': '21B, 21C'},
    '21D / 21E': {'addr:housenumber': '21D, 21E'},
    '21F / 21G': {'addr:housenumber': '21F, 21G'},
    '21H / 21J': {'addr:housenumber': '21H, 21J'},
    '21K / 21L': {'addr:housenumber': '21K, 21L'},
    '21M / 21N': {'addr:housenumber': '21M, 21N'},
    '#01-01, 1': {'addr:housenumber': '1', 'addr:unit': '#01-01'},
    '#01-01, 100': {'addr:housenumber': '100', 'addr:unit': '#01-01'},
    '#01-01, 130': {'addr:housenumber': '130', 'addr:unit': '#01-01'},
    '#01-01, 137': {'addr:housenumber': '137', 'addr:unit': '#01-01'},
    '#01-01, 31': {'addr:housenumber': '31', 'addr:unit': '#01-01'},
    '#01-01, 87': {'addr:housenumber': '87', 'addr:unit': '#01-01'},
    '#01-01, Asia Square Tower 1, 8': {'addr:housename': 'Asia Square Tower 1', 'addr:housenumber': '8', 'addr:unit': '#01-01'},
    '#01-01, Hong Leong Building, 16': {'addr:housename': 'Hong Leong Building', 'addr:housenumber': '16', 'addr:unit': '#01-01'},
    '#01-01/02, 1': {'addr:housenumber': '1', 'addr:unit': '#01-01/#01-02'},
    '#01-01/02, Riverside Point, 30': {'addr:housename': 'Riverside Point', 'addr:housenumber': '30', 'addr:unit': '#01-01/#01-02'},
    '#01-02': 'addr:unit',
    '#01-02, 87': {'addr:housenumber': '87', 'addr:unit': '#01-02'},
    '#01-02, Asia Square Tower 2, 12': {'addr:housename': 'Asia Square Tower 2', 'addr:housenumber': '12', 'addr:unit': '#01-02'},
    '#01-02, CPF Building, 79': {'addr:housename': 'CPF Building', 'addr:housenumber': '79', 'addr:unit': '#01-02'},
    '#01-02, Hong Leong Building, 16': {'addr:housename': 'Hong Leong Building', 'addr:housenumber': '16', 'addr:unit': '#01-02'},
    '#01-02, Tower 1 MBFC, 8': {'addr:housename': 'Tower 1 MBFC', 'addr:housenumber': '8', 'addr:unit': '#01-02'},
    '#01-02/03, 100': {'addr:housenumber': '100', 'addr:unit': '#01-02/#01-03'},
    '#01-03, 200': {'addr:housenumber': '200', 'addr:unit': '#01-03'},
    '#01-03, Asia Square Tower 2': {'addr:housename': 'Asia Square Tower 2', 'addr:housenumber': '12', 'addr:unit': '#01-03'},
    '#01-03, Hong Leong Building, 16': {'addr:housename': 'Hong Leong Building', 'addr:housenumber': '16', 'addr:unit': '#01-03'}, '#01-04': 'addr:unit', '#01-04, 87': {'addr:housenumber': '87', 'addr:unit': '#01-04'}, '#01-04, 9': {'addr:housenumber': '9', 'addr:unit': '#01-04'},
    '#01-04, Asia Square Tower 1, 8': {'addr:housename': 'Asia Square Tower 1', 'addr:housenumber': '8', 'addr:unit': '#01-04'},
    '#01-04, CPF Building, 79': {'addr:housename': 'CPF Building', 'addr:housenumber': '79', 'addr:unit': '#01-04'},
    '#01-04, Marina Bay Financial Centre Tower ': {'addr:housename': 'Marina Bay Financial Centre Tower', 'addr:unit': '#01-04'},
    '#01-05 Asia Square Tower 1, 8': {'addr:housename': 'Asia Square Tower 1', 'addr:housenumber': '8', 'addr:unit': '#01-05'},
    '#01-05, CPF Building, 79': {'addr:housename': 'CPF Building', 'addr:housenumber': '79', 'addr:unit': '#01-05'},
    '#01-05, Capital Tower, 168': {'addr:housename': 'Capital Tower', 'addr:housenumber': '168', 'addr:unit': '#01-05'},
    '#01-06, CPF Building, 79': {'addr:housename': 'CPF Building', 'addr:housenumber': '79', 'addr:unit': '#01-06'},
    '#01-07': 'addr:unit',
    '#01-07, 1': {'addr:housenumber': '1', 'addr:unit': '#01-01'}, '#01-07, CPF Building, 79': {'addr:housename': 'CPF Building', 'addr:housenumber': '79', 'addr:unit': '#01-07'},
    '#01-08, CPF Building, 79': {'addr:housename': 'CPF Building', 'addr:housenumber': '79', 'addr:unit': '#01-08'},
    '#01-08, One Shenton, 1': {'addr:housename': 'One Shenton', 'addr:housenumber': '1', 'addr:unit': '#01-08'},
    '#01-08/09/10, 168': {'addr:housenumber': '168', 'addr:unit': '#01-08/#01-09/#01-10'},
    '#01-09, CPF Building, 79': {'addr:housename': 'CPF Building', 'addr:housenumber': '79', 'addr:unit': '#01-09'},
    '#01-10, CPF Building, 79': {'addr:housename': 'CPF Building', 'addr:housenumber': '79', 'addr:unit': '#01-10'},
    '#01-126, 721': {'addr:housenumber': '721', 'addr:unit': '#01-126'},
    '#01-17, The Sail, 6': {'addr:housename': 'The Sail', 'addr:housenumber': '6', 'addr:unit': '#01-17'},
    '#01-177, Block 21': {'addr:housenumber': '21', 'addr:unit': '#01-177'},
    '#01-18/20, Sunset Way, Block 105': {'addr:street': 'Sunset Way', 'addr:housenumber': '105', 'addr:unit': '#01-18/#01-20'},
    '#01-20': 'addr:unit', '#01-201, 26': {'addr:housenumber': '26', 'addr:unit': '#01-201'},
    '#01-203/204, 26': {'addr:housenumber': '26', 'addr:unit': '#01-203/#01-204'},
    '#01-215 Block 21': {'addr:housenumber': '21', 'addr:unit': '#01-215'},
    '#01-225, Block 21': {'addr:housenumber': '21', 'addr:unit': '#01-225'},
    '#01-229, Block 19': {'addr:housenumber': '19', 'addr:unit': '#01-229'},
    '#01-237, Block 19': {'addr:housenumber': '19', 'addr:unit': '#01-237'},
    '#01-24': 'addr:unit',
    '#01-27/29, Sunset Way, Block 109': {'addr:street': 'Sunset Way', 'addr:housenumber': '109', 'addr:unit': '#01-27/#01-29'},
    '#01-272': 'addr:unit',
    '#01-31, 4': {'addr:housenumber': '4', 'addr:unit': '#01-31'},
    '#01-31A, The Sail, 4': {'addr:housename': 'The Sail', 'addr:housenumber': '4', 'addr:unit': '#01-31A'},
    '#01-3501C, 711': {'addr:housenumber': '711', 'addr:unit': '#01-3501C'},
    '#01-41/42, 177': {'addr:housenumber': '177', 'addr:unit': '#01-41/#01-42'},
    '#01-42, 1': {'addr:housenumber': '1', 'addr:unit': '#01-42'},
    '#01-43': {'addr:unit': '#01-43'},
    '#01-43, 1': {'addr:housenumber': '1', 'addr:unit': '#01-43'},
    '#01-517': 'addr:unit',
    '#01-52': 'addr:unit',
    '#01-52, Sunset Way, Block 106': {'addr:street': 'Sunset Way', 'addr:housenumber': '106', 'addr:unit': '#01-52'},
    '#01-53, Blk 43': {'addr:housenumber': '43', 'addr:unit': '#01-53'},
    '#01-54/56, Sunset Way, Block 106': {'addr:street': 'Sunset Way', 'addr:housenumber': '106', 'addr:unit': '#01-54/#01-56'},
    '#01-55, Blk 43': {'addr:housenumber': '43', 'addr:unit': '#01-55'},
    '#01-64, Sunset Way, Block 106': {'addr:street': 'Sunset Way', 'addr:housenumber': '106', 'addr:unit': '#01-64'},
    '#01-83, 28': {'addr:housenumber': '28', 'addr:unit': '#01-83'},
    '#01-835': 'addr:unit',
    '#01-85, 28': {'addr:housenumber': '28', 'addr:unit': '#01-85'},
    '#02- 401/402, Suntec City Tower 5, 3': {'addr:housename': 'Suntec City Tower 5', 'addr:housenumber': '3', 'addr:unit': '#02-401/#02-402'},
    '#02-01 2': {'addr:housenumber': '2', 'addr:unit': '#02-01'},
    '#02-01, 12': {'addr:housenumber': '12', 'addr:unit': '#02-01'},
    '#02-01, 120': {'addr:housenumber': '120', 'addr:unit': '#02-01'},
    '#02-01, Asia Square Tower 2, 12': {'addr:housename': 'Asia Square Tower 2', 'addr:housenumber': '12', 'addr:unit': '#02-01'},
    '#02-02, 1': {'addr:housenumber': '1', 'addr:unit': '#02-02'},
    '#02-02, Customs House, 70': {'addr:housename': 'Customs House', 'addr:housenumber': '70', 'addr:unit': '#02-02'},
    '#02-03': 'addr:unit',
    '#02-03, 61': {'addr:housenumber': '61', 'addr:unit': '#02-03'},
    '#02-03/04/05 Asia Square Tower 1, 8': {'addr:housename': 'Asia Square Tower 1', 'addr:housenumber': '8', 'addr:unit': '#02-03/#02-04/#02-05'},
    '#02-05': 'addr:unit',
    '#02-05, Asia Square Tower 2, 12': {'addr:housename': 'Asia Square Tower 2', 'addr:housenumber': '12', 'addr:unit': '#02-05'},
    '#02-06 Asia Square Tower 1, 8': {'addr:housename': 'Asia Square Tower 1', 'addr:housenumber': '8', 'addr:unit': '#02-06'},
    '#02-07, Asia Square Tower 1, 8': {'addr:housename': 'Asia Square Tower 1', 'addr:housenumber': '8', 'addr:unit': '#02-07'},
    '#02-08/09/10 Asia Square Tower 1, 8': {'addr:housename': 'Asia Square Tower 1', 'addr:housenumber': '8', 'addr:unit': '#02-08/#02-09/#02-10'},
    '#02-106': 'addr:unit',
    '#02-18/19 Asia Square Tower 1, 8': {'addr:housename': 'Asia Square Tower 1', 'addr:housenumber': '8', 'addr:unit': '#02-18/#02-19'},
    '#02-22, Asia Square Tower 2, 12': {'addr:housename': 'Asia Square Tower 2', 'addr:housenumber': '12', 'addr:unit': '#02-22'},
    '#02-55': 'addr:unit',
    '#02-83': 'addr:unit',
    '#03-02, 87': {'addr:housenumber': '87', 'addr:unit': '#03-02'},
    '#03-16, 1': {'addr:housenumber': '1', 'addr:unit': '#03-16'},
    '#03-21B': 'addr:unit',
    '#04-06 152': {'addr:housenumber': '152', 'addr:unit': '#04-06'},
    '#05-05 (Lobby A) /#02-43 (Lobby C)': {'addr:unit': '#05-05(Lobby A)/#02-43(Lobby C)'},
    '#10': {'addr:housenumber': '10'},
    '#10-03': 'addr:unit',
    '#285': {'addr:housenumber': '285'},
    '#319': {'addr:housenumber': '319'},
    '#54': {'addr:housenumber': '54'},
    '#B1-09, 1': {'addr:housenumber': '1', 'addr:unit': '#B1-09'},
    '#B1-45/46, 1': {'addr:housenumber': '1', 'addr:unit': '#B1-45/#B1-46'},
    '#B1-50-52, 154': {'addr:housenumber': '154', 'addr:unit': '#B1-50/#B1-51/#B1-52'},
    '#B2-05, Marina Bay Link Mall, 8A': {'addr:housename': 'Marina Bay Link Mall', 'addr:housenumber': '8A', 'addr:unit': '#B2-05'},
    '0': 'rm',
    '01-01': 'addr:unit',
    '01-01/02': {'addr:unit': '#01-01/#01-02'},
    '01-03/04': {'addr:unit': '#01-03/#01-04'},
    '01-05/06': {'addr:unit': '#01-05/#01-06'},
    '01-07/08': {'addr:unit': '#01-07/#01-08'},
    '01-11': {'addr:unit': '#01-11'},
    '01-12': 'addr:unit',
    '01-13/14': {'addr:unit': '#01-13/#01-14'},
    '01-15/16': {'addr:unit': '#01-15/#01-16'},
    '01-17/18': {'addr:unit': '#01-17/#01-18'},
    '01-20': 'addr:unit',
    '01-21': 'addr:unit',
    '01-22': 'addr:unit',
    '01-23': 'addr:unit',
    '01-24 to 27': {'addr:unit': '#01-24/#01-25/#01-26/#01-27'},
    '01-25': 'addr:unit',
    '01-28': 'addr:unit',
    '01-30/31': {'addr:unit': '#01-30/#01-31'},
    '01-31': 'addr:unit',
    '01-32/33': {'addr:unit': '#01-32/#01-33'},
    '01-34': 'addr:unit',
    '01-35': 'addr:unit',
    '01-36A': 'addr:unit',
    '01-36B': 'addr:unit',
    '03-02': 'addr:unit',
    '05-110': 'addr:unit',
    '1 #01-24/25/26': {'addr:housenumber': '1', 'addr:unit': '#01-24/#01-25/#01-26'},
    '1 #03-29': {'addr:housenumber': '1', 'addr:unit': '#03-29'},
    '1, #02-26/27/28': {'addr:housenumber': '1', 'addr:unit': '#02-26/#02-27/#02-28'},
    '101 ，#01-08': {'addr:housenumber': '101', 'addr:unit': '#01-08'},
    '2 #B4-38': {'addr:housenumber': '2', 'addr:unit': '#B4-38'},
    '2-156/157': {'addr:unit': '#02-156/#02-157'},
    '200, 10th floor': {'addr:housenumber': '200', 'addr:floor': '10'},
    '21 Claymore Road': {'addr:street': 'Claymore Road', 'addr:housenumber': '21'},
    '29 - 33': {'addr:housenumber': '29, 33, 31, 32, 33'},
    '3 #01-34': {'addr:housenumber': '3', 'addr:unit': '#01-34'},
    '313 #02-10': {'addr:housenumber': '313', 'addr:unit': '#02-10'},
    '313 #B3-17': {'addr:housenumber': '313', 'addr:unit': '#B3-17'},
    '390 #03-34': {'addr:housenumber': '390', 'addr:unit': '#03-34'},
    '3E, #01-01': {'addr:housenumber': '3E', 'addr:unit': '#01-01'},
    '40     3-14': {'addr:housenumber': '40', 'addr:unit': '#03-14', 'addr:street': 'Lengkok Tujoh'},
    '45 Armenian Street': {'addr:street': 'Armenian Street', 'addr:housenumber': '45'}, '55, 56, 57A, 57B': 'addr:housenumber',
    '58 #01-06': {'addr:housenumber': '58', 'addr:unit': '#01-06'},
    '6 #04-102B': {'addr:housenumber': '6', 'addr:unit': '#04-102B'},
    '641, #20-50': {'addr:housenumber': '641', 'addr:unit': '#20-50'},
    '65\n#01-38': {'addr:housenumber': '65', 'addr:unit': '#01-38'},
    '7/9/11': {'addr:housenumber': '7, 9, 11'},
    '7，#01-05/07': {'addr:housenumber': '7', 'addr:unit': '#01-05/#01-07'},
    '8，#01-14': {'addr:housenumber': '8', 'addr:unit': '#01-14'},
    '9F 36': {'addr:unit': '#9F-36'},
    '??': 'rm',
    'B1 442': {'addr:housenumber': '442', 'addr:floor': 'B1'},
    'B1-01/02': {'addr:unit': '#B1-01/#B1-02'},
    'B1-03': 'addr:unit',
    'B1-04 to 07': {'addr:unit': '#B1-04/#B1-05/#B1-06/#B1-07'},
    'B1-08': 'addr:unit',
    'B1-09': 'addr:unit',
    'B1-10': 'addr:unit',
    'B1-11': 'addr:unit',
    'B1-12': 'addr:unit',
    'B1-13': 'addr:unit',
    'B1-14/15': {'addr:unit': '#B1-14/#B1-15'},
    'B1-16': 'addr:unit',
    'B1-17': 'addr:unit',
    'B1-19': 'addr:unit',
    'B1-20/21': {'addr:unit': '#B1-20/#B1-21'},
    'B1-22': 'addr:unit',
    'B1-23': 'addr:unit',
    'B1-24': 'addr:unit',
    'B1-25': 'addr:unit',
    'B1-26/27': {'addr:unit': '#B1-26/#B1-27'},
    'B1-28/29': {'addr:unit': '#B1-28/#B1-29'},
    'B1-30/31': {'addr:unit': '#B1-30/#B1-31'},
    'B1-32': 'addr:unit', 'B1-33': 'addr:unit',
    'B1-34': 'addr:unit', 'B1-35': 'addr:unit',
    'B1-36': 'addr:unit', 'B1-37': 'addr:unit',
    'B1-38/39': {'addr:unit': '#B1-38/#B1-39'},
    'B1-40': 'addr:unit', 'B1-41': 'addr:unit',
    'B1-42': 'addr:unit', 'B1-43': 'addr:unit',
    'B1-44 & 48 to 51': {'addr:unit': '#B1-44/#B1-48/#B1-49/#B1-50/#B1-51'},
    'B1-45': 'addr:unit',
    'B1-46': 'addr:unit',
    'B1-47': 'addr:unit',
    'B1-53': 'addr:unit',
    'B1-54': 'addr:unit',
    'B1-55': 'addr:unit',
    'B1-56': 'addr:unit',
    'B1-57': 'addr:unit',
    'B1-58': 'addr:unit',
    'B1-K6': 'addr:unit',
    'Blk 149, #01-64': {'addr:housenumber': '149', 'addr:unit': '#01-64'},
    'Blk 58-01-09': {'addr:housenumber': '58', 'addr:unit': '#01-09'},
    'Blk236 #01-1000': {'addr:housenumber': '236', 'addr:unit': '#01-1000'},
    'Block 836, Level 1': {'addr:housenumber': '836', 'addr:floor': '1'},
    'Floor 22 #884': {'addr:housenumber': '884', 'addr:floor': '22'},
    'Ground floor': {'addr:floor': 'G'},
    'Level 57, 10': {'addr:housenumber': '10', 'addr:floor': '57'},
    'Level G2, Crockfords Tower, 10': {'addr:housename': 'Crockfords Tower', 'addr:housenumber': '10', 'addr:floor': 'G2'},
    'Ministry of Social and Family Development': {'addr:housename': 'Ministry of Social and Family Development'},
    'Polo Club Restaurant & Bar': {'name': 'Polo Club Restaurant & Bar'},
    'Sentosa Island, Singapore': {'addr:suburb': 'Sentosa Island', 'addr:city': 'Singapore'},
    'Tower Blk, 20': {'addr:housename': 'Tower Block', 'addr:housenumber': '20'},
    'econ building 2': {'addr:housename': 'Econ Industrial Building', 'addr:housenumber': '2'},
    'j8호테ㄹ': {'addr:housename': 'J8', 'addr:housenumber': '8'},
    '#01-43': {'addr:unit':'#01-43'}}

KEY_SWAPS['building'] = {
    '138A': {'building': 'yes'},
    '5': {'building': 'yes'},
    'CET_Campus_East': {'building': 'yes'},
    'Caltex Petrol Pump Station': {'building': 'yes', 'name': 'Caltex Petrol Pump Station'},
    'EiS_Residences': {'name': 'EiS Residences', 'building': 'yes', 'building:use': 'residential'},
    'Garbage Collection Center': {'building': 'yes', 'name': 'Garbage Collection Center'},
    'IMM': {'building': 'yes'},
    'Kid Power Towers': {'building': 'yes', 'name': 'Kid Power Towers'},
    'Level_3,_JCube': {'building': 'yes', 'addr:housename': 'JCube', 'addr:floor': '3'},
    'Multi-storey_Carpark': {'building': 'yes', 'building:use': 'carpark'},
    'Office': {'building': 'yes', 'building:use': 'office'},
    'Orchard Central': {'building': 'yes', 'building:use': 'retail'},
    'Power_House': {'building': 'yes', 'building:use': 'power_house'},
    'Temple': {'building': 'yes', 'building:use': 'temple'},
    'apartments': {'building': 'yes', 'building:use': 'apartments'},
    'carpark': {'building': 'yes', 'building:use': 'carpark'},
    'cathedral': {'building': 'yes', 'building:use': 'cathedral'},
    'checkpoint': {'building': 'yes', 'building:use': 'checkpoint'},
    'church': {'building': 'yes', 'building:use': 'church'},
    'civic': {'building': 'yes', 'building:use': 'civic'},
    'collapsed': {'building': 'yes', 'building:use': 'collapsed'},
    'college': {'building': 'yes', 'building:use': 'college'},
    'commercial': {'building': 'yes', 'building:use': 'commercial'},
    'condominium': {'building': 'yes', 'building:use': 'condominium'},
    'construction': {'building': 'yes', 'building:use': 'construction'},
    'detached': {'building': 'yes', 'building:use': 'detached'},
    'dormitory': {'building': 'yes', 'building:use': 'dormitory'},
    'education': {'building': 'yes', 'building:use': 'education'},
    'entrance': {'building': 'yes', 'building:use': 'entrance'},
    'garage': {'building': 'yes', 'building:use': 'garage'},
    'garages': {'building': 'yes', 'building:use': 'garage'},
    'grandstand': {'building': 'yes', 'building:use': 'grandstand'},
    'greenhouse': {'building': 'yes', 'building:use': 'greenhouse'},
    'hangar': {'building': 'yes', 'building:use': 'hangar'},
    'hospital': {'building': 'yes', 'building:use': 'hospital'},
    'hotel': {'building': 'yes', 'building:use': 'hotel'},
    'house': {'building': 'yes', 'building:use': 'house'},
    'hut': {'building': 'yes', 'building:use': 'hut'},
    'industrial': {'building': 'yes', 'building:use': 'industrial'},
    'kindergarten': {'building': 'yes', 'building:use': 'kindergarten'},
    'manufacture': {'building': 'yes', 'building:use': 'manufacture'},
    'medical': {'building': 'yes', 'building:use': 'medical'},
    'mix_used': {'building': 'yes', 'building:use': 'mix_used'},
    'mosque': {'building': 'yes', 'building:use': 'mosque'},
    'o': 'rm',
    'office': {'building': 'yes', 'building:use': 'office'},
    'parlour': {'building': 'yes', 'building:use': 'parlour'},
    'political': {'building': 'yes', 'building:use': 'political'},
    'public': {'building': 'yes', 'building:use': 'public'},
    'railway_station': {'building': 'yes', 'building:use': 'railway_station'},
    'religious': {'building': 'yes', 'building:use': 'religious'},
    'residential': {'building': 'yes', 'building:use': 'residential'},
    'residential;yes': {'building': 'yes', 'building:use': 'residential'},
    'residentiale': {'building': 'yes', 'building:use': 'residential'},
    'retail': {'building': 'yes', 'building:use': 'retail'},
    'roof': {'building': 'yes', 'building:use': 'roof'},
    'ruins': {'building': 'yes', 'building:use': 'ruins'},
    'school': {'building': 'yes', 'building:use': 'school'},
    'semidetached_house': {'building': 'yes', 'building:use': 'semidetached_house'},
    'service': {'building': 'yes', 'building:use': 'service'},
    'shed': {'building': 'yes', 'building:use': 'shed'},
    'shop': {'building': 'yes', 'building:use': 'shop'},
    'shrine': {'building': 'yes', 'building:use': 'shrine'},
    'stable': {'building': 'yes', 'building:use': 'stable'},
    'temple': {'building': 'yes', 'building:use': 'temple'},
    'terrace': {'building': 'yes', 'building:use': 'terrace'},
    'train_station': {'building': 'yes', 'building:use': 'train_station'},
    'transportation': {'building': 'yes', 'building:use': 'transportation'},
    'university': {'building': 'yes', 'building:use': 'university'},
    'wall': {'building': 'yes', 'building:use': 'wall'},
    'warehouse': {'building': 'yes', 'building:use': 'warehouse'},
    'yes;retail': {'building': 'yes', 'building:use': 'retail'},
}

KEY_SWAPS['building_1'] = {
    'Blk 68': {'building': 'yes', 'name': 'Blk 68','addr:housenumber': '68', 'building:use': 'convention_center'}
}

KEY_SWAPS['building:use'] = {
    'parking': {'building': 'yes', 'amenity': 'parking', 'building:use': 'carpark'}
}

KEY_SWAPS['email'] = {
    'http://www.founderbakkutteh.com/': 'contact:website',
    'http://www.ngahsiobkt.com/': 'contact:website'}

KEY_SWAPS['contact:email'] = {
    'http://www.founderbakkutteh.com/': 'contact:website',
    'http://www.ngahsiobkt.com/': 'contact:website'}

KEY_SWAPS['phone'] = {
    '90259090 www.apple-corner.com': {'contact:phone': '90259090', 'contact:website': 'www.apple-corner.com'}, 
    '2755555': {'contact:phone': '18002755555'},
    '+65 +65 6694 0630':  {'contact:phone': '+6566940630'}}

KEY_SWAPS['contact:phone'] = {
    '90259090 www.apple-corner.com': {'contact:phone': '90259090', 'contact:website': 'www.apple-corner.com'}, 
    '2755555': {'contact:phone': '18002755555'},
    '+65 +65 6694 0630':  {'contact:phone': '+6566940630'}}

KEY_SWAPS['website'] = {
    'amrisehotel.com': {'contact:website': 'http://amrisehotel.com'},
    'bike.shimano.com.sg/': {'contact:website': 'http://bike.shimano.com.sg'},
    'fax 67088787': {'contact:fax': '+6567088787'},
    'ghihotels.com': {'contact:website': 'http://ghihotels.com'},
    'holidayinnexpress.com': {'contact:website': 'http://holidayinnexpress.com'},
    'morihostel.com': {'contact:website': 'http://morihostel.com'},
    'nccs.com.sg\u200e': {'contact:website': 'http://www.nccs.com.sg/'},
    'neosmiles.com.sg': {'contact:website': 'http://neosmiles.com.sg'},
    'ppcc.org.sg': {'contact:website': 'http://www.ppcc.org.sg/'},
    'singapore.capribyfraser.com': {'contact:website': 'http://singapore.capribyfraser.com/en'},
    'sttemple.com\u200e': {'contact:website': 'http://sttemple.com'},
    'thegrandimperialhotel.com': {'contact:website': 'http://bike.shimano.com.sg'}
}

KEY_SWAPS['source'] = {
    '+65 6338 6131': {'contact:phone': '+6563386131'},
    '+65 6376 9740': {'contact:phone': '+6563769740'},
    'http://emint.com/': 'contact:website',
    'http://en.wikipedia.org/wiki/Sembawang_Hot_Spring': 'contact:website',
    'http://lake-lifeec.com/site-plan/': 'contact:website',
    'http://learntoswim.com.sg/': 'contact:website',
    'http://makespace.sg': 'rm',
    'http://map.nus.edu.sg/#page=home': 'contact:website',
    'http://www.cantonmentpri.moe.edu.sg/': 'contact:website',
    'http://www.cdl.com.sg/oceanfront/main.html': 'contact:website',
    'http://www.lowereastsidesg.com/': 'contact:website',
    'http://www.ntu.edu.sg/has/Graduate/Pages/GH2.aspx': 'contact:website',
    'http://www.pinnacleduxton.com.sg/': 'contact:website',
    'http://www.propertyguru.com.sg/project/domus-1542': 'contact:website',
    'http://www.propertyguru.com.sg/project/iresidences-1368': 'contact:website',
    'http://www.propertyguru.com.sg/search/pearl-hill-terrace': 'contact:website',
    'http://www.sgcarmart.com/news/carpark_index.php?ID=121&LOC=all&TYP=carpark&SRH=': 'contact:website',
    'http://www.tpcc.sg/': 'contact:website',
    'https://www.facebook.com/tropica.singapore': 'contact:website',
    'nparks.gov.sg;Bing': {'contact:website': 'nparks.gov.sg'},
    'swedenabroad.com': 'contact:website',
    'www.Westwood-Residences-EC.com': 'contact:website',
    'www.mhe-demag.com': 'contact:website',
}

KEY_SWAPS['amenity'] = {
    'Childcare Centre': {'amenity': 'childcare'},
    'Factory': {'amenity': 'factory'},
    'Mail drop': {'amenity': 'mail_drop'},
    'Mall': {'amenity': 'mall'},
    'community_center': {'amenity': 'community_centre'}
}

KEY_SWAPS['landuse'] = {
    'Punggol CC': {'alt_name': 'Punggol CC', 'amenity': 'community_centre', 'landuse': 'public_building'},
    'garages': {'landuse': 'garage'},
}

KEY_SWAPS['denomination'] = {
    'Charismatic': {'denomination': 'charismatic'},
    'Chinese': {'denomination': 'taoist'},
    'Christian': {'denomination': 'christian'},
    'De Jiao - Teaching of Virtue': {'denomination': 'de_jiao'},
    'Taoist': {'denomination': 'taoist'},
    'tua_pek_gong': {'denomination': 'christian'}
}

KEY_SWAPS['service'] = {
    'Sixth Avenue': 'name'
}

KEY_SWAPS['oneway'] = {
    '-1': {'oneway': 'no'}
} 

KEY_SWAPS['name'] = {
    'Makespace Singapore': {'contact:website': 'http://makespace.sg', 'addr:housename': 'King George\'s Building', 'amenity': 'office'},
}

KEY_MERGE = {
    'email': 'contact:email',
    'facebook': 'social:facebook',
    'contact:facebook': 'social:facebook',
    'fax': 'contact:fax',
    'contact:google_plus': 'social:google_plus',
    'contact:instagram': 'social:instagram',
    'phone': 'contact:phone',
    # 'postal_code': 'addr:postcode'
    'contact:twitter': 'social:twitter',
    'website': 'contact:website',
    'site': 'landuse'
}

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
                            

INPUT_OSM_FILE = "singapore_sg_10.osm"  # Replace this with your osm file
OUTPUT_OSM_FILE = "singapore_fixed_10.osm"

def str_to_list(str_value):
    split_chars = [';', ',', '/']
    lst_value = list()
    for char in split_chars: 
        if str_value.find(char) > -1:
            lst_value = str_value.split(char)
    if len(lst_value) == 0:
        lst_value.append(str_value)
    print('str_to_list :: str_value: {0}, lst_value: {1}'.format(str_value, lst_value))
    return lst_value

def list_to_str(lst_value, deliminator=', '):
    str_value = deliminator.join(str(e) for e in lst_value)
    return str_value

def format_cuisine(str_value):
    return str_value.replace('_', ' ').strip().title()

def format_addrunit(str_unit):
    if str_unit.startswith('#') == False:
        return '#' + str_unit.strip()
    return str_unit

def format_url(str_url):
    if str_url.startswith('http') == False:
        return 'http://' + str_url
    return str_url

def format_phonefax(str_phonefax):
    rm_chars = ['(', ')', ' ', '-']
    print(' >> pre-format_phonefax : {0}'.format(str_phonefax))
    for char in rm_chars: 
        str_phonefax = str_phonefax.replace(char, '')
        print(' >>>> rmchar-format_phonefax : {0}, char: {1}'.format(str_phonefax, char))
    print(' >> post-rmchar-format_phonefax : {0}'.format(str_phonefax))
    
    if len(str_phonefax) == 10 and str_phonefax.startswith('65'):
        str_phonefax = '+' + str_phonefax
    if len(str_phonefax) == 10 and str_phonefax.startswith('800'):
        str_phonefax = '1' + str_phonefax
    elif len(str_phonefax) == 8:
        str_phonefax = '+65' + str_phonefax
    elif str_phonefax.find('1800') > -1:
        str_phonefax = str_phonefax[str_phonefax.find('1800'):]
    print(' >> post-format_phonefax : {0}'.format(str_phonefax))
    
    return str_phonefax


def replace_abbreviate(str_value):
    lst_str = str_value.split()
    new_lst_str = [ABBREV_KEYS[w] if w in ABBREV_KEYS.keys() else w for w in lst_str]
    return ' '.join(new_lst_str)
  
def fix_value_formats(elem):
    for tag in elem.iter("tag"):
        k = tag.attrib['k']
        v = tag.attrib['v']
        if k == 'cuisine':
            lst_v = str_to_list(v)
            lst_new_v = list()
            for val in lst_v:
                val = format_cuisine(val)
                lst_new_v.append(val)
                print('cuisine_iter_val:: {0}'.format(val))
            print('cuisine_lst_new_v:: {0}'.format(lst_new_v))
            new_v = list_to_str(lst_new_v, '; ')
            print('FORMAT_cuisine :: k: {0}, v: {1}, formatted_v: {2}'.format(k, v, new_v))
            tag.set('v', new_v)
        elif k == 'contact:website' or k == 'website':
            new_v = format_url(v)
            print('FORMAT_website :: k: {0}, v: {1}, formatted_v: {2}'.format(k, v, new_v))
            tag.set('v', new_v)
        elif k == 'contact:phone' or k == 'contact:fax' or k == 'phone' or k == 'fax':
            lst_v = str_to_list(v)
            lst_new_v = list()
            for val in lst_v:
                val = format_phonefax(val)
                lst_new_v.append(val)
                print('phonefax_iter_val:: {0}'.format(val))
            print('phonefax_lst_new_v:: {0}'.format(lst_new_v))
            new_v = list_to_str(lst_new_v, '/')
            print('FORMAT_phonefax :: k: {0}, v: {1}, formatted_v: {2}'.format(k, v, new_v))
            tag.set('v', new_v)
        elif k == 'addr:unit':
            lst_v = str_to_list(v)
            lst_new_v = list()
            for val in lst_v:
                val = format_addrunit(val)
                lst_new_v.append(val)
                print('addrunit_iter_val:: {0}'.format(val))
            print('addrunit_lst_new_v:: {0}'.format(lst_new_v))
            new_v = list_to_str(lst_new_v, '/')
            print('FORMAT_unit :: k: {0}, v: {1}, formatted_v: {2}'.format(k, v, new_v))
            tag.set('v', new_v)
    return elem


def fix_spelling_case(elem):
    spellcheck_keys = ['addr:street', 'addr:housename', 'addr:city', 'contact:phone', 'phone']
    for tag in elem.iter("tag"):
        k = tag.attrib['k']
        v = tag.attrib['v']
        if k in spellcheck_keys :
            if v in TYPO_FIXES.keys():
                print('TYPO_FIX :: k: {0}, v: {1}, fixed_v: {2}'.format(k, v, TYPO_FIXES[v]))
                v = TYPO_FIXES[v]
            v = replace_abbreviate(v)
            if k == 'addr:street': 
                v = v.title()
            tag.set('v', v)

    return elem


def merge_key(elem):
    for tag in elem.iter("tag"):
        k = tag.attrib['k']
        v = tag.attrib['v']

        ## KEY MERGE to consolidate values for repeated keys
        for old_key, new_key in KEY_MERGE.items():
            if k == old_key:
                print('KEYMERG :: old_key: {0}, v: {1}, new_key:{2}'.format(k, v, new_key))
                tag.set('k', new_key)
    return elem

def swap_key(elem):
    for tag in elem.iter("tag"):
        k = tag.attrib['k']
        v = tag.attrib['v']
        for kys, new_keyvalues in KEY_SWAPS.items():
            if v in new_keyvalues.keys() and k == kys:
                
                print('KEYSWAP :: k: {0}, v: {1}, kys: {2}, newky: {3}'.format(k, v, kys, new_keyvalues[v]))
                # elem.remove(tag)
                if isinstance(new_keyvalues[v], dict):
                    for newk, newv in new_keyvalues[v].items():
                        # str_xPath = "tag[@name='" + newk + "']"
                        # print("str_xPath {0} elem.tag {1}".format(str_xPath, elem.tag))
                        # existing = elem.find(str_xPath)
                        # if existing != None:
                        #     print("existing {0}".format(existing))
                        newtag = ET.Element("tag")
                        newtag.set('k', newk)
                        newtag.set('v', newv)
                        elem.append(newtag)
                    elem.remove(tag)
                else:
                    if new_keyvalues[v] == 'rm':
                        elem.remove(tag)
                    else:
                        tag.set('k', new_keyvalues[v])
    return elem

def fix_element(elem):
    for tag in elem.iter("tag"):
        k = tag.attrib['k']
        v = tag.attrib['v']

        ## KEY MERGE to consolidate values for repeated keys
        for old_key, new_key in KEY_MERGE.items():
            if k == old_key:
                print('KEYMERG :: old_key: {0}, v: {1}, new_key:{2}'.format(k, v, new_key))
                tag.set('k', new_key)

        ##  KEY SWAPS for Incorrect key/value pairs
        for kys, new_keyvalues in KEY_SWAPS.items():
            if v in new_keyvalues.keys() and k == kys:
                # print(tag.attrib['k'])
                # print(tag.attrib['v'])

                print('KEYSWAP :: k: {0}, v: {1}, kys: {2}, newky: {3}'.format(k, v, kys, new_keyvalues[v]))
                # elem.remove(tag)
                if isinstance(new_keyvalues[v], dict):
                    for newk, newv in new_keyvalues[v].items():
                        newtag = ET.Element("tag")
                        newtag.set('k', newk)
                        newtag.set('v', newv)
                        elem.append(newtag)
                    elem.remove(tag)

                else:
                    if new_keyvalues[v] == 'rm':
                        elem.remove(tag)
                    else:
                        tag.set('k', new_keyvalues[v])

        
        ## TYPO & Abbreviation Fix
        spellcheck_keys = ['addr:street', 'addr:housename', 'addr:city', 'contact:phone', 'phone']
        if k in spellcheck_keys :
            if v in TYPO_FIXES.keys():
                print('TYPO_FIX :: k: {0}, v: {1}, fixed_v: {2}'.format(k, v, TYPO_FIXES[v]))
                v = TYPO_FIXES[v]
            v = replace_abbreviate(v)
            tag.set('v', v)

        ## Fix Value Formats
        if k == 'cuisine':
            lst_v = str_to_list(v)
            lst_new_v = list()
            for val in lst_v:
                val = format_cuisine(val)
                lst_new_v.append(val)
                print('cuisine_iter_val:: {0}'.format(val))
            print('cuisine_lst_new_v:: {0}'.format(lst_new_v))
            new_v = list_to_str(lst_new_v, '; ')
            print('FORMAT_cuisine :: k: {0}, v: {1}, formatted_v: {2}'.format(k, v, new_v))
            tag.set('v', new_v)
        elif k == 'contact:website' or k == 'website':
            new_v = format_url(v)
            print('FORMAT_website :: k: {0}, v: {1}, formatted_v: {2}'.format(k, v, new_v))
            tag.set('v', new_v)
        elif k == 'contact:phone' or k == 'contact:fax' or k == 'phone' or k == 'fax':
            lst_v = str_to_list(v)
            lst_new_v = list()
            for val in lst_v:
                val = format_phonefax(val)
                lst_new_v.append(val)
                print('phonefax_iter_val:: {0}'.format(val))
            print('phonefax_lst_new_v:: {0}'.format(lst_new_v))
            new_v = list_to_str(lst_new_v, '/')
            print('FORMAT_phonefax :: k: {0}, v: {1}, formatted_v: {2}'.format(k, v, new_v))
            tag.set('v', new_v)
        elif k == 'addr:unit':
            lst_v = str_to_list(v)
            lst_new_v = list()
            for val in lst_v:
                val = format_addrunit(val)
                lst_new_v.append(val)
                print('addrunit_iter_val:: {0}'.format(val))
            print('addrunit_lst_new_v:: {0}'.format(lst_new_v))
            new_v = list_to_str(lst_new_v, '/')
            print('FORMAT_unit :: k: {0}, v: {1}, formatted_v: {2}'.format(k, v, new_v))
            tag.set('v', new_v)
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
            yield fix_value_formats(fix_spelling_case(swap_key(merge_key(elem))))
            root.clear()


with open(OUTPUT_OSM_FILE, 'wb') as output:
    output.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write(b'<osm>\n')

    # Write every kth top level element
    for i, element in enumerate(get_element(INPUT_OSM_FILE)):
        # if i % k == 0:
        output.write(ET.tostring(element, encoding='utf-8'))

    output.write(b'</osm>')
