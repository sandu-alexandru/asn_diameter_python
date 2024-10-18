"""
Diameter server's responses.

The response logic is based on the request's command code,
generating first a generic Diameter message as a response,
which is later customized for the specific command code.
"""

import diameter_base
from libDiameter import *

logging.getLogger().setLevel(logging.INFO)


def generate_generic_diameter_message(diameter_request,
                                      origin_host,
                                      origin_realm):
    """
    Builds a generic Diameter message, with a Diameter header
    and the standard AVPs.

    :param origin_realm: Diameter Server's origin host
    :param origin_host: Diameter origin realm
    :param diameter_request: request for which we're building the response
    :return: generic Diameter response that can be used for further processing
    """
    # Creating message header
    response_header = HDRItem()
    # Set Diameter message's command code
    response_header.cmd = diameter_request.command_code
    # Set Hop-by-Hop and End-to-End
    # initializeHops(response_header)
    response_header.HopByHop = diameter_request.HopByHop
    response_header.EndToEnd = diameter_request.EndToEnd

    # Generating response's standard AVPs
    response_avps = list()

    # Adding server's origin host and realm
    response_avps.append(encodeAVP('Origin-Host', origin_host))
    response_avps.append(encodeAVP('Origin-Realm', origin_realm))

    # Setting as the destination host and realm request's origin
    response_avps.append(encodeAVP(
        'Destination-Host', diameter_request.avps['Origin-Host']))
    response_avps.append(encodeAVP(
        'Destination-Realm', diameter_request.avps['Origin-Realm']))

    # returning the generic Diameter response
    generic_response = {
        'header': response_header,
        'avps': response_avps,
    }
    return generic_response


def generate_capability_exchange_answer(diameter_request,
                                        origin_host,
                                        origin_realm):
    """
    Method used with the purpose of handling CER requests
    and sending CEA responses.(Capability Exchange)

    Build CEA message, the header and AVPs list separately,
    then create a Diameter response based on them.
    """

    logging.info("Responding to Capability Exchange Request ...")
    # Generating a standard Diameter response
    generic_response = generate_generic_diameter_message(diameter_request,
                                                         origin_host,
                                                         origin_realm)
    cea_header = generic_response['header']
    cea_avps = generic_response['avps']

    # Customizing it for Capability Exchange Answer
    cea_avps.append(encodeAVP(
        'Result-Code', diameter_base.result_codes['DIAMETER_SUCCESS']))

    # Iterating over the request's AVPs and adding them to the response
    for attribute, value in diameter_request.avps.items():
        # Grouped AVPs handling
        if isinstance(value, list):
            values = []
            # Handling each AVP from the group
            for group in value:
                values.append(encodeAVP(group[0], group[1]))
            # After creating the list of AVPs
            # add them as a grouped AVP under the response
            cea_avps.append((encodeAVP(attribute, values)))
        # Standard AVPs handling
        else:
            if attribute != 'Origin-Host' and attribute != 'Origin-Realm':
                cea_avps.append((encodeAVP(attribute, value)))

    # Create the Diameter response message by joining the header and the AVPs
    cea_message = createRes(cea_header, cea_avps)
    return cea_message


def generate_device_watchdog_answer(diameter_request,
                                    origin_host,
                                    origin_realm):
    """
    Method used with the purpose of handling DWR requests
    and sending DWA responses.(Device Watchdog)

    Builds the DWA message, the header and AVPs list separately,
    then create a Diameter response based on them.
    """

    logging.info("Responding to Device Watchdog Request ...")
    # Generating a standard Diameter response
    generic_response = generate_generic_diameter_message(diameter_request,
                                                         origin_host,
                                                         origin_realm)
    dwa_header = generic_response['header']
    dwa_avps = generic_response['avps']

    # Customizing it for Device Watchdog Answer
    dwa_avps.append(encodeAVP(
        'Result-Code', diameter_base. result_codes['DIAMETER_SUCCESS']))
    dwa_avps.append(encodeAVP(
        'Origin-State-Id', diameter_request.avps['Origin-State-Id']))

    # Create the Diameter response message by joining the header and the AVPs
    dwa_message = createRes(dwa_header, dwa_avps)
    return dwa_message


def response_to_invalid_request(diameter_request,
                                origin_host,
                                origin_realm):
    """
    Method used to respond to invalid Diameter request.

    We define an invalid Diameter request by comparing its command code
    with the ones that we have support for.
    """

    logging.info("Responding to invalid request...")
    # Generating a standard Diameter response
    generic_response = generate_generic_diameter_message(diameter_request,
                                                         origin_host,
                                                         origin_realm)
    response_header = generic_response['header']
    response_avps = generic_response['avps']

    # Customizing the standard response for invalid request answer
    response_avps.append(
        encodeAVP('Result-Code',
                  diameter_base.result_codes['DIAMETER_UNABLE_TO_COMPLY']))

    # Generating the actual Diameter response
    # by joining the header and the AVPs
    response_message = createRes(response_header, response_avps)
    return response_message


cmd_code_responses = {

    # Response for Capabilities Exchange Request
    diameter_base.cmd_codes['Capability-Exchange']:
        generate_capability_exchange_answer,

    # Response for Device Watchdog Request
    diameter_base.cmd_codes['Device-Watchdog']:
        generate_device_watchdog_answer,

}
