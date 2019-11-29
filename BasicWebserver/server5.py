from threading import Thread
import threading
import socket
import cv2
import numpy as np
from flask import Flask, render_template, Response

lock = threading.Lock()
HOST = ''
PORT = 3000
global size;
users = []
flag = 0;
stringData=b'';
k=0;
next = False;
app = Flask(__name__,template_folder="D://ras");
def recvall(sock,count):
    buf =b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def ras_receive(conn): 
    print("Socket accepting ras")
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    while True:
        length = recvall(conn,16) #길이정보
        #print("length :" ,length)
        #print("length :",int(length))
        #print("length : ",length)
        global stringData;
        stringData = recvall(conn,int(length)) #길이만큼 버퍼 정보 받아오기
        #print("stringData : ",stringData);
        data = np.fromstring(stringData, dtype='uint8')
        frame = cv2.imdecode(data,cv2.IMREAD_COLOR)
    

        #if size > 0: # 안드로이드로 데이터 보내기(소켓)
        #    #print("stringData : " , stringData);
        #    for i in range(len(users)):
        #        users[i].sendall((str(len(stringData))).encode().ljust(16)+stringData)
        #        #users[i].sendall((str(len(stringData))).encode().ljust(16))

        cv2.imshow('ImageWindow',frame)
        cv2.waitKey(1)
        #cv2.imwrite('./images/person.jpg',frame)
        #global next;
        #next=True;
        #print("next :",next)

def socket_start():
    flag = 1;
    size = 0;
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print('Socket created')
    s.bind((HOST,PORT))
    print('Socket bind complete')
    s.listen(10)
    print('Socket now listening')

    while True:
        print("before access")
        conn,addr = s.accept()
        print("access success")
        if flag == 1:
            t1 =Thread(target = ras_receive, args=(conn,)) #라즈베리로 부터 데이터 받기
            t1.start()
            flag = 0
        else:
            print("flag =0");
            lock.acquire()
            users.append(conn)
            lock.release();
            size=size+1
            data = conn.recv(1024)
            msg = data.decode("utf").strip();
            print("android recieved : "+msg)

            
s_t = Thread(target = socket_start, args=())
s_t.setDaemon(True);
s_t.start();

@app.route('/')
def index():
    return render_template('index.html');
        

def gen():
    while True:
        global stringData;
        #print("gen next : ",next);
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + stringData + b'\r\n')
        #print('yield');
        
@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    print("webView")
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')

app.run('192.168.43.14');
#app.run();
#내부아이피 쓰면 와이파이마다 다르지만 대체적으로 느리고 스트리밍이 거의안된다.
#룩백주소 쓰면 빠르다.
#안드로이드 웹뷰에서 돌아가는지 확인하기.
