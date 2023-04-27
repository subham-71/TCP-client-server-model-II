import socket
import datetime

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

    def send_message(self, message,active_users):
        for user in self.users:
            self.active_users[user].send(message.encode())


class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostname()
        self.port_no = 8000
        self.connection = socket.socket()
        self.filename = "received_by_server.txt"
        self.users = {}
        self.chat_rooms = set()
        self.active_users = {}
        self.users_chat_room = {}

    def server_socket_init(self):
        self.server_socket.bind((self.host, self.port_no))

    def server_listen(self):
        self.server_socket.listen(2)
        print(
            f"\n \n =========================== \n Server listening on port {self.port_no} \n =========================== \n")
        self.connection, address = self.server_socket.accept()
        print("Connection from: ", str(address))

    def login(self):
        username = self.connection.recv(1024).decode()

        if username in self.users:
            password = self.connection.recv(1024).decode()
            if password == self.users[username]:
                return username
            else:
                self.connection.send('Incorrect password!'.encode())
        else:
            self.connection.send('User not registered!'.encode())

        return False

    def signup(self):

        username = self.connection.recv(1024).decode()

        if username in self.users:
            self.connection.send('User already registered!'.encode())
            return
        else:
            password = self.connection.recv(1024).decode()

            password = self.connection.recv(1024).decode()
            self.users[username] = password
            self.connection.send('User registered successfully!'.encode())
            return username

    def handleAuth(self):

        method = self.connection.recv(1024).decode()
        
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
                chat_room.send_message(chat_room_message.encode() ,self.active_users)

                # Send a message to the client
                self.connection.send(f"[System]: You have joined the chat room \"{chat_room_name}\"".encode())

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

                chat_room.send_message(chat_room_message.encode() ,self.active_users)

                # Send a message to the client
                self.connection.send(
                    f"[System]: You have created the chat room \"{chat_room_name}\" ".encode())

    def leave_chat_room(self, username, chat_room):

        # Remove the user from the chat room
        chat_room.remove_user(username)
        self.users_chat_room.pop(username)

        # Send a message to the chat room
        chat_room_message = f"[System][{datetime.datetime.now().strftime('%H:%M:%S')}]: {username} has left the chat room."
        chat_room.send_message(chat_room_message.encode(),self.active_users)

        # Send a message to the client
        self.connection.send(
            f"[System]: You have left the chat room \"{chat_room.name}\".".encode())

    def handle_user(self, username):

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

        else :
            # Get the chat room name
            chat_room_name = self.users_chat_room[username]

            # Find the chat room
            for chat_room in self.chat_rooms:
                if chat_room.name == chat_room_name:

                    # Send the message to the chat room
                    chat_room.send_message(message.encode(),self.active_users)

    def server_program(self):

        self.server_socket_init()
        self.server_listen()

        # Get username
        username = self.handleAuth()

        # Send list of chat rooms to the client
        self.connection.send(f"[System]: Chat rooms: {list(self.chat_rooms)}".encode())

        # Handle the user
        self.handle_user(username)

        self.connection.close()


if __name__ == '__main__':

    server = Server()
    server.receive_file()
