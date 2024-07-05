import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from client import Client
from datetime import datetime
import security
import DBManager
from random import randint
from Crypto.Random import get_random_bytes

key = None
class ChatAppGui:

    def __init__(self, root,client):
        self.root = root
        self.client = client
        self.root.title("Chat App")
        self.results = "Test"
        self.username = None
        self.otherUser = None
        # Variables for user input
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.signup_username_var = tk.StringVar()
        self.signup_password_var = tk.StringVar()
        self.signup_bio_var = tk.StringVar()
        self.signup_CreatedDate_var = tk.StringVar()
        # Create frames
        self.login_frame = tk.Frame(root)
        self.signup_frame = tk.Frame(root)
        self.contact_frame = tk.Frame(root)
        self.chat_frame = tk.Frame(root)

        self.last_known_message_count = 0
        # Initialize frames
        self.setup_login_frame()
        self.setup_signup_frame()
        self.set_up_chat_frame()

        # Show login frame by default
        self.show_login_frame()

        #Creates a DB Instance 
        self.instance = DBManager.ChatAppOrm()

        # Keep track of the last known number of users
        self.last_known_user_count = self.instance.get_user_count()

    def display_message(self, message):
        # Insert the message into the chat_display
        self.chat_display.config(state=tk.NORMAL)
        #deletes the current chat.


        # Insert the message with formatting based on the sender

        if(message == ""):
            return
        self.chat_display.delete(1.0, tk.END)  
        self.chat_display.insert(tk.END, message + "\n")
        #Disable user writing 
        self.chat_display.config(state=tk.DISABLED)
        # Automatically scroll to the bottom to show the latest message
        self.chat_display.yview(tk.END)

    def send_message(self):
        global key
        message = self.entry.get()
        # Clear the input area
        self.entry.delete(0, tk.END)
        if message:
            formatted_string_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            client_instance.send_message_in_chat(self.username,self.otherUser,message,formatted_string_time,key)
            chatMessages = client_instance.get_messages(self.username,self.otherUser)
            print("Messages That are Displaying are : " + chatMessages)
            self.display_message(chatMessages)

    def set_up_chat_frame(self):
        self.chat_frame = tk.Frame(self.root)
        self.signup_frame.pack_forget()
        self.label_username = tk.Label(root, text=f"Logged in as: {self.username}")
        self.label_username.pack(pady=10)        

        # Create a StringVar to track the content of the search box
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.search_callback)

        # Create and place the search box (Entry widget)
        self.search_entry = tk.Entry(root, textvariable=self.search_var)
        self.search_entry.pack(padx=10, pady=10)

        # Create a Text widget for displaying messages
        self.chat_display = tk.Text(self.root, wrap="word", state=tk.DISABLED)
        self.chat_display.pack(expand=True, fill=tk.BOTH)

        # Entry for user input
        self.entry = tk.Entry(self.chat_frame, width=30)
        self.entry.pack(side=tk.LEFT, padx=10, pady=10)
        # Button to send messages
        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=10, pady=10)

        #Displaying all the users to choose from
        self.list_box = tk.Listbox(self.chat_frame)
        self.list_box.pack(fill=tk.Y, padx=10, pady=10)
        self.list_box.bind("<<ListboxSelect>>", self.on_listbox_select)
        self.load_users()

    #Gets called when the search box text changes
    def search_callback(self, *args):
        search_term = self.search_var.get()
        search_results = self.instance.search_messages(search_term,self.username,self.otherUser)
        printed_messages = []
        for message_row in search_results:
            printed_messages.append(message_row[3] + '\n') 
            print(printed_messages)
        if printed_messages:
            self.chat_display = self.display_message(search_results)
        else:
            self.display_message("No Messages Yet")
    
    def load_users(self):
        result = self.client.get_users_names()
        result = result.split("~")
        if result:
            for name in result:
                if name == self.username:
                    pass 
                self.list_box.insert(tk.END,name)    

    def setup_login_frame(self):
        self.login_frame.pack(pady=20)
        # Widgets for login frame
        tk.Label(self.login_frame, text="Username:").pack()
        tk.Entry(self.login_frame, textvariable=self.username_var).pack()
        tk.Label(self.login_frame, text="Password:").pack()
        tk.Entry(self.login_frame, textvariable=self.password_var, show="*").pack()
        tk.Label(self.login_frame, text=self.results).pack()

        tk.Button(self.login_frame, text="Login", command=lambda event=None: self.login(self.username_var.get(), self.password_var.get())).pack()
        tk.Button(self.login_frame, text="Switch to Sign-Up", command=self.show_signup_frame).pack()

    def setup_signup_frame(self):

        self.signup_frame.pack_forget()

        # Widgets for sign-up frame
        tk.Label(self.signup_frame, text="Username:").pack()
        tk.Entry(self.signup_frame, textvariable=self.signup_username_var).pack()
        tk.Label(self.signup_frame, text="Password:").pack()
        tk.Entry(self.signup_frame, textvariable=self.signup_password_var, show="*").pack()
        tk.Label(self.signup_frame, text="Bio:").pack()
        tk.Entry(self.signup_frame, textvariable=self.signup_bio_var).pack()
        tk.Label(self.signup_frame, text="CreatedDate:").pack()
        tk.Entry(self.signup_frame, textvariable=self.signup_CreatedDate_var).pack()
        tk.Button(self.signup_frame, text="Sign Up", command=lambda event=None: self.signup(self.signup_username_var.get(), self.password_var.get(),self.signup_bio_var.get(),self.signup_CreatedDate_var.get())).pack()
        tk.Button(self.signup_frame, text="Switch to Login", command=self.show_login_frame).pack()
    
    def check_for_updates(self):
        # Check for updates only when the number of users changes
        current_user_count = self.instance.get_user_count()
        current_message_count = 0
        if self.username is not None and self.otherUser is not None:
            current_message_count = self.instance.get_message_count(self.username,self.otherUser)
            if current_user_count != self.last_known_user_count:
                self.load_users()
                self.last_known_user_count = current_user_count
            if current_message_count != self.last_known_message_count:
                self.load_messages()
                self.last_known_message_count = current_message_count
        # Schedule the next update after a delay (e.g., 2000 milliseconds or 5 seconds)
        self.root.after(1, self.check_for_updates)

    #when you click on a user, displaying all the users.
    def on_listbox_select(self, event):
        selected_index = self.list_box.curselection()
        if selected_index:
            self.otherUser = self.list_box.get(selected_index[0])
            self.load_messages()
            self.last_known_message_count = self.instance.get_message_count(self.username,self.otherUser)


    def load_messages(self):
        chatMessages = client_instance.get_messages(self.username,self.otherUser)
        if(chatMessages == "No Messages"):
            self.display_message("No Messages Yet")
        else:
            self.display_message(chatMessages)

    def show_login_frame(self):
        self.signup_frame.pack_forget()
        self.login_frame.pack(pady=20)

    def show_signup_frame(self):
        self.login_frame.pack_forget()
        self.signup_frame.pack(pady=20)
    
    def show_chat_frame(self):
        self.login_frame.pack_forget()
        self.signup_frame.pack_forget()
        self.chat_frame.pack()
    
    def login(self,username,password):
        result = self.client.login(username,password)
        success = result
        print("success : " + success)
        success,message = success.split("~")
        if success == "True":
            messagebox.showinfo("Logged In successfuly.")
            self.show_chat_frame()
            self.username = username
            self.label_username.config(text=f"Logged in as: {self.username}")
        else:
            messagebox.showinfo(f"Login Was failed. {message}")

    def signup(self,name,password,bio,signup_createdate):
        hashedPass,salt = security.hash_password(password)
        result = self.client.sign_up(name,hashedPass,bio,signup_createdate,salt)
        success,message = result.split("~") 
        print("result : " + success)
        print("result : " + message)
        if success == "True":
            messagebox.showinfo(message)
            self.login(name,password)
        else:
            messagebox.showerror(f"{message}")

def send_random_number(client,G,P,number):
    client.send_message(str(int(pow(G, number, P))))
if __name__ == "__main__":
    root = tk.Tk()
    client_instance = Client()
    client_instance.connect()
    app = ChatAppGui(root,client_instance)
    app.check_for_updates()
    client_instance.send_message("Exchange_Keys")
    PGMessage = client_instance.recive_message().split("~")
    print(PGMessage)
    P = int(PGMessage[0])
    G = int(PGMessage[1])
    number_recive = client_instance.recive_message()
    print(number_recive)
    randNum = randint(1,30)
    send_random_number(client_instance,G,P,randNum)
    key = pow(int(number_recive), randNum, P).to_bytes(16, byteorder='big')
    print("KEYYY")
    print(key)

    root.mainloop()