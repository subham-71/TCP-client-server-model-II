import socket
import threading

SERVER = "127.0.0.1"
PORT = 8080


class Client:
    def __init__(self, client_socket):

        self.client_socket = client_socket
        self.username = ""

    def login(self):
        self.client_socket.send("login".encode())

        # Get the username from the user
        username = input('Enter username: ')
        self.client_socket.send(username.encode())

        # Get the password from the user
        password = input('Enter password: ')
        self.client_socket.send(password.encode())

        # Receive acknowledgement from the server
        server_message = self.client_socket.recv(1024).decode()

        if server_message == "Login successful!":
            self.username = username
            print("Login successful!")
            return 1
        else:
            print(server_message)
            return -1

    def signup(self):
        self.client_socket.send("signup".encode())

        # Get the username from the user
        username = input('Enter username: ')
        self.client_socket.send(username.encode())

        # Get server message
        server_message = self.client_socket.recv(1024).decode()
        if (server_message == "Username already exists!"):
            print("Username already exists!")
            return -1
        else:
            print("Username accepted!")
            # Get the password from the user
            password = input('Enter password: ')
            self.client_socket.send(password.encode())

            server_message = self.client_socket.recv(1024).decode()
            if (server_message == "User registered successfully!"):
                self.username = username
                print("User registered successfully!")
                return 1

    def handleAuth(self):
        # Login or Signup
        print("=================================== \nWelcome to the Chat Room. Press \n1. to Login or \n2. to Signup \n3. Exit \n===================================")

        choice = input("Enter your choice: ")

        if choice == "1":
            return self.login()

        elif choice == "2":
            return self.signup()

        elif choice == "3":
            self.client_socket.close()
            return 2
        else:
            print("Invalid choice")
            return -1

    def receive_messages(self):

        message = self.client_socket.recv(1024).decode()
        print(message)

    def send_message(self):

        print(f"{self.username}: ")
        user_input = input()
        if (user_input == "/leave"):
            self.client_socket.send(user_input.encode())
            return -1
        elif (user_input == "/logout"):
            self.client_socket.send(user_input.encode())
            return -1
        else:
            self.client_socket.send(user_input.encode())
            server_message = self.client_socket.recv(1024).decode()
            if (server_message == "[System]: You are not in any chat room."):
                print(server_message)
                return -1
            else:
                print(server_message)
                return 1

    def handleChat(self):

        # Multi-threading to send and receive messages
        receive_thread = threading.Thread(target=self.receive_messages)
        send_thread = threading.Thread(target=self.send_message)

        receive_thread.start()
        send_thread.start()

    def handleChatRoom(self):
        while (1):
            # Rules
            print("=================================== \nWelcome to the Chat Room. Press \n1. Join a chat room \n2. Create a chat room \n3. Logout \n======================= \n \n Once joined in a chatroom, you have the following commands : \n  1. /leave : to leave the chatroom \n   2. /logout : to logout and exit \n===================================")

            # Receive list of active chat rooms from server
            active_chat_rooms = self.client_socket.recv(1024).decode()

            # Print the list of active chat rooms
            print(active_chat_rooms)

            # Get the user input
            user_input = input()

            # Join a chat room
            if (user_input == "1"):

                chat_room_name = input("Enter chat room name: ")
                chat_room_name = "/join " + chat_room_name
                self.client_socket.send(chat_room_name.encode())

                server_message = self.client_socket.recv(1024).decode()
                print(server_message)
                if (server_message == f"[System]: Chat room {chat_room_name} does not exist."):
                    print(server_message)
                    continue
                else:
                    print(
                        "=============================================================")
                    print(server_message)
                    print(
                        "=============================================================")
                    while (1):
                        x = self.handleChat()
                        if (x == -1):
                            break

            # Create a chat room
            elif (user_input == "2"):

                chat_room_name = input("Enter chat room name: ")
                chat_room_name = "/create " + chat_room_name
                self.client_socket.send(chat_room_name.encode())

                server_message = self.client_socket.recv(1024).decode()
                if (server_message == f"[System]: Chat room {chat_room_name} does not exist."):
                    print(server_message)
                    continue
                else:
                    print(
                        "=============================================================")
                    print(server_message)
                    print(
                        "=============================================================")
                    while (1):
                        x = self.handleChat()
                        if (x == -1):
                            break

            # Logout
            elif (user_input == "3"):
                print("Logging out...")
                break

            else:
                print("Invalid choice")
                continue

    def client_program(self):

        while (1):

            x = self.handleAuth()

            if x == -1:
                continue
            elif x == 2:
                break
            else:
                self.handleChatRoom()

        self.client_socket.close()


if __name__ == '__main__':

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER, PORT))

    client = Client(client_socket)
    client.client_program()
