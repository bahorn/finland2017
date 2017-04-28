import json
import redis
import time

import os

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO
from flask_socketio import send, emit

import text

app = Flask(__name__)

# read the config
config = open('config.json', 'r')
json_details = json.load(config)
key = json_details['secret_key']
user_details = json_details['user']
config.close()

app.config['SECRET_KEY'] = key
app.secret_key = key
socketio = SocketIO(app)

@app.route("/", methods=['GET','POST'])
def index():
    # check if logged in
    if request.method == 'POST':
        if ('username' in request.form) and ('password' in request.form['password']):
            username = request.form['username']
            password = request.form['password']
            # connect to the redis instance to lookup the username
            if username == user_details['username'] and password == user_details['password']:
                session['username'] = username
        else:
            print('lol')
        return redirect(url_for('index'))
    else:
        loggedin = False
        title = "Login"
        if 'username' in session:
            title = "Management Panel"
            loggedin = True

        return render_template('index.html',title=title,
                loggedin=loggedin)

@app.route("/photo", methods=["GET"])
def photo():
    try:
        r = redis.Redis('127.0.0.1')
        photo = r.get("camera:photo")
        return photo, 200, {'Content-Type': 'image/jpeg'}
    except:
        return "AAA"

@app.route("/logout", methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route("/message", methods=['POST'])
def message():
    if 'username' in session:
        text.dispMessage(request.form['message'])
    return redirect(url_for('index'))

@app.route("/getcropped", methods=['GET'])
def getcropped():
    r = redis.Redis('127.0.0.1')
    try:
        a = r.get("cropped:%s" % request.args.get('id'))
        return a, 200, {'Content-Type': 'image/jpeg'}
    except:
        return '', 404

@app.route("/settings", methods=['POST'])
def settings():
    if 'username' in session:
        if 'email' in request.form:
            r = redis.Redis('127.0.0.1')
            r.set('settings:email',request.form['email'])
    return redirect(url_for('index'))           

@socketio.on('connect')
def connected():
    print("connected")

@socketio.on('new')
def new(message):
    emit('photos', {"date":message['date'], "faces":message['faces']}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
