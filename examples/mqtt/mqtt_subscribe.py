# Example of using the MQTT client class to subscribe to a feed and print out
# any changes made to the feed.  Edit the variables below to configure the key,
# username, and feed to subscribe to for changes.

# Import standard python modules.
import sys
import json
import time
import random
import requests
# Import Adafruit IO MQTT client.

from Adafruit_IO import MQTTClient

# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
a = requests.get(url ='http://dadn.esp32thanhdanh.link/')
ADAFRUIT_IO_KEYBBC  = a.json().get("keyBBC")
ADAFRUIT_IO_KEYBBC1  = a.json().get("keyBBC1")
# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = 'CSE_BBC'
ADAFRUIT_IO_USERNAME1 = 'CSE_BBC1'
# Set to the ID of the feed to subs
# cribe to for updates.
LED_Feed = 'bk-iot-led' #pub #sub
DHT11_Feed = 'bk-iot-temp-humid' #sub
RTC_Feed = 'bk-iot-time' #sub
LIGHT_Feed = 'bk-iot-light' #sub
RELAY_Feed = 'bk-iot-relay' #SUB


data_for_DHT11 = json.dumps('{"id":"7","name":"TEMP-HUMID","data":"X","unit": *C-%"}')

data_for_RTC = json.dumps('{ "id" : "22","name" : "TIME","data": "x","unit":"}')
#X = 0 tat , X = 1 mo
data_for_RELAY = json.dumps('{"id":"11","name":"RELAY","data":"X","unit":””}')

#INPUT:  X<100 toi, X>100 sang
data_for_LIGHT =json.dumps('{"id":"13","name":"LIGHT","data":"X","unit":""}')

#X = 0 – OFF, X = 1 – RED,X = 2 – BLUE
data_for_LED =json.dumps('{"id":"1","name":"LED","data":"1","unit":""}')


# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    ## passed to this function is the Adafruit IO MQTT client so you can make
    ## calls against it easily.
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(LED_Feed))
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe(LED_Feed)

def subscribe(client, userdata, mid, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print('Subscribed to {0} with QoS {1}'.format(LED_Feed, granted_qos[0]))

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print('Feed {0} received new value: {1}'.format(feed_id, payload))


# Create an MQTT client instance.
mqttclientLED = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEYBBC)
#mqttclientLED2 = MQTTClient(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEY0)

#qttclientDHT11 = MQTTClient(ADAFRUIT_IO_USERNAME0, ADAFRUIT_IO_KEY0)

# Setup the callback functions defined above.
mqttclientLED.on_connect    = connected
mqttclientLED.on_disconnect = disconnected
mqttclientLED.on_message    = message
mqttclientLED.on_subscribe  = subscribe



# mqttclientLED2.on_connect    = connected
# mqttclientLED2.on_disconnect = disconnected
# mqttclientLED2.on_message    = message
# mqttclientLED2.on_subscribe  = subscribe

# Connect to the Adafruit IO server.
mqttclientLED.connect()
# mqttclientLED2.connect()
mqttclientLED.loop_background()
print('Publishing a new message every 10 seconds (press Ctrl-C to quit)...')
while True:
    value = random.randint(0, 100);
    time.sleep(10);
# mqttclientLED2.loop_background()
#client.loop_background

