#!/usr/bin/env python
# -*- coding: utf-8 -*-

# original source: http://www.ohjelmointiputka.net/koodivinkit/24548-python-tilinumeron-tarkistus
# license: Saako tätä käyttää sellaisenaan jollakin lisenssillä? Koodia saa minun puolestani käyttää vapaasti omalla vastuullaan. Koodasin sen koodausajankohtana saatavilla olevien dokumenttien perusteella, mutten voi taata täyttä virheettömyyttä.

# Validate and convert Finnish bank account number

# More info:
# http://www.fkl.fi/teemasivut/sepa/tekninen_dokumentaatio/


import re

class AccountNumberException(Exception):
    pass

# create compiled validation regular expressions for efficiency
old_re = re.compile(r'([0-9]{6})-([0-9]{2,8})')
mlf_re = re.compile(r'[0-9]{14}')
fi_iban_re = re.compile(r'FI[0-9]{16}')

# account number prefix: (bank name, BIC code, position to add zeros)
bank_data = {'1': ('Nordea Pankki (Nordea)', 'NDEAFIHH', 6),
             '2': ('Nordea Pankki (Nordea)', 'NDEAFIHH', 6),
             '31': ('Handelsbanken', 'HANDFIHH', 6),
             '33': ('Skandinaviska Enskilda Banken (SEB)', 'ESSEFIHX', 6),
             '34': ('Danske Bank', 'DABAFIHX', 6),
             '36': ('Tapiola Pankki', 'TAPIFI22', 6),
             '37': ('DNB Bank ASA, Finland Branch', 'DNBAFIHX', 6),
             '38': ('Swedbank', 'SWEDFIHH', 6),
             '39': ('S-Pankki', 'SBANFIHH', 6),
             '4': ('Aktia Pankki, Säästöpankit (Sp) ja Paikallisosuuspankit (POP)', 'HELSFIHH', 7),
             '5': ('Pohjola Pankki (OP-Pohjola-ryhmän pankkien keskusrahalaitos)', 'OKOYFIHH', 7),
             '6': ('Ålandsbanken (ÅAB)', 'AABAFI22', 6),
             '8': ('Sampo Pankki', 'DABAFIHH', 6),
             '711': ('Calyon', 'BSUIFIHH', 6),  # IBAN only
             '713': ('Citibank', 'CITIFIHX', 6),  # IBAN only
             '715': ('Itella Pankki', 'ITELFIHH', 6)  # IBAN only
            }

def old_to_mlf(old_s):
    """Return old Finnish account number in machine format language.

    Raise exception if account number is invalid.

    """

    # Check if number format is correct
    m = old_re.match(old_s)
    if m is None:
        raise AccountNumberException('Number format incorrect:')

    number = ''.join(m.groups())
    for k, v in bank_data.items():
        if k.startswith('7'):
            continue  # only used in IBAN, ignore

        if number.startswith(k):
            br_point = v[2] # the position of zeroes depends on bank prefix
            zeroes = '0' * (14 - len(number))
            mlf_s = number[:br_point] + zeroes + number[br_point:]
            if not validate_mlf(mlf_s):
                raise AccountNumberException('Invalid account number')
            return mlf_s

    raise AccountNumberException('Prefix not in use')

def mlf_to_iban(mlf_s):
    """return IBAN for given Finnish account number machine language format"""
    raw_iban = mlf_s + '151800'  # '15' = 'F', '18' = 'I'
    check_digits = '{0:02d}'.format(98 - int(raw_iban) % 97)
    return 'FI' + check_digits + mlf_s

def old_to_iban(old_s, spaced=False):
    """return IBAN version of given old account number"""
    iban_s = mlf_to_iban(old_to_mlf(old_s))
    return iban_s if not spaced else spaced_iban(iban_s)

def spaced_iban(iban_s):
    """return IBAN in four character groups, separated by spaces"""
    iban_s = iban_s.replace(' ', '')
    iban_spaced = [(' ' if i and i % 4 == 0 else '') + c for i, c in enumerate(iban_s)]
    return ''.join(iban_spaced)

def validate_old(old_s):
    """return True for valid old format account number, False otherwise"""
    try:
        return validate_mlf(old_to_mlf(old_s))
    except AccountNumberException:
        return False

def validate_mlf(mlf_s):
    """return True for valid machine language format, False otherwise"""

    if mlf_re.match(mlf_s) is None:
        return False

    weights = (2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2)  # weights for 13 first digits
    mlf_numbers = map(int, mlf_s)

    # 13 first account number digits are multiplied by weights
    products = map(lambda (a, b): str(a * b), zip(weights, mlf_numbers))

    # products are put together in a single string and the sum of digits is calculated
    total = sum(int(x) for x in ''.join(products))

    # modulo check for 13 first digits must match the last (14th) digit
    return (10 - total) % 10 == mlf_numbers[-1]

def validate_fi_iban(iban_s):
    """return True for valid Finnish IBAN, False otherwise"""
    iban_s = iban_s.replace(' ', '')

    if fi_iban_re.match(iban_s) is None:
        return False

    # number format = machine language format + 'FI' as digits + check digits
    # 'A' = '10', ..., 'Z' = '35', 'FI' = '1518'
    number_format = iban_s[4:] + '1518' + iban_s[2:4]
    return int(number_format) % 97 == 1

def _get_bank_data_by_iban(iban_s, data_i):
    if not validate_fi_iban(iban_s):
        raise AccountNumberException('Invalid IBAN')

    iban_s = iban_s.replace(' ', '')
    acc_number_part = iban_s[4:]
    for k, v in bank_data.items():
        if acc_number_part.startswith(k):
            return v[data_i]

    raise AccountNumberException('Unknown bank')

def bic_of_iban(iban_s):
    """return bank identification code (BIC) of given IBAN"""
    return _get_bank_data_by_iban(iban_s, 1)

def bank_name_of_iban(iban_s):
    """return name of the bank of given IBAN"""
    return _get_bank_data_by_iban(iban_s, 0)

def main():
    # examples

    old = '123456-785'
    print 'Account number in old format: {0:s}'.format(old)
    print 'Machine language format: {0:s}'.format(old_to_mlf(old))
    iban = old_to_iban(old)
    print 'IBAN: {0:s}'.format(iban)
    print 'BIC: {0:s}'.format(bic_of_iban(iban))
    print 'Bank name: {0:s}'.format(bank_name_of_iban(iban))

    real_iban = 'FI3715903000000776'
    result = validate_fi_iban(real_iban)
    print '{0:s} is {1:s} IBAN'.format(real_iban, 'valid' if result else 'invalid')

    fake_iban = 'FI3715903000000777'
    result = validate_fi_iban(fake_iban)
    print '{0:s} is {1:s} IBAN'.format(fake_iban, 'valid' if result else 'invalid')

    fake_old = '123457-785'
    result = validate_old(fake_old)
    print '{0:s} is {1:s}'.format(fake_old, 'valid' if result else 'invalid')

    # error handling example:
    try:
        print '{0:s} to IBAN: {1:s}'.format(fake_old, old_to_iban(fake_old))
    except AccountNumberException as e:
        print 'Unable to convert: {0:s}'.format(e)

if __name__ == '__main__':
    main()