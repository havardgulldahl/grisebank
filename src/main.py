
import configparser 
import logging

from SbankenClient import SbankenClient, SbankenError

class GriseUser:
    def __init__(self, name:str, account:str, bank:'GriseBank'):
        self.name = name
        self.account = account
        self.bank = bank

    def __str__(self) -> str:
        return '<GriseUser: {}, account # {}>'.format(self.name, self.account)

    def info(self) -> dict:
        'Return info on the account'
        return self.bank.client.account(self.account).get('item')

    def latest(self) -> dict:
        'Return last transactions on the account'
        return self.bank.client.transactions(self.account).get('items')

    def reward(self, amount:float) -> bool:
        'Add amount to user's account. Returns boolean True if it succeeded.'
        result = self.bank.reward(self, amount)
        return not result.get('isError')

class GriseBank:
    '''The main class, that binds users and accounts together.

    Pass the constructor an instance of configparser.ConfigParser that holds the setup. See `config.ini.example` 
    for the structure.

    After init, look at 
    `.users` -- a list of GriseUsers
    `.baseAccount` -- the base account for all operations

    '''
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.client = SbankenClient(config)
        self.users = [GriseUser(opt, config.get('accounts', opt), self) for opt in config.options('accounts') if opt != "BASE"]
        self.baseAccount = config.get('accounts', 'BASE')

    def reward(self, receiver:GriseUser, amount:float, message:str=None) -> dict:
        'Transfer amount to receiver from BASE account, with optional message'
        return self.client.transfer(self.baseAccount, receiver.account, amount, message or 'Rewarded by Grisebank')

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Grisebank")
    parser.add_argument('--configfile', default='config.ini')

    args = parser.parse_args()

    c = configparser.RawConfigParser()
    c.optionxform = lambda option: option # make configparser case aware
    c.read(args.configfile)

    Gris = GriseBank(c)