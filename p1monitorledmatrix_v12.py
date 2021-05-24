################################################################################
#!/usr/bin/env python3
# Frank van der Niet
# 26 april 2021
# This scripts reads the UDP broadcast on poort 40721 from the P1monitor software
# Link to P1 monitor software: https://www.ztatz.nl/p1-monitor/ 
# The jason message is decodes and printed on a LED matrix display
# This script uses the luma led matrix driver
# link to luma led: https://luma-led-matrix.readthedocs.io/en/latest/
################################################################################

#This section imports the necessary python libs
import json                 # for decoding the json message
import select               # the unix select() function
import socket               # for setting up de UDP listener
import re                   # for using regular expressions
import time                 # for time functions

#This sections imports the necessaty python luma led matrix libs
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

#Setup of the UDP broadast read    
port = 40721 
bufferSize = 1024 
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('<broadcast>', port))
s.setblocking(0)

#create matrix device and setup
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, width=48, height=8, block_orientation=0, rotate=0, blocks_arranged_in_reverse_order=True)

#Initialize some variables for max production
maxproduction = 0                                   #Set max production to zero
counter = 0                                         #Counter used for printing max production

#Endless loop
while True:
    msg="leeg"
    while msg=="leeg":
        #Get the broadcast
        result = select.select([s],[],[])               #Wait for the broadcast
        msg = result[0][0].recv(bufferSize)             #Write the broadcast to msg
        msg_utf = msg.decode('utf-8')                   #Decode msg using the utf-8 encoding

    counter = counter + 1

    #Get the values we need from the json message
    broadcast   = json.loads(msg_utf) 
    datetime    = str(broadcast['TIMESTAMP_lOCAL'])
    production  = int((broadcast['PRODUCTION_KW'])*1000)
    consumption = int((broadcast['CONSUMPTION_KW'])*1000)
    
    #Print to console for debugging, uncomment when used
    #print("---------------------------------")
    #print(msg)
    #print("Datum/tijd:  "   + (datetime))
    #print("Production:  "   + str(production))
    #print("Consumption: "   + str(consumption))
    #print("Counter: "       + str(counter))
    #print("maxproduction: " + str(maxproduction))

    #Make the message, send production or consumption to the ledmatrix
    if production>consumption:
      bigmsg = "T: " + str(production) + " W" 
    else:
      bigmsg = "V: " + str(consumption) + " W"
   
    #If there is a new production record, load its value in maxproduction
    if production > maxproduction:
      maxproduction = production

    #Print message
    with canvas(device) as draw:
      text(draw, (0, 0), bigmsg, fill="white", font=proportional(LCD_FONT))

    #For every 20 rounds print maxproduction
    #Uncomment when you want to use this
    #if counter == 20:
    #  bigmsg = "Max: " + str(maxproduction)
    #  with canvas(device) as draw:
    #    text(draw, (0, 0), bigmsg, fill="white", font=proportional(LCD_FONT))
    #  counter = 0
    #  time.sleep(5)

################################################################################
# END OF PROGRAM
################################################################################
