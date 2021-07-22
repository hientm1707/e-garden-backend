# ----------------------Base setup-----------------------
import json
import time
from flask import Flask
from flask_socketio import SocketIO, emit, join_room
from app.model import get_mqtt
from logger import logger
main = Flask(__name__)
main.secret_key = "Secret Key"
socketio = SocketIO(main, cors_allowed_origins="*", engineio_logger=True, logger=True)
from threading import Thread

#----------------------------------------ROUTES------------------------------------------------
from routes import *
thread = None
#----------------------------------------background------------------------------------------------
@socketio.on('message')
def handle_message(msg):
    logger.info(msg)

def background_thread(roomname):
        while True:
            socketio.emit('server-send-mqtt',"FUCK YOU",to=roomname)
            time.sleep(3)

@socketio.on('join')
def on_join(data):
    user = data["user"]
    room = data["room"]
    join_room(room)
    global thread
    if thread is None:
        thread = Thread(target=background_thread, args=(room,))
        thread.daemon = True
        thread.start()
    emit("server-send-mqtt", "FUCK YOU BITCH", room=room)


@socketio.on('connect')
def handle_connected_user():
    logger.info("=======================================A user connected========================================")
    global global_sids
    currentSocketId = request.sid
    logger.info(currentSocketId)
    global_sids =currentSocketId
    global thread
    def background_thread():
        while True:
            socketio.emit('server-send-mqtt',json.loads(get_mqtt(feed_id=LED_FEED)),to=global_sids)
            time.sleep(3)
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()


@socketio.on('server-send-mqtt')
def handle_server_send_mqtt(message):
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)


@socketio.on('disconnect')
def handle_disconnected_user():
    logger.info("=======================================A user DISCONNECTED========================================")

if __name__=='__main__':
    #[socketio.start_background_task(handle_mqtt("haha"), debug=True) for feed in all_feeds]
    socketio.run(main, port = 413, debug=True)




