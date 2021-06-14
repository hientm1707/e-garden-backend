import sys
import json
import time
import requests
from Adafruit_IO import MQTTClient, Client
from flask import Flask, flash, request, session,jsonify,make_response
# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
key_json = requests.get('http://dadn.esp32thanhdanh.link/')


ADAFRUIT_IO_USERNAME0 = 'CSE_BBC'
ADAFRUIT_IO_USERNAME1 = 'CSE_BBC1'

ADAFRUIT_IO_KEYBBC0 = key_json.json().get("keyBBC")
ADAFRUIT_IO_KEYBBC1 = key_json.json().get("keyBBC1")

topics_id = ['bk-iot-led', 'bk-iot-soil', 'bk-iot-light', 'bk-iot-lcd', 'bk-iot-relay', 'bk-iot-temp-humid']
topics_pub = ['bk-iot-led', 'bk-iot-lcd', 'bk-iot-relay']

global_data = {}

test_feed = 'bbc-led'
# Define callback functions which will be called when certain events happen.
def connected(client):
  
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(test_feed))
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe(test_feed) # only feed key

    # APP 
    # for topic in topics_id: # sub all
    #     print('Connected to Adafruit IO!  Listening for {0} changes...'.format(topic))
    #     client.subscribe(topic)

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
    print('Feed {0} received new value: {1}'.format(test_feed, payload))
    global global_data
    try:
        global_data[feed_id] += [payload]
    except KeyError:
        global_data[feed_id] = [payload]
    print(global_data)

# TEST using my key 
ADAFRUIT_IO_USERNAME0 = "huydinh0612"
ADAFRUIT_IO_KEYBBC0 = "aio_totj91CBZJzKc6M0vVdTDgdD5LQ2"
mqttclient0 = MQTTClient(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
client0 = Client(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
client1 = Client(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)

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

    return_status = {"status": "true"}
    if topic_id in ['bk-iot-led', 'bk-iot-lcd']:
        mqttclient0.publish(topic_id, param)
        # mqttclient0.publish('CSE_BBC/feeds/' + topic_name, param)
        print(f"Publishing {param} to {topic_id}")

    elif topic_id in ['bk-iot-relay']:
        mqttclient1.publish(topic_id, param)
        # mqttclient1.publish('CSE_BBC1/feeds/' + topic_name, param)
        print(f"Publishing {param} to {topic_id}")

    else:
        print('Feeds not exist')
        return_status = {"status": "false", "msg": "Feeds not exist"}
        # return json.dumps('{"status": "false"}')

    response = make_response(
        jsonify(
            return_status
        ),
        200
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
            data = feed.get(feed.key) # get latest data
            return_value['data'] += [{
                "id": topic,
                "value": data.value if data else None
            }]
            
        else :
            client0 = Client(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
            feed = client0.feeds(topic)
            data = feed.get(feed.key) # get latest data
            return_value['data'] += [{
                "id": topic,
                "value": data.value if data else None
            }]
    response = make_response(
        jsonify(
            return_value
        ),
        200
    )
    response.headers["Content-Type"] = "application/json"
    return response

def get_mqtt():
    global global_data, topics_pub

    return_value = {"data": [], "status": "true"}
    for topic in topics_pub: # topic is topic name
        value = None
        try:
            value = global_data[topic] # list
        except KeyError:
            value = None
        
        itemDict = { 
            "id": topic,
            "value": value[-1] if value else None
        }
        return_value['data'] += [itemDict]

    return json.dumps(return_value)


