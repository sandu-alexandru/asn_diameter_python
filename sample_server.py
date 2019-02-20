"""
Sample Diameter Server, which can be used for testing purposes.
Generates a Diameter Server with the default(local) config,
and then starts the server, making it available
for incoming connections and requests handling.
"""

from diameter_server import *

if __name__ == "__main__":
    """
    Main method for the Sample Diameter Server.

    Instantiates a Diameter Server, and then starts it.
    """

    # Generating a Diameter server and starting it
    server = DiameterServer()
    server.start()
