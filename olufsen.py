#!/usr/bin/python
# Domoticz to Bang and Olufsen ML Gateway Bridge
#
# Useage: python olufsen.py <Device> <A or V> <Source>
# An example would be python olufsen.py BS3 V V.MEM
# Configure your devices based on the device ML number in the ML Gateway 
# programming screen. In this example, a Beovision 10 (BV10) has a MLN of 1
# put the command in the On or Off action of the Domoticz button using:
# script:///home/pi/domoticz/progs/olufsen.py BV10 V V.MEM.
# Note the <Source> should be one of the sources listed in the BEO4Source
# array below. the <Device> can be whatever name you wish - it just refers to the MLN
# number of the device you wish to control
# Normally the Off script would be (for the Beovision 10 example):
#    script:///home/pi/domoticz/progs/olufsen.py BV10 V STANDBY
#
# Don't forget to make this python script executable (chmod +x olufsen.py)



import socket               # Import socket module
import time		    # Import Time module for delays
import sys
import getopt
import urllib2
import json

Debug = True

# Environmental Parameters
# If necessary, change to your own environment
Domoticz = '127.0.0.1:8080'
hostname = 'mlgw.local'		# Masterlink Gateway hostname (or IP address)
# MLNDict is the MLN Number of the devices you want to control taken from MLGW setup
MLNDict = {'BS3':'01','BV10':'02', 'BLP':'03'}

#port number of MLGW (from MLGW System/MLGW Protocol settings) ethernet option must be set 
port = 9000                # Reserve a port for your service.

# Not strictly necessary, but this will keep the Domoticz status on the B&O switches
# consistant.
# When switching on a device, it will switch off othe device statuses only in Domoticz
# Just update with the button name and IDX of the B&O switches for each MLN device.
# If you aren't bothered, just set the next constant to False.
consistentSwitch = True
Domoswitches = {'BS3': [366, 371, 368], 'BV10': [367, 372, 365]}

#Shouldn't need to change anything below this line______________________________________

# Setup B&O datagrams
if Debug:
   ping  = '01360000'.decode('hex')
   pong  = '01370000'.decode('hex')

serno = '01390000'.decode('hex')


BEO4Source = {'STANDBY': '0C', 'SLEEP': '47', 'TV': '80', 'RADIO': '81', 'AUX_V': '82',  \
		'DTV2': '82', 'AUX_A': '83', 'VTR': '85', 'V.MEM': '85', 'DVD2': '85',   \
		'CDV': '86', 'DVD': '86', 'CAMCORDER': '87','CAMERA': '87', 'TEXT': '88',\
		'V_SAT': '8A', 'DTV': '8A', 'PC': '8B', 'DOORCAM': '8D', 'V.AUX2': '8D', \
		'TP1': '91', 'A.MEM': '91', 'CD': '92', 'PH': '93','N.RADIO': '93',      \
		'TP2': '94','N.MUSIC': '94', 'CD2': '97','JOIN': '97', 'VTR2': 'A8',     \
		'MEDIA': '84', 'WEB': '8C', 'PHOTO': '8E', 'USB2':'90','SERVER': '95',   \
		'NET': '96', 'PICTURE_IN_PICTURE': 'FA', 'P-AND-P': 'FA'}
BEO4Digits =   {'CIFFER_0': '00', 'CIFFER_1': '01', 'CIFFER_2': '02', 'CIFFER_3': '03',  \
		'CIFFER_4': '04', 'CIFFER_5': '05', 'CIFFER_6': '06', 'CIFFER_7': '07',  \
		'CIFFER_8': '08', 'CIFFER_9': '09'}
BEO4SrcCtrl=   {'STEP_UP': '1E', 'STEP_DW': '1F', 'REWIND': '32', 'REC_RETURN': '33',    \
		'RETURN': '33', 'WIND': '34', 'GO': '35', 'PLAY': '35', 'STOP': '36',    \
		'CNTL_WIND': 'D4', 'Yellow':  'D4', 'CNTL_REWIND': 'D5', 'Green': 'D5',  \
		'CNTL_STEP_UP': 'D8', 'Blue': 'D8', 'CNTL_STEP_DW': 'D9', 'Red': 'D9'}
BEO4SPCtrl=    {'MUTE': '0D','PICTURE_TOGGLE': '1C','P.MUTE': '1C','PICTURE_FORMAT':'2A',\
		'FORMAT': '2A', 'SOUND': '44', 'SPEAKER': '44', 'MENU': '5C',            \
		'ANALOG_UP_1': '60', 'Volume.UP': '60', 'ANALOG_DW_1': '64',             \
		'Volume_DOWN': '64', 'CINEMA_ON': 'DA', 'CINEMA_OFF': 'DB'}
BEO4Other=     {'OPEN_STAND': 'F7', 'STAND': 'F7', 'CLEAR': '0A', 'STORE': '0B',         \
		'RESET': '0E', 'INDEX': '0E', 'BACK': '14', 'CMD_A': '15', 'MOTS': '15', \
		'GOTO': '20', 'TRACK': '20', 'LAMP': '20', 'SHOW_CLOCK': '28',           \
		'CLOCK':'28', 'EJECT': '2D', 'RECORD': '37', 'MEDIUM_SELECT': '3F',      \
		'SELECT': '3F', 'TURN': '46', 'SOUND': '46', 'EXIT': '7F'}
BEO4Cont=      {'C_REWIND': '70', 'Continue_REWIND': '70', 'C_WIND': '71',
		'Continue_WIND': '71', 'C_STEP_UP': '72', 'Continue_step_UP': '72',      \
		'C_STEP_DW': '73', 'Continue_step_DOWN': '73', 'CONTINUE': '75',         \
		'Continue_(other_keys)': '75', 'CNTL_C_REWIND': '76',                    \
		'Continue_Green': '76', 'CNTL_C_WIND': '77', 'Continue_Yellow': '77',    \
		'CNTL_C_STEP_UP': '78', 'Continue_Blue': '78', 'CNTL_C_STEP_DW': '79',   \
		'Continue_Red': '79', 'KEY_RELEASE': '7E'}
BEO4Curs=      {'SELECT': '13', 'Cursor_SELECT': '13', 'CURSOR_UP':'CA','CURSOR_DW':'CB',\
		'CNTL_0': 'C0', 'SHIFT-0': 'C0', 'EDIT': 'C0', 'CNTL_1': 'C1',           \
		'SHIFT-1': 'C1', 'RANDOM': 'C1', 'CNTL_2': 'C2', 'SHIFT-2': 'C2',        \
		'CNTL_3': 'C3', 'SHIFT-3': 'C3', 'CNTL_4': 'C4', 'SHIFT-4': 'C4',        \
		'CNTL_5': 'C5', 'SHIFT-5': 'C5', 'CNTL_6': 'C6', 'SHIFT-6': 'C6',        \
		'CNTL_7': 'C7', 'SHIFT-7': 'C7', 'CNTL_8': 'C8', 'SHIFT-8': 'C8',        \
		'CNTL_9': 'C9', 'SHIFT-9': 'C9', 'REPEAT': 'C3', 'SELECT': 'C4'}


def clearIDX(device):
   if consistentSwitch:
     for idx in Domoswitches[device]:
        command = 'http://'+Domoticz+'/json.htm?type=devices&rid='+str(idx)
	if Debug:
	   print command
	response = urllib2.urlopen(command)
	response_dict = json.loads(response.read())	
        rev = response_dict.get('result',{})[0].get('Name',{})
        result = response_dict.get('result',{})[0].get('Status',{})
	print rev,result
	if result == 'On':
	   command = 'http://'+Domoticz+'/json.htm?type=command&param=udevice&idx='+str(idx)+'&nvalue=0&svalue=0'
	   if Debug:
	  	print command
	   urllib2.urlopen(command)
   return

def buildMLString(device,va,source):
   MLString = '01010300'
   if va == 'V':
	otype = '00'
   else:
	otype = '01'
   if Debug:
     print (MLString, device, va, source)
   if source in BEO4Source:   
	clearIDX(device)
	return(''.join((MLString,MLNDict[device],otype,BEO4Source[source])))
   if source in BEO4SPCtrl:
	return(''.join((MLString,MLNDict[device],otype,BEO4SPCtrl[source])))


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
try:
   host = socket.gethostbyname(hostname) # Connect to Mlgw.local
   if Debug:
      print "Connecting to: ",host, port
except socket.gaierror,err:
   print "cannot resolve hostname: ",hostname,err


s.connect((host, port))
if Debug:
   print ("Connected")
   # Sending Serial Number Request	
   print "Sending Serial Number Request"
s.send(serno)
if Debug:
   print s.recv(12)
MLString = buildMLString(sys.argv[1], sys.argv[2], sys.argv[3])
if Debug:
   print MLString
result = s.send(MLString.decode('hex'))
print result
s.close                     # Close the socket when done


