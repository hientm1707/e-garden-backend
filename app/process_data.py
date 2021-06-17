from logging import NOTSET
import sys
import json
import time
import requests
from Adafruit_IO import MQTTClient, Client
from flask import Flask, flash, request, session,jsonify,make_response
# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
# key_json = requests.get('http://dadn.esp32thanhdanh.link/')


ADAFRUIT_IO_USERNAME0 = 'CSE_BBC'
ADAFRUIT_IO_USERNAME1 = 'CSE_BBC1'

# ADAFRUIT_IO_KEYBBC0 = key_json.json().get("keyBBC")
# ADAFRUIT_IO_KEYBBC1 = key_json.json().get("keyBBC1")

global_data = {}
topics_id = ['bk-iot-led', 'bk-iot-soil', 'bk-iot-light', 'bk-iot-lcd', 'bk-iot-relay', 'bk-iot-temp-humid']
topics_pub = ['bk-iot-led', 'bk-iot-lcd', 'bk-iot-relay']


## TEST
# topics_id = ['bbc-led','test','bk-iot-led']
test_feed = 'bbc-led'
# Define callback functions which will be called when certain events happen.
def connected(client):
  
   
    # APP 
    for topic in topics_id: # sub all
        print('Listening for {0} changes...'.format(topic))
        client.subscribe(topic)

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

# not used
# def subscribe(client, userdata, mid, granted_qos):
#     print('Subscribed to {0} with QoS {1}'.format(test_feed, granted_qos[0]))

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print('Feed {0} received new value: {1}'.format(feed_id, payload))
    global global_data
    try:
        global_data[feed_id] += [json.loads(payload)] # json to dict
    except KeyError:
        global_data[feed_id] = [json.loads(payload)] # json to dict
    print(global_data)

# TEST using my key 
# ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_USERNAME1 = "huydinh0612", "huydinh0612"
# ADAFRUIT_IO_KEYBBC0, ADAFRUIT_IO_KEYBBC1 = "aio_totj91CBZJzKc6M0vVdTDgdD5LQ2", "aio_totj91CBZJzKc6M0vVdTDgdD5LQ2"
ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0 = 'trminhhien17', 'aio_Phfr33tNoyth68Tg6gWsVJXNkVbA'
ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1 = 'trminhhien17', 'aio_Phfr33tNoyth68Tg6gWsVJXNkVbA'

mqttClient0 = MQTTClient(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
mqttClient1 = MQTTClient(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)

client0 = Client(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
# client1 = Client(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)

# APP
# client0 = Client(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
# client1 = Client(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)

# mqttClient0 = MQTTClient(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
# mqttClient1 = MQTTClient(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)

mqttClient0.on_connect    = connected
mqttClient0.on_disconnect = disconnected
mqttClient0.on_message    = message
# mqttClient0.on_connect    = connected
# mqttClient0.on_disconnect = disconnected
# mqttClient0.on_message    = message

mqttClient0.connect()
# mqttClient1.connect()

mqttClient0.loop_background()
# mqttClient1.loop_background()


def publish_data(topic_id, param):
    # topic_id : bk-iot-led
    # topic_name = topic_id.split('/')[-1]  
    topic_index ={'bk-iot-led' : "1", 'bk-iot-lcd': "3", 'bk-iot-relay': "11"}
    return_status = {"status": "true"}
    if topic_id in ['bk-iot-led', 'bk-iot-lcd']:
        item_json = {
            "id" : topic_index[topic_id],
            "name" : topic_id[7:].upper(),
            "data" : param,
            "unit" : ""
        }
        mqttClient0.publish(topic_id, json.dumps(item_json))
        print(f"Publishing {param} to {topic_id}")

    elif topic_id in ['bk-iot-relay']:
        item_json = {
            "id" : topic_index[topic_id],
            "name" : topic_id[7:].upper(),
            "data" : param,
            "unit" : ""
        }
        mqttClient1.publish(topic_id, json.dumps(item_json))
        print(f"Publishing {param} to {topic_id}")

    elif topic_id in topics_id: # pub for sub too # just for testing
        topic_index = {'bk-iot-soil': "9", "bk-iot-light": "13", 'bk-iot-temp-humid': "7"} 
        
        item_json = {
            "id" : topic_index[topic_id],
            "name" : topic_id[7:].upper(),
            "data" : param,
            "unit" : "*C-%" if 'temp' in topic_id else ""
        }
        mqttClient0.publish(topic_id, json.dumps(item_json))
        print(f"Publishing {param} to {topic_id}")

    else:
        print('Feeds not exist')
        return_status = {"status": "false", "msg": "Feeds not exist"}
        # return json.dumps('{"status": "false"}')
        response = make_response(
                                    jsonify(return_status),404
                                )
        response.headers["Content-Type"] = "application/json"
        return response

    response = make_response(
                                jsonify(return_status),200
        )
    response.headers["Content-Type"] = "application/json"
    return response
    # return json.dumps('{"status": "true"}')
    


## optimized 2: <= 5s
def receive_new_data():
    dict_data = []
    client1 = Client(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1) 
    client0 = Client(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
    topic1 = ['bk-iot-light', 'bk-iot-relay']
    topic0 = ['bk-iot-led', 'bk-iot-soil', 'bk-iot-lcd', 'bk-iot-temp-humid']
    
    for topic in topic1:
        data = client1.receive(topic)[3]
        
        dict_data += [{
            "id": topic,
            "value": json.loads(data)['data'] if data != None else None
        }]

    for topic in topic0:
        data = client0.receive(topic)[3] 
        value = json.loads(data)['data'] if data != None else None
        if topic =='bk-iot-temp-humid':
            if value:
                temp,humid = value.split('-')
                value = {'temp': temp, 'humid':humid}

        dict_data += [{
            "id": topic,
            "value": value
        }]

    return_value = {"data": dict_data, "status": "true"}
    return jsonify(return_value),200


## optimize 7data #1:
def getSevenNearestValue(feed_id):
    dict_data = []
    topic1 = ['bk-iot-light', 'bk-iot-relay']
    # topic0 = ['bk-iot-led', 'bk-iot-soil', 'bk-iot-lcd', 'bk-iot-temp-humid']
    
    client = Client(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1) if feed_id in topic1 else Client(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)

    data = client.data(feed_id)[:7]
    if data:
        for i in data:
            try:
                value = json.loads(i[3])['data']
            except TypeError:
                value = i[3]

            if feed_id == 'bk-iot-temp-humid':
                temp,humid = value.split('-')
                value = { 'temp': temp, 'humid': humid }
            
            dict_data += [{
                "created_at": i.created_at,
                "value": value
            }]
        return_value = {"data": dict_data, "status":"true"}
        return jsonify(return_value),200
    else:
        return_value = {"data": None, "status":"false", "msg": "Feed has no data"}
        return jsonify(return_value),404


def get_mqtt(topic_name):
    global global_data

    value = None
    try:
        value = global_data[topic_name] # value is list of dict
    except KeyError:
        value = None
    itemDict = {}
    if topic_name == 'bk-iot-temp-humid':
        if value:
            value = value[-1] # last dict
            temp,humid = value['data'].split('-')
            itemDict = {
                'id': topic_name,
                'value': {'temp': temp,'humid': humid}
                }
        else: # if value is None
            itemDict = {
                'id': topic_name,
                'value': {
                    'temp': None,
                    'humid': None
                }
            }
    else:
        itemDict ={
            'id': topic_name,
            'value': value[-1]['data'] if value else None
        }
    return json.dumps(itemDict)


