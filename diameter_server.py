import sys
import socket
import thread
import time
import string
import struct
import logging
from libDiameter import *

import signal
def signal_handler(signal, frame):
    print("Closing server...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Readable time format
def now():
    return str(time.ctime(time.time( )))

HOST = "127.0.0.1"
PORT = 3868

BUFFER_SIZE = 4096 # Limit buffer size to detect complete message
MAX_CLIENTS = 5

class Diameter_Message:
    def __init__(self, request_data):
        self.version = request_data.ver
        self.flags = request_data.flags
        self.length = request_data.len
        self.command_code = request_data.cmd
        self.application_Id = request_data.appId
        self.HobByHop = request_data.HobByHop
        self.EndToEnd = request_data.EndToEnd
        self.hex_msg = request_data.msg
        self.hex_avps = splitMsgAVPs(self.hex_msg)
        self.avps = {}
        for hex_avp in self.hex_avps:
            field, value = decodeAVP(hex_avp)
            self.avps[field] = value


def generate_CEA(diameter_request):
    """
    Handling CER requests and sending CEA responses.

    Build CEA message, the header and AVPs list separately,
    then create a diameter response based on them.
    """
    
    # Creating message header
    CEA_header = HDRItem()
    # Set Diameter message's command code
    CEA_header.cmd = dictCOMMANDname2code('Capabilities-Exchange')
    # Set Hop-by-Hop and End-to-End
    initializeHops(CEA_header)

    # Generating the CEA message's AVPs
    CEA_avps = []
    CEA_avps.append(encodeAVP('Origin-Host', diameter_request.avps['Origin-Host']))
    CEA_avps.append(encodeAVP('Origin-Realm', diameter_request.avps['Origin-Realm']))
    CEA_avps.append(encodeAVP('Vendor-Id', diameter_request.avps['Vendor-Id']))
    CEA_avps.append(encodeAVP('Origin-State-Id', diameter_request.avps['Origin-State-Id']))
    CEA_avps.append(encodeAVP('Supported-Vendor-Id', diameter_request.avps['Supported-Vendor-Id']))
    CEA_avps.append(encodeAVP('Acct-Application-Id', diameter_request.avps['Acct-Application-Id']))
    
    # Create the Diameter message by joining the header and the AVPs
    CEA_message = createRes(CEA_header, CEA_avps)
    return CEA_message


def handle_request(connection, address):
    while True:                    
        #get input ,wait if no data
        #connection.setblocking(True)
        try:
            data = connection.recv(BUFFER_SIZE)
        except:
            break
        #suspect more data (try to get it all without stopping if no data)
        if len(data)==BUFFER_SIZE:
            while 1:
                #connection.setblocking(False)
                try:
                    data += connection.recv(BUFFER_SIZE)
                except:
                    #error means no more data
                    break
        #no data found exit loop (posible closed socket)
        if len(data)==0:
            break
        else:
            # actual handling of the Diameter message
            logging.warning("Handling request for address " + str(address))
            message_sent = send_response(connection, data)
            logging.warning(
                "\n\nSent " + str(dictCOMMANDcode2name(message_sent.flags, message_sent.command_code))
                + "\nAVPs:\n" + str(message_sent.avps) + "\n\n")
    connection.close()


def send_response(connection, request_info):
    # Creating a diameter request message based on the data received
    request = HDRItem()
    stripHdr(request,request_info.encode("hex"))
    diameter_request = Diameter_Message(request)
    # Creating a response based on the request info and command code
    if str(diameter_request.command_code) == '257':
        # Capabilities Exchange Request, generating and sending an answer
        response = generate_CEA(diameter_request)

    # Sending the message and returning a Diameter Message object
    connection.send(response.decode('hex'))
    response_data = HDRItem()
    stripHdr(response_data,response)
    diameter_sent_message = Diameter_Message(response_data)
    return diameter_sent_message



if __name__ == "__main__":
    """
    Main function containing the Diameter Server
    """

    # Loading the Diameter dictionary for messages, codes and AVPs
    LoadDictionary("dictDiameter.xml")

    # Create the server, binding to HOST:PORT and set max peers
    diameter_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    diameter_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    diameter_server.bind((HOST, PORT))  
    diameter_server.listen(MAX_CLIENTS)

    while True:
        connection, address = diameter_server.accept()
        logging.warning('Connected at ' + str(address) + 'at' + now())
        thread.start_new(handle_request, (connection, address))
    
    # Closing the socket connection
    diameter_server._sock.close()
    diameter_server.close()
