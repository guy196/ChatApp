import socket
import threading
import DBManager
import pickle
import security
import logging
from random import randint
from sympy import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
from Crypto.Random import get_random_bytes

#Instance of DB to use
instance = DBManager.ChatAppOrm()

def send_message(client_socket, message):
    try:
        client_socket.send(message.encode("utf-8"))
    except Exception as e:
        logging.error(f"Error sending message: {e}")

def get_users_names():
    try:
        user_names = [user.name for user in instance.get_all_users()]
        # Join the names using the tilde (~) separator
        returned_string = "~".join(user_names)
        return returned_string
    except Exception as e:
        # Log the exception for debugging purposes
        logging.error(f"Error getting user names: {e}")
        # Return a meaningful error message or raise the exception
        return "Error retrieving user names."

def get_messages(sender,receiver):
    try:
        messages = instance.get_all_messages(sender, receiver)

        if not messages:
            return "No Messages"

        # Use a list comprehension to format messages with date and content
        formatted_messages = [f"{message[3]}~{message[4]}" for message in messages]

        # Join the formatted messages using newline separator
        returned_messages = "\n".join(formatted_messages)

        return returned_messages
    except Exception as e:
        logging.error(f"Error getting messages: {e}")
        return f"Error retrieving messages: {e}"

def checkLogin(username, password):
    try:
        logging.info("Checking the login information")
        logging.info(f"Username: {username} and password: {password}")

        stored_hash_row = instance.GetUserHashPass(username)

        if stored_hash_row:
            hashed_password = stored_hash_row[2]
            salt = stored_hash_row[5]
            print(hashed_password)
            print(salt)
            if security.verify_password(password, hashed_password,salt):
                # Password is correct, proceed with your logic
                logging.info("Login successful")
                result = "True~Login successful"
                return result
            else:
                # Password is incorrect
                logging.info("Login failed: Incorrect password")
                result = "False~Incorrect password"
                return result
        else:
            # User not found
            logging.info("Login failed: User not found")
            result = "False~User not found"
            return result

    except Exception as e:
        logging.error(f"Error during login check: {e}")
        result = f"False~Error during login check: {e}"
        return result

def checkSignUp(name, password, bio, created_date, salt):
    try:
        print("Checking the signup information")

        if not name or not password:
            return "False~Invalid username or password"

        # Check if the username already exists
        existing_users = [user.name for user in instance.get_all_users()]
        if name in existing_users:
            return "False~Username already exists"

        # Insert the new user
        returned_value = instance.insert_user((name, password, bio, created_date, salt))
        print(returned_value)

        if returned_value:
            return "True~User successfully created"
        else:
            return "False~Error creating user"

    except Exception as e:
        # Log the exception for debugging purposes
        logging.error(f"Error during signup check: {e}")
        # Return a meaningful error message or raise the exception
        return f"False~Error during signup check: {e}"

def checkMessage(sender,reciver,message,date_time,key):
    print(f"Checking the message from {sender} to {reciver}")
    print("Enctyped :")
    print(message)
    # decrypted_message = decrypt(message,key)
    print("Dycryped")
    # print(decrypted_message)
    returnedValue = instance.insert_message((sender,reciver,message,date_time))
    if returnedValue:
        return True
    else:
        return False



def handle_client(client_socket):

    # Handle messages from a client
    #try:
    key = None
    while True:
        message = client_socket.recv(1024).decode()
        if not message:
            break
        message = message.split("~")
        print(message)
        if message[0] == "login":
            result = checkLogin(message[1],message[2])
            send_message(client_socket,result)
        elif message[0] == "signup":
            result = checkSignUp(message[1],message[2],message[3],message[4],message[5])
            send_message(client_socket,result) 

        elif message[0] == "names":
            result = get_users_names()
            send_message(client_socket,result)
        elif message[0] == "sendmessage":
            result = checkMessage(message[1],message[2],message[3],message[4],key)
            if result:
                result = message[1] + "~" + message[2] + "~" + message[3] + "~" + message[4] 
                print(result)
                send_message(client_socket, result)
        elif message[0] == "messages":
            result = get_messages(message[1],message[2])
            send_message(client_socket,result)
        elif message[0] == "Exchange_Keys":
                P,G = generate_PG(client_socket)
                number = randint(1,30)
                send_random_number(client_socket,G,P,number)
                key = recive_client_number(client_socket,number,P)
                print("KEYYY")
                print(key)
    # except Exception as e:
    #     logging.error(f"Error handling client: {e}")
    # finally:
    #     client_socket.close()


def prim_roots(num):
    o = 1
    roots_ls = []
    r = 2
    while r < num:
        k = pow(r, o, num)
        while k > 1:
            o = o + 1
            k = (k * r) % num
        if o == (num - 1):
            roots_ls.append(r)
        o = 1
        r = r + 1
    return roots_ls


def send_PG(s, P,G):
    
    data = f"{P}~{G}"
    print(data)
    s.send(data.encode())


def generate_PG(c):
    P = randprime(1000, 10000)
    roots = prim_roots(P)
    G = roots[randint(0, len(roots) - 1)]
    send_PG(c, str(P),str(G))
    return P, G

def send_random_number(client,G,P,number):
    client.send(str(int(pow(G, number, P))).encode())

def recive_client_number(client_socket,number,P):
    B = int(client_socket.recv(1024).decode('utf-8'))
    return pow(B, number, P).to_bytes(16, byteorder='big')


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
    server_socket = socket.socket()
    server_socket.bind(("127.0.0.1",55))
    server_socket.listen()
    clients = []
    while True:
        client_socket, addr = server_socket.accept()
        clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()
        
    