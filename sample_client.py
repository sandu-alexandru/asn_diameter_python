#!/usr/bin/env python

"""
Sample Diameter Client, which can be used for testing purposes.
Generates a client instance, starts it, establishing the server connection
and then sends the specified Diameter Requests and interprets the response.
"""

from diameter_client import *

if __name__ == '__main__':
    """
    The main method for the client,
    which simulates basic interaction with the server.
    """

    # Starting the client
    client = DiameterClient()
    client.start()

    # Sending the CER message
    cea_avps = client.send_cer()
    print '\nCEA response:'
    print cea_avps

    # Sending the DWR message
    dwa_avps = client.send_dwr()
    print '\nCEA response:'
    print dwa_avps

    # Sending the invalid message
    invalid_msg_avps = client.send_invalid_message()
    print '\nInvalid message response:'
    print invalid_msg_avps
