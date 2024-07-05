import sqlite3
class ChatAppOrm:
    def __init__(self):#You don't need to pass something into the self. 
        self.conn = None  # will store the DB connection
        self.cursor = None  # will store the DB connection cursor
    
    def create_tables(self):
        create_table_users_table = '''
            CREATE TABLE IF NOT EXISTS users_table (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT,
                Password TEXT,
                Bio TEXT,
                CreatedDate TEXT,
                salt TEXT
            );
        '''
        alter_table_users_table = '''
            ALTER TABLE users_table
            ADD COLUMN salt TEXT;
        '''

        # Execute the ALTER TABLE statement

        create_table_users_recentChats = '''
        CREATE TABLE IF NOT EXISTS recentChats (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            CurrentName TEXT,
            UserName TEXT
        );
        '''

        create_table_users_messages = '''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        '''
        self.open_DB()
        self.cursor.execute(create_table_users_table)
        self.cursor.execute(create_table_users_recentChats)
        self.cursor.execute(create_table_users_messages)
        self.cursor.execute(alter_table_users_table)
        self.commit()
        self.close_DB()
    
    def close_DB(self):
        self.conn.close()
    
    def commit(self):
        self.conn.commit()

    def open_DB(self):
        self.conn = sqlite3.connect('./AppChatDB.db')
        self.cursor = self.conn.cursor()
    
    def get_all_users(self):
        self.open_DB()
        users = []
        sql = "SELECT * FROM users_table"
        res = self.cursor.execute(sql)
        for row in res:
            user = User(row[1], row[2], row[3], row[4])
            users.append(user)
        self.close_DB()
        return users
    
    def get_all_messages(self,sender,reciver):
        try:
            self.open_DB()
            # Retrieve messages where sender is 'guy' and receiver is 'Alon' or vice versa
            sql = """
                SELECT * FROM messages
                WHERE (sender = ? AND receiver = ?)
                OR (sender = ? AND receiver = ?)
            """
            self.cursor.execute(sql, (sender, reciver, reciver, sender))
            result = self.cursor.fetchall()

            # Print the retrieved messages for debugging
            for message in result:
                print(message)

            # Check if the result is empty
            if not result:
                # No messages found, return an empty list
                return []
            return result
        except Exception as e:
            return False, e
        finally:
            self.close_DB()
    
    def update_user(self,data):
        current_name, name,password,bio,created_date = data
        try:

            all_users = self.get_all_users()
            self.open_DB()
            found_user = None
            for user in all_users:
                if(user.name == current_name):
                    found_user = name
                    self.cursor.execute("UPDATE users_table set Name=?, password=?, Bio=?, CreatedDate=? WHERE Name=?", (name,password,bio,created_date,current_name))
                    self.commit()
            if(found_user == None):
                return False
            
        except Exception as e:
            print(f"Exception : {e} ")
            return False
        
        finally:
            self.close_DB()
    
    def insert_user(self,data):
        try:

            name,password,bio,created_date,salt = data
            users = self.get_all_users()
            self.open_DB()

            for user in users:
                if(user.name == name):
                    return "User already exists"
            
            self.cursor.execute("INSERT INTO users_table (Name, Password, Bio, CreatedDate, salt) VALUES (?, ?, ?, ?,?)",(name,password,bio,created_date,salt))
            self.commit()
            return True
        
        except Exception as e:
            print(e)
            return False,e
        
        finally:
            self.close_DB()
    
    def insert_message(self,data):
        try:

            sender,reciver,message,date_time = data
            self.open_DB()
            sql = "INSERT INTO messages (sender , receiver, message, timestamp) VALUES (?, ?, ?, ?)"
            self.cursor.execute(sql,(sender,reciver,message,date_time))
            self.commit()
            return True
        
        except Exception as e:
            print(e)
            return False
        
        finally:
            self.close_DB()
    
    def delete_user(self,name):
        try:

            self.open_DB()
            sql = "DELETE FROM users_table WHERE Name=?"
            self.cursor.execute(sql, (name,))
            self.commit()
        except Exception as e:
            print(f"Exception: {e}")
        finally:
            self.close_DB()
    
    def add_user_to_recent_chats(self,current_name, username):
        try:

            self.open_DB()
            sql = "Insert Into recentChats (current_name,username) Values (?,?)"
            self.cursor.execute(sql, (current_name,username))
            self.commit()
        except Exception as e:
            print(f"Exception: {e}")
        finally:
            self.close_DB()

    def search_messages(self, search_value,sender,receiver):
        try:
            if(sender != None and receiver != None):
                self.open_DB()
                sql = "SELECT * FROM Messages WHERE message LIKE ? AND ((sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?))"            
                self.cursor.execute(sql, ('%' + search_value + '%', sender, receiver, receiver, sender))
                result = self.cursor.fetchall()
                return result#Returns a list of tuples.
        except Exception as e:
            return False, e
        finally:
            self.close_DB()

    def GetUserHashPass(self,user):
        try:
            self.open_DB()
            sql = "SELECT * FROM users_table WHERE Name = ?"
            self.cursor.execute(sql, (user,))
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            return False, e
        finally:
            self.close_DB()

    def get_user_count(self):
        self.open_DB()
        sql = "SELECT COUNT(*) FROM users_table"
        self.cursor.execute(sql)
        # Retrieve the count of users from the database
        return self.cursor.fetchone()[0]
    
    def get_message_count(self, sender, receiver):
        try:
            self.open_DB()
            sql_count = """
                SELECT COUNT(*) FROM messages
                WHERE (sender = ? AND receiver = ?)
                OR (sender = ? AND receiver = ?)
            """
            self.cursor.execute(sql_count, (sender, receiver, receiver, sender))
            count_result = self.cursor.fetchone()

            count = count_result[0] if count_result else 0 #If nothing is returned puts 0

            return count
        except Exception as e:
            return False, e
        finally:
            self.close_DB()
        


class User:
    def __init__(self,name,password,bio,created_date):
        self.name = name
        self.password = password
        self.bio = bio
        self.created_date = created_date
    def __str__(self):
        return f"Name : {self.name}\nPassword : {self.password}\nBio : {self.bio}\ncreated_date : {self.created_date}\n"
    

class Message:
    def __init__(self,sender,receiver,message,timestamp):
        self.sender =sender
        self.receiver = receiver
        self.message = message
        self.timestamp = timestamp

if __name__ == "__main__":
    user1 = User("Guy","GGG123", "Hello World","10/10/2005")
    instance = ChatAppOrm()
    instance.create_tables()
    #instance.delete_user("Alon")
    #message = Message("Guy","Alon","Hello Alon","10/10/25")
    #instance.insert_message(message.sender,message.receiver,message.message,message.timestamp)
    #instance.insert_user((user1.name,user1.password,user1.bio,user1.created_date))
    #instance.update_user((user1.name,"Alon",user1.password,user1.bio,user1.created_date))