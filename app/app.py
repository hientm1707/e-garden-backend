import json
import yaml
import requests
with open("app/db.yaml", "r") as ymlfile:
    configuration = yaml.load(ymlfile,Loader=yaml.FullLoader)
from Adafruit_IO import MQTTClient, Client, RequestError
import login as login
from flask import Flask, flash, request, session,jsonify,make_response
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

'''Setups'''
app = Flask(__name__)
app.secret_key ="Secret Key"
app.config['SQLALCHEMY_DATABASE_URI'] = configuration['mysql_uri']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

# a = requests.get(url ='http://dadn.esp32thanhdanh.link/')
# ADAFRUIT_IO_KEYBBC  = a.json().get("keyBBC")
# ADAFRUIT_IO_KEYBBC1  = a.json().get("keyBBC1")
# ADAFRUIT_IO_USERNAME = 'CSE_BBC'
# ADAFRUIT_IO_USERNAME1 = 'CSE_BBC1'
ADAFRUIT_IO_USERNAME = 'trminhhien17'
ADAFRUIT_IO_KEYBBC = 'aio_Phfr33tNoyth68Tg6gWsVJXNkVbA'


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
def register():
    if request.method == 'POST':
        data = request.get_json()
        uname = data['username']
        pword = data['password']
        account = User.query.filter_by(username = uname, password =pword).first()
        if account:
            flash("Account already existed")
            response = make_response(
                jsonify(
                    {"status": "false","msg": "Account already existed"}
                ),
                200,
            )
        else:
            my_user = User(uname,pword)
            db.session.add(my_user)
            db.session.commit()
            response = make_response(
                jsonify(
                    {"status": "true"}
                ),
                200,
            )
        response.headers["Content-Type"] = "application/json"
        return response



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
            response = make_response(
                jsonify(
                    {"status": "true"}
                ),
                200,
            )
        else:
            response = make_response(
                jsonify(
                    {"status": "false", "msg": "Incorrect username/password"}
                ),
                200,
            )
        response.headers["Content-Type"] = "application/json"
        return response

@app.route('/api/account/logout')
def logout():
    session.pop('id',None)
    session.pop('username',None)
    session.pop('loggedin',None)
    response = make_response(
        jsonify(
            {"status": "true"}
        ),
        200
    )
    response.headers["Content-Type"] = "application/json"
    return response

@app.route('/api/account/minhhientran/add',methods=['POST'])
def subscribeToFeed():
    if request.method =='POST':
        data = request.get_json()
        topic_id = data['topic_id']




@app.route('/api/account/<username>/<feed_id>/data', methods = ['GET'])
def getSevenNearestValue(username,feed_id):
    restClient = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEYBBC)
    try:
        temperature = restClient.feeds(feed_id)
    except RequestError:
            response = make_response(
                jsonify(
                    {"status": "false", "msg": "No feed available on username"}
                ),
                404
            )
            response.headers["Content-Type"] = "application/json"
            return response
    listCreatedAt = [x.created_at for x in restClient.data('co2')[-7:]]
    listValue= [x.value for x in restClient.data('co2')[-7:]]
    if not listValue:
        responseObj = {"status":"false","msg": "Feed has no data yet"}
        trueResponse = make_response(
            jsonify(
                responseObj
            ),
            404
        )
    else:
        listOfDicts = []
        for i in range(len(listCreatedAt)):
            dict = {}
            dict['create_at'] = listCreatedAt[i]
            dict['value'] = listValue[i]
            listOfDicts.append(dict)
        reponseObj = {"data":listOfDicts, "status":"true"}

        trueResponse = make_response(
            jsonify(
                reponseObj
            ),
            200
        )
    trueResponse.headers["Content-Type"] = "application/json"
    return trueResponse

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
    app.run(threaded=True, port=5000)#debug=True)
    ##
