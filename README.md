Diameter Client-Server Architecture in Python
==========

This repository contains a sample server which can be used as an Diameter Terminator (sending Diameter responses to specific requests) for the purpose of testing, which I plan to develop further in the future, in order to simulate a CDF (Charging Data Function).


Features
==========

At the moment, it can only process requests with command code 257 (Capability Exchange), sending an answer containing information based on the data present in the AVPs of the request message. This is to be improved, as well as adding Device Watchdog messages support and then continue with Rf charging implementation.


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
