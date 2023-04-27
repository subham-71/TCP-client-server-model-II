import socket
import threading
import time

SERVER = "127.0.0.1"
PORT = 8080

token = ""


class Client:
    def __init__(self, client_socket):

        self.client_socket = client_socket
        self.username = ""
        self.chat_messages = ""
        self.chatroom = ''
        self.line_no = 0

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

        if server_message == "[SYSTEM] :Login successful!":
            self.username = username
            print("\n"+server_message+"\n")
            return 1
        else:
            print("\n"+server_message+"\n")
            return -1

    def signup(self):
        self.client_socket.send("signup".encode())

        # Get the username from the user
        username = input('Enter username: ')
        self.client_socket.send(username.encode())

        # Get server message
        server_message = self.client_socket.recv(1024).decode()
        if (server_message == "[SYSTEM] :Username already exists!"):
            print("\n"+server_message+"\n")
            return -1
        else:
            # Get the password from the user
            password = input('Enter password: ')
            self.client_socket.send(password.encode())

            server_message = self.client_socket.recv(1024).decode()
            if (server_message == "[USER] :User registered successfully!"):
                self.username = username
                print("\n"+server_message+"\n")
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
        with open(self.chat_room_name+'.txt') as f:
            for i,line  in enumerate(f):
                if i > self.line_no:
                    print(line)
                    self.line_no = i

    def send_message(self):
        print(f"{self.username}: ")

        user_input = input()
        if (user_input == "/leave "):
            self.client_socket.send(user_input.encode())
            return -1

        elif (user_input == "/logout "):
            self.client_socket.send(user_input.encode())
            return -1

        else:
            self.client_socket.send(user_input.encode())
            server_message = self.client_socket.recv(1024).decode()
            if (server_message == "[SYSTEM]: You are not in any chat room."):
                print("\n"+server_message+"\n")
                return -1
            else:
                print("\n"+server_message+"\n")
                return 1

    def handleChat(self):
        
        user_input = input("Enter 1 to send a message :  2 to receive messages: ")
        if (user_input == "1"):
            return self.send_message()
        elif (user_input == "2"):
            self.receive_messages()
            return 1

    def handleChatRoom(self):
        while (1):
            # Rules
            print("=================================== \nWelcome to the Chat Room. Press \n1. Join a chat room \n2. Create a chat room \n3. Logout \n===================================")

            # Receive list of active chat rooms from server
            active_chat_rooms_users = self.client_socket.recv(1024).decode()

            # Print the list of active chat rooms
            print("\n"+active_chat_rooms_users+"\n")

            # Get the user input
            user_input = input("Enter Choice : ")

            # Join a chat room
            if (user_input == "1"):

                self.chat_room_name = input("Enter chat room name: ")
                chat_room_name_message = "/join " + self.chat_room_name
                self.client_socket.send(chat_room_name_message.encode())

                server_message = self.client_socket.recv(1024).decode()
                if (server_message == f"[SYSTEM]: Chat room {self.chat_room_name} does not exist."):
                    print( server_message )
                    self.client_socket.send("NO_INPUT 8f9e1d6c5b4a32".encode())
                    continue
                else:
          
                    print("\n"+server_message+"\n")
                    print("=================================== \nWelcome to the Chat Room. Press \n1. to send a message \n2. to receive messages \n =========================== \n While sending messages, You have the following commands \n  1. /leave : to leave the chatroom \n  2. /logout : to logout and exit \n===================================\n\n")

                    while (1):

                        x = self.handleChat()
                        if (x == -1):
                            break

            # Create a chat room
            elif (user_input == "2"):

                self.chat_room_name = input("Enter chat room name: ")
                chat_room_name_message = "/create " + self.chat_room_name
                self.client_socket.send(chat_room_name_message.encode())

                server_message = self.client_socket.recv(1024).decode()
                print("\n"+server_message+"\n")
                if (server_message == f"[SYSTEM]: Chat room {self.chat_room_name} does not exist."):
                    print("\n"+server_message+"\n")
                    self.client_socket.send("NO_INPUT 8f9e1d6c5b4a32".encode())
                    continue
                else:
                    
                    print("\n"+server_message+"\n")
                
                    print("\n\n=================================== \nWelcome to the Chat Room. Press \n1. to send a message \n2. to receive messages \n =========================== \n While sending messages, You have the following commands \n  1. /leave : to leave the chatroom \n  2. /logout : to logout and exit \n===================================\n\n")
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
                self.client_socket.send("NO_INPUT 8f9e1d6c5b4a32".encode())
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
