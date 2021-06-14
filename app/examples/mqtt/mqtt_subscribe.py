# Example of using the MQTT client class to subscribe to a feed and print out
# any changes made to the feed.  Edit the variables below to configure the key,
# username, and feed to subscribe to for changes.

# Import standard python modules.
import sys
import json
import requests
# Import Adafruit IO MQTT client.

from Adafruit_IO import MQTTClient
# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
# a = requests.get(url ='http://dadn.esp32thanhdanh.link/')
# ADAFRUIT_IO_KEYBBC  = a.json().get("keyBBC")
# ADAFRUIT_IO_KEYBBC1  = a.json().get("keyBBC1")
# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
# ADAFRUIT_IO_USERNAME = 'CSE_BBC'
# ADAFRUIT_IO_USERNAME1 = 'CSE_BBC1'

# LED_FEED = 'bk-iot-led'
# SOIL_FEED = 'bk-iot-soil'
# LIGHT_FEED = 'bk-iot-light'
# LCD_FEED = 'bk-iot-lcd'
# RELAY_FEED = 'bk-iot-relay'
# DHT11_FEED =  'bk-iot-temp-humid'


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


# Create an MQTT client instance.

mqttClient = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEYBBC)
#mqttClient1 = MQTTClient(ADAFRUIT_IO_USERNAME2,ADAFRUIT_IO_KEYBBC1)
# Setup the callback functions defined above.
mqttClient.on_connect    = connected
mqttClient.on_disconnect = disconnected
mqttClient.on_message    = message
mqttClient.on_subscribe  = subscribe

mqttClient.connect()
mqttClient.loop_background()



