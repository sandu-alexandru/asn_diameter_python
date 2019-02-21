"""
Module implementing a Diameter client able to send requests
and decode and interpret the response based on the received information.

Using the libDiameter library, as well as the dictDiameter .xml dictionary
"""

from diameter_responses import *


class DiameterClient:
    """
    Object used to generate the Diameter Client.
    """

    def __init__(self,
                 host='127.0.0.1',
                 port=3868,
                 origin_host='client.asn.test',
                 origin_realm='asn.test',
                 destination_host='server.asn.test',
                 destination_realm='asn.test'):
        """
        The client establishes a socket connection to server's host address
        at the specified port, and sends the desired Diameter Requests
        based on the configured destination host and realm.

        :param host: server host address
        :param port: port for socket connection
        :param origin_host: Diameter Origin Host
        :param origin_realm: Diameter Origin Realm
        """

        self.host = host
        self.port = port
        self.origin_host = origin_host
        self.origin_realm = origin_realm
        self.destination_host = destination_host
        self.destination_realm = destination_realm
        self.connection = None

    def generate_generic_request(self, command_code):
        """
        Builds a generic Diameter request, with a Diameter header
        and the standard AVPs.

        :return: dictionary containing header and AVPs
        for a generic request on a given command code
        """

        # Creating the Diameter Message object to base the request on
        diameter_request = diameter_base.DiameterMessage()
        diameter_request.command_code = command_code
        diameter_request.avps['Origin-Host'] = self.origin_host
        diameter_request.avps['Origin-Realm'] = self.origin_realm
        diameter_request.avps['Destination-Host'] = self.destination_host
        diameter_request.avps['Destination-Realm'] = self.destination_realm

        # Generating a standard Diameter request
        generic_request = generate_generic_diameter_message(
            diameter_request, self.origin_host, self.origin_realm)
        return generic_request

    @staticmethod
    def send_diameter_request(header, avps, connection):
        """
        Sends a Diameter Request message and returns response's AVPs info.

        Creates a request based on the received header and AVPs,
        sends them over the socket connection, receives the response for it,
        which is later decapsulated in order to retrieve the AVPs information.

        :param header: Diameter message header
        :param avps: Diameter message's AVPs
        :param connection: socket connection used to send the message
        :return: dictionary containing the response AVPs
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

    def send_cer(self, connection=None):
        """
        Method used to send the Capability Exchange Request message
        Encodes in Hex each AVP, appends them to the Diameter header,
        build a Diameter message based on those values,
        and sends them to the already established socket connection.

        :param connection: socket connection
        :return: dictionary of received AVPs
        """

        if not connection:
            connection = self.connection

        # Generating a standard Diameter request
        generic_request = self.generate_generic_request(
            diameter_base.cmd_codes['Capability-Exchange'])

        cer_header = generic_request['header']
        cer_avps = generic_request['avps']

        # Appending the CER specific AVPs
        cer_avps.append(encodeAVP(
            'Vendor-Id',
            diameter_base.standard_avp_values['Vendor-Id']))
        cer_avps.append(encodeAVP(
            'Product-Name', diameter_base.standard_avp_values['Product-Name']))
        cer_avps.append(encodeAVP('Origin-State-Id', 1))
        cer_avps.append(encodeAVP(
            'Supported-Vendor-Id',
            diameter_base.standard_avp_values['Supported-Vendor-Id']))
        cer_avps.append(encodeAVP(
            'Acct-Application-Id',
            diameter_base.standard_avp_values['Acct-Application-Id']))

        # returning a dictionary of the received AVPs
        avps_dict = self.send_diameter_request(cer_header, cer_avps, connection)
        return avps_dict

    def send_invalid_message(self, connection=None):
        """
        Method used to send an invalid Diameter Request message
        Encodes in Hex each AVP, appends them to the Diameter header,
        build a Diameter message based on those values,
        and sends them to the already established socket connection.

        :param connection: socket connection
        :return: dictionary of received AVPs
        """

        if not connection:
            connection = self.connection

        # Generating a standard Diameter request
        generic_request = self.generate_generic_request(
            diameter_base.cmd_codes['Re-Auth'])

        invalid_message_header = generic_request['header']
        invalid_message_avps = generic_request['avps']

        # Appending to the generic request an additional AVP
        invalid_message_avps.append(encodeAVP('Vendor-Id', 11))

        # returning a dictionary of the received AVPs
        avps_dict = self.send_diameter_request(
            invalid_message_header, invalid_message_avps, connection)
        return avps_dict

    def send_dwr(self, connection=None):
        """
        Method used to send an invalid Diameter Request message
        Encodes in Hex each AVP, appends them to the Diameter header,
        build a Diameter message based on those values,
        and sends them to the already established socket connection.

        :param connection: socket connection
        :return: list of received AVPs
        """

        if not connection:
            connection = self.connection

        # Generating a standard Diameter request
        generic_request = self.generate_generic_request(
            diameter_base.cmd_codes['Device-Watchdog'])

        dwr_header = generic_request['header']
        dwr_avps = generic_request['avps']

        # Appending to the generic message the DWR specific AVPs
        dwr_avps.append(encodeAVP('Origin-State-Id', 1))

        # returning a dictionary of the received AVPs
        avps_dict = self.send_diameter_request(dwr_header, dwr_avps, connection)
        return avps_dict

    def start(self):
        """
        Start the Diameter Client.

        Establishes a socket connection to the server,
        to be used by the client in order to able to send Diameter Requests,
        and loads the standard Diameter Dictionary.
        """

        # Establishing the socket connection to the server
        self.connection = Connect(self.host, self.port)
        # Loading the Diameter dictionary for messages, codes and AVPs
        LoadDictionary("dictDiameter.xml")
