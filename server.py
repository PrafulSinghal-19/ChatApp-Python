import socket
from threading import Thread, Lock
from datetime import datetime
from typing import List, Tuple

# Host and Port of server
HOST = '127.0.0.1'
PORT = 9090

def broadcast_msg(msg: str, clients: List[Tuple[socket.socket, str]], send_lock: Lock):
    msg = msg.encode('UTF-8')
    with send_lock:
        for client in clients:
            try:
                client[0].send(msg)
            except:
                pass

def handle_client(client: socket.socket, clients: List[Tuple[socket.socket, str]], clients_lock: Lock, send_lock: Lock):
    try:
        client_nickname = client.recv(1024).decode('UTF-8')
        with clients_lock:
            clients.append((client, client_nickname))
        
        recv_msg = f'*** {client_nickname} joined the chat ***'
        broadcast_msg(recv_msg, clients, send_lock)

        while True:
            recv_msg = client.recv(1024).decode('UTF-8')
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