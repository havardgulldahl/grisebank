from pirc522 import RFID
import signal
import time

#rdr = RFID()
rdr = RFID(device=1, pin_ce=0, pin_rst=37, pin_irq=29)
util = rdr.util()
# Set util debug to true - it will print what's going on
util.debug = True

while True:
    # Wait for tag
    rdr.wait_for_tag()
    # Request tag
    (error, data) = rdr.request()
    if not error:
        print("\nDetected")
        (error, uid) = rdr.anticoll()
        if not error:
            # Print UID
            print("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))
rdr.cleanup()
