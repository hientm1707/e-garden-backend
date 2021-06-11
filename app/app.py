import json

import requests

from Adafruit_IO import MQTTClient, Client, RequestError
import login as login
from flask import Flask, flash, request, session
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

'''Setups'''
app = Flask(__name__)
app.secret_key ="Secret Key"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:minhhien37@localhost/crud"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

a = requests.get(url ='http://dadn.esp32thanhdanh.link/')
ADAFRUIT_IO_KEYBBC  = a.json().get("keyBBC")
ADAFRUIT_IO_KEYBBC1  = a.json().get("keyBBC1")
# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = 'CSE_BBC'
ADAFRUIT_IO_USERNAME1 = 'CSE_BBC1'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False,)
    password = db.Column(db.String(120), unique=True, nullable=False)

    def __init__(self,username,password):
        self.username = username
        self.password =password
    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/api/account/register', methods = ['POST'])
def createAccount():
    if request.method == 'POST':
        data = request.get_json()
        uname = data['username']
        pword = data['password']
        account = User.query.filter_by(username = uname, password =pword).first()
        if account:
            flash("Account already existed")
            return json.dumps('{"status": "false","msg": "Account already existed"}')
        my_user = User(uname,pword)
        db.session.add(my_user)
        db.session.commit()
        return json.dumps('{"status": "true"}')


@app.route('/api/account/',methods = ['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        uname = data['username']
        pword = data['password']
        account = User.query.filter_by(username=uname, password=pword).first()
        if account:
            # db.session.configure('loggedin',True)
            # db.session.configure('id', account['id'])
            # db.session.configure('username', account['username'])
            # db.session['loggedin'] = True;
            # db.session['id'] = account['id']
            # db.session['username'] =account['username']
            return json.dumps('{"status":"true"}')
        return json.dumps('{"status":"FAILED","msg":"Incorrect username/password')

@app.route('/api/account/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return json.dumps('{"status":"OK"}')

@app.route('/api/account/minhhientran/add',methods=['POST'])
def subscribeToFeed():
    if request.method =='POST':
        data = request.get_json()
        topic_id = data['topic_id']




# @app.route('/api/account/<username>/<feed_id>/data', methods = ['POST'])
# def getSevenNearestValue(username,feed_id):
#     restClient = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEYBBC)
#     try:
#         temperature = restClient.feeds(feed_id)
#     except RequestError:
#         return json.dumps('{"status":"false","msg":"Invalid feed_id"}')
#     listCreatedAt = [x.created_at for x in restClient.data('co2')[-7:]]
#     listValue= [x.value for x in restClient.data('co2')[-7:]]
#     listOfDicts = []
#     for i in range(7):
#         dict = {}
#         dict['create_at'] = listCreatedAt[i]
#         dict['value'] = listValue[i]
#         listOfDicts.append(dict)
#     object
#     return json.dumps(listOfDicts)



# @app.route('/index')
# def index():
#     # Check if user is loggedin
#     if 'loggedin' in session:
#         # User is loggedin show them the home page
#         return json.dumps('{"status":"true"}')
#     # User is not loggedin redirect to login page
#     return json.dumps('{"msg":"Not authenticated"}')
#
@socketio.on('incoming_message')
def handle_message(data):
    print('received message: ' + data)

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))
#

if __name__ == "__main__":
    app.run(debug=True)
    ##