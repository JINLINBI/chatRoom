import socket,select
import time,hashlib,random,sys,struct,os
import redis,pymysql
import redis
import signal
red="\033[0;31m"
green="\033[0;32m"
none="\033[0m"
def handler(signal_num,frame):
    print("service stopping!")
    sys.exit(signal_num)
signal.signal(signal.SIGINT,handler)
class Table_ctrl():
    def __init__(self,tablename):
        self.tablename=tablename
        self.connect_db()
    def connect_db(self):
        try:
            self.conn=pymysql.connect(user="jin",password="123456",database="CHATROOM",charset="utf8")
        except:
            os.system("service mysql start")
            self.conn=pymysql.connect(user="jin",password="123456",database="CHATROOM",charset="utf8")
        finally:
            self.cur=self.conn.cursor()
    def get_timeId(self):
        now=time.time()
        intnow=int(now)
        ms=int((now-intnow)*1000)
        timeId=time.strftime("%y%m%d%H%M%S",time.localtime(time.time()))+str(ms)
        return timeId
    def write_db(self,*data):
        sql="INSERT INTO "+str(self.tablename)+" VALUES('"+self.get_timeId()+"'"
        for i in range(len(data)):
            if type(data[i])==type("string"):
                sql+=",'"+data[i]+"'"
            else:
                sql+=","+str(data[i])
        sql+=")"
        try:
            self.cur.execute(sql.encode('utf-8'))
            self.conn.commit()
        except Exception as e:
            print("writting  database error:%s"%e)
    def checkExist(self,column,value):
        Exist=False
        if type(value)==type("string"):
            sql="select * from "+str(self.tablename)+" where "+str(column)+"='"+str(value)+"'"
        else:
            sql="select * from "+str(self.tablename)+" where "+str(column)+"="+str(value)
        try:
            self.cur.execute(sql)
            if self.cur.fetchone():
                    Exist=True
        except:
            print("check value Error!")
        return Exist
    def query_db(self,kColumn,kValue,queryField):
        if type(kValue)==type("string"):
            sql="select %s from %s where %s='%s'"%(queryField,self.tablename,kColumn,kValue)
        else:
            sql="select %s from %s where %s=%s"%(queryField,self.tablename,kColumn,kValue)
        print(sql)
        try:
            self.cur.execute(sql)
            return self.cur.fetchone()[0]
        except:
            print("query Error!")
    def __del__(self):
        self.conn.close()
class Login(Table_ctrl):
    def __init__(self,username,password):
        Table_ctrl.__init__(self,"USER")
        self.username=username
        self.password=password
    def login(self):
        sha1=hashlib.sha1()
        sha1.update(self.password.encode('utf-8'))
        self.password=sha1.hexdigest()
        return self.isLegal(self.username,self.password)
    def isLegal(self,username,password):
        sql="SELECT * FROM USER WHERE USERNAME='{0}' AND PASSWORD='{1}'".format(username,password)
        print(sql)
        self.cur.execute(sql)
        result=self.cur.fetchone()
        if result:
            self.niname=result[3]
            return True
        else:
            return False
class Register(Table_ctrl):
    def __init__(self,username,password,niname):
        Table_ctrl.__init__(self,"USER")
        self.username=username
        self.password=password
        self.niname=niname
        self.age=0
        self.sex='N'
        self.picId='NULL'
    def register(self):
        sha1=hashlib.sha1()
        sha1.update(self.password.encode('utf-8'))
        self.password=sha1.hexdigest()
        return self.isLegal()
    def isLegal(self):
        if self.checkExist("USERNAME",self.username) or  self.checkExist("NINAME",self.niname):
           return False
        self.write_db(self.username,self.password,self.niname,self.age,self.sex,self.picId)
        return True
def offline(sock):
    if online.get(sock):
        del online[sock]
    if online_niname.get(sock):
        broadcast_data(sock,"system:broadcast\nlogout:[%s] is offline."%online_niname[sock])
        print(green+"[%s] is offline" % online_niname[sock]+none)
        del online_niname[sock]
    print(red+"Client (%s,%s) disconnected." % sock.getpeername()+none)
    sock.close()
    CONNECTION_LIST.remove(sock)
def broadcast_data (sock, message):
    global online
    for socket in CONNECTION_LIST:
        if socket != server_socket and socket != sock and socket!=sys.stdin and online.get(socket):
            try :
                if message:
                    message+="\n"
                    socket.send(message.encode())
            except Exception as e:
                print("Error:%s"%e)
                socket.close()
                CONNECTION_LIST.remove(socket)
def parse_data(socket,data):
    global online
    global online_niname
    global CONNECTION_LIST
    try:
        mes=data.split(":")[0]
        if mes=="data":
            if not  online.get(socket):
                return "system:data\nfailed:loginFirst"
        elif mes=="register":
            datalist=data.split(",")
            username=datalist[1].split(":")[1]
            password=datalist[2].split(":")[1]
            niname=datalist[3].split(":")[1]
            register_user=Register(username,password,niname)
            if register_user.register():
                return "system:register\nsuccess:"+niname
            else:
                return "system:register\nfailed:user or niname exist"
        elif mes=="login":
            if online.get(socket):
                return "system:login\nfailed:login repeat"
            datalist = data.split(",")
            username=datalist[1].split(":")[1]
            password=datalist[2].split(":")[1]
            login_user=Login(username,password)
            if login_user.login():
                print("login successfully!")
                tc=Table_ctrl("USER")
                niname=tc.query_db("USERNAME",username,"NINAME")
                online[sock]=True
                if not  niname:
                    niname="NULL"
                online_niname[sock]=niname
                broadcast_data(sock,"system:broadcast\nlogin:[%s]entered room" %online_niname[sock])
                return "system:login\nsuccess:%s"%niname
            else:
                del login_user
                return "system:login\nfailed:user not exist!"
        elif mes=="update":
            if not  online.get(socket):
                return "system:update\nfailed:loginFirst"
            print("update!")
        elif mes=="query":
            if not  online.get(socket):
                return "system:query\nfailed:loginFirst"
            sentence=""
            for i in CONNECTION_LIST:
                if online_niname.get(i):
                    sentence+=","+online_niname.get(i)
            return "system:query\nsuccess:"+sentence
        elif mes=="message":
            if not  online.get(socket):
                return "system:message\nfailed:loginFirst"
            broadcast_data(sock,"system:broadcast\n{0}:{1}".format(online_niname[sock],data.partition(":")[2]))
            print("{0}:{1}".format(online_niname[sock],data.partition(":")[2]))
            dataLength=len(data.partition(":")[2])
            return "system:message\nsuccess:%s"%dataLength
        elif mes=="logout":
            if online.get(sock):
                return "system:logout\nFailed:you did not login"
            broadcast_data(sock,"system:broadcast\nlogout:{0} left the room.".format(online_niname[sock]))
            now=time.strftime("%y-%m-%d",time.localtime(time.time()))
            logout_flag=True
            return "system:logout\nsuccess:"+now
        else:
            return "system:unknown"
    except Exception as e:
        print(" parse data Error:%s"%e)
        return "system:unknown"
if __name__ == "__main__":
    CONNECTION_LIST = [sys.stdin]
    RECV_BUFFER = 4096 
    PORT = 5000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)
    online={}
    online_niname={}
    CONNECTION_LIST.append(server_socket)
    print(green+"Chat server started on port "+none + str(PORT))
    running=True
    while running:
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
        for sock in read_sockets:
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                message=green+"Client (%s, %s) connected\t" % addr+none
                print(message)
                tc=Table_ctrl("RECORD")
                tc.write_db(message)
            elif sock==sys.stdin:
                junk=sys.stdin.readline()
                if junk=="exit":
                    running=False
                else:
                    broadcast_data(sock,"testing\n")
            else:
                try:
                    data = sock.recv(RECV_BUFFER)
                    logout_flag=False
                    if data:
                        redata=parse_data(sock,data.decode().rstrip())+"\n"
                        sock.send(redata.encode())
                        if  logout_flag:
                            offline(sock)
                    else:
                        offline(sock)
                except Exception as e:
                        offline(sock)
    server_socket.close()
def service(conn,addr):
    while True:
        data=conn.recv(1024).decode().rstrip()
        if data:
            parse_data(data)
        else:
            offline(conn)
