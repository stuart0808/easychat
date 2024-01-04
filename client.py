from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextBrowser
from PyQt5.QtCore import Qt, QDateTime, QObject, pyqtSignal, pyqtSlot, QThread
import socket

class ReceiveThread(QThread):
    messageReceived = pyqtSignal(str)

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket

    def run(self):
        while True:
            message = self.client_socket.recv(1024).decode()

            if message:
                self.messageReceived.emit(message)

class ClientWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Client Window")
        self.layout = QVBoxLayout()

        self.messageBrowser = QTextBrowser()
        self.layout.addWidget(self.messageBrowser)

        self.inputBox = QLineEdit()
        self.layout.addWidget(self.inputBox)

        self.sendBtn = QPushButton("Send")
        self.sendBtn.clicked.connect(self.sendMessage)
        self.sendBtn.setShortcut(Qt.Key_Return)
        self.sendBtn.setAutoDefault(True)
        self.layout.addWidget(self.sendBtn)

        self.setLayout(self.layout)

        # 连接服务端
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(("localhost", 8888))

        # 启动消息接收线程
        self.receiveThread = ReceiveThread(self.client_socket)
        self.receiveThread.messageReceived.connect(self.handleMessageReceived)
        self.receiveThread.start()

    def sendMessage(self):
        message = self.inputBox.text()
        self.inputBox.clear()

        # 发送消息给服务端
        self.client_socket.sendall(message.encode())

        # 在消息浏览器中显示自己发送的消息
        timestamp = QDateTime.currentDateTime().toString(Qt.DefaultLocaleShortDate)
        self.messageBrowser.append(f"[{timestamp}] (Me): {message}")

    def handleMessageReceived(self, message):
        # 在消息浏览器中显示接收到的消息
        timestamp = QDateTime.currentDateTime().toString(Qt.DefaultLocaleShortDate)
        self.messageBrowser.append(f"[{timestamp}] : {message}")

    def closeEvent(self, event):
        super().closeEvent(event)
        self.client_socket.close()

app = QApplication([])
client_window = ClientWindow()
client_window.show()
app.exec_()