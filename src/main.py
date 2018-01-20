


from SbankenClient import SbankenClient


if __name__ == '__main__':
    import argparse
    import configparser 

    parser = argparse.ArgumentParser(description="Grisebank")
    parser.add_argument('--clientId')
    parser.add_argument('--secret')
    parser.add_argument('--userId')
    parser.add_argument('--configfile', default='config.ini')

    args = parser.parse_args()

    c = configparser.RawConfigParser()
    c.optionxform = lambda option: option # make configparser case aware
    c.read(args.configfile)

    Sbanken = SbankenClient(c)