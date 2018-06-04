from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.logger import Logger

from pitftscreen import PiTFT_Screen 
from pirc522 import RFID # pip install pirc522

import yaml # pip install PyYAML

import configparser

import bank

class GriseBank(Widget):
    accountName = StringProperty("Ingen")
    accountValue = NumericProperty(0.0)
    status = StringProperty("Velg konto...")

    def update(self, dt):
        'update stuff'
        #Logger.info("updating gris , %r", dt)

    def setScreen(self, screen):
        screen.Button1Interrupt(lambda x: self.button(1, x))
        screen.Button2Interrupt(lambda x: self.button(2, x))
        screen.Button3Interrupt(lambda x: self.button(3, x))
        screen.Button4Interrupt(lambda x: self.button(4, x))
        screen.Backlight(True)
        self.screen = screen

    def setAccounts(self, accounts:[]):
        print("setting accounts")
        #pr(accounts)
        self.accounts = accounts

    def button(self, btnNumber:int, channel:int):
        print('pressed button {}, gpio channel {}'.format(btnNumber, channel))
        _map = {2:0, 4:1}
        acc = self.accounts[_map[btnNumber]]
        self.accountName = acc.title
        self.accountValue = acc.details.balance
        return
        if btnNumber == 1:
            self.accountName = "Bjarne"
            self.accountValue = 20 
        elif btnNumber == 2:
            self.accountName = "Anna"
            self.accountValue = 50 
        elif btnNumber == 3:
            self.accountName = "Cecilie"
            self.accountValue = 92 
        elif btnNumber == 4:
            self.accountName = "BASE"
            self.accountValue = -1 
        self.status = "Skann kortet..."

    def scan(self, card):
        'scaning rfid card'
        Logger.debug ('scanning rfid card: %s', card)
        self.status = card.name or card.hex
        if card.reward > 0:
            Logger.info("Rewarding %s based on card", card.reward)

    def on_stop(self):
        Logger.debug("on_stop")

class GriseBankApp(App):
    def setScreen(self, screen):
        self.screen = screen

    def setBank(self, bank):
        self.bank = bank

    def setCards(self, cards):
        self.cards = cards

    def build(self):
        self.gris = GriseBank()
        self.gris.setScreen(self.screen)
        self.gris.setAccounts(self.bank.users)
        Clock.schedule_interval(self.gris.update, 1.0/60.0)
        self.RFID = RFIDReader(self.on_rfid_card)
        Clock.schedule_interval(self.RFID.update, 1.0/20.0)
        return self.gris

    def on_stop(self):
        """Event handler for the on_stop event which is fired when the
        application has finished running (i.e. the window is about to be
        closed).
        """
        self.gris.on_stop()
        self.RFID.on_stop()

    def on_rfid_card(self, card):
        'this is run when a new card is read'
        Logger.info('rfid card read: %r', card)
        # look for card in known cards list
        for c in self.cards:
            if c['hex'] == card.hex:
                # we know it
                card.name = c['name']
                card.reward = c['reward']

        self.gris.scan(card)

class RFIDCard:
    'Model for rfid (mifare rc522) cards or tags'

    def __init__(self, uid):
        self.uid = uid
        self.hex = ''.join('{:02X}'.format(a) for a in uid)
        self.name = None # set later
        self.reward = -1 # set later

    def __str__(self):
        return '<RFIDCard: {} ({})>'.format(self.hex, self.name)

class RFIDReader:

    # The 2.8TFT uses the hardware SPI pins (SCK, MOSI, MISO, CE0, CE1), #25 and #24. 
    # buttons: #23, #22, #27/#21, and #18
    # 
    # Thus, we need to set up the rc522 RFID reader on SPI1, and on unused pins
    # SDA = BOARD12
    # SCK = BOARD40
    # MOSI = BOARD38
    # MISO = BOARD35
    # IRQ = BOARD32
    # RST = BOARD15
    # self.rdr = RFID(bus=1, device=0, pin_ce=12, pin_irq=32, pin_rst=15)

    def __init__(self, callback_new_rfid_fn):
        'Set up RFID reader'
        self.rdr = RFID(bus=1, device=0, pin_ce=12, pin_irq=32, pin_rst=15)
        util = self.rdr.util()
        util.debug = True
        self.callbackfn = callback_new_rfid_fn # call this function with a RFIDCard() on new card detected
        # TODO: use kivy events https://kivy.org/docs/guide/events.html
        self.last_card = None # to filter out duplicates

    def on_stop(self):
        #Logger.debug("on_stop")
        self.rdr.cleanup()

    def card_detected(self, uid):
        'Is run on each card detected'
        if uid == self.last_card:
            # duplicate
            return
        self.last_card = uid
        self.callbackfn(RFIDCard(uid))

    def update(self, dt):
        'check if we have a new card nearby. Run this periodically'

        #Logger.info("wating fir tag, %r", dt)
        (error, data) = self.rdr.request()
        if not error:
            Logger.debug("Detected RFID: %s", format(data, "02x"))
            (error, uid) = self.rdr.anticoll()
            if error:
                Logger.error("Error reading RFID: %r <UID: %r>", error, uid)
            else:
                Logger.debug("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))
                self.card_detected(uid)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Grisebank")
    parser.add_argument('configfile', default='config.ini')
    parser.add_argument('cardsfile', default='cards.yaml')

    args = parser.parse_args()

    c = configparser.RawConfigParser() 
    c.optionxform = lambda option: option # make configparser case aware
    c.read(args.configfile)


    cards = yaml.safe_load(open(args.cardsfile))
    Logger.info('%i rfid card definitions loaded', len(cards))

    sbank = bank.GriseBank(c)

    from kivy.config import Config
    Config.set('graphics', 'fullscreen', 'auto')

    gapp = GriseBankApp()
    pitft = PiTFT_Screen()
    gapp.setScreen(pitft)
    gapp.setBank(sbank)
    gapp.setCards(cards)
    gapp.run()
