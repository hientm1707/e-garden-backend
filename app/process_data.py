import sys
import json
import time
import requests
from Adafruit_IO import MQTTClient, Client
from flask import Flask, flash, request, session, jsonify, make_response
from app.app import connected,disconnected,message,subscribe
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

# def connected(client):
#     # APP
#     for topic in topics_id:  # sub all
#         print('Listening for {0} changes...'.format(topic))
#         client.subscribe(topic)
#
#
# def disconnected(client):
#     # Disconnected function will be called when the client disconnects.
#     print('Disconnected from Adafruit IO!')
#     sys.exit(1)
#
# def message(client, feed_id, payload):
#     # Message function will be called when a subscribed feed has a new value.
#     # The feed_id parameter identifies the feed, and the payload parameter has
#     # the new value.
#     print('Feed {0} received new value: {1}'.format(feed_id, payload))
#     global global_data
#     try:
#         global_data[feed_id] += [json.loads(payload)]  # json to dict
#     except KeyError:
#         global_data[feed_id] = [json.loads(payload)]  # json to dict
#     print(global_data)


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

mqttClient0.on_connect = connected
mqttClient0.on_disconnect = disconnected
mqttClient0.on_message = message
# mqttClient0.on_connect    = connected
# mqttClient0.on_disconnect = disconnected
# mqttClient0.on_message    = message

mqttClient0.connect()
# mqttClient1.connect()

mqttClient0.loop_background()


# mqttClient1.loop_background()


