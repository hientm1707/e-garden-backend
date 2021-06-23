# ----------------------Base setup-----------------------
import json
from Adafruit_IO import MQTTClient
from flask import Flask, jsonify, request, session
import yaml
from passlib.hash import pbkdf2_sha256
import uuid
from flask_socketio import SocketIO
from username_and_key import *
import sys
import socketio as sio
with open("config/db.yaml", "r") as ymlfile:
    configuration = yaml.load(ymlfile, Loader=yaml.FullLoader)
from pymongo import MongoClient
from logger import logger
app = Flask(__name__)
app.secret_key = "Secret Key"
mgClient = MongoClient(configuration['mongoRemote'])
db = mgClient.get_database('DoAnDaNganh')
socketio = SocketIO(app, cors_allowed_origins="*", engineio_logger=True, logger=True)
socketioClient = sio.Client()
logger.info('Created socketio client')
socketioClient.connect('https://iotdudes-smart-garden.herokuapp.com')
logger.info('A user connected')
# --------------------------------------GlabalData------------------------
from globalData import *
#---------------------------------------FEEDS--------------------------------
from feeds import *
#----------------------------------------SEND EMAAIL --------------------------------------------------------------------
from smtp import *
SENDER_USERNAME = configuration['sender_username']
SENDER_PASSWORD = configuration['sender_password']
RECEIVERS = configuration['receivers']
#--------------------------------------Function for MQTT-----------------------------------------------------------------------

def connected(client):
    [client.subscribe(x) for x in feeds_of_client[0]] if client is User.mqttClient0 else [client.subscribe(x) for x in feeds_of_client[1]]

def disconnected(client):
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    print('Feed {0} received new value: {1}'.format(feed_id, payload))
    socketioClient.emit('server-send-mqtt', json.loads(payload))
    socketio.emit('server-send-mqtt', json.loads(payload))
    payloadDict = json.loads(payload)
    if feed_id == DHT11_FEED:
        temp, humid = payloadDict['data'].split('-')
        if int(temp) >= global_ctx['temp_rate']:
            SUBJECT = 'TEMPERATURE WARNING!'
            MESSAGE = 'Your garden is too hot!!!!\n\nPLEASE TAKE ACTION!!'
            [sendEmail(SENDER_USERNAME, SENDER_PASSWORD, RECEIVER, msg='Subject: {}\n\n{}'.format(SUBJECT, MESSAGE))
             for RECEIVER in RECEIVERS]
        if int(humid) <= global_ctx['humidity_rate']:
            SUBJECT = 'HUMIDITY WARNING!'
            MESSAGE = 'Your garden is too dry, it needs watering!!!!\n\nPLEASE TAKE ACTION!!'
            [sendEmail(SENDER_USERNAME, SENDER_PASSWORD, RECEIVER, msg='Subject: {}\n\n{}'.format(SUBJECT, MESSAGE))
             for RECEIVER in RECEIVERS]
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
    if feed_id == DHT11_FEED:
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
        User.mqttClient0.publish(LCD_FEED, json.dumps({"id": "3", "name": "LCD", "data": "HI! IOTDUDES", "unit": ""}))
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
        return jsonify({"error": "Not authenticated"}), 400

    @staticmethod
    def unsubscribeFeed(feed_id):
        if 'logged_in' in session and session['logged_in'] is True:
            realClient = User.mqttClient0 if feed_id in feeds_of_client[0] else User.mqttClient1
            realClient.unsubscribe(feed_id)
            return jsonify({"status": "true", "msg": "Feed {0} unsubscribed successfully".format(feed_id)}), 200
        return jsonify({"error": "Not authenticated"}), 400

#----------------------------------------ROUTES------------------------------------------------
from routes import *

@socketio.on('connect')
def handle_connected_user():
    logger.info("=======================================A user connected========================================")
    print("=======================================A user connected========================================")

@socketio.on('server-send-mqtt')
def handle_mqtt(message):
    socketio.emit('server-send-mqtt',message)
    logger.info("Emiting payload")

@socketioClient.on('connect')
def handle_connected_user():
    logger.info("==============================A user connected (SIO CLIENT)========================================")

@socketioClient.on('server-send-mqtt')
def handle_mqttClient(message):
    socketioClient.emit('server-send-mqtt',message)

if __name__ == "__main__":
    #app.run(debug=True)
    socketio.run(app,port = 413, debug=True)

