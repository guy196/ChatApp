import socket
import logging
from sympy import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
from Crypto.Random import get_random_bytes

class Client:

    def __init__(self):
        global key
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.client_socket.connect(("127.0.0.1", 55))
        except Exception as e:
            logging.error(f"Error connecting to the server: {e}")
    
    def send_message(self,message):
        self.client_socket.send(message.encode('utf-8'))# Send the message to the server

    def recive_message(self):
        return self.client_socket.recv(1024).decode('utf-8')
    
    def login(self,username,password):
        self.send_message(f"login~{username}~{password}")
        return self.recive_message()

    def sign_up(self,name,password,bio,created_date,salt):
        print(salt)
        self.send_message(f"signup~{name}~{password}~{bio}~{created_date}~{salt.decode('utf-8')}")
        return self.recive_message()
    
    def get_users_names(self):
        self.send_message("names")
        return self.recive_message()
    
    def get_messages(self,sender,receiver):
        self.send_message(f"messages~{sender}~{receiver}")
        return self.recive_message()
    
    def send_message_in_chat(self,sender,receiver,message,date_time,key):
        print("KEeeee")
        # encypted_message = encrypt(message,key)
        self.send_message(f"sendmessage~{sender}~{receiver}~{message}~{date_time}")
        return self.recive_message()




def encrypt(data, key):
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    return iv + ciphertext

def decrypt(ciphertext, key):
    cipher = AES.new(key, AES.MODE_CBC, iv=ciphertext[:AES.block_size])
    decrypted_data = unpad(cipher.decrypt(ciphertext[AES.block_size:]), AES.block_size)
    return decrypted_data.decode('utf-8')




if __name__ == "__main__":
    client_instance = Client()
    client_instance.connect()
   
    #print(client_instance.login("G12345","G12345"))

