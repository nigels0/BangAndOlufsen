# BangAndOlufsen
Bridging code to link a Bang and Olufsen ML Gateway to Domoticz home automation software

This python script is used within an action button from Domoticz (www.domoticz.com) to be able to control Bang and Olufsen Masterlink connected products. You will need the B&O ML Gateway to be able to use this.

This was written for a Raspberry PI running Domoticz, with this code running on the same Raspberry Pi. Some environmental variables (IP addresses, ports etc) may need to be changed for this to work for you.

Useage from the command line: python olufsen.py {Device} {A or V} {Source}

An example would be python olufsen.py BS3 V V.MEM

Configure your devices based on the device ML number in the ML Gateway 
programming screen. In the code, a Beovision 10 (BV10) has a MLN of 3 but change this based on your ML Gateway configuration.

You can put the command in the On or Off action of the Domoticz button using:

script:///home/pi/domoticz/progs/olufsen.py BV10 V V.MEM.

Note the {Source} should be one of the sources listed in the BEO4Source
array below. the {Device} can be whatever name you wish - it just refers to the MLN
number of the device you wish to control
Choose A or V depending whether it is an audio or video product
Normally the Off script would be (for the Beovision 10 example):

  script:///home/pi/domoticz/progs/olufsen.py BV10 V STANDBY

 Don't forget to make this python script executable (chmod +x olufsen.py)

You need to edit the python script to be able to add your devices and their masterlink number.
