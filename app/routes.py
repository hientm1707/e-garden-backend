from multiprocessing.connection import Client

from Adafruit_IO import RequestError
from flask import Flask, make_response, jsonify
from source import app
from source.models import User

@app.route('/', methods = ['GET'])
def homepage():
    return '<p> ok </p>'
@app.route('/api/account/register', methods = ['POST'])
def register():
    return User().signup()

@app.route('/api/account/',methods = ['POST'])
def login():
    return User().login()

@app.route('/api/account/logout')
def logout():
    return User().signout()


from examples.mqtt.mqtt_subscribe import ADAFRUIT_IO_KEYBBC,ADAFRUIT_IO_USERNAME
@app.route('/api/account/<feed_id>/data', methods = ['GET'])
def getSevenNearestValue(username,feed_id):
    restClient = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEYBBC)
    try:
        temperature = restClient.feeds(feed_id)
    except RequestError:
            response = make_response(
                jsonify(
                    {"status": "false", "msg": "No feed available on username"}
                ),
                404
            )
            response.headers["Content-Type"] = "application/json"
            return response
    listCreatedAt = [x.created_at for x in restClient.data('co2')[-7:]]
    listValue= [x.value for x in restClient.data('co2')[-7:]]
    if not listValue:
        responseObj = {"status":"false","msg": "Feed has no data yet"}
        trueResponse = make_response(
            jsonify(
                responseObj
            ),
            404
        )
    else:
        listOfDicts = []
        for i in range(len(listCreatedAt)):
            dict = {}
            dict['create_at'] = listCreatedAt[i]
            dict['value'] = listValue[i]
            listOfDicts.append(dict)
        reponseObj = {"data":listOfDicts, "status":"true"}

        trueResponse = make_response(
            jsonify(
                reponseObj
            ),
            200
        )
    trueResponse.headers["Content-Type"] = "application/json"
    return trueResponse

