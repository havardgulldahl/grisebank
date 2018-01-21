
import configparser 
import logging

from SbankenClient import SbankenClient, SbankenError

class GriseUser:
    def __init__(self, name:str, account:str, bank:'GriseBank'):
        self.name = name
        self.account = account
        self.bank = bank

    def __str__(self):
        return '<GriseUser: {}, account # {}>'.format(self.name, self.account)

    def info(self):
        'Return info on the account'
        return self.bank.client.account(self.account).get('item')

    def latest(self):
        'Return last transactions on the account'
        return self.bank.client.transactions(self.account).get('items')

class GriseBank:
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.client = SbankenClient(config)
        self.users = [GriseUser(opt, config.get('accounts', opt), self) for opt in config.options('accounts') if opt != "BASE"]
        self.baseAccount = config.get('accounts', 'BASE')

    def reward(self, receiver:GriseUser, amount:float, message:str=None):
        'Transfer amount to receiver from BASE account, with optional message'
        return self.client.transfer(self.baseAccount, receiver.account, amount, message or 'Revarded by Grisebank')

    def info(self, user:GriseUser):
        return user.info()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Grisebank")
    parser.add_argument('--clientId')
    parser.add_argument('--secret')
    parser.add_argument('--userId')
    parser.add_argument('--configfile', default='config.ini')

    args = parser.parse_args()

    c = configparser.RawConfigParser()
    c.optionxform = lambda option: option # make configparser case aware
    c.read(args.configfile)

    Gris = GriseBank(c)