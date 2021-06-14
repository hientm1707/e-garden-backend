
from flask import Flask, request
import yaml
with open("db.yaml", "r") as ymlfile:
    configuration = yaml.load(ymlfile,Loader=yaml.FullLoader)
from flask_socketio import SocketIO
from pymongo import MongoClient
mgClient = MongoClient(configuration['mongoRemote'],tls=True,tlsCRLFile=configuration['tlsPath'])
db = mgClient.get_database('DoAnDaNganh')
app = Flask(__name__)
app.secret_key ="Secret Key"
# app.config['MONGODB_SETTINGS'] = {
#     "db" : "doandanganh",
#     "host" : "localhost",
#     "port":27017
# }



# @socketio.on('incoming_message')
# def handle_message(data):
#     print('received message: ' + data)
#
# @socketio.on('json')
# def handle_json(json):
#     print('received json: ' + str(json))
#
from examples.mqtt.mqtt_subscribe import *

if __name__ == "__main__":
    app.run(debug=True)
    ##