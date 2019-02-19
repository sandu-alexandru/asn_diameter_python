#!/usr/bin/env python
from diameter_responses import *

# Diameter specific values for the base AVPs
ORIGIN_HOST = 'asn.client.test'
ORIGIN_REALM = 'asn.test'

# Connection parameters
HOST = '127.0.0.1'
PORT = 3868


def generate_generic_request(command_code):
    """
    Builds a generic Diameter request, with a Diameter header
    and the standard AVPs.

    :return: dictionary containing header and AVPs
    for a generic request on a given command code
    """

    # Creating the Diameter Message object to base the request on
    diameter_request = diameter_base.DiameterMessage()
    diameter_request.command_code = command_code
    diameter_request.avps['Origin-Host'] = ORIGIN_HOST
    diameter_request.avps['Origin-Realm'] = ORIGIN_REALM

    # Generating a standard Diameter request
    generic_request = generate_generic_diameter_message(diameter_request)
    return generic_request


def send_diameter_request(header, avps, connection):
    """

    :param header: Diameter message header
    :param avps: Diameter message's AVPs
    :param connection: socket connection used to send the message
    :return:
    """

    # Create the Diameter message by joining the header and the AVPs
    request_message = createReq(header, avps)

    # send the cer message using the socket connection
    connection.send(request_message.decode('hex'))
    # receiving the response for the request
    response_data = connection.recv(4096)

    # Creating a CEA header to be removed during message decapsulation
    response = HDRItem()
    stripHdr(response, response_data.encode("hex"))
    # Generating the received AVPs from the CEA message
    response_avps = splitMsgAVPs(response.msg)
    # returning the decoded AVPs
    return diameter_base.decode_avp_list(response_avps)


def send_cer(connection):
    """
    Method used to send the Capability Exchange Request message
    Encodes in Hex each AVP, appends them to the Diameter header,
    build a Diameter message based on those values,
    and sends them to the already established socket connection.

    :param connection: socket connection
    :return: dictionary of received AVPs
    """

    # Generating a standard Diameter request
    generic_request = generate_generic_request(
        diameter_base.cmd_codes['Capability-Exchange'])

    cer_header = generic_request['header']
    cer_avps = generic_request['avps']

    # Appending the CER specific AVPs
    cer_avps.append(encodeAVP('Vendor-Id', 11))
    cer_avps.append(encodeAVP('Origin-State-Id', 1094807040))
    cer_avps.append(encodeAVP('Supported-Vendor-Id', 11))
    cer_avps.append(encodeAVP('Acct-Application-Id', 16777265))

    # returning a dictionary of the received AVPs
    avps_dict = send_diameter_request(cer_header, cer_avps, connection)
    return avps_dict


def send_invalid_message(connection):
    """
    Method used to send an invalid Diameter Request message
    Encodes in Hex each AVP, appends them to the Diameter header,
    build a Diameter message based on those values,
    and sends them to the already established socket connection.

    :param connection: socket connection
    :return: dictionary of received AVPs
    """

    # Generating a standard Diameter request
    generic_request = generate_generic_request(
        diameter_base.cmd_codes['Re-Auth'])

    invalid_message_header = generic_request['header']
    invalid_message_avps = generic_request['avps']

    # Appending to the generic request an additional AVP
    invalid_message_avps.append(encodeAVP('Vendor-Id', 11))

    # returning a dictionary of the received AVPs
    avps_dict = send_diameter_request(
        invalid_message_header, invalid_message_avps, connection)
    return avps_dict


def send_dwr(connection):
    """
    Method used to send an invalid Diameter Request message
    Encodes in Hex each AVP, appends them to the Diameter header,
    build a Diameter message based on those values,
    and sends them to the already established socket connection.

    :param connection: socket connection
    :return: list of received AVPs
    """

    # Generating a standard Diameter request
    generic_request = generate_generic_request(
        diameter_base.cmd_codes['Device-Watchdog'])

    dwr_header = generic_request['header']
    dwr_avps = generic_request['avps']

    # Appending to the generic message the DWR specific AVPs
    dwr_avps.append(encodeAVP('Vendor-Id', 11))

    # returning a dictionary of the received AVPs
    avps_dict = send_diameter_request(dwr_header, dwr_avps, connection)
    return avps_dict


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

    # Sending the CER message
    cea_avps = send_cer(socket_connection)
    print '\nCEA response:'
    print cea_avps

    # Sending the DWR message
    dwa_avps = send_dwr(socket_connection)
    print '\nCEA response:'
    print dwa_avps

    # Sending the invalid message
    invalid_msg_avps = send_invalid_message(socket_connection)
    print '\nInvalid message response:'
    print invalid_msg_avps
