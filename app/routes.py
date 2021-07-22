from app import *
from Adafruit_IO import Client, RequestError
from flask import make_response, jsonify, json, request
from feeds import *
from globalData import *
from username_and_key import *
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
        del restClient
        return response
    data = json.loads(restClient.receive(feed.key)[3])['data']
    if feed.key != DHT11_FEED:
        del restClient
        return jsonify({"status": "true", "value": data}), 200
    else:
        temp,humid = data.split('-')
        del restClient
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
                dict_data += [{
                    "created_at": i.created_at,
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
    del client0
    del client1
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
