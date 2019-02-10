#!/usr/bin/env python
from libDiameter import *

# CER='0100008c8000010100000000000000010860000100000108400000167374612e737072696e742e636f6d00000000012840000012737072696e742e636f6d0000000001014000000e00010a1e60c800000000010a4000000c000028af0000010d000000154c616e64736c69646548534757000000000001024000000c01000022000001164000000c4f32a086'

# Diameter specific values for the base AVPs
ORIGIN_HOST = 'asn.client.test'
ORIGIN_REALM = 'asn.test'

# Connection parameters
HOST='127.0.0.1'
PORT=3868

def send_cer(connection):
    # Bulding the AVPs to be encapsulated 
    CER_avps=[ ]
    CER_avps.append(encodeAVP('Origin-Host', ORIGIN_HOST))
    CER_avps.append(encodeAVP('Origin-Realm', ORIGIN_REALM))
    CER_avps.append(encodeAVP('Vendor-Id', 11))
    CER_avps.append(encodeAVP('Origin-State-Id', 1094807040))
    CER_avps.append(encodeAVP('Supported-Vendor-Id', 11))
    CER_avps.append(encodeAVP('Acct-Application-Id', 16777265))
    # Creating message header
    CER_header = HDRItem()
    # Set Diameter message's command code
    CER_header.cmd = dictCOMMANDname2code('Capabilities-Exchange')
    # Set Hop-by-Hop and End-to-End
    initializeHops(CER_header)
    # Create the Diameter message by joining the header and the AVPs
    CER_message=createReq(CER_header, CER_avps)
    # send the CER message using the socket connection
    connection.send(CER_message.decode('hex'))
    # receiving the response for the request
    CEA_info = connection.recv(4096)
    # Creating a CEA header to be removed during message decapsulation
    CEA_header = HDRItem()
    stripHdr(CEA_header,CEA_info.encode("hex"))
    # Genereating the received AVPs from the CEA message
    received_avps = splitMsgAVPs(CEA_header.msg)
    # returning the AVPs
    return received_avps


if __name__ == '__main__':
    """
    The main method for the client,
    which simulates basic interaction with the server,
    for testing purposes
    """
    # Establishing the socket connection to the server
    socket_connection = Connect(HOST,PORT)
    # Loading the Diameter dictionary for messages, codes and AVPs
    LoadDictionary("dictDiameter.xml")
    # Sending the CER message
    received_avps = send_cer(socket_connection)
    # Retrieving Destination Host and Realm
    DEST_HOST = findAVP("Origin-Host", received_avps)
    DEST_REALM = findAVP("Origin-Realm", received_avps)
    print 'Destination Host:'
    print DEST_HOST
    print 'Destination Realm:'
    print DEST_REALM
    print 'Received AVPs:'
    for avp in received_avps:
        field, value = decodeAVP(avp)
        print field, value
    