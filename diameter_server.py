"""
Module implementing a Diameter server able to handle requests
and build up a response based on the messages from the requests.

Using the libDiameter library, as well as the dictDiameter .xml dictionary
"""

import thread
from diameter_base import *
from diameter_responses import *
import logging

logging.getLogger().setLevel(logging.INFO)


class DiameterServer:
    """
    Object used to generate a Diameter Server.

    The Diameter Server is responsible for being able to
    receive requests and handle them, in order to generate proper
    Diameter responses based on the information received in the requests.
    """

    def __init__(self,
                 host="127.0.0.1",
                 port=3868,
                 buffer_size=4096,  # Limit buffer size to collect data
                 max_clients=5,     # Maximum number of clients accepted
                 origin_host='server.asn.test',
                 origin_realm='asn.test'):
        """
        The server accepts data over an open socket, decodes it into
        Diameter Request messages, interprets the data and builds up
        Diameter Response message based on the received information.

        :param host: host of the server
        :param port: port used for connection
        :param buffer_size: size of the buffer for receiving data
        :param max_clients: maximum number of clients at a given time
        """

        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.max_clients = max_clients
        self.origin_host = origin_host
        self.origin_realm = origin_realm

    def send_response(self, socket_connection, request_info):
        """
        Method used to send a Diameter response to a request for the server.

        Creates a DiameterMessage object based on the encoded data
        received from the peer, prepares a specific response
        based on the request's Diameter command code, which is then
        being sent over the same socket connection back to the peer
        that performed the request.

        :param socket_connection: peer connection to the server
        :param request_info: data received from the socket connection
        :return: a DiameterMessage object containing the response sent
        """

        # Creating a diameter request message based on the data received
        request = HDRItem()
        stripHdr(request, request_info.encode("hex"))
        diameter_request = DiameterMessage(request)

        # Generating a response based on the request info and command code
        response = cmd_code_responses.get(
            diameter_request.command_code,
            response_to_invalid_request
        )(diameter_request, self.origin_host, self.origin_realm)

        # Sending the message and returning a Diameter Message object
        socket_connection.send(response.decode('hex'))
        response_data = HDRItem()
        stripHdr(response_data, response)
        diameter_sent_message = DiameterMessage(response_data)
        return diameter_sent_message

    def handle_request(self, connection, address):
        """
        Method used to handle the incoming requests from the server.
        Represents one of the processing threads,
        for a specific request sent by a peer.

        Tries to receive data from the socket connection based on the buffer,
        and if the buffer is full, then re-tries to add data from the next
        buffered packet, since it may be related to the first one.

        Once the data receiving process is finished, the information is being
        sent for further analysis and building up a response for it.

        :param connection: socket connection on which we handle the request
        :param address: address of the peer requesting the connection
        """

        while True:
            # get input, wait if no data is being received
            try:
                data = connection.recv(self.buffer_size)
            except socket.error:
                break
            # suspect more data(try to get it all without stopping if no data)
            if len(data) == self.buffer_size:
                while 1:
                    try:
                        data += connection.recv(self.buffer_size)
                    except socket.error:
                        # error means no more data
                        break
            # no data found exit loop (possible closed socket)
            if len(data) == 0:
                break
            else:
                # actual handling of the Diameter message
                logging.info("Handling request for address " + str(address))
                message_sent = self.send_response(connection, data)
                logging.info(
                    "\n\nSent "
                    + str(dictCOMMANDcode2name(
                        message_sent.flags, message_sent.command_code))
                    + "\nAVPs:\n" + str(message_sent.avps) + "\n\n")
        connection.close()

    def start(self):
        """
        Main function containing the Diameter Server implementation.

        Loads the Diameter dictionary, enables a socket connection
        listening on the pre-defined port, and then starts a processing thread
        which handles possible requests for each of the incoming connections
        on said socket from any potential peers.
        """

        # Loading the Diameter dictionary for messages, codes and AVPs
        LoadDictionary("dictDiameter.xml")

        # Create the server, binding to HOST:PORT and set max peers
        socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_connection.bind((self.host, self.port))
        socket_connection.listen(self.max_clients)

        try:
            while True:
                incoming_connection, peer_address = socket_connection.accept()
                logging.info('Connected to ' + str(peer_address))
                thread.start_new(
                    self.handle_request, (incoming_connection, peer_address))
        except KeyboardInterrupt:
            print("\nClosing server...")

        # Closing the socket connection
        socket_connection.close()
