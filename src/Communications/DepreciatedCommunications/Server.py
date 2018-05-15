import EEGInterface.EEG_INDEX as EEG_INDEX
import SocketServer
import os
import time
import warnings

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def __init__(self, queue_list=None):
        raise warnings.warn(DeprecationWarning)
        self.queue_list = [] if queue_list is None else queue_list

    def handle(self):
        print "Connected!"
        while True:
            # self.request is the TCP socket connected to the client
            data = self.request.recv(1024).strip()
            global_time = time.time()
            eeg_index = EEG_INDEX.CURR_EEG_INDEX
            message = str(data)
            recieve_dict = {'global_time': global_time, 'eeg_index': eeg_index, 'message': message}


            if not data:
                print "Game Ended Abruptly!!"
                time.sleep(2)
                os._exit(1)
            for q in self.queue_list:
                q.put(recieve_dict)


def start_server(host="192.168.1.2", port=27015, clss=MyTCPHandler):
    # host, port = "128.95.226.122", 27015  # TMS computer
    # Create the server, binding to localhost on port 9999
    print 'Connecting...'
    server = SocketServer.TCPServer((host, port), clss)
    server.serve_forever()

if __name__ == '__main__':
    start_server()
