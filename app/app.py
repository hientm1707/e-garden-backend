#-----------------------FEED_ID------------------------
class FEED_ID:
    LED_FEED = 'bk-iot-led'
    SOIL_FEED = 'bk-iot-soil'
    LIGHT_FEED = 'bk-iot-light'
    LCD_FEED = 'bk-iot-lcd'
    RELAY_FEED = 'bk-iot-relay'
    DHT11_FEED =  'bk-iot-temp-humid'
#----------------------Base setup-----------------------
from Adafruit_IO import Client, RequestError
from flask import Flask, request, jsonify, request, session, redirect, make_response
import yaml
from mqtt_setup import *
with open("db.yaml", "r") as ymlfile:
    configuration = yaml.load(ymlfile,Loader=yaml.FullLoader)
from pymongo import MongoClient
# -----------------------Warning rate------------------------
warningRates = {'temp_rate' : 40, 'humidity_rate': 65}

# --------------------- MQTT Setups--------------------------
import sys
ADAFRUIT_IO_USERNAME = 'trminhhien17'
ADAFRUIT_IO_KEYBBC = 'aio_Phfr33tNoyth68Tg6gWsVJXNkVbA'
# Set to the ID of the feed to subs
# cribe to for updates.

data_for_DHT11 = {"id":"7","name":"TEMP-HUMID","data":"X","unit": "*C-%"}

data_for_RTC = { "id" : "22","name" : "TIME","data": "x","unit":""}
#X = 0 tat , X = 1 mo
data_for_RELAY = {"id":"11","name":"RELAY","data":"X","unit":""}

#INPUT:  X<100 toi, X>100 sang
data_for_LIGHT ={"id":"13","name":"LIGHT","data":"X","unit":""}

#X = 0 – OFF, X = 1 – RED,X = 2 – BLUE
data_for_LED = {"id":"1","name":"LED","data":"1","unit":""}


# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    ## passed to this function is the Adafruit IO MQTT client so you can make
    ## calls against it easily.
    # Subscribe to changes on a feed named DemoFeed.
    # client.subscribe(LCD_FEED)
    # client.subscribe(LED_FEED)
    # client.subscribe(SOIL_FEED)
    # client.subscribe(DHT11_FEED)
    # client.subscribe(LIGHT_FEED)
    # client.subscribe(RELAY_FEED)
    client.subscribe('co2')
    client.subscribe('humidity')
    client.subscribe('temperature')
    print('Connected to Adafruit IO! Listening for changes on feeds...')
def subscribe(client, userdata, mid, granted_qos):
    # This method is called when the client subscribes to a new feed.

    print('Subscribed to  feed with QoS {0}'.format(granted_qos[0]))


def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print('Feed {0} received new value: {1}'.format(feed_id, payload))

def wake_up_MQTT():
    # mqttClient1 = MQTTClient(ADAFRUIT_IO_USERNAME2,ADAFRUIT_IO_KEYBBC1)
    # Setup the callback functions defined above.
    mqttClient.on_connect = connected
    mqttClient.on_disconnect = disconnected
    mqttClient.on_message = message
    mqttClient.on_subscribe = subscribe
    mqttClient.connect()
    mqttClient.loop_background()

#-----------------------------

#tls=True,tlsCRLFile=configuration['tlsPath']
mgClient = MongoClient(configuration['mongoRemote'])
db = mgClient.get_database('DoAnDaNganh')
app = Flask(__name__)
app.secret_key ="Secret Key"

mqttClient = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEYBBC)

from passlib.hash import pbkdf2_sha256
import uuid
class User:
    def start_session(self, user):
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        # Create an MQTT client instance.
        wake_up_MQTT()
        return jsonify({"status":"true"}), 200

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
        return jsonify({"status":"true"}), 200

    def login(self):

        user = db.User.find_one({
            "username": request.get_json()['username']
        })

        if user and pbkdf2_sha256.verify(request.get_json()['password'], user['password']):
            return self.start_session(user)

        return jsonify({"error": "Invalid login Username or password"}), 400

    @staticmethod
    def publishToFeed(topic_id):
        if (session['logged_in'] == True):
            value = request.get_json()['value']
            mqttClient.publish(topic_id,value)
            return jsonify({"status":"true"})
        return jsonify({"error": "Not logged in"})

@app.route('/', methods = ['GET'])
def homepage():
    return '<p> ok </p>'
@app.route('/api/account/register', methods = ['POST'])
def register():
    return User().signup()

@app.route('/api/account/',methods = ['POST'])
def login():
    return User().login()

@app.route('/api/account/logout',methods =['POST'])
def logout():
    return User().signout()

@app.route('/api/account/<topic_id>/data',methods= ['GET'])
def getDataOfTopic(topic_id):
    restClient = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEYBBC)
    try:
        feed = restClient.feeds(topic_id)
    except RequestError:
            response = make_response(
                jsonify(
                    {"status": "false", "msg": "No feed available on username"}
                ),
                404
            )
            response.headers["Content-Type"] = "application/json"
            return response
    data = restClient.receive(feed.key)[3]
    return jsonify({"status":"true", "value": data}),200




@app.route('/api/account/<feed_id>/data', methods = ['GET'])
def getSevenNearestValue(feed_id):
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
@app.route('/api/account/data',methods = ['GET'])
def getAllSensorsLatestData():
    restClient = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEYBBC)
    feeds = restClient.feeds()
    data = [{feed.key: restClient.receive(feed.key)[3]} for feed in feeds]
    return jsonify({"status":"true","data": data}),200



@app.route('/api/account/<topic_id>', methods=['POST'])
def publishToFeed(topic_id):
    return User.publishToFeed(topic_id)


@app.route('/api/account/humidity_warning', methods=['GET', 'PUT'])
def modifyHumidityRate():
    if request.method == 'PUT':
        value = request.get_json()['value']
        if not value:
            return jsonify({"status": "false", "msg": "Invalid body format"}), 400
        if isinstance(value, int):
            warningRates['humidity_rate'] = value
            return jsonify({"status": "true"}), 200
        return jsonify({"error": "Invalid input format"}), 400

    else:
        return jsonify({"rate":warningRates['humidity_rate'], "status":"true"}),200

@app.route('/api/account/temp_warning', methods = ['GET','PUT'])
def modifyTempRate():
    if request.method == 'PUT':
        value = request.get_json()['value']
        if not value:
            return jsonify({"status":"false","msg":"Invalid body format"}),400
        if isinstance(value,int):
            warningRates['temp_rate'] = value
            return jsonify({"status":"true"}),200
        return jsonify({"error":"Invalid input format"}),400

    else:
        return jsonify({"rate":warningRates['temp_rate'],"status":"true"}),200




# @socketio.on('incoming_message')
# def handle_message(data):
#     print('received message: ' + data)
#
# @socketio.on('json')
# def handle_json(json):
#     print('received json: ' + str(json))
#
if __name__ == "__main__":
    app.run(debug=True)
    ##