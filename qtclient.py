"""
聊天室客户端程序代码
"""
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
from PyQt5.QtGui import QFont,QColor,QPainter,QPolygonF,QIcon,QCursor
from math import *
from customWidget import BubbleText,MsgList

class LoginWindow(QMainWindow):
    """
    聊天室的登录窗口：
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #usernameLabel=QLabel("用户名：")
        #passwdLabel=QLabel("用户名：")
        #self.label=QTex
        self.label=QLabel("<h4 style='text-align:center'>544 ChatRoom</h4>")
        #self.label=BubbleText("<h4 style='text-align:center'>544 ChatRoom</h4>")
        #self.label=BubbleText()
        self.label.setDisabled(True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.username = QLineEdit()
        self.username.setPlaceholderText("username")
        self.password = QLineEdit()
        self.password.setPlaceholderText("password")
        self.password.setEchoMode(2)
        layout = QGridLayout()
        self.btnSend = QPushButton("login")
        self.btnQuit = QPushButton("quit")
        self.btnSend.pressed.connect(self.onBtnSend)
        self.btnQuit.pressed.connect(self.close)
        
        layout.addWidget(self.label, 0, 0, 1, 2)
        layout.addWidget(self.username, 1, 0, 2, 2)
        
        layout.addWidget(self.password, 3, 0, 2, 2)
        layout.addWidget(self.btnSend, 5, 0)
        layout.addWidget(self.btnQuit, 5, 1)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.btnSend.setStyleSheet("QPushButton:pressed{color:black;\
        background-color:rgb(210,255,240);}")
        self.btnQuit.setStyleSheet("QPushButton:pressed{color:black;\
        background-color:rgb(210,255,240);}")
        self.username.setStyleSheet("QLineEdit:focus{border:1px solid #aaaaf0}")
        self.password.setStyleSheet("QLineEdit:focus{border:1px solid #aaaaf0}")
        self.setStyleSheet("color:rgb(210,225,240);background-color:black")
        #self.resize(450,250)
        self.setFixedSize(320, 150)
        self.center()
        self.setWindowOpacity(0.95)

    def mousePressEvent(self, event):
        print(event.globalPos())
        self.windowPos=self.pos()
        self.mousePos=event.globalPos()
        self.dPos=self.mousePos-self.windowPos

    def mouseMoveEvent(self, event):
        print(event.globalPos())
        self.move(event.globalPos()-self.dPos)

    def center(self):
        """
        center the window
        """
        qr_ = self.frameGeometry()
        cp_ = QDesktopWidget().availableGeometry().center()
        qr_.moveCenter(cp_)
        self.move(qr_.topLeft())

    def onBtnSend(self):
        """
        触发
        """
        self.loginDialog = LoginDialog()
        self.loginDialog.connect()

    def keyPressEvent(self, QKeyEvent):
        """
        登录对话框的按键处理函数：按下回车键或者小键盘的enter键触发点击login按钮。
        """
        if QKeyEvent.key() == Qt.Key_Return or QKeyEvent.key() == Qt.Key_Enter:
            self.btnSend.animateClick()
        if QKeyEvent.key() == Qt.Key_Escape:
            self.btnQuit.animateClick()


class LoginDialog(QDialog):
    """
    登录对话框，调用不显示窗口，处理登录数据，成功则显示聊天室窗口，不成功则不显示聊天室窗口
    """
    close_signal = pyqtSignal()

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.sock = QTcpSocket()
        print("init successfully!")

    def connect(self):
        """
        socket连接函数
        """
        self.sock.connectToHost("localhost", 5000)
        #if not self.sock.isWritable():
        loginmessage = "login:1,username:" + loginWindow.username.text() + ",password:" + loginWindow.password.text()
        print(loginmessage)
        if  self.sock.isWritable():
            self.sock.write(loginmessage.encode())
            self.sock.readyRead.connect(self.slotreadyread)
        else:
            QMessageBox.warning(loginWindow, "Tips:", "Service Down", QMessageBox.Cancel)

    def slotreadyread(self):
        """
        收到服务器发来的数据处理
        """
        if self.sock.bytesAvailable() > 0:
            data = bytes(self.sock.readLine()).decode().rstrip()
            print("dialog recv"+data)
            try:
                head,junk,tail = data.partition(":")
            finally:
                print(data)
                print("invalid data!")
            if head == "system" and tail=="login":
                data = bytes(self.sock.readLine()).decode().rstrip()
                try:
                    head,junk,tail = data.partition(":")
                finally:
                    print(data)
                    print("invalid data!")
                if head=="success":
                    chatWindow.show()
                    chatWindow.getSocket(self.sock)
                    self.sock.readyRead.disconnect(self.slotreadyread)
                    del self.sock
                    loginWindow.close()
                    print("Login Successfully!")
                    self.close()
                else:
                    QMessageBox.warning(loginWindow,"Warning","Username or Password invalid!",QMessageBox.Cancel)
                    
                    
    def send(self, data, type_):
        """
        发送数据函数
        """
        if type_ == "data":
            pass
        elif type_ == "message":
            if self.sock.isWritable():
                self.sock.write(type_.encode()+":".encode()+data.encode())


class ChatWindow(QMainWindow):
    """
    聊天室主体窗口：有两个QTextBrowser控件，分别实现系统和用户聊天信息显示\
    ，一个QLineEdit控件用于获取用户输入，一个QPushButton控件用于处理用户发送消息
    """
    def __init__(self, *args, **kwargs):
        super(ChatWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("ChatRoom")
        self.view = QTextBrowser(self)
        self.chat = MsgList()
        self.content = QLineEdit()
        self.btnsend = QPushButton("send")
        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.view, 0, 0, 4, 3)
        layout.addWidget(self.chat, 0, 3, 3, 5)
        layout.addWidget(self.content, 3, 3, 1, 4)
        layout.addWidget(self.btnsend, 3, 7)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.center()
        self.setStyleSheet("ChatWindow{background-color:black}")
        self.setFixedSize(680, 480)
        self.content.setFocus(Qt.ActiveWindowFocusReason)
        
    def getSocket(self,socket):
        """从登录框中获取socket"""
        self.sock=socket
        self.sock.readyRead.connect(self.slotreadyread)
    def slotreadyread(self):
        """接受socket数据处理函数"""
        if self.sock.bytesAvailable() > 0:
            data = bytes(self.sock.readLine()).decode().rstrip()
            print("chat room recv:"+data)
            pass
            head,junk,tail = data.partition(":")
            if head=="system" and tail == "message":
                data = bytes(self.sock.readLine()).decode().rstrip()
                print("hello from "+data)
                head,junk,tail = data.partition(":")
                
            elif head=="system" and tail == "broadcast":
                data = bytes(self.sock.readLine()).decode().rstrip()
                print("hello from "+data)
                head,junk,tail = data.partition(":")
                if head in ("login","logout"):
                    self.view.append(data)
                else:
                    self.chat.addTextMsg(tail,True)
                print("head===%s"%head)

    def center(self):
        """"窗口中心化"""
        qr_ = self.frameGeometry()
        cp_ = QDesktopWidget().availableGeometry().center()
        qr_.moveCenter(cp_)
        self.move(qr_.topLeft())

    def handle_click(self):
        """
        处理点击事件函数
        """
        if not self.isVisible():
            self.show()
        else:
            QMessageBox.warning(self, "Tips:", "Service Down", QMessageBox.Cancel)
            self.close()

    def handle_close(self):
        """关闭函数："""
        self.close()

    def keyPressEvent(self, QKeyEvent):
        """按键处理函数："""
        if QKeyEvent.key() == Qt.Key_Return or QKeyEvent.key() == Qt.Key_Enter:
            if self.content.hasFocus():
                self.sock.write("message:".encode()+self.content.text().encode())
                buble=BubbleText(self.content.text(),False)
                data=self.content.text()
                self.content.clear()
                self.chat.addTextMsg(data,False)

    def closeEvent(self,e):
        self.sock.write("logout:1".encode())
        e.accept()

class TestWindow(QMainWindow):
    """
    测试用的窗口
    """
    def __init__(self, *args, **kwargs):
        super(TestWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("listWidget")
        listWidget=QListWidget()
        bubble=BubbleText("hello")
        item_=QListWidgetItem(bubble,"icon",listWidget)
        listWidget.insertItem(1,item_)
        layout=QHBoxLayout()
        layout.addWidget(listWidget) 
        widget=QWidget()      
        widget.setLayout(layout)
        self.setCentralWidget(widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loginWindow = LoginWindow()
    chatWindow = ChatWindow()

    #loginWindow.btnSend.clicked.connect(chatWindow.handle_click)
    #loginWindow.btnSend.clicked.connect(loginWindow.close)
    
    loginWindow.show()
    #test=TestWindow()
    #test.show()
    app.exec_()