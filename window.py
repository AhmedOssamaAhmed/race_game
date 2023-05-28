from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import networking

chat = None

class Message(QWidget):
    def __init__(self,msg,isMine, parent=None):
        QWidget.__init__(self, parent)
        layout = QHBoxLayout()
        if isMine:
            layout.addStretch(1)
        label = QLabel(msg)
        label.setStyleSheet(""" 
            padding:20px;
            border-radius:20px;
            background-color:#a331fb;
            color:#fff; 
        """)
        layout.addWidget(label)
        if not isMine:
            layout.addStretch(1)
        self.setLayout(layout)


class LiveChat(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        layout = QVBoxLayout()
        messages = QWidget()
        self.messagesLayout = QVBoxLayout()
        messages.setLayout(self.messagesLayout)
        layout.addWidget(messages)
        layout.addStretch(1)

        bottomBar = QWidget()
        bottomLayout = QHBoxLayout()
        self.chatText = QLineEdit()
        sendBtn = QPushButton()
        sendBtn.setText("Send")
        sendBtn.clicked.connect(self.sendMessage)
        bottomLayout.addWidget(self.chatText)
        bottomLayout.addWidget(sendBtn)
        bottomBar.setLayout(bottomLayout)

        layout.addWidget(bottomBar)
        self.setLayout(layout)
        self.resize(1080, 720)
        self.setWindowTitle("Live Chat")

        myWorker = NetworkWoker(self)
        myWorker.msg_signal.connect(self.onDataRecieved)
        myWorker.start()

        self.show()
    
    def sendMessage(self, event):
        msg = self.chatText.text()
        networking.send(msg)
        self.addMessage(msg, True)

    def onDataRecieved(self, indx):
        print(networking.recieve_buffer)
        self.addMessage(networking.recieve_buffer.pop(0), False)

    def addMessage(self, data, isMine):
        self.messagesLayout.addWidget(Message(data, isMine))

class NetworkWoker(QThread):
    msg_signal = pyqtSignal(int)

    def __init__(self,  parent=None):
        QThread.__init__(self, parent)
        self.currSize = 0

    def run(self):
        while True:
            if len(networking.recieve_buffer) != self.currSize and len(networking.recieve_buffer) > 0:
                print(networking.recieve_buffer, " from emit")
                self.msg_signal.emit(0)
                self.currSize = len(networking.recieve_buffer)
            elif len(networking.recieve_buffer) != self.currSize and len(networking.recieve_buffer) == 0:
                self.currSize = 0


def main():
    global chat
    networking.start_threads()
    app = QApplication([])
    chat = LiveChat()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()