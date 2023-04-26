import socket
import time

class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostname()
        self.port_no = 8000
        self.connection = socket.socket()
        self.filename = "received_by_server.txt"

    def server_socket_init(self):
        self.server_socket.bind((self.host, self.port_no))

   
    def server_listen(self):
        self.server_socket.listen(2)
        print(f"\n \n =========================== \n Server listening on port {self.port_no} \n =========================== \n")
        self.connection, address = self.server_socket.accept()
        print("Connection from: ", str(address))

    def receive_filename(self):
        self.filename = self.connection.recv(1024).decode()
        print(f"Received filename: {self.filename} \n")
        self.filename = "received_by_server_"+ self.filename

    def receive_file(self):

        self.server_socket_init()
        self.server_listen()

        self.receive_filename()
        time.sleep(3)

        with open(self.filename, "wb") as f:
            while True:
                file_contents = self.connection.recv(1024)
                if not file_contents:
                    break
                f.write(file_contents)

        print("============================ \n File received from client \n ============================")
        self.connection.close()


if __name__ == '__main__':

    server = Server()
    server.receive_file()
