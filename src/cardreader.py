#!/usr/bin/env python

import signal
import time
import sys

from pirc522 import RFID

run = True
#rdr = RFID(bus=1, device=0, pin_irq=32, pin_rst=22)
rdr = RFID(bus=1, device=0, pin_ce=12, pin_irq=32, pin_rst=22)
# this works by 3. jun 5 pm
# rdr = RFID(bus=1, device=0, pin_ce=12, pin_irq=32, pin_rst=22)
# SDA = BOARD12
# SCK = BOARD40
# MOSI = BOARD38
# MISO = BOARD35
# IRQ = BOARD32
# RST = BOARD22

util = rdr.util()
util.debug = True

def end_read(signal,frame):
    global run
    print("\nCtrl+C captured, ending read.")
    run = False
    rdr.cleanup()
    sys.exit()

signal.signal(signal.SIGINT, end_read)

print("Starting")
while run:
    rdr.wait_for_tag()

    (error, data) = rdr.request()
    print(error)
    if not error:
        print("\nDetected: " + format(data, "02x"))

    (error, uid) = rdr.anticoll()
    if not error:
        print("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))

        print("Setting tag")
        util.set_tag(uid)
        print("\nAuthorizing")
        #util.auth(rdr.auth_a, [0x12, 0x34, 0x56, 0x78, 0x96, 0x92])
        util.auth(rdr.auth_b, [0x74, 0x00, 0x52, 0x35, 0x00, 0xFF])
        print("\nReading")
        util.read_out(4)
        print("\nDeauthorizing")
        util.deauth()

        time.sleep(1)
