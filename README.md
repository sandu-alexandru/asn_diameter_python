Diameter Client-Server Architecture in Python
==========

This repository contains a sample server which can be used as an Diameter Terminator (sending Diameter responses to specific requests) for the purpose of testing, which I plan to develop further in the future, in order to simulate a CDF (Charging Data Function).


For additional information about the Diameter Protocol, please consult https://tools.ietf.org/html/rfc3588

Features
==========

Currently, the Diameter Server can only process requests with following command codes:
 - 257 (Capability Exchange), sending an answer containing information based on the data present in the AVPs of the request message.
 - 280 (Device Watchdog), sending a watchdog answer based on requests data to ensure the connection keepalive mechanism.
 
 This is to be improved, mainly by Accounting messages support with Rf charging implementation(Session management, etc.).

**On any Diameter request that is being processed having a command code which is not present/implemented support for, the application will respond with ***DIAMETER_UNABLE_TO_COMPLY(5012)*** result code

Protocol information
==========

Diameter is a Authentication Authorization and Accounting (AAA) protocol. It works on the Application Layer if we consider OSI Layered model. Diameter is a message based protocol, where AAA  nodes exchange messages and receive Positive or Negative acknowledgment for each message exchanged between nodes. For  message exchange  it internally uses the TCP and SCTP which makes diameter reliable. Its technical specifications are given in RFC-6733 Diameter Base Protocol.

Diameter is Message (Packet) based protocol. There are two types of messages Request Messages and Answer Messages. The message structure is of following sort:

````````````````````````````````````````````````````````````````````
____________________________________________________________________
|   0                   1                   2                   3   |
|   0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 |
|___________________________________________________________________|
|       Version       |              Message Length                 |
|___________________________________________________________________|
|      command flags  |               Command-Code                  |
|___________________________________________________________________|
|                           Application-ID                          |
|___________________________________________________________________|
|                        Hop-by-Hop Identifier                      |
|___________________________________________________________________|
|                        End-to-End Identifier                      |
|___________________________________________________________________|
|    AVPs ...													    |
|___________________________________________________________________|

````````````````````````````````````````````````````````````````````


Capability negotiation
----------
The basic motive of this process is to KNOW about the other node to which a node intended to communicate before establishing the connection, ie. whether other node contains the applications for which node wants to communicate. 

Technically speaking, It is the process where two diameter peer exchange their identity and its capabilities (such as protocol version number, supported diameter applications, security mechanism etc.). Peer share their capabilities by CER/CEA Message (Capability-Exchange-Request/Capability-Exchange-Answer).


Transport Failure Detection
----------

Given the nature of the Diameter protocol, it is recommended that
transport failures be detected as soon as possible.  Detecting such
failures will minimize the occurrence of messages sent to unavailable
agents, resulting in unnecessary delays, and will provide better
failover performance.  The Device-Watchdog-Request and Device-
Watchdog-Answer messages, defined in this section, are used to pro-
actively detect transport failures.

- Device-Watchdog-Request

   The Device-Watchdog-Request (DWR), indicated by the Command-Code set
   to 280 and the Command Flags' 'R' bit set, is sent to a peer when no
   traffic has been exchanged between two peers (see Section 5.5.3).
   Upon detection of a transport failure, this message MUST NOT be sent
   to an alternate peer.

   Message Format

      <DWR>  ::= < Diameter Header: 280, REQ >
                 { Origin-Host }
                 { Origin-Realm }
                 [ Origin-State-Id ]

- Device-Watchdog-Answer

   The Device-Watchdog-Answer (DWA), indicated by the Command-Code set
   to 280 and the Command Flags' 'R' bit cleared, is sent as a response
   to the Device-Watchdog-Request message.

      <DWA>  ::= < Diameter Header: 280 >
                       { Result-Code }
                       { Origin-Host }
                       { Origin-Realm }
                       [ Error-Message ]
                     * [ Failed-AVP ]
                       [ Original-State-Id ]

