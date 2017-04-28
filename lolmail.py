#!/usr/bin/env python3
import picamera
import time
import smtplib
import random
import RPi.GPIO as GPIO
import json
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

serv_username = "<CHANGE_ME>"
password = "<CHANGE_ME>"
server = "<CHANGE_ME>"

basedir = "photos/"

def sendemail(to, title, file):
    msg = MIMEMultipart()
    msg['Subject'] = 'photo'
    msg['From'] = serv_username
    msg['To'] = to
    msg.preamble = "Photo"
    fp = open(file, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)
    s = smtplib.SMTP_SSL(server)
    s.login(serv_username, password)
    s.sendmail(serv_username, to, msg.as_string())
    s.quit()

def main():
    a = picamera.PiCamera()
    id = random.randint(0,2**32)
    file = "%s/%i.jpg" % (basedir, id)
    a.capture(file)
    sendemail(username, 'Photos', file)

if __name__ == "__main__":
    main()
