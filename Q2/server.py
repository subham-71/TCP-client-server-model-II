import socket
import threading
import datetime
import time
import threading

HOST = "127.0.0.1"
PORT = 8080

# Dictionary to store usernames and passwords

USERS = {}
USERS['admin'] = 'admin'

# Dictionary to store chat rooms

CHAT_ROOMS = set()

# Dictionary to store active users

ACTIVE_USERS = {}

# Dictionary to which user is in which chat room

USERS_CHAT_ROOM = {}


# Class to represent a chat room
class ChatRoom:
    def __init__(self, name, creator):
        self.name = name
        self.users = set()
        self.users.add(creator)
        self.history = ""
        
    def add_user(self, user):
        self.users.add(user)

    def remove_user(self, user):
        self.users.remove(user)

    def send_message(self, message):

        with open(self.name+'.txt', 'a') as f:
            f.write(message + '\n')



class ClientThread(threading.Thread):

    def __init__(self, address, connection):

        threading.Thread.__init__(self)

        self.connection = connection
        self.address = address
        self.username = ''

        print("New connection added: ", address)

        

    def login(self):
        self.username = self.connection.recv(1024).decode()
        password = self.connection.recv(1024).decode()

        print("Username: ", self.username)
        print("Password: ", password)

        if self.username in USERS:
            if password == USERS[self.username]:
                self.connection.send('Login successful!'.encode())
                print('Login successful!')
                return 1
            else:
                self.connection.send('Incorrect password!'.encode())
                print('Incorrect password!')
                return -1

        else:
            print('User not registered!')
            self.connection.send('User not registered!'.encode())
            return -1

        return False

    def signup(self):

        self.username = self.connection.recv(1024).decode()

        if self.username in USERS:
            self.connection.send('Username already exists!'.encode())
            print('Username already exists!')
            return -1
        else:
            self.connection.send('Enter Password : '.encode())

            password = self.connection.recv(1024).decode()
            USERS[self.username] = password
            self.connection.send('User registered successfully!'.encode())
            print('User registered successfully!')
            return 1

    def handleAuth(self):

        while True:

            print("Handling authentication...")

            method = self.connection.recv(1024).decode()
            print(method)
            if method == 'login':
                if (self.login() == 1):
                    break

            elif method == 'signup':
                if (self.signup() == 1):
                    break

        # Add the client to the dictionary of active clients
        ACTIVE_USERS[self.username] = self.connection

        # Send the list of active users to the client
        self.connection.send('Active users: {}'.format(
            list(ACTIVE_USERS.keys())).encode())

    def join_chat_room(self, chat_room_name):

        if(CHAT_ROOMS==set()):
            self.connection.send(
            f"[System]: Chat room {chat_room_name} does not exist.".encode())

        else :
            for chat_room in CHAT_ROOMS:
                # Check if the chat room exists
                if chat_room.name == chat_room_name:

                    # Add the user to the chat room
                    chat_room.add_user(self.username)
                    USERS_CHAT_ROOM[self.username] = chat_room_name

                    # Send a message to the chat room
                    chat_room_message = f"[System][{datetime.datetime.now().strftime('%H:%M:%S')}]: {self.username} has joined the chat room."
                    chat_room.send_message(
                        chat_room_message)

                    # Send a message to the client
                    self.connection.send(
                        f"[System]: You have joined the chat room \"{chat_room_name}\"".encode())

                else:

                    # Send a message to the client
                    self.connection.send(
                        f"[System]: Chat room {chat_room_name} does not exist.".encode())

    def create_chat_room(self, chat_room_name):

        if CHAT_ROOMS != set():

            for chat_room in CHAT_ROOMS:

                # Check if the chat room exists
                if chat_room.name == chat_room_name:

                    # Send a message to the client
                    self.connection.send(
                        f"[System]: Chat room {chat_room_name} already exists. Please join it.".encode())
                    return 
                
        # Create a new chat room
        chat_room = ChatRoom(
            chat_room_name, self.username)
        CHAT_ROOMS.add(chat_room)

        # Add the user to the chat room
        chat_room.add_user(self.username)
        USERS_CHAT_ROOM[self.username] = chat_room_name

        # Send a message to the chat room
        chat_room_message = f"[System][{datetime.datetime.now().strftime('%H:%M:%S')}]: {self.username} has created the chat room."

        f = open(chat_room_name+'.txt', 'w')
        f.close()

        chat_room.send_message(
            chat_room_message)

        # Send a message to the client
        self.connection.send(
            f"[System]: You have created the chat room \"{chat_room_name}\" ".encode())
            

    def leave_chat_room(self, chat_room):

        # Remove the user from the chat room
        chat_room.remove_user(self.username)
        USERS_CHAT_ROOM.pop(self.username)

        # Send a message to the chat room
        chat_room_message = f"[System][{datetime.datetime.now().strftime('%H:%M:%S')}]: {self.username} has left the chat room."
        chat_room.send_message(chat_room_message)

        # Send a message to the client
        self.connection.send(
            f"[System]: You have left the chat room \"{chat_room.name}\".".encode())

    def handle_user(self):

        while (1):
            
            # Send list of chat rooms to the client
            chat_room_list = [chat_room.name for chat_room in CHAT_ROOMS]
            self.connection.send(
                f"\n[System]: Chat rooms: {chat_room_list}".encode())
            print("Chat rooms: ", chat_room_list)

            # Receive the message from the client
            message = self.connection.recv(1024).decode()
            print(message)

            # Check if the user wants to join a chat room
            if message.startswith('/join'):

                # Get the chat room name
                chat_room_name = message.split(" ")[1]
                # print("[] :  chat_room : ",chat_room_name)

                # Join the chat room
                self.join_chat_room(chat_room_name)

            # Check if the user wants to join a chat room
            elif message.startswith('/create'):

                # Get the chat room name
                chat_room_name = message.split(" ")[1]

                # Join the chat room
                self.create_chat_room(chat_room_name)

            # Check if the user wants to leave a chat room
            elif message.startswith('/leave'):

                chat_room_name = USERS_CHAT_ROOM[self.username]

                # Find the chat room
                for chat_room in CHAT_ROOMS:
                    if chat_room.name == chat_room_name:
                        self.leave_chat_room(chat_room)

            elif message.startswith('/logout'):
                chat_room_name = USERS_CHAT_ROOM[self.username]

                # Find the chat room
                for chat_room in CHAT_ROOMS:
                    if chat_room.name == chat_room_name:
                        self.leave_chat_room(chat_room)

                # Remove the user from the active users
                ACTIVE_USERS.pop(self.username)

                # Send a message to the client
                self.connection.send(
                    "[System]: Logged out successfully!".encode())

                # Close the self.connection
                self.connection.close()
                return -1
            elif message == "NO_INPUT 8f9e1d6c5b4a32":
                continue

            else:
                if (USERS_CHAT_ROOM[self.username] == None):
                    self.connection.send(
                        "[System]: You are not in any chat room.".encode())

                else:
                    # Get the chat room name
                    chat_room_name = USERS_CHAT_ROOM[self.username]

                    room_message = f"[System][{datetime.datetime.now().strftime('%H:%M:%S')}]: {self.username} : {message} "

                    # Find the chat room
                    for chat_room in CHAT_ROOMS:
                        if chat_room.name == chat_room_name:

                            # Send the message to the chat room
                            chat_room.send_message(
                                room_message)
                            
            

    def handle_client(self):

        # Get username
        username = self.handleAuth()

        
        # Handle the user
        print("Handling user")
        x = self.handle_user()


        if (x == -1):
            # self.connection.close()
            return -1

    def run(self):
        print("Connection from : ", self.address)
        if (self.handle_client() == -1):
            print("Client at ", self.address, " disconnected...")


if __name__ == "__main__":

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    print("Server started on port : ", PORT)
    print("Waiting for client request..")

    while True:
        server.listen(1)
        clientsock, clientAddress = server.accept()

        try:
            newthread = ClientThread(clientAddress, clientsock)
            newthread.start()
        except:
            print("Error in thread")
            clientsock.close()
