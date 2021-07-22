
from feeds import *
from pymongo import MongoClient
from smtp import *
from username_and_key import *
import yaml
with open("config/db.yaml", "r") as ymlfile:
    configuration = yaml.load(ymlfile, Loader=yaml.FullLoader)
mgClient = MongoClient(configuration['mongoRemote'])
db = mgClient.get_database('DoAnDaNganh')
SENDER_USERNAME = configuration['sender_username']
SENDER_PASSWORD = configuration['sender_password']
RECEIVERS = configuration['receivers']