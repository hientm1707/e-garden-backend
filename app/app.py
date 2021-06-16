# -----------------------FEED_ID------------------------

# ----------------------Base setup-----------------------
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
app = Flask(__name__)
app.secret_key = "Secret Key"
mgClient = MongoClient(configuration['mongoRemote'])
db = mgClient.get_database('DoAnDaNganh')
socketio = SocketIO(app, cors_allowed_origins="*")
# --------------------------------------GlabalData------------------------
context = {'temp_rate': 40, 'humidity_rate': 65}
global_data ={}
#---------------------------------------FEEDS--------------------------------
LED_FEED = 'bk-iot-led'
SOIL_FEED = 'bk-iot-soil'
LIGHT_FEED = 'bk-iot-light'
LCD_FEED = 'bk-iot-lcd'
RELAY_FEED = 'bk-iot-relay'
DHT11_FEED = 'bk-iot-temp-humid'


all_feed_ids = [LED_FEED,SOIL_FEED,LIGHT_FEED,LCD_FEED,RELAY_FEED,DHT11_FEED]
feed_pub =[LED_FEED, LCD_FEED, RELAY_FEED]

feeds_of_client = [[LED_FEED,SOIL_FEED,LCD_FEED,DHT11_FEED],[LIGHT_FEED,RELAY_FEED]]
ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0 = 'trminhhien17', 'aio_Phfr33tNoyth68Tg6gWsVJXNkVbA'
ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1 = 'trminhhien17', 'aio_Phfr33tNoyth68Tg6gWsVJXNkVbA'

# ------------------------------- MQTT Setups---------------------------------------------------------------
mqttClient0 = MQTTClient(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
mqttClient1 = MQTTClient(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)
mqttClientList = [mqttClient0,mqttClient1]
#--------------------------------Data prepare-------------------------------------------------------
data_for_DHT11 = {"id": "7", "name": "TEMP-HUMID", "data": "X", "unit": "*C-%"}
data_for_RTC = {"id": "22", "name": "TIME", "data": "x", "unit": ""}
# X = 0 tat , X = 1 mo
data_for_RELAY = {"id": "11", "name": "RELAY", "data": "X", "unit": ""}
# INPUT:  X<100 toi, X>100 sang
data_for_LIGHT = {"id": "13", "name": "LIGHT", "data": "X", "unit": ""}
# X = 0 – OFF, X = 1 – RED,X = 2 – BLUE
data_for_LED = {"id": "1", "name": "LED", "data": "1", "unit": ""}

#--------------------------------------Function for MQTT-----------------------------------------------------------------------
def wake_up_MQTT(client):
    client.on_connect = connected
    client.on_disconnect = disconnected
    client.on_message = message
    client.on_subscribe = subscribe
    client.connect()
    client.loop_background()

def connected(client):
    [client.subscribe(x) for x in feeds_of_client[0]] if client is mqttClient0 else [client.subscribe(x) for x in feeds_of_client[1]]

def subscribe(client, userdata, mid, granted_qos):
    print('Subscribed to  feed with QoS {0}'.format(granted_qos[0]))

def disconnected(client):
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    print('Feed {0} received new value: {1}'.format(feed_id, payload))
    global global_data
    try:
        global_data[feed_id] += [json.loads(payload)]  # json to dict
    except KeyError:
        global_data[feed_id] = [json.loads(payload)]  # json to dict
    print(global_data)

def get_mqtt(topic_name):
    global global_data
    value = None
    try:
        value = global_data[topic_name]
    except KeyError:
        value = None
    itemDict = {}
    if topic_name == 'bk-iot-temp-humid':
        if value:
            value = value[-1]  # last dict
            temp, humid = value['data'].split('-')
            return json.dumps({"id": topic_name, "value": {"temp": temp, "humid": humid}})
        else:  # if value is None
            return json.dumps({"id": topic_name,"value": {"temp": None,"humid": None}})
    else:
        return json.dumps({"id": topic_name, "value": value[-1]['data'] if value else None})

#-------------------------------------------------------------
# def publish_data(topic_id, param):
#     topic_index = {'bk-iot-led': "1", 'bk-iot-lcd': "3", 'bk-iot-relay': "11"}
#     return_status = {"status": "true"}
#     if topic_id in ['bk-iot-led', 'bk-iot-lcd']:
#         item_json = {
#             "id": topic_index[topic_id],
#             "name": topic_id[7:].upper(),
#             "data": param,
#             "unit": ""
#         }
#         mqttClient0.publish(topic_id, json.dumps(item_json))
#         print(f"Publishing {param} to {topic_id}")
#
#     elif topic_id in ['bk-iot-relay']:
#         item_json = {
#             "id": topic_index[topic_id],
#             "name": topic_id[7:].upper(),
#             "data": param,
#             "unit": ""
#         }
#         mqttClient1.publish(topic_id, json.dumps(item_json))
#         print(f"Publishing {param} to {topic_id}")
#
#     elif topic_id in topics_id:  # pub for sub too # just for testing
#         topic_index = {'bk-iot-soil': "9", "bk-iot-light": "13", 'bk-iot-temp-humid': "7"}
#
#         item_json = {
#             "id": topic_index[topic_id],
#             "name": topic_id[7:].upper(),
#             "data": param,
#             "unit": "*C-%" if 'temp' in topic_id else ""
#         }
#         mqttClient0.publish(topic_id, json.dumps(item_json))
#         print(f"Publishing {param} to {topic_id}")
#
#     else:
#         print('Feeds not exist')
#         return_status = {"status": "false", "msg": "Feeds not exist"}
#         # return json.dumps('{"status": "false"}')
#         response = make_response(
#             jsonify(return_status), 404
#         )
#         response.headers["Content-Type"] = "application/json"
#         return response
#
#     response = make_response(
#         jsonify(return_status), 200
#     )
#     response.headers["Content-Type"] = "application/json"
#     return response
    # return json.dumps('{"status": "true"}')

# --------------------------------------------User-------------------------------------------------

class User:
    session = {'logged_in': False, 'user': None}
    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        # Create an MQTT client instance.
        [wake_up_MQTT(client) for client in mqttClientList]
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
        session.clear()
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
        if 'logged_in' in session and session['logged_in'] == True:
            value = request.get_json()['value']
            if feed_id in feeds_of_client[0]:
                mqttClient0.publish(feed_id, value)
            else:
                mqttClient1.publish(feed_id,value)
            return jsonify({"status": "true","msg":"Published {0} to feed {1}".format(value,feed_id)})
        return jsonify({"error": "Not authorized in"}), 400

    @staticmethod
    def subscribeFeed(feed_id):
        if 'logged_in' in session and session['logged_in'] == True:
            realClient = mqttClient0 if feed_id in feeds_of_client[0] else mqttClient1
            realClient.subscribe(feed_id)
            return jsonify({"status": "true", "msg": "Feed {0} subscribed successfully".format(feed_id)}), 200
        return jsonify({"error": "Not authorized"}), 400

    @staticmethod
    def unsubscribeFeed(feed_id):
        if 'logged_in' in session and session['logged_in'] == True:
            realClient = mqttClient0 if feed_id in feeds_of_client[0] else mqttClient1
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

@app.route('/api/account/unsubscribe/<topic_id>', methods=['GET'])
def unsubscribe(topic_id):
    return User.unsubscribeFeed(topic_id)

@app.route('/api/account/<topic_id>', methods=['POST'])
def publishToFeed(topic_id):
    return User.publishToFeed(topic_id)

@app.route('/api/account/subscribe/<topic_id>', methods=['GET'])
def subscribe(topic_id):
    return User.subscribeFeed(topic_id)

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
            return jsonify(return_value),404

    elif feed_id in feeds_of_client[0]:
        data = client0.data(feed_id)[:7]
        if data:
            for i in data:
                print(i,type(i)) #
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
            return jsonify(return_value),404
    else:
        return_value = {"data": None, "status":"false", "msg": "Feed not exist"}
        return jsonify(return_value),404

@app.route('/api/account/data', methods=['GET'])
def getAllSensorsLatestData():
    dict_data = []
    client1 = Client(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)
    client0 = Client(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)

    for topic in feeds_of_client[1]:
        data = client1.receive(topic)[3]

        dict_data += [{
            "id": topic,
            "value": json.loads(data)['data'] if data is not None else None
        }]

    for topic in feeds_of_client[0]:
        data = client0.receive(topic)[3]
        value = json.loads(data)['data'] if data is not None else None
        if topic == 'bk-iot-temp-humid':
            if value:
                temp, humid = value.split('-')
                value = {'temp': temp, 'humid': humid}

        dict_data += [{
            "id": topic,
            "value": value
        }]
    return_value = {"data": dict_data, "status": "true"}
    return jsonify(return_value), 200

@app.route('/api/account/humidity_warning', methods=['GET', 'PUT'])
def modifyHumidityRate():
    if request.method == 'PUT':
        value = request.get_json()['value']
        if not value:
            return jsonify({"status": "false", "msg": "Invalid body format"}), 400
        if isinstance(value, int):
            context['humidity_rate'] = value
            return jsonify({"status": "true"}), 200
        return jsonify({"error": "Invalid input format"}), 400
    else:
        return jsonify({"rate": context['humidity_rate'], "status": "true"}), 200

@app.route('/api/account/temp_warning', methods=['GET', 'PUT'])
def modifyTempRate():
    if request.method == 'PUT':
        value = request.get_json()['value']
        if not value:
            return jsonify({"status": "false", "msg": "Invalid body format"}), 400
        if isinstance(value, int):
            context['temp_rate'] = value
            return jsonify({"status": "true"}), 200
        return jsonify({"error": "Invalid input format"}), 400
    else:
        return jsonify({"rate": context['temp_rate'], "status": "true"}), 200


@socketio.on('bk-iot-led')
def handle_client_listen_data(data=None):
    socketio.emit('server-send-mqtt', get_mqtt('bk-iot-led'))


@socketio.on('bk-iot-soil')
def handle_client_listen_data(data=None):
    socketio.emit('server-send-mqtt', get_mqtt('bk-iot-soil'))


@socketio.on('bk-iot-light')
def handle_client_listen_data(data=None):
    socketio.emit('server-send-mqtt', get_mqtt('bk-iot-light'))


@socketio.on('bk-iot-lcd')
def handle_client_listen_data(data=None):
    socketio.emit('server-send-mqtt', get_mqtt('bk-iot-lcd'))


@socketio.on('bk-iot-relay')
def handle_client_listen_data(data=None):
    socketio.emit('server-send-mqtt', get_mqtt('bk-iot-relay'))


@socketio.on('bk-iot-temp-humid')
def handle_client_listen_data(data=None):
    socketio.emit('server-send-mqtt', get_mqtt('bk-iot-temp-humid'))

if __name__ == "__main__":
    #app.run(debug=True)
    socketio.run(app, debug=True)
    ##
