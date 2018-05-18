"""
This method is for sending messages between computers on the same network.

Messages are sent as strings.  If sending a nonstring object, it will be converted
to a string.
"""
import os
import socket
import threading
import queue
import warnings

class Send(object):

    def __init__(self, host_ip, port, send_message_queue):

        """
        Sends messages to the specified host and port for computers on the same network.
        
        :param host_ip: (string) Set to the ip address (host) of the target computer (example: 173.250.XXX.XX)
        :param port: (int) Set to desired port. Only one Send object can be opened on a given port. Example: 13000
        :param send_message_queue: Place messages on this queue to have them sent.
        """
        self.addr = (host_ip, port)
        self.UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_message_queue = send_message_queue
        warnings.warn(DeprecationWarning('Use TCP instead'))

    def run_send_from_queue(self):
        """
        Reads messages from the send_messages_queue passed during initialization

        Sends data in accordance with the host and port set during initialization
        
        Pass 'exit' to close the socket.
        
        Data put on queue will be cast to a string!
        """
        while True:
            message = str(self.send_message_queue.get())
            self.UDPSock.sendto(message, self.addr)

if __name__ == '__main__':
    SEND_MESSAGE_QUEUE = queue.Queue()
    PERSONAL_COMPUTER_IP = '173.250.180.118'
    SEND_OBJECT = Send(host_ip='128.208.5.218', port=13000, send_message_queue=SEND_MESSAGE_QUEUE)
    threading.Thread(target=SEND_OBJECT.run_send_from_queue).start()
    while True:
        data = input("Enter message to send or type 'exit': ")
        SEND_MESSAGE_QUEUE.put(data)

























