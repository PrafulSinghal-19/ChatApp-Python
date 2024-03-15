import socket
import rsa
from rsa import PublicKey
from threading import Thread, Lock
from datetime import datetime
from typing import List, Tuple

# Host and Port of server
HOST = '127.0.0.1'
PORT = 9090

# public and private key of server
public_key, private_key = rsa.newkeys(1024)

def broadcast_msg(msg: str, clients: List[Tuple[socket.socket, str, PublicKey]], send_lock: Lock):
    with send_lock:
        for client in clients:
            try:
                client[0].send(rsa.encrypt(msg.encode('UTF-8'), client[2]))
            except:
                pass

def handle_client(client: socket.socket, clients: List[Tuple[socket.socket, str, PublicKey]], clients_lock: Lock, send_lock: Lock):
    try:
        # send the server public key to client
        client.send(public_key.save_pkcs1('PEM'))
        # recv the client public key
        public_key_partner = rsa.PublicKey.load_pkcs1(client.recv(1024))
        # recv the client nickname
        client_nickname = rsa.decrypt(client.recv(1024), private_key).decode('UTF-8')

        with clients_lock:
            clients.append((client, client_nickname, public_key_partner))
        
        recv_msg = f'*** {client_nickname} joined the chat ***'
        broadcast_msg(recv_msg, clients, send_lock)

        while True:
            recv_msg = rsa.decrypt(client.recv(1024), private_key).decode('UTF-8')
            if recv_msg:
                recv_msg = f'{datetime.now().strftime("%c")} ({client_nickname}) - {recv_msg}' 
                broadcast_msg(recv_msg, clients, send_lock)
            else:
                break
    except:
        pass
    finally:
        client.close()
        msg = f'*** {client_nickname} left the chat ***'
        with clients_lock:
            if (client, client_nickname) in clients:
                clients.remove((client, client_nickname))
        broadcast_msg(msg, clients, send_lock)

def handle_connection_req(server: socket.socket):
    # clients have socket object, client name and the public key of client
    clients = []
    clients_lock = Lock()
    send_lock = Lock()
    while True:
        connection_socket, addr = server.accept()
        Thread(target = handle_client, args = (connection_socket, clients, clients_lock, send_lock, )).start()

def main():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen()

        print(f'*** SERVER STARTED ON {HOST}:{PORT} ***')
        handle_connection_req(server)
    except Exception as e:
        print(e) 
        print(f'*** Server Stopped ***')
    finally:
        server.close()

if __name__ == '__main__':
    main()