import struct


def send_msg(conn, msg):
    # pack a four-byte unsigned int as the message length
    msg = struct.pack('<I', len(msg)) + msg
    conn.sendall(msg)


def recv_msg(conn):
    # get message length (4 byte)
    msg_len = recvall(conn, 4)
    if not msg_len:
        return None
    msg_len = struct.unpack('<I', msg_len)[0]
    # return msg
    return recvall(conn, msg_len)


def recvall(conn, n):
    data = ''
    # record time
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data
