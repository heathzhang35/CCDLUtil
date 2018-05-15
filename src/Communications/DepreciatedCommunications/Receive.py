"""
This method is for receiving messages between computers on the same network.

Messages are sent as strings.  If sending a nonstring object, it will be converted
to a string.
"""

import os
import socket
import Queue
import threading
import warnings

class Receive(object):

    def __init__(self, port, receive_message_queue, host="", buf=1024):
        """
        Sends messages to the specified host and port for computers on the same network.
        :param host: Defaults to ""
        :param port: Set to desired port. Only one Send object can be opened on a given port. Example: 13000
        :param send_message_queue: Place messages on this queue to have them sent.
        """
        host = host
        port = port
        self.buf = buf
        self.addr = (host, port)
        self.UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.UDPSock.bind(self.addr)
        self.receive_message_queue = receive_message_queue
        warnings.warn(DeprecationWarning)

    def receive_from_queue(self):
        """
        Receives messages and passes them to the receive_message_queue passed during initialization

        Received data in accordance with the host and port set during initialization

        Pass 'exit' to close the socket.

        All data passed is of string format -- meaning all data placed on the receive_message_queue will
        be a string.
        """
        while True:
            message, addr = self.UDPSock.recvfrom(self.buf)
            self.receive_message_queue.put(message)
            if message == "exit":
                self.UDPSock.close()

if __name__ == '__main__':
    RECEIVE_MESSAGE_QUEUE = Queue.Queue()
    RECEIVE_OBJECT = Receive(port=13000, receive_message_queue=RECEIVE_MESSAGE_QUEUE)
    threading.Thread(target=RECEIVE_OBJECT.receive_from_queue).start()
    print "Waiting to Receive"
    while True:
        data = RECEIVE_MESSAGE_QUEUE.get()
        print "Received message: " + data




















