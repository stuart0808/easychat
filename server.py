import socket
import threading
from PyQt5.QtCore import QDateTime, Qt

class Server:
    def __init__(self):
        self.clients = []
        self.running = True

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("localhost", 8888))
        self.server_socket.listen(5)

        print("Server started.")

        # 启动消息转发线程
        self.forwardThread = threading.Thread(target=self.forwardMessages)
        self.forwardThread.start()

        try:
            while self.running:
                client_socket, address = self.server_socket.accept()
                self.clients.append(client_socket)

                # 启动消息接收线程
                receive_thread = threading.Thread(target=self.receiveMessages, args=(client_socket,))
                receive_thread.start()

        except ConnectionError:
            print("Server stopped.")

    def receiveMessages(self, client_socket):
        try:
            while self.running:
                # 接收客户端消息
                message = client_socket.recv(1024).decode()

                if message:
                    timestamp = QDateTime.currentDateTime().toString(Qt.DefaultLocaleShortDate)
                    print(f"[{timestamp}] Received message:", message)

                    # 转发消息给除了发送者之外的客户端
                    for other_client in self.clients:
                        if other_client != client_socket:
                            other_client.sendall(message.encode())

        except ConnectionError:
            self.clients.remove(client_socket)
            client_socket.close()

    def forwardMessages(self):
        try:
            while self.running:
                message = input("Enter message to forward: ")

                for client_socket in self.clients:
                    # 转发消息给客户端
                    client_socket.sendall(message.encode())

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        self.server_socket.close()

server = Server()
