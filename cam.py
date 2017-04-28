import redis
import io
import time
import picamera
import datetime
import cv2
import hashlib

import lolmail

from wand.image import Image
from socketIO_client import SocketIO

def maybeemail():
    r = redis.Redis('127.0.0.1')
    address = r.get("settings:email")
    if r.get("emailcooldown") == None:
        lolmail.sendemail(address, "Person at your door!", '/tmp/blahblah.jpeg')
        r.set("emailcooldown", 1)
        r.expire("emailcooldown", 10*60)

def getTimestamp():
    then = datetime.datetime.now()
    return time.mktime(then.timetuple())*1e3 + then.microsecond/1e3

def main():
    stream = io.BytesIO()
    camera = picamera.PiCamera()
    camera.resolution = (240,160)
    cascade = cv2.CascadeClassifier('./face.xml')

    socketio = SocketIO('127.0.0.1', 5000)
    r = redis.Redis('127.0.0.1')
    r.set("lastcount", 0)
    while True:
        timestamp = getTimestamp()
        print("Taking a picture")
        camera.capture(stream, 'jpeg')
        r.set('camera:photo', stream.getvalue())
        f = open('/tmp/blahblah.jpeg', 'wb')
        f.write(stream.getvalue())
        f.close()
        image = cv2.imread('/tmp/blahblah.jpeg')
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(
            grayscale,
            scaleFactor=1.2,
            minNeighbors=2,
            minSize=(30, 30),
            flags = cv2.cv.CV_HAAR_SCALE_IMAGE
        )
        list_of_keys = []
        print(faces)
        if len(faces) >= 1:
            if len(faces) > int(r.get("lastcount")):
                k = r.get("lastupdated")
                print k
                if k == None:
                    with Image(filename="/tmp/blahblah.jpeg") as img:
                        img.format = 'jpeg'
                        for i in faces:
                            with img[i[0]:i[0]+i[2], i[1]:i[1]+i[3]] as chunk:
                                key = hashlib.sha256(chunk.make_blob()).hexdigest()
                                r.set("cropped:%s" % key, chunk.make_blob())
                                list_of_keys.append(key)
                                maybeemail()
                    r.set("lastupdated", 1)
                    r.expire("lastupdated", 10)
        socketio.emit('new', {'date':timestamp, 'faces':list_of_keys})
        stream = io.BytesIO()
        time.sleep(0.1)

if __name__ == "__main__":
    main()
