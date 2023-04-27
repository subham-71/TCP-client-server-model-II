import socket
import threading
import datetime
import time
import threading

HOST = "127.0.0.1"
PORT = 8080

# Class to represent a chat room


class ChatRoom:
    def __init__(self, name, creator):
        self.name = name
        self.users = set()
        self.users.add(creator)

    def add_user(self, user):
        self.users.add(user)

    def remove_user(self, user):
        self.users.remove(user)

    def send_message(self, message, active_users):
        for user in self.users:
            self.active_users[user].send(message.encode())


class ClientThread(threading.Thread):

    def __init__(self, address, connection):

        threading.Thread.__init__(self)

        self.connection = connection
        self.address = address

        print("New connection added: ", address)

        self.users = {}
        self.chat_rooms = set()
        self.active_users = {}
        self.users_chat_room = {}

    def login(self):
        username = self.connection.recv(1024).decode()
        password = self.connection.recv(1024).decode()

        if username in self.users:
            if password == self.users[username]:
                self.connection.send('Login successful!'.encode())
                print('Login successful!')
                return username
            else:
                self.connection.send('Incorrect password!'.encode())
                print('Incorrect password!')
        else:
            print('User not registered!')
            self.connection.send('User not registered!'.encode())

        return False

    def signup(self):

        username = self.connection.recv(1024).decode()

        if username in self.users:
            self.connection.send('Username already exists!'.encode())
            print('Username already exists!')
            return
        else:
            self.connection.send('Enter Password : '.encode())

            password = self.connection.recv(1024).decode()
            self.users[username] = password
            self.connection.send('User registered successfully!'.encode())
            print('User registered successfully!')
            return username

    def handleAuth(self):

        method = self.connection.recv(1024).decode()
        print(method)
        time.sleep(5)

        username = ''
        if method == 'login':
            username = self.login()
        elif method == 'signup':
            username = self.signup()

        # Add the client to the dictionary of active clients
        self.active_users[username] = self.connection

        # Send the list of active users to the client
        self.connection.send('Active users: {}'.format(
            list(self.active_users.keys())).encode())

        return username

    def join_chat_room(self, username, chat_room_name):

        for chat_room in self.chat_rooms:
            # Check if the chat room exists
            if chat_room.name == chat_room_name:

                # Add the user to the chat room
                chat_room.add_user(username)
                self.users_chat_room[username] = chat_room_name

                # Send a message to the chat room
                chat_room_message = f"[System][{datetime.datetime.now().strftime('%H:%M:%S')}]: {username} has joined the chat room."
                chat_room.send_message(
                    chat_room_message.encode(), self.active_users)

                # Send a message to the client
                self.connection.send(
                    f"[System]: You have joined the chat room \"{chat_room_name}\"".encode())

            else:

                # Send a message to the client
                self.connection.send(
                    f"[System]: Chat room {chat_room_name} does not exist.".encode())

    def create_chat_room(self, username, chat_room_name):

        for chat_room in self.chat_rooms:

            # Check if the chat room exists
            if chat_room.name == chat_room_name:

                # Send a message to the client
                self.connection.send(
                    f"[System]: Chat room {chat_room_name} already exists. Please join it.".encode())

            else:
                # Create a new chat room
                chat_room = ChatRoom(
                    chat_room_name, username, self.active_users)
                self.chat_rooms.add(chat_room)

                # Add the user to the chat room
                chat_room.add_user(username)
                self.users_chat_room[username] = chat_room_name

                # Send a message to the chat room
                chat_room_message = f"[System][{datetime.datetime.now().strftime('%H:%M:%S')}]: {username} has created the chat room."

                chat_room.send_message(
                    chat_room_message.encode(), self.active_users)

                # Send a message to the client
                self.connection.send(
                    f"[System]: You have created the chat room \"{chat_room_name}\" ".encode())

    def leave_chat_room(self, username, chat_room):

        # Remove the user from the chat room
        chat_room.remove_user(username)
        self.users_chat_room.pop(username)

        # Send a message to the chat room
        chat_room_message = f"[System][{datetime.datetime.now().strftime('%H:%M:%S')}]: {username} has left the chat room."
        chat_room.send_message(chat_room_message.encode(), self.active_users)

        # Send a message to the client
        self.connection.send(
            f"[System]: You have left the chat room \"{chat_room.name}\".".encode())

    def handle_user(self, username):

        while (1):

            # Receive the message from the client
            message = self.connection.recv(1024).decode()

            # Check if the user wants to join a chat room
            if message.startswith('/join'):

                # Get the chat room name
                chat_room_name = message.split(" ")[1]

                # Join the chat room
                self.join_chat_room(username, chat_room_name)

            # Check if the user wants to join a chat room
            elif message.startswith('/create'):

                # Get the chat room name
                chat_room_name = message.split(" ")[1]

                # Join the chat room
                self.create_chat_room(username, chat_room_name)

            # Check if the user wants to leave a chat room
            elif message.startswith('/leave'):

                chat_room_name = self.users_chat_room[username]

                # Find the chat room
                for chat_room in self.chat_rooms:
                    if chat_room.name == chat_room_name:
                        self.leave_chat_room(username, chat_room)

            elif message.startswith('/logout'):
                chat_room_name = self.users_chat_room[username]

                # Find the chat room
                for chat_room in self.chat_rooms:
                    if chat_room.name == chat_room_name:
                        self.leave_chat_room(username, chat_room)

                # Remove the user from the active users
                self.active_users.pop(username)

                # Send a message to the client
                self.connection.send(
                    "[System]: Logged out successfully!".encode())

                # Close the self.connection
                self.connection.close()
                return -1

            else:
                if (self.users_chat_room[username] == None):
                    self.connection.send(
                        "[System]: You are not in any chat room.".encode())

                else:
                    # Get the chat room name
                    chat_room_name = self.users_chat_room[username]

                    # Find the chat room
                    for chat_room in self.chat_rooms:
                        if chat_room.name == chat_room_name:

                            # Send the message to the chat room
                            chat_room.send_message(
                                message.encode(), self.active_users)

    def handle_client(self):

        # Get username
        print("Handling Auth")
        username = self.handleAuth()

        # Send list of chat rooms to the client
        chat_room_list = [chat_room.name for chat_room in self.chat_rooms]
        self.connection.send(
            f"[System]: Chat rooms: {chat_room_list}".encode())
        print("Chat rooms: ", chat_room_list)

        # Handle the user
        print("Handling user")
        x = self.handle_user(username)
        if (x == -1):
            # self.connection.close()
            return -1

    def run(self):
        print("Connection from : ", self.address)
        while True:
            if (self.handle_client() == -1):
                break
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
        newthread = ClientThread(clientAddress, clientsock)
        newthread.start()
