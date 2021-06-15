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

mqttclient0 = MQTTClient(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
mqttclient1 = MQTTClient(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)

client0 = Client(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
# client1 = Client(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)

# APP
# client0 = Client(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
# client1 = Client(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)

# mqttclient0 = MQTTClient(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
# mqttclient1 = MQTTClient(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)

mqttclient0.on_connect    = connected
mqttclient0.on_disconnect = disconnected
mqttclient0.on_message    = message
# mqttclient0.on_connect    = connected
# mqttclient0.on_disconnect = disconnected
# mqttclient0.on_message    = message

mqttclient0.connect()
# mqttclient1.connect()

mqttclient0.loop_background()
# mqttclient1.loop_background()


def publish_data(topic_id, param):
    # topic_id : bk-iot-led
    # topic_name = topic_id.split('/')[-1]  
    topic_index ={'bk-iot-led' : "1", 'bk-iot-lcd': "3", 'bk-iot-relay': "11"}
    return_status = {"status": "true"}
    if topic_id in ['bk-iot-led', 'bk-iot-lcd']:
        item_json = {
            "id" : topic_index[topic_id],
            "name" : "LED" if topic_id == 'bk-iot-led' else "LCD",
            "data" : param,
            "unit" : ""
        }
        mqttclient0.publish(topic_id, json.dumps(item_json))
        print(f"Publishing {param} to {topic_id}")

    elif topic_id in ['bk-iot-relay']:
        item_json = {
            "id" : topic_index[topic_id],
            "name" : "RELAY",
            "data" : param,
            "unit" : ""
        }
        mqttclient1.publish(topic_id, json.dumps(item_json))
        print(f"Publishing {param} to {topic_id}")

    elif topic_id in topics_id: # pub for sub too # just for testing
        topic_index = {'bk-iot-soil': "9", "bk-iot-light": "13", 'bk-iot-temp-humid': "7"} # todo create pub for soil to pub again cause soil is spoiled
        
        item_json = {
            "id" : topic_index[topic_id],
            "name" : topic_id[7:].upper(),
            "data" : param,
            "unit" : "*C-%" if 'temp' in topic_id else ""
        }
        mqttclient0.publish(topic_id, json.dumps(item_json))
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
    


def receive_new_data():

    global topics_id 
    return_value = {"data": [], "status": "true"}
    
    for topic in topics_id:

        if topic in ['bk-iot-light', 'bk-iot-relay']:
            client1 = Client(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)
            feed = client1.feeds(topic)
            data = client1.receive(feed.key) # get latest data : json
            data = json.loads(data.value)['data'] # FIXME
            return_value['data'] += [{
                "id": topic,
                "data": data if data else None
            }]
            
        else :
            client0 = Client(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
            feed = client0.feeds(topic)
            data = client0.receive(feed.key) # get latest data : json
            print(data,data.value, type(data.value))
            data = json.loads(data.value)['data'] # FIXME
            if topic == 'bk-iot-temp-humid':
                temp,humid = data.split('-')
                return_value['data'] += [{
                    "id": topic,
                    "data": {
                        "temp": temp,
                        'humid': humid
                    }
                }]
            else: #not temp-humid
                return_value['data'] += [{
                    "id": topic,
                    "data": data if data else None
                }]
    response = make_response(
        jsonify(
            return_value
        ),
        200
    )
    response.headers["Content-Type"] = "application/json"
    return response


# def get_mqtt(topic_name = None):
#     global global_data, topics_id

#     return_value = {"data": [], "status": "true"}
#     for topic in topics_id: # topic is topic_name
#         value = None
#         try:
#             value = global_data[topic] # list
#         except KeyError:
#             value = None
        
#         if topic_name == 'bk-iot-temp-humid':
#             if value:
#                 value = value[-1]
#                 temp,humid = value.replace(' ','').split('-')
#                 itemDict = {
#                     "id": topic,
#                     "temp": temp,
#                     "humid": humid
#                 }
#         else:
#             itemDict = { 
#                 "id": topic,
#                 "value": value[-1] if value else None
#             }
#             return_value['data'] += [itemDict]

#     return json.dumps(return_value)

## new json
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
                'value': {
                    'temp': temp,
                    'humid': humid
                }
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


