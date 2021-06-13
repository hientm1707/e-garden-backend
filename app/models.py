import uuid
from app.app import db
from flask import Flask,request,jsonify

# class Users:
#     def register(self):
#         requestBody = request.get_json()
#         user = {
#             "_id": uuid.uuid4().hex,
#             "username": requestBody['username']
#             "password": requestBody['password']
#         }
#         # Check for existing email address
#         if db.user.find_one({"username": user['username']}):
#             return jsonify({"error": " Username already existed"}) , 400
#         if db.users.insert_one(user):
#             return jsonify(user),200
#         return jsonify({"msg": "Signup failed", "status":"false" }),400


class User(db.Document):
    username = db.StringField()
    password = db.StringField()