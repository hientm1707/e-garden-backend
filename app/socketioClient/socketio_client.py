
import socketio
from logger import logger

sio = socketio.Client()
logger.info('Created socketio client')

@sio.event
def connect():
    logger.info('connected to server')

@sio.event
def disconnect():
    logger.info('disconnected from server')

sio.connect('https://iotdudes-smart-garden.herokuapp.com')
print("haha")