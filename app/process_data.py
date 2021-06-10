import sys
import json
import time
import requests
from Adafruit_IO import MQTTClient, Client

# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
key_json = requests.get('http://dadn.esp32thanhdanh.link/')


ADAFRUIT_IO_USERNAME0 = 'CSE_BBC'
ADAFRUIT_IO_USERNAME1 = 'CSE_BBC1'

ADAFRUIT_IO_KEYBBC0 = key_json.json().get("keyBBC")
ADAFRUIT_IO_KEYBBC1 = key_json.json().get("keyBBC1")
TRAFFIC_LIGHTS_Feed =  'CSE_BBC/feeds/bk-iot-traffic' # for testing
LED_Feed = 'CSE_BBC/feeds/bk-iot-led'
# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(LED_Feed))
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe(LED_Feed)

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def subscribe(client, userdata, mid, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print('Subscribed to {0} with QoS {1}'.format(LED_Feed, granted_qos[0]))

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print('Feed {0} received new value: {1}'.format(feed_id, payload))

# my key
# ADAFRUIT_IO_USERNAME = "huydinh0612"
# ADAFRUIT_IO_KEY = "aio_totj91CBZJzKc6M0vVdTDgdD5LQ2"
# mqttclient0 = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

mqttclient0 = MQTTClient(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEYBBC0)
# mqttclient1 = MQTTClient(ADAFRUIT_IO_USERNAME1, ADAFRUIT_IO_KEYBBC1)

mqttclient0.on_connect    = connected
mqttclient0.on_disconnect = disconnected
mqttclient0.on_message    = message
mqttclient0.on_subscribe  = subscribe

mqttclient0.connect()
# mqttclient1.connect()

mqttclient0.loop_background()
# mqttclient1.loop_background()

def publish_data(topic_id, param):
    # topic_id : CSE_BBC/feeds/bk-iot-led
    topic_name = topic_id.split('/')[-1]  
    # path = None
    if topic_name in ['bk-iot-led', 'bk-iot-lcd']:
        mqttclient0.publish(topic_id, param)
        # mqttclient0.publish('CSE_BBC/feeds/' + topic_name, param)

        print(f"Publishing {param} to {topic_name}")

    elif topic_name in ['bk-iot-relay']:
        mqttclient1.publish(topic_id, param)
        # mqttclient1.publish('CSE_BBC1/feeds/' + topic_name, param)

        print(f"Publishing {param} to {topic_name}")
    return json.dumps('{"status": "OK"}')
    
def receive_data():
    pass
