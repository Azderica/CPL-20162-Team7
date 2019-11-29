import cv2
import socket
import numpy as np
## using TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
## server ip, port
s.connect(('220.66.214.12', 3000))
## webcam image capture
cam = cv2.VideoCapture(0)
print('camera on')
## img property... 3 = width, 4 = height
cam.set(3, 400)
cam.set(4, 400)
## img quality 0~100... default = 95
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
while True:
    # read frames one by one
    # if succeed, ret = True, fali ret = False, 'frame' is red frame
    ret, frame = cam.read()
    print('camera reading')
    # cv2.imencode(ext, img [, params])
    # encode the frame to jpg 'encode_param's format
    result, frame = cv2.imencode('.jpg', frame, encode_param)
    # change the frame to String type
    data = np.array(frame)
    stringData = data.tostring()
    # transfer data to Server
    #(str(len(stringData))).encode().ljust(16)
    s.sendall((str(len(stringData))).encode().ljust(16) + stringData)#utf-8 encode
   # print(len(str(len(stringData)).encode.ljust(16)))
    print("send_buffer_len" , (str(len(stringData))).encode().ljust(16))
    print("stringData length :" ,len(stringData))
cam.release()

