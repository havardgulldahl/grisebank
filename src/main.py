
import configparser 
import logging

from SbankenClient import SbankenClient, SbankenError, SbankenAccount'

class GriseAccount(SbankenAccount):
    def __init__(self, name:str, account:str, bank:'GriseBank'):
        super(GriseAccount, self).__init__(name, account, bank.client)
        self.bank = bank

    def reward(self, amount:float, message:str=None) -> bool:
        '''Add amount to user's account. Returns boolean True if it succeeded.'''
        result = self.bank.reward(self, amount, message)
        return not result.get('isError')

class GriseBank:
    '''The main class, that binds users and accounts together.

    Pass the constructor an instance of configparser.ConfigParser that holds the setup. See `config.ini.example` 
    for the structure.

    After init, look at 
    `.users` -- a list of GriseAccounts
    `.baseAccount` -- the base account for all operations

    '''
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.client = SbankenClient(config)
        self.users = [GriseAccount(opt, config.get('accounts', opt), self) for opt in config.options('accounts') if opt != "BASE"]
        self.baseAccount = GriseAccount('base', config.get('accounts', 'BASE'), self)

    def reward(self, receiver:GriseAccount, amount:float, message:str=None) -> dict:
        'Transfer amount to receiver from BASE account, with optional message'
        return self.client.transfer(self.baseAccount.account, receiver.account, amount, message or 'Rewarded by Grisebank')

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Grisebank")
    parser.add_argument('--configfile', default='config.ini')

    args = parser.parse_args()

    c = configparser.RawConfigParser()
    c.optionxform = lambda option: option # make configparser case aware
    c.read(args.configfile)

    Gris = GriseBank(c)