import socket
import select

def broadcast_data(message):
    """ Sends a message to all sockets in the connection list. """
    # Send message to everyone, except the server.
    for sock in CONNECTION_LIST:
        if sock != SERVER_SOCKET:
            try:
                sock.sendall(message) # send all data at once
            except Exception as msg: # Connection was closed. Errors
                print(type(msg).__name__)
                sock.close()
                try:
                    CONNECTION_LIST.remove(sock)
                    index = CONNECTION_LIST.index(sock)
                    CONNECTION_ADDR.pop(index)
                except ValueError as msg:
                    print("{}:{}".format(type(msg).__name__, msg))


def privatechat_data(message, target_add):
    """ Sends a message to special sockets in the connection list. """
    # Send message to specific person
    for sock in CONNECTION_LIST:
        index = CONNECTION_LIST.index(sock)
        add = CONNECTION_ADDR[index]
        if sock != SERVER_SOCKET and add == target_add:
            try:
                sock.sendall(message) # send all data at once
            except Exception as msg: # Connection was closed. Errors
                print(type(msg).__name__)
                sock.close()
                try:
                    CONNECTION_LIST.remove(sock)
                    index = CONNECTION_LIST.index(sock)
                    CONNECTION_ADDR.pop(index)
                except ValueError as msg:
                    print("{}:{}".format(type(msg).__name__, msg))

    
CONNECTION_LIST = []
CONNECTION_ADDR= [00000]
RECV_BUFFER = 4096
PORT = 1338

SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
SERVER_SOCKET.bind(("", PORT)) # empty addr string means INADDR_ANY

print("Listening...")
SERVER_SOCKET.listen(10) # 10 connections

CONNECTION_LIST.append(SERVER_SOCKET)
print("Server started!")

while True:
    # Get the list sockets which are ready to be read through select
    READ_SOCKETS, WRITE_SOCKETS, ERROR_SOCKETS = select.select(CONNECTION_LIST, [], [])
    for SOCK in READ_SOCKETS: # New connection
        # Handle the case in which there is a new connection recieved through server_socket
        if SOCK == SERVER_SOCKET:
            SOCKFD, ADDR = SERVER_SOCKET.accept()
            CONNECTION_LIST.append(SOCKFD) # add socket descriptor
            CONNECTION_ADDR.append(ADDR[1])
            # Adding \r to prevent message overlapping when another user
            print("\rClient ({0}, {1}) connected".format(ADDR[0], ADDR[1]))
            broadcast_data("Client ({0}:{1}) entered room\n".format(ADDR[0], ADDR[1]).encode())
        else: # Some incoming message from a client
            try: # Data recieved from client, process it
                DATA = SOCK.recv(RECV_BUFFER)
                if DATA:
                    ADDR = SOCK.getpeername() # get remote address of the socket
                    message = "\r avaiable user{}[{}:{}]: {}".format(CONNECTION_ADDR, 
                                               ADDR[0], ADDR[1], DATA.decode())
                    print(message, end="")
                    #public chat
                    if '@' not in message:
                        broadcast_data(message.encode())
                    else:
                    #private chat
                        target_add = message.split('@', 1)[1]
                        privatechat_data(message.encode(), int(target_add))
            except Exception as msg: # Errors happened, client disconnected
                print(type(msg).__name__, msg)
                print("\rClient ({0}, {1}) disconnected.".format(ADDR[0], ADDR[1]))
                broadcast_data("\rClient ({0}, {1}) is offline\n"
                               .format(ADDR[0], ADDR[1]).encode())
                SOCK.close()
                try:
                    CONNECTION_LIST.remove(SOCK)
                    index = CONNECTION_LIST.index(SOCK)
                    CONNECTION_ADDR.pop(index)
                except ValueError as msg:
                    print("{}:{}.".format(type(msg).__name__, msg))
                continue

SERVER_SOCKET.close()











