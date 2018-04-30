from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock

from pitftscreen import PiTFT_Screen 

import configparser

import bank

class GriseBank(Widget):
    accountName = StringProperty("Ingen")
    accountValue = NumericProperty(0.0)
    status = StringProperty("Velg konto...")

    def update(self, dt):
        'update stuff'

    def setScreen(self, screen):
        #screen.Button1Interrupt(lambda x: self.button(1, x))
        screen.Button2Interrupt(lambda x: self.button(2, x))
        screen.Button3Interrupt(lambda x: self.button(3, x))
        screen.Button4Interrupt(lambda x: self.button(4, x))
        self.screen = screen

    def button(self, btnNumber, channel):
        print('pressed button {}, channel {}'.format(btnNumber, channel))
        if btnNumber == 2:
            self.accountName = "Bjarne"
            self.accountValue = 20 
        elif btnNumber == 3:
            self.accountName = "Anna"
            self.accountValue = 50 
        self.status = "Skann kortet..."

class GriseBankApp(App):
    def setScreen(self, screen):
        self.screen = screen

    def setBank(self, bank):
        self.bank = bank

    def build(self):
        self.gris = GriseBank()
        self.gris.setScreen(self.screen)
        self.gris.setBank(self.bank)
        Clock.schedule_interval(self.gris.update, 1.0/60.0)
        return self.gris

if __name__ == '__main__':
    import argparse
    from pprint import pprint as pr

    parser = argparse.ArgumentParser(description="Grisebank")
    parser.add_argument('configfile', default='config.ini')

    args = parser.parse_args()

    c = configparser.RawConfigParser()
    c.optionxform = lambda option: option # make configparser case aware
    c.read(args.configfile)

    sbank = bank.GriseBank(c)

    gapp = GriseBankApp()
    pitft = PiTFT_Screen()
    gapp.setScreen(pitft)
    gapp.setBank(sbank)
    gapp.run()
