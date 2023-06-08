import socket
import time


class Client:
    def __init__(self, file_path):

        self.host = socket.gethostname()
        self.port_no = 8000
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file_path = file_path

    def client_socket_init(self):
        self.client_socket.connect((self.host, self.port_no))

    def send_filename(self):
        filename = self.file_path.split("/")[-1]
        self.client_socket.send(filename.encode())

    def send_file(self):

        self.client_socket_init()

        self.send_filename()

        time.sleep(3)

        with open(self.file_path, "rb") as f:
            file_contents = f.read()
            self.client_socket.send(file_contents)

        print("============================ \n File sent to server \n ============================")
        self.client_socket.close()


if __name__ == "__main__":

    path = input("Enter absolute path of file to be sent: ")
    client = Client(path)
    client.send_file()
