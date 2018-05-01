
import configparser 
import logging

from SbankenClient import SbankenClient, SbankenError, SbankenAccount, Account

class GriseError(SbankenError):
    pass

class GriseAccount:
    def __init__(self, title:str, account:Account, bank:'GriseBank'):
        self.title = title
        self.bank = bank
        self.account = account
        self.details = account.details
    
    def __str__(self) -> str:
        return '<GriseAccount: {}, account # {}, balance:{}>'.format(self.title, self.details.accountNumber, self.details.balance)

    def reward(self, amount:float, message:str=None) -> bool:
        '''Add amount to user's account. Returns boolean True if it succeeded.'''
        result = self.bank.reward(self, amount, message)
        if not result.get('isError'):
            self.account.update()
            self.details = self.account.details
            return True
        return False

class GriseBank:
    '''The main class, that binds users and accounts together.

    Pass the constructor an instance of configparser.ConfigParser that holds the setup. See `config.ini.example` 
    for the structure.

    After init, look at 
    `.users` -- a list of GriseAccounts
    `.baseAccount` -- the base account for all operations (the one with all the money that is rewarded)

    '''
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.client = SbankenClient(config)
        self.users = []
        # read through user=account combos from config file and populate user list
        for name in config.options('accounts'):
            if name == "BASE": continue
            userAccount = config.get('accounts', name) # get account number
            for acct in self.client.accounts(): # parse SbankenAccounts
                if acct.details.accountNumber == userAccount: #this is it
                    self.users.append(GriseAccount(name, acct, self))

        # TODO: fix this algo
        for acct in self.client.accounts(): # parse SbankenAccounts
            if acct.details.accountNumber == config.get('accounts', 'BASE') :
                self.baseAccount = GriseAccount('base', acct, self)

    def reward(self, receiver:GriseAccount, amount:float, message:str=None) -> dict:
        'Transfer amount to receiver from BASE account, with optional message'
        if receiver.details.accountNumber == self.baseAccount.details.accountNumber:
            # can't transfer to itself, the base account never receives money
            raise GriseError('''You can't reward the base account''')
        return self.client.transfer(self.baseAccount.details.accountNumber, 
                                    receiver.details.accountNumber, 
                                    amount, 
                                    message or 'Rewarded by Grisebank')

if __name__ == '__main__':
    import argparse
    from pprint import pprint as pr

    parser = argparse.ArgumentParser(description="Grisebank")
    parser.add_argument('--configfile', default='config.ini')

    args = parser.parse_args()

    c = configparser.RawConfigParser()
    c.optionxform = lambda option: option # make configparser case aware
    c.read(args.configfile)

    Gris = GriseBank(c)

