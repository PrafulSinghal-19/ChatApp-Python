import socket
import rsa
from threading import Thread

# Host and Port of server
HOST = '127.0.0.1'
PORT = 9090

public_key, private_key = rsa.newkeys(1024)
public_key_server = None

def send_msg(msg: str, nickname: str, client: socket.socket)-> None:
    msg = f'{msg}' 
    client.send(rsa.encrypt(msg.encode('UTF-8'), public_key_server))

def receive_msg(client: socket.socket)-> None:
    while True:
        recv_msg = rsa.decrypt(client.recv(1024), private_key).decode('UTF-8')
        if recv_msg:
            print(recv_msg)
        else:
            raise Exception('Connection Interrupted')

def handle_send_thread(client: socket.socket, nickname: str)-> None:
    try:
        while True:
            msg= input()
            send_msg(msg, nickname, client)
    except:
        raise Exception('Connection Interrupted') 

def main():
    nickname = input('Enter your nickname: ')

    while not nickname:
        nickname = input('Please enter your nickname')

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:       
        client.connect((HOST, PORT))
        print(f'*** Connected successfully to the server ***')

        global public_key_server
        public_key_server = rsa.PublicKey.load_pkcs1(client.recv(1024))

        client.send(public_key.save_pkcs1('PEM'))

        send_msg(nickname, nickname, client)

        Thread(target = handle_send_thread, args= (client, nickname) ).start()
        
        receive_msg(client)

    except: 
        pass
    finally: 
        print(f'*** Connection Interrupted ***')
        client.close()
        

if __name__ == "__main__":
    main()