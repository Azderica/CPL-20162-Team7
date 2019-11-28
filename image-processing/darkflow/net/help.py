"""
tfnet secondary (helper) methods
"""
from ..utils.loader import create_loader
from time import time as timer
import tensorflow as tf
import numpy as np
import sys
import cv2
import os

stringData_original = bytes(10)
stringData_grayscale = bytes(10)
stringData_colorized = bytes(10)
stringData_yolo = bytes(10)

old_graph_msg = 'Resolving old graph def {} (no guarantee)'

def build_train_op(self):
    self.framework.loss(self.out)
    self.say('Building {} train op'.format(self.meta['model']))
    optimizer = self._TRAINER[self.FLAGS.trainer](self.FLAGS.lr)
    gradients = optimizer.compute_gradients(self.framework.loss)
    self.train_op = optimizer.apply_gradients(gradients)

def load_from_ckpt(self):
    if self.FLAGS.load < 0: # load lastest ckpt
        with open(os.path.join(self.FLAGS.backup, 'checkpoint'), 'r') as f:
            last = f.readlines()[-1].strip()
            load_point = last.split(' ')[1]
            load_point = load_point.split('"')[1]
            load_point = load_point.split('-')[-1]
            self.FLAGS.load = int(load_point)
    
    load_point = os.path.join(self.FLAGS.backup, self.meta['name'])
    load_point = '{}-{}'.format(load_point, self.FLAGS.load)
    self.say('Loading from {}'.format(load_point))
    try: self.saver.restore(self.sess, load_point)
    except: load_old_graph(self, load_point)

def say(self, *msgs):
    if not self.FLAGS.verbalise:
        return
    msgs = list(msgs)
    for msg in msgs:
        if msg is None: continue
        print(msg)

def load_old_graph(self, ckpt): 
    ckpt_loader = create_loader(ckpt)
    self.say(old_graph_msg.format(ckpt))
    
    for var in tf.global_variables():
        name = var.name.split(':')[0]
        args = [name, var.get_shape()]
        val = ckpt_loader(args)
        assert val is not None, \
        'Cannot find and load {}'.format(var.name)
        shp = val.shape
        plh = tf.placeholder(tf.float32, shp)
        op = tf.assign(var, plh)
        self.sess.run(op, {plh: val})

def _get_fps(self, frame):
    elapsed = int()
    start = timer()
    preprocessed = self.framework.preprocess(frame)
    feed_dict = {self.inp: [preprocessed]}
    net_out = self.sess.run(self.out, feed_dict)[0]
    processed = self.framework.postprocess(net_out, frame, False)
    return timer() - start

def rapi(self):

    print('###you intered RAPI FUNCTION ###')
    from flask import Flask, render_template, Response
    from threading import Thread
    import socket


    app = Flask(__name__, template_folder='C://Project')

###GAN 변수들
    import imutils
    args = {"prototxt":"model/colorization_deploy_v2.prototxt",  "model":"model/colorization_release_v2.caffemodel", "points":"model/pts_in_hull.npy", "width":500}    
    print("[INFO] loading GAN model...")
    net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
    pts = np.load(args["points"])

    class8 = net.getLayerId("class8_ab")
    conv8 = net.getLayerId("conv8_313_rh")

    pts = pts.transpose().reshape(2, 313, 1, 1)
    net.getLayer(class8).blobs = [pts.astype("float32")]
    net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]
###
    
########웹서버
    def my_thread(val):
        def recvall(sock, count):
            # 바이트 문자열
            buf = b''
            while count:
                newbuf = sock.recv(count)
                if not newbuf: return None
                buf += newbuf
                count -= len(newbuf)
            return buf

        HOST=''
        PORT=8068

        #TCP 사용
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print('Socket created')

        s.bind((HOST,PORT))
        print('Socket bind complete')
        s.listen(10)
        print('Socket now listening')

        conn, addr=s.accept()
        print('New Client')
        global stringData_original
        global stringData_grayscale
        global stringData_colorized
        global stringData_yolo

        elapsed = int()

        buffer_inp = list()
        buffer_pre = list()

        file=0

        start = timer()
        self.say('Press [ESC] to quit RAPI')

        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        is_FIRST=True

        while True:
            elapsed += 1
            length = recvall(conn, 16)
            stringData = recvall(conn, int(length))
            data = np.fromstring(stringData, dtype = 'uint8')
    
            frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
            #print('frame1', type(frame))
#### 머신러닝 부분
            frame = imutils.resize(frame, width=args["width"])
            scaled = frame.astype("float32") / 255.0
            lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)

            # resize the Lab frame to 224x224 (the dimensions the colorization
            # network accepts), split channels, extract the 'L' channel, and
            # then perform mean centering
            resized = cv2.resize(lab, (224, 224))
            L = cv2.split(resized)[0]
            L -= 50

            # pass the L channel through the network which will *predict* the
            # 'a' and 'b' channel values
            net.setInput(cv2.dnn.blobFromImage(L))
            ab = net.forward()[0, :, :, :].transpose((1, 2, 0))

            # resize the predicted 'ab' volume to the same dimensions as our
            # input frame, then grab the 'L' channel from the *original* input
            # frame (not the resized one) and concatenate the original 'L'
            # channel with the predicted 'ab' channels
            ab = cv2.resize(ab, (frame.shape[1], frame.shape[0]))
            L = cv2.split(lab)[0]
            colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)

            # convert the output frame from the Lab color space to RGB, clip
            # any values that fall outside the range [0, 1], and then convert
            # to an 8-bit unsigned integer ([0, 255] range)
            colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
            colorized = np.clip(colorized, 0, 1)
            colorized = (255 * colorized).astype("uint8")

### 영상 저장하는 부분
            if is_FIRST:
                is_FIRST=False
                fourcc = cv2.VideoWriter_fourcc('D', 'I', 'V', 'X')
                height, width, _ = frame.shape
                print(width, height)
                videoWriter_1 = cv2.VideoWriter('video_1.avi', fourcc, 30.0, (width, height))
                videoWriter_2 = cv2.VideoWriter('video_2.avi', fourcc, 30.0, (width, height), 0)
                videoWriter_3 = cv2.VideoWriter('video_3.avi', fourcc, 30.0, (width, height))
                videoWriter_4 = cv2.VideoWriter('video_4.avi', fourcc, 30.0, (width, height))

            videoWriter_3.write(colorized)
###

            #print('frame2', type(colorized))

            result, colorized_data = cv2.imencode('.jpg', colorized, encode_param)
            colorized_data = np.array(colorized_data)
            colorized_data = colorized_data .tostring()
            #print('frame3', type(colorized_data))

            stringData_colorized = colorized_data 
            #cv2.imshow("Colorized", colorized_backup) #ndarray, (375, 500, 3)
            # show the original and final colorized frames

    ########
            preprocessed = self.framework.preprocess(colorized)
            buffer_inp.append(colorized)
            buffer_pre.append(preprocessed)

            # Only process and imshow when queue is full
            if elapsed % self.FLAGS.queue == 0:
                feed_dict = {self.inp: buffer_pre}
                net_out = self.sess.run(self.out, feed_dict)
                for img, single_out in zip(buffer_inp, net_out):
                    postprocessed = self.framework.postprocess(
                        single_out, img, False)

                    if file == 0: #camera window

                        print('now')
                        result, colorized_data = cv2.imencode('.jpg', frame, encode_param)
                        original_data = np.array(colorized_data )
                        original_data = original_data.tostring()
                        stringData_original = original_data

                        result, grayscale_data  = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), encode_param)
                        grayscale_data = np.array(grayscale_data  )
                        grayscale_data = grayscale_data .tostring()
                        stringData_grayscale = grayscale_data 

                        result, yolo_data  = cv2.imencode('.jpg', postprocessed, encode_param)
                        yolo_data = np.array(yolo_data)
                        yolo_data = yolo_data .tostring()
                        stringData_yolo = yolo_data 

                        #cv2.imshow("Original", frame)
                        #cv2.imshow("Grayscale", cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
                        #cv2.imshow("Colorized", colorized_backup) #ndarray, (375, 500, 3)
                        #cv2.imshow('Yolo', postprocessed)
###영상 저장하는 부분.
                        videoWriter_1.write(frame)
                        videoWriter_2.write(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
                        #videoWriter_3.write(colorized_backup)
                        videoWriter_4.write(postprocessed)
###
                        #print(self.framework.get_json_box())

                # Clear Buffers
                buffer_inp = list()
                buffer_pre = list()

            if elapsed % 5 == 0:
                sys.stdout.write('\r')
                sys.stdout.write('{0:3.3f} FPS'.format(
                    elapsed / (timer() - start)))
                sys.stdout.flush()
            if file == 0: #camera window
                choice = cv2.waitKey(1)
                if choice == 27: break

            key = cv2.waitKey(1) & 0xFF

            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
### 저장 세팅
                videoWriter_1.release()
                videoWriter_2.release()
                videoWriter_3.release()
                videoWriter_4.release()
###
                break


####

    t1 = Thread(target = my_thread, args=(1,))
    t1.setDaemon(True)
    t1.start()


    @app.route('/')
    def index():
        """Video streaming home page."""
        temp_box = self.framework.get_json_box()
        temp_str = ""

        for one_box in temp_box:
            temp_str+= str(one_box)
        return render_template('index.html')

    @app.route('/box')
    def box():
        temp_box = self.framework.get_json_box()
        temp_str = "["
        #for one_box_key in temp_box.keys():
        #    temp_str+= temp_box(one_box_key)

#objData=temp_str
        for one_box in temp_box:
            temp_str+= str(one_box)
            temp_str+=", "

        temp_str = temp_str[0:-2]

        temp_str+="]"
        print(temp_str)
        return render_template('box.html', objData = temp_str)

    @app.route('/box2')
    def box2():
        temp_box = self.framework.get_json_box()
        return str(temp_box)

    def gen_original():
        """Video streaming generator function."""
        global stringData_original
        while True:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + stringData_original + b'\r\n')

    def gen_grayscale():
        """Video streaming generator function."""
        global stringData_grayscale
        while True:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + stringData_grayscale + b'\r\n')

    def gen_colorized():
        """Video streaming generator function."""
        global stringData_colorized
        while True:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + stringData_colorized + b'\r\n')

    def gen_yolo():
        """Video streaming generator function."""
        global stringData_yolo
        while True:
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + stringData_yolo + b'\r\n')

    # open('C://Project/t.jpg', 'rb').read()

    @app.route('/video_feed_original')
    def video_feed_original():
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(gen_original(),mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/video_feed_grayscale')
    def video_feed_grayscale():
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(gen_grayscale(),mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/video_feed_colorized')
    def video_feed_colorized():
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(gen_colorized(),mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/video_feed_yolo')
    def video_feed_yolo():
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(gen_yolo(),mimetype='multipart/x-mixed-replace; boundary=frame')



    app.run(host='0.0.0.0')


###

def camera(self):
### gan추가되는 설정들
    import imutils
    args = {"prototxt":"model/colorization_deploy_v2.prototxt",  "model":"model/colorization_release_v2.caffemodel", "points":"model/pts_in_hull.npy", "width":500}    
    print("[INFO] loading GAN model...")
    net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])
    pts = np.load(args["points"])

    class8 = net.getLayerId("class8_ab")
    conv8 = net.getLayerId("conv8_313_rh")

    pts = pts.transpose().reshape(2, 313, 1, 1)
    net.getLayer(class8).blobs = [pts.astype("float32")]
    net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]
###
    file = self.FLAGS.demo
    SaveVideo = self.FLAGS.saveVideo
    
    if file == 'camera':
        file = 0
    else:
        assert os.path.isfile(file), \
        'file {} does not exist'.format(file)
        
    camera = cv2.VideoCapture(file)

    if file == 0:
        self.say('Press [ESC] to quit demo')
        
    assert camera.isOpened(), \
    'Cannot capture source'
    
    if file == 0:#camera window
        cv2.namedWindow('', 0)
        _, frame = camera.read()
        height, width, _ = frame.shape
        cv2.resizeWindow('', width, height)
    else:
        _, frame = camera.read()
        height, width, _ = frame.shape

    if SaveVideo:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        if file == 0:#camera window
          fps = 1 / self._get_fps(frame)
          if fps < 1:
            fps = 1
        else:
            fps = round(camera.get(cv2.CAP_PROP_FPS))
        videoWriter = cv2.VideoWriter(
            'video.avi', fourcc, fps, (width, height))

    # buffers for demo in batch
    buffer_inp = list()
    buffer_pre = list()
    
    elapsed = int()
    start = timer()
    # Loop through frames
    while camera.isOpened():
        elapsed += 1
        _, frame = camera.read()
        if frame is None:
            print ('\nEnd of Video')
            break

### frame읽고 여기부터
        frame = imutils.resize(frame, width=args["width"])
        scaled = frame.astype("float32") / 255.0
        lab = cv2.cvtColor(scaled, cv2.COLOR_BGR2LAB)

        # resize the Lab frame to 224x224 (the dimensions the colorization
        # network accepts), split channels, extract the 'L' channel, and
        # then perform mean centering
        resized = cv2.resize(lab, (224, 224))
        L = cv2.split(resized)[0]
        L -= 50

        # pass the L channel through the network which will *predict* the
        # 'a' and 'b' channel values
        net.setInput(cv2.dnn.blobFromImage(L))
        ab = net.forward()[0, :, :, :].transpose((1, 2, 0))

        # resize the predicted 'ab' volume to the same dimensions as our
        # input frame, then grab the 'L' channel from the *original* input
        # frame (not the resized one) and concatenate the original 'L'
        # channel with the predicted 'ab' channels
        ab = cv2.resize(ab, (frame.shape[1], frame.shape[0]))
        L = cv2.split(lab)[0]
        colorized = np.concatenate((L[:, :, np.newaxis], ab), axis=2)

        # convert the output frame from the Lab color space to RGB, clip
        # any values that fall outside the range [0, 1], and then convert
        # to an 8-bit unsigned integer ([0, 255] range)
        colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
        colorized = np.clip(colorized, 0, 1)
        colorized = (255 * colorized).astype("uint8")
        colorized_backup = colorized 
        cv2.imshow("Colorized", colorized_backup) #ndarray, (375, 500, 3)
        # show the original and final colorized frames


########
        preprocessed = self.framework.preprocess(colorized)
        buffer_inp.append(colorized)
        buffer_pre.append(preprocessed)
        
        # Only process and imshow when queue is full
        if elapsed % self.FLAGS.queue == 0:
            feed_dict = {self.inp: buffer_pre}
            net_out = self.sess.run(self.out, feed_dict)
            for img, single_out in zip(buffer_inp, net_out):
                postprocessed = self.framework.postprocess(
                    single_out, img, False)
                if SaveVideo:
                    videoWriter.write(postprocessed)
                if file == 0: #camera window
                    cv2.imshow("Original", frame)
                    cv2.imshow("Grayscale", cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
                    #cv2.imshow("Colorized", colorized_backup) #ndarray, (375, 500, 3)
                    cv2.imshow('Yolo', postprocessed)
            # Clear Buffers
            buffer_inp = list()
            buffer_pre = list()

        if elapsed % 5 == 0:
            sys.stdout.write('\r')
            sys.stdout.write('{0:3.3f} FPS'.format(
                elapsed / (timer() - start)))
            sys.stdout.flush()
        if file == 0: #camera window
            choice = cv2.waitKey(1)
            if choice == 27: break

        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    sys.stdout.write('\n')
    if SaveVideo:
        videoWriter.release()
    camera.release()
    if file == 0: #camera window
        cv2.destroyAllWindows()


def to_darknet(self):
    darknet_ckpt = self.darknet

    with self.graph.as_default() as g:
        for var in tf.global_variables():
            name = var.name.split(':')[0]
            var_name = name.split('-')
            l_idx = int(var_name[0])
            w_sig = var_name[1].split('/')[-1]
            l = darknet_ckpt.layers[l_idx]
            l.w[w_sig] = var.eval(self.sess)

    for layer in darknet_ckpt.layers:
        for ph in layer.h:
            layer.h[ph] = None

    return darknet_ckpt