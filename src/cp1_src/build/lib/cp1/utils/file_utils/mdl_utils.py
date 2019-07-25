"""mdl_utils.py

Any helper functions related to parsing MDL files.
Author: Tameem Samawi (tsamawi@cra.com)
"""
from cp1.common.exception_class import MACAddressParseError
import re


def mac_to_id(mac_address):
    """
    Translates a RadioLink ID to TA and Ground ID strings.

    i.e. RadioLink_4097to61473
                   /        \
           Src Radio RF    Dst Group RF
           MAC Address     MAC Address

    If you convert these numbers into their hex representations, you would get the following:
    4097  : 0x1001  : Ground Radio 1
    61473 : 0xF021  : Uplink for TA 2
    4129  : 0x1021  : TA 2 Radio
    61472 : 0xF020  : Downlink from TA 2

    •	All Source RF MAC Addresses start with first hex digit as 0x1
    •	All Destination RF MAC Addresses start with first hex digit as 0xF
    •	Second hex digit is 0x0 for all RF MAC Addresses
    •	Third hex digit represents location or test mission association: (0 = ground radio, 1 = TA 1, 2 = TA 2, 3 = TA3, etc.)
    •	Fourth hex digit represents radio number

    o	On ground radios, they increment: 00, 01, 02, etc.
    o	On a TA, we assume there is only one radio, so this digit is a 1.
    o	For RF Group MAC Addresses, ‘0’ is the downlink (transmitted by the TA, received by the ground) and ‘1’ is the uplink (transmitted by the ground, received by the TA).


    :param str mac_address: The ID field of a RadioLink element, i.e. RadioLink_4097to61473
    :returns (str, str) ids: The source TA id and Destination id. (source, destination)
    """
    ids = [int(s) for s in mac_address[10:].split('to') if s.isdigit()]
    source_mac = ids[0]
    destination_mac = ids[1]

    source_hex = hex(source_mac)
    destination_hex = hex(destination_mac)

    source_type = _determine_type(source_hex)
    destination_type = _determine_type(destination_hex)

    source_id = str((int(source_hex[4:6])))
    destination_id = str((int(destination_hex[4:6])))

    source = source_type + source_id
    destination = destination_type + destination_id

    return (source, destination)


def id_to_mac(ta_id, direction):
    """
    Takes in a TA ID and direction and translates it to a MAC Address according
    to the SwRI naming convention.
    i.e. TA100, up ---> RadioLink_4196to61540
         TA100, down ---> RadioLink_8292to61796

    :param str ta_id: The id to translate into a MAC Address
    :param str direction: The direction the transmission is going. i.e. TA to Ground (down) or Ground to TA (up).
    """
    ground_mac = 0x1000
    ta_mac = 0x2000
    uplink_mac = 0xF000
    downlink_mac = 0xF100

    id_number = int(re.sub("[^0-9]", "", ta_id))

    if direction == 'up':
        mac = str(ground_mac + id_number) + 'to' + str(uplink_mac + id_number)
    else:
        mac = str(ta_mac + id_number) + 'to' + str(downlink_mac + id_number)

    return 'RadioLink_' + mac

def _determine_type(x):
    y = x[0:4]

    if y == '0xf0':
        type = 'Uplink '
    elif y == '0xf1':
        type = 'Downlink '
    elif y == '0x10':
        type = 'Ground '
    elif y == '0x20':
        type = 'TA '
    else:
        raise MACAddressParseError('{0} does not match any of the known abbreviations'.format(y), 'MDLUtils._determine_type')

    return type
