''' A testing module for checking bidirectional communication '''
import Queue
import threading

import Receive
import Send

if __name__ == '__main__':

    PERSONAL_COMPUTER_IP = '173.250.180.118'
    CSE208_IP = '128.208.5.218'

    RECEIVE_MESSAGE_QUEUE = Queue.Queue()
    SEND_MESSAGE_QUEUE = Queue.Queue()
    RECEIVE_OBJECT = Receive.Receive(port=13001, receive_message_queue=RECEIVE_MESSAGE_QUEUE)
    SEND_OBJECT = Send.Send(host_ip=PERSONAL_COMPUTER_IP, port=13000, send_message_queue=SEND_MESSAGE_QUEUE)
    threading.Thread(target=RECEIVE_OBJECT.receive_from_queue).start()
    threading.Thread(target=SEND_OBJECT.run_send_from_queue).start()

    while True:
        data = raw_input("Enter message to send or type 'exit': ")
        SEND_MESSAGE_QUEUE.put(data)
        data = RECEIVE_MESSAGE_QUEUE.get()
        print "Received message: " + data
