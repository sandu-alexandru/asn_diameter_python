#!/usr/bin/env python
from libDiameter import *

# Diameter specific values for the base AVPs
ORIGIN_HOST = 'asn.client.test'
ORIGIN_REALM = 'asn.test'

# Connection parameters
HOST = '127.0.0.1'
PORT = 3868


def send_cer(connection):
    """
    Method used to send the Capability Exchange Request message
    Encodes in Hex each AVP, appends them to the Diameter header,
    build a Diameter message based on those values,
    and sends them to the already established socket connection.

    :param connection: socket connection
    :return: list of received AVPs
    """

    # Creating message header
    cer_header = HDRItem()
    # Set Diameter message's command code
    cer_header.cmd = dictCOMMANDname2code('Capabilities-Exchange')
    # Set Hop-by-Hop and End-to-End
    initializeHops(cer_header)

    # Building the AVPs to be encapsulated
    cer_avps = list()
    cer_avps.append(encodeAVP('Origin-Host', ORIGIN_HOST))
    cer_avps.append(encodeAVP('Origin-Realm', ORIGIN_REALM))
    cer_avps.append(encodeAVP('Vendor-Id', 11))
    cer_avps.append(encodeAVP('Origin-State-Id', 1094807040))
    cer_avps.append(encodeAVP('Supported-Vendor-Id', 11))
    cer_avps.append(encodeAVP('Acct-Application-Id', 16777265))

    # Create the Diameter message by joining the header and the AVPs
    cer_message = createReq(cer_header, cer_avps)

    # send the cer message using the socket connection
    connection.send(cer_message.decode('hex'))
    # receiving the response for the request
    cea_info = connection.recv(4096)

    # Creating a CEA header to be removed during message decapsulation
    cea_header = HDRItem()
    stripHdr(cea_header, cea_info.encode("hex"))
    # Generating the received AVPs from the CEA message
    cea_response_avps = splitMsgAVPs(cea_header.msg)
    # returning the decoded AVPs
    return decode_avp_list(cea_response_avps)


def send_invalid_message(connection):
    """
    Method used to send an invalid Diameter Request message
    Encodes in Hex each AVP, appends them to the Diameter header,
    build a Diameter message based on those values,
    and sends them to the already established socket connection.

    :param connection: socket connection
    :return: list of received AVPs
    """

    # Creating message header
    invalid_message_header = HDRItem()
    # Set Diameter message's command code -> 258
    invalid_message_header.cmd = dictCOMMANDname2code('Re-Auth')
    # Set Hop-by-Hop and End-to-End
    initializeHops(invalid_message_header)

    # Building the AVPs to be encapsulated
    invalid_message_avps = list()
    invalid_message_avps.append(encodeAVP('Origin-Host', ORIGIN_HOST))
    invalid_message_avps.append(encodeAVP('Origin-Realm', ORIGIN_REALM))
    invalid_message_avps.append(encodeAVP('Vendor-Id', 11))

    # Create the Diameter message by joining the header and the AVPs
    invalid_message = createReq(invalid_message_header, invalid_message_avps)

    # send the invalid message using the socket connection
    connection.send(invalid_message.decode('hex'))
    # receiving the response for the request
    response_info = connection.recv(4096)

    # Creating a CEA header to be removed during message decapsulation
    response_header = HDRItem()
    stripHdr(response_header, response_info.encode("hex"))

    # Generating the received AVPs from the CEA message
    response_avps_encoded = splitMsgAVPs(response_header.msg)

    # returning the decoded AVPs
    return decode_avp_list(response_avps_encoded)


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


if __name__ == '__main__':
    """
    The main method for the client,
    which simulates basic interaction with the server,
    for testing purposes.
    """
    # Establishing the socket connection to the server
    socket_connection = Connect(HOST, PORT)
    # Loading the Diameter dictionary for messages, codes and AVPs
    LoadDictionary("dictDiameter.xml")

    # Sending the cer message
    cea_avps = send_cer(socket_connection)
    print '\nCEA response:'
    print cea_avps

    # Sending the invalid message
    invalid_msg_avps = send_invalid_message(socket_connection)
    print '\nInvalid message response:'
    print invalid_msg_avps
