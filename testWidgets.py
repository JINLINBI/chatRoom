from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys,math

class myDial(QDial):
    def __init__(self,parent=None,w=50,h=50):
        QDial.__init__(self,parent)
        self.setFixedSize(w+2,h+2)
        self.w=w
        self.h=h

        self.body=w*5/50
        self.cp=(w/2+1,h/2+1)
        self.d=w/5
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.update)
        self.count=0
        self.timer.start(100)
    def setColor(self,qp,point):
        head,middle,little,tail=0,0,0,0
        head=point
        middle=head+1
        little=middle+1
        tail=little+1

        if point==9:
            tail=0
        elif point==10:
            little,tail=0,1
        elif point==11:
            middle,little,tail=0,1,2
        if self.count==head:
            qp.setPen(QPen(QColor("#686868"), self.body, Qt.SolidLine, Qt.RoundCap))
        elif self.count==middle:
            qp.setPen(QPen(QColor("#888888"), self.body, Qt.SolidLine, Qt.RoundCap))
        elif self.count==little:
            qp.setPen(QPen(QColor("#a8a8a8"), self.body, Qt.SolidLine, Qt.RoundCap))
        elif self.count==tail:
            qp.setPen(QPen(QColor("#c8c8c8"), self.body, Qt.SolidLine, Qt.RoundCap))
        else:
            qp.setPen(QPen(QColor("#d8d8d8"), self.body, Qt.SolidLine, Qt.RoundCap))


    def paintEvent(self,e):
        qp=QPainter()
        qp.begin(self)
        qp.setPen(QPen(QColor("#a8a8a8"), self.body, Qt.SolidLine, Qt.RoundCap))
        qp.setBrush(QColor("#c8c8c8"))
        #qp.drawEllipse(QRectF(1, 1, self.w, self.h))
        
        #12点
        self.setColor(qp,0)
        qp.drawLine(self.cp[0], self.cp[1]-self.h*3/8, self.cp[0], self.cp[1]-self.h/4)

        self.setColor(qp,1)
        qp.drawLine(self.cp[0]+0.5*self.h*3/8, self.cp[1]-math.sqrt(3)*0.5*self.h*3/8, self.cp[0]+self.h/4*0.5, self.cp[1]-math.sqrt(3)*0.5*self.h/4)


        self.setColor(qp,2)
        qp.drawLine(math.sqrt(3)/2*(self.w*3/8)+self.cp[0], self.cp[1]-0.5*(self.w*3/8), math.sqrt(3)/2*(self.w/4)+self.cp[0],self.cp[1]-0.5*(self.w/4))

        #3点
        self.setColor(qp,3)
        qp.drawLine(self.cp[0]+self.w*3/8, self.cp[1], self.cp[0]+self.w/4, self.cp[1])



        self.setColor(qp,4)
        qp.drawLine(math.sqrt(3)/2*(self.w*3/8)+self.cp[0], self.cp[1]+0.5*(self.w*3/8), math.sqrt(3)/2*(self.w/4)+self.cp[0],self.cp[1]+0.5*(self.w/4))

        self.setColor(qp,5)
        qp.drawLine(self.cp[0]+0.5*self.h*3/8, self.cp[1]+math.sqrt(3)*0.5*self.h*3/8, self.cp[0]+self.h/4*0.5, self.cp[1]+math.sqrt(3)*0.5*self.h/4)

        #6点
        self.setColor(qp,6)
        qp.drawLine(self.cp[0], self.cp[1]+self.h*3/8, self.cp[0], self.cp[1]+self.h/4)


        self.setColor(qp,7)
        qp.drawLine(self.cp[0]-0.5*self.h*3/8, self.cp[1]+math.sqrt(3)*0.5*self.h*3/8, self.cp[0]-self.h/4*0.5, self.cp[1]+math.sqrt(3)*0.5*self.h/4)
        self.setColor(qp,8)
        qp.drawLine(self.cp[0]-math.sqrt(3)/2*(self.w*3/8), self.cp[1]+0.5*(self.w*3/8),self.cp[0]- math.sqrt(3)/2*(self.w/4),self.cp[1]+0.5*(self.w/4))

        #9点
        self.setColor(qp,9)
        qp.drawLine(self.cp[0]-self.w*3/8, self.cp[1], self.cp[0]-self.w/4, self.cp[1])

        self.setColor(qp,10)
        qp.drawLine(self.cp[0]-math.sqrt(3)/2*(self.w*3/8), self.cp[1]-0.5*(self.w*3/8),self.cp[0]- math.sqrt(3)/2*(self.w/4),self.cp[1]-0.5*(self.w/4))


        
        self.setColor(qp,11)
        qp.drawLine(self.cp[0]-0.5*self.h*3/8, self.cp[1]-math.sqrt(3)*0.5*self.h*3/8, self.cp[0]-self.h/4*0.5, self.cp[1]-math.sqrt(3)*0.5*self.h/4)
        qp.end()
        self.count+=1
        if self.count==12:
            self.count=0
            


class MyWidget(QMainWindow):
    def __init__(self):
        QWidget.__init__(self)
        spin=myDial(self)
        self.setCentralWidget(spin)

if __name__=="__main__":
    app=QApplication(sys.argv)
    myWidget=MyWidget()
    myWidget.show()
    app.exec_()
