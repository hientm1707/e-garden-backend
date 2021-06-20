# ----------------------Base setup-----------------------
import json

from Adafruit_IO import Client, RequestError
from flask import Flask, jsonify, request, session, make_response
import yaml
from mqtt_setup import *
from passlib.hash import pbkdf2_sha256
import uuid
from flask_socketio import SocketIO
import sys
with open("db.yaml", "r") as ymlfile:
    configuration = yaml.load(ymlfile, Loader=yaml.FullLoader)
from pymongo import MongoClient
import ssl
context = ssl.create_default_context()
app = Flask(__name__)
app.secret_key = "Secret Key"
mgClient = MongoClient(configuration['mongoRemote'])
db = mgClient.get_database('DoAnDaNganh')
socketio = SocketIO(app, cors_allowed_origins="*", engineio_logger=True, logger=True )
# --------------------------------------GlabalData------------------------
global_ctx = {'temp_rate': 40, 'humidity_rate': 65}
global_data = {}
#---------------------------------------FEEDS--------------------------------
LED_FEED = 'bk-iot-led'
SOIL_FEED = 'bk-iot-soil'
LIGHT_FEED = 'bk-iot-light'
LCD_FEED = 'bk-iot-lcd'
RELAY_FEED = 'bk-iot-relay'
DHT11_FEED = 'bk-iot-temp-humid'
feed_pub =[LED_FEED, LCD_FEED, RELAY_FEED]
feeds_of_client = [[LED_FEED,SOIL_FEED,LCD_FEED,DHT11_FEED],[LIGHT_FEED,RELAY_FEED]]
ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0 = 'trminhhien17', 'aio_Phfr33tNoyth68Tg6gWsVJXNkVbA'
ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1 = 'trminhhien17', 'aio_Phfr33tNoyth68Tg6gWsVJXNkVbA'

#----------------------------------------SEND EMAIL --------------------------------------------------------------------
from smtp import *
SENDER_USERNAME = configuration['sender_username']
SENDER_PASSWORD = configuration['sender_password']
RECEIVER = 'minhhien1772000@gmail.com'
#--------------------------------------Function for MQTT-----------------------------------------------------------------------

def connected(client):
    [client.subscribe(x) for x in feeds_of_client[0]] if client is User.mqttClient0 else [client.subscribe(x) for x in feeds_of_client[1]]

def disconnected(client):
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    print('Feed {0} received new value: {1}'.format(feed_id, payload))
    socketio.emit('message',payload)
    socketio.emit('server-send-mqtt',payload)
    payloadDict = json.loads(payload)
    if feed_id == DHT11_FEED:
        temp, humid = payloadDict['data'].split('-')
        if int(temp) >= global_ctx['temp_rate']:
            sendEmail(SENDER_USERNAME, SENDER_PASSWORD, RECEIVER, msg='ALERT!\n\n Your garden temperature is too high!!!!')
        if int(humid) <= global_ctx['humidity_rate']:
            sendEmail(SENDER_USERNAME, SENDER_PASSWORD, RECEIVER, msg='ALERT!\n\n Your garden humidity is too low!!!!!!')
    global global_data
    try:
        global_data[feed_id] += [payloadDict]  # json to dict
    except KeyError:
        global_data[feed_id] = [payloadDict]  # json to dict

def get_mqtt(feed_id):
    global global_data
    value = None
    try:
        value = global_data[feed_id]
    except KeyError:
        value = None
    itemDict = {}
    if feed_id == 'bk-iot-temp-humid':
        if value:
            value = value[-1]  # last dict
            temp, humid = value['data'].split('-')
            return json.dumps({"id": feed_id, "value": {"temp": temp, "humid": humid}})
        else:  # if value is None
            return json.dumps({"id": feed_id,"value": {"temp": None,"humid": None}})
    else:
        return json.dumps({"id": feed_id, "value": value[-1]['data'] if value else None})

def wake_up_MQTT(client):
    client.on_connect = connected
    client.on_disconnect = disconnected
    client.on_message = message
    client.connect()
    client.loop_background()
# --------------------------------------------User-------------------------------------------------

class User:
    #Static objects
    mqttClient0 = None
    mqttClient1 = None
    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        User.mqttClient0 = MQTTClient(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
        User.mqttClient1 = MQTTClient(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)
        wake_up_MQTT(User.mqttClient0);
        wake_up_MQTT(User.mqttClient1);
        return jsonify({"status": "true"}), 200

    def signup(self):
        # Create the user object
        user = {
            "_id": uuid.uuid4().hex,
            "username": request.get_json()['username'],
            "password": request.get_json()['password'],
        }

        # Encrypt the password
        user['password'] = pbkdf2_sha256.encrypt(user['password'])

        # Check for existing email address
        if db.User.find_one({"username": user['username']}):
            return jsonify({"error": "Username already in use"}), 400

        if db.User.insert_one(user):
            return self.start_session(user)

        return jsonify({"error": "Signup failed"}), 400

    def signout(self):
        if session:
            session.clear()
            User.mqttClient0.disconnect()
            User.mqttClient1.disconnect()
            User.mqttClient0 = None
            User.mqttClient1 = None
        else:
            return jsonify({"error": "Not logged in"})

        return jsonify({"status": "true"}), 200

    def login(self):
        user = db.User.find_one({
            "username": request.get_json()['username']
        })
        if user and pbkdf2_sha256.verify(request.get_json()['password'], user['password']):
            return self.start_session(user)

        return jsonify({"error": "Invalid Username or password"}), 400

    @staticmethod
    def publishToFeed(feed_id):
        data_for_RELAY = {"id": "11", "name": "RELAY", "data": "X", "unit": ""}
        data_for_LED = {"id": "1", "name": "LED", "data": "X", "unit": ""}
        data_for_LCD = {"id": "3", "name": "LCD", "data": "X", "unit": ""}
        if feed_id not in feed_pub:
            return jsonify({"error": "You cannot publish to this feed"}), 400
        dataToPublish = None
        if 'logged_in' in session and session['logged_in'] is True:
            value = request.get_json()['value']
            if feed_id == LED_FEED:
                if (not isinstance(value,int)) or (value not in range(3)):
                    return jsonify({"error":"Invalid input"}),400
                else:
                    data_for_LED['data']= str(value)
                    dataToPublish = data_for_LED
            elif feed_id == LCD_FEED:
                if (not isinstance(value,str)) or (len(value) > 12):
                    return jsonify({"error": "Invalid input"}), 400
                else:
                    data_for_LCD['data'] = value
                    dataToPublish = data_for_LCD
            else: #Relay:
                if (not isinstance(value,int)) or (value not in range(2)):
                    return jsonify({"error": "Invalid input"}), 400
                else:
                    data_for_RELAY['data'] = str(value)
                    dataToPublish = data_for_LCD

            if feed_id in feeds_of_client[0]:
                User.mqttClient0.publish(feed_id, json.dumps(dataToPublish))
            else:
                User.mqttClient1.publish(feed_id, json.dumps(dataToPublish))
            return jsonify({"status": "true", "msg": "Published {0} to feed {1}".format(value, feed_id)}), 200
        return jsonify({"error": "Not authenticated "}), 400

    @staticmethod
    def subscribeFeed(feed_id):
        if 'logged_in' in session and session['logged_in'] is True:
            realClient = User.mqttClient0 if feed_id in feeds_of_client[0] else User.mqttClient1
            realClient.subscribe(feed_id)
            return jsonify({"status": "true", "msg": "Feed {0} subscribed successfully".format(feed_id)}), 200
        return jsonify({"error": "Not authorized"}), 400

    @staticmethod
    def unsubscribeFeed(feed_id):
        if 'logged_in' in session and session['logged_in'] is True:
            realClient = User.mqttClient0 if feed_id in feeds_of_client[0] else User.mqttClient1
            realClient.unsubscribe(feed_id)
            return jsonify({"status": "true", "msg": "Feed {0} unsubscribed successfully".format(feed_id)}), 200
        return jsonify({"error": "Not authorized"}), 400
#----------------------------------------ROUTES------------------------------------------------
@app.route('/', methods=['GET'])
def homepage():
    return '<p> ok </p>'

@app.route('/api/account/register', methods=['POST'])
def register():
    return User().signup()

@app.route('/api/account/', methods=['POST'])
def login():
    return User().login()

@app.route('/api/account/logout', methods=['POST'])
def logout():
    return User().signout()

@app.route('/api/account/unsubscribe/<feed_id>', methods=['GET'])
def unsubscribe(feed_id):
    return User.unsubscribeFeed(feed_id)

@app.route('/api/account/<feed_id>', methods=['POST'])
def publishToFeed(feed_id):
    return User.publishToFeed(feed_id)

@app.route('/api/account/subscribe/<feed_id>', methods=['GET'])
def subscribe(feed_id):
    return User.subscribeFeed(feed_id)

@app.route('/api/account/<feed_id>/data', methods=['GET'])
def getDataOfTopic(feed_id):
    restClient = Client(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0) if feed_id in feeds_of_client[0] else Client(ADAFRUIT_IO_USERNAME1,ADAFRUIT_IO_KEYBBC1)
    try:
        feed = restClient.feeds(feed_id)
    except RequestError:
        response = make_response(
            jsonify(
                {"status": "false", "msg": "No feed available on username"}
            ),
            400
        )
        response.headers["Content-Type"] = "application/json"
        return response
    data = json.loads(restClient.receive(feed.key)[3])['data']
    if feed.key != DHT11_FEED:
        return jsonify({"status": "true", "value": data}), 200
    else:
        temp,humid = data.split('-')
        return jsonify({"status":"true", "value":{"temp":temp,"humid":humid}}),200

@app.route('/api/account/<feed_id>/seven_data', methods=['GET'])
def getSevenNearestValue(feed_id):
    dict_data = []
    client1 = Client(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)
    client0 = Client(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
    if feed_id in feeds_of_client[1]:
        data = client1.data(feed_id)[:7] # list of 7 Data()
        if data:
            for i in data: # i : Data()
                try:
                    value = json.loads(i[3])['data']
                except TypeError: # if value == int not json
                    value = i[3]
                dict_data += [{
                    "created_at": i.created_at,
                    "value": value
                }]
            return_value = {"data": dict_data, "status":"true"}
            return jsonify(return_value),200
        else:
            return_value = {"data": None, "status":"False", "msg": "Feed has no data"}
            return jsonify(return_value),400

    elif feed_id in feeds_of_client[0]:
        data = client0.data(feed_id)[:7]
        if data:
            for i in data:
                try:
                    value = json.loads(i[3])['data']
                except TypeError:
                    value = i[3]
                if feed_id == 'bk-iot-temp-humid':
                    temp,humid = value.split('-')
                    value = { 'temp':temp, 'humid':humid}
                dict_data += [{
                    "created_at": i.created_at,
                    "value": value
                }]
            return_value = {"data": dict_data, "status":"true"}
            return jsonify(return_value),200
        else:
            return_value = {"data": None, "status":"false", "msg": "Feed has no data"}
            return jsonify(return_value),400
    else:
        return_value = {"data": None, "status":"false", "msg": "Feed not exist"}
        return jsonify(return_value),400

@app.route('/api/account/data', methods=['GET'])
def getAllSensorsLatestData():
    dict_data = []
    client1 = Client(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)
    client0 = Client(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
    for feed in feeds_of_client[1]:
        data = client1.receive(feed)[3]
        dict_data += [{
            "id": feed,
            "value": json.loads(data)['data'] if data is not None else None
        }]
    for feed in feeds_of_client[0]:
        data = client0.receive(feed)[3]
        value = json.loads(data)['data'] if data is not None else None
        if feed == 'bk-iot-temp-humid':
            if value:
                temp, humid = value.split('-')
                value = {'temp': temp, 'humid': humid}
        dict_data += [{
            "id": feed,
            "value": value
        }]
    return jsonify({"data": dict_data, "status": "true"}), 200

@app.route('/api/account/humidity_warning', methods=['GET', 'PUT'])
def modifyHumidityRate():
    if request.method == 'PUT':
        value = request.get_json()['value']
        if not value:
            return jsonify({"status": "false", "msg": "Invalid body format"}), 400
        if isinstance(value, int):
            global_ctx['humidity_rate'] = value
            return jsonify({"status": "true"}), 200
        return jsonify({"error": "Invalid input format"}), 400
    else:
        return jsonify({"rate": global_ctx['humidity_rate'], "status": "true"}), 200

@app.route('/api/account/temp_warning', methods=['GET', 'PUT'])
def modifyTempRate():
    if request.method == 'PUT':
        value = request.get_json()['value']
        if not value:
            return jsonify({"status": "false", "msg": "Invalid body format"}), 400
        if isinstance(value, int):
            global_ctx['temp_rate'] = value
            return jsonify({"status": "true"}), 200
        return jsonify({"error": "Invalid input format"}), 400
    else:
        return jsonify({"rate": global_ctx['temp_rate'], "status": "true"}), 200


# @socketio.on('bk-iot-led')
# def handle_client_listen_data(data=None):
#     socketio.emit('server-send-mqtt', get_mqtt('bk-iot-led'))
#
#
# @socketio.on('bk-iot-soil')
# def handle_client_listen_data(data=None):
#     socketio.emit('server-send-mqtt', get_mqtt('bk-iot-soil'))
#
#
# @socketio.on('bk-iot-light')
# def handle_client_listen_data(data=None):
#     socketio.emit('server-send-mqtt', get_mqtt('bk-iot-light'))
#
#
# @socketio.on('bk-iot-lcd')
# def handle_client_listen_data(data=None):
#     socketio.emit('server-send-mqtt', get_mqtt('bk-iot-lcd'))
#
#
# @socketio.on('bk-iot-relay')
# def handle_client_listen_data(data=None):
#     socketio.emit('server-send-mqtt', get_mqtt('bk-iot-relay'))
#
#
# @socketio.on('bk-iot-temp-humid')
# def handle_client_listen_data(data=None):
#     socketio.emit('server-send-mqtt', get_mqtt('bk-iot-temp-humid'))

if __name__ == "__main__":
    #app.run(debug=True)
    socketio.run(app,port = 413, debug=True)
    ##
