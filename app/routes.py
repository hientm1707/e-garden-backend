from app import *
from app.model import User, writeLogToDatabase
from Adafruit_IO import Client, RequestError
from flask import make_response, jsonify, json, request,session
from app.feeds import *
from app.globalData import *
from app.username_and_key import *
from app.main import main
from datetime import datetime, timedelta
@main.route('/', methods=['GET'])
def homepage():
    db.LOGS.delete_many({})
    return '<p> ok </p>'

@main.route('/api/account/register', methods=['POST'])
def register():
    return User().signup()

@main.route('/api/account/', methods=['POST'])
def login():
    return User().login()

@main.route('/api/account/logout', methods=['POST'])
def logout():
    return User().signout()

@main.route('/api/account/unsubscribe/<feed_id>', methods=['GET'])
def unsubscribe(feed_id):
    return User.unsubscribeFeed(feed_id)

@main.route('/api/account/<feed_id>', methods=['POST'])
def publishToFeed(feed_id):
    return User.publishToFeed(feed_id)

@main.route('/api/account/subscribe/<feed_id>', methods=['GET'])
def subscribe(feed_id):
    return User.subscribeFeed(feed_id)

@main.route('/api/account/<feed_id>/data', methods=['GET'])
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
        del restClient
        return response
    #data = restClient.receive(feed.key)[3]
    listData= restClient.data(feed_id)
    if listData:
        realData = json.loads(listData[0][3])['data']
        print("======================================YES WE GOT SOME DATA===========================================")
        if feed.key != DHT11_FEED:
            del restClient
            return jsonify({"status": "true", "value": realData}), 200
        else:
            temp,humid = realData.split('-')
            del restClient
            return jsonify({"status":"true", "value":{"temp":temp,"humid":humid}}),200
    else:
        print("======================================NO DATA AVAILABLE===========================================")
        return jsonify({"status": "false", "msg": "No feed available at the moment on this feed"}), 200

@main.route('/api/account/<feed_id>/seven_data', methods=['GET'])
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
                time_ = datetime.strptime(i.created_at, '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=7)
                dict_data += [{
                    "created_at": datetime.strftime(time_, '%Y-%m-%dT%H:%M:%SZ' ),
                    "value": value
                }]
            return_value = {"data": dict_data, "status":"true"}
            del client0
            del client1
            return jsonify(return_value),200
        else:
            return_value = {"data": None, "status":"False", "msg": "Feed has no data"}
            del client0
            del client1
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
                time_ = datetime.strptime(i.created_at, '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=7)
                dict_data += [{
                    "created_at": datetime.strftime(time_, '%Y-%m-%dT%H:%M:%SZ' ),
                    "value": value
                }]
            return_value = {"data": dict_data, "status":"true"}
            del client0
            del client1
            return jsonify(return_value),200
        else:
            return_value = {"data": None, "status":"false", "msg": "Feed has no data"}
            del client0
            del client1
            return jsonify(return_value),400
    else:
        return_value = {"data": None, "status":"false", "msg": "Feed not exist"}
        del client0
        del client1
        return jsonify(return_value),400

@main.route('/api/account/data', methods=['GET'])
def getAllSensorsLatestData():
    dict_data = []
    client1 = Client(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)
    client0 = Client(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
    for feed in feeds_of_client[1]:
        data = client1.data(feed)[0][3]
        if data is not None:
            dict_data += [{
                "id": feed,
                "value":json.loads(data)['data']
            }]
        else:
            dict_data += [{
                "id": feed,
                "value": "None"
            }]
        print(dict_data)
    for feed in feeds_of_client[0]:
        print(feed)
        data = client0.data(feed)[0][3]
        value = json.loads(data)['data'] if data is not None else "None"
        if feed == 'bk-iot-temp-humid':
            if value:
                temp, humid = value.split('-')
                value = {'temp': temp, 'humid': humid}
        dict_data += [{
            "id": feed,
            "value": value
        }]
    return jsonify({"data": dict_data, "status": "true"}), 200

@main.route('/api/account/humidity_warning', methods=['GET', 'PUT'])
def modifyHumidityRate():
    if request.method == 'PUT':
        value = request.get_json()['value']
        if not value:
            return jsonify({"status": "false", "msg": "Invalid body format"}), 400
        if isinstance(value, int):
            global_ctx['humidity_rate'] = value
            user_name = session['user']['username']
            writeLogToDatabase(username=user_name, msg=f"User {user_name} set humidity warning rate to {value}", time=datetime.now() )
            return jsonify({"status": "true"}), 200
        return jsonify({"error": "Invalid input format"}), 400
    else:
        return jsonify({"rate": global_ctx['humidity_rate'], "status": "true"}), 200

@main.route('/api/account/temp_warning', methods=['GET', 'PUT'])
def modifyTempRate():
    if request.method == 'PUT':
        value = request.get_json()['value']
        if not value:
            return jsonify({"status": "false", "msg": "Invalid body format"}), 400
        if isinstance(value, int):
            global_ctx['temp_rate'] = value
            user_name = session['user']['username']
            writeLogToDatabase(username=user_name, msg=f"User {user_name} set temperature warning rate to {value}", time=datetime.now() )
            return jsonify({"status": "true"}), 200
        return jsonify({"error": "Invalid input format"}), 400
    else:
        return jsonify({"rate": global_ctx['temp_rate'], "status": "true"}), 200

@main.route('/api/account/logs', methods=['GET'])
def getLogs():
    listOfLogs = list(db.LOGS.find({},{"_id":0}))
    if listOfLogs:
        return jsonify({
            "status": "true",
            "logs": listOfLogs
        }), 200
    return jsonify({"status": "false","msg":"No logs yet"}),200