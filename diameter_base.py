"""
Base/Common information for the Diameter implementation used.

Contains:
- command codes mapping
- result codes mapping
- Diameter message object
- method used to decode hex AVPs into a dictionary
"""

from libDiameter import *

cmd_codes = {
    'Capability-Exchange': 257,
    'Re-Auth': 258,
    'Device-Watchdog': 280,
}

result_codes = {
    'DIAMETER_SUCCESS': 2001,
    'DIAMETER_UNABLE_TO_COMPLY': 5012,
}

standard_avp_values = {
    'Product-Name': 'asn.python.diameter',
    'Vendor-Id': 10415,
    'Supported-Vendor-Id': 10415,
    'Acct-Application-Id': 3,
}


class DiameterMessage:
    """
    Diameter Message object, containing header info and AVPs
    """
    def __init__(self, request_data=None):
        """
        Object encompassing a Diameter Protocol message.

        Contains information available in the Diameter message header, like:

        - version
        - flags
        - length
        - command code
        - application Id
        - Hop by Hop ID and End to End info

        The object also contains in a dictionary structure the AVP values,
        using key:value pairs between the attribute-value pairs.
        """

        self.avps = {}
        if request_data:
            self.version = request_data.ver
            self.flags = request_data.flags
            self.length = request_data.len
            self.command_code = request_data.cmd
            self.application_Id = request_data.appId
            self.HopByHop = request_data.HopByHop
            self.EndToEnd = request_data.EndToEnd
            self.hex_msg = request_data.msg
            self.hex_avps = splitMsgAVPs(self.hex_msg)
            # decoding AVP info and setting them up into a dictionary
            for hex_avp in self.hex_avps:
                field, value = decodeAVP(hex_avp)
                self.avps[field] = value


def decode_avp_list(avp_list):
    """
    Decodes a list of AVPs and returns a dictionary having
    AVP names as key with the actual value for dictionary values.

    :param avp_list: list of encoded AVPs
    :return: dictionary of decoded AVPs
    """
    decoded_avps = dict()
    for avp in avp_list:
        field, value = decodeAVP(avp)
        decoded_avps[field] = value
    return decoded_avps
