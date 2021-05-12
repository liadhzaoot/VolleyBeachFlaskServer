import sys

from flask import Flask, jsonify, request, json, session
import uuid
from passlib.hash import pbkdf2_sha256
from home import user_collection
import re

class User:

    def start_session(self, user):
        print(user)
        session['logged_in'] = True
        session['user'] = user
        return user, 200

    def login(self):
        request_data = json.loads(request.data)
        user = user_collection.find_one({"email": request_data["email"]})
        if user and pbkdf2_sha256.verify(request_data["password"], user['password']):
            return self.start_session(user)
        return jsonify({"error": "Invalid login credentials"}), 401

    def signup(self):
        # create the user object
        request_data = json.loads(request.data)
        user = {
            "_id": uuid.uuid4().hex,
            "firstName": request_data["firstName"],
            "lastName": request_data["lastName"],
            "phoneNumber": request_data["phoneNumber"],
            "email": request_data["email"],
            "password": request_data["password"],
        }
        # encrypt the password

        validation = self.validation(user)
        if validation:
            return validation
        user["password"] = pbkdf2_sha256.encrypt(user["password"])

        if user_collection.insert_one(user):
            return jsonify(user), 200

        return jsonify({"error": "signup failed"}), 400

    def validation(self, user):
        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

        if not user["firstName"] or not user["lastName"] or not user["phoneNumber"] or not user["email"] or not user["password"]:
            return jsonify({"error": "Some Fields Are Empty "}), 400

            # check for existing email address
        if user_collection.find_one({"email": user["email"]}):
            return jsonify({"error": "Email address already in use"}), 400

        if not re.search(regex, user["email"]):
            return jsonify({"error": "Invalid Email"}), 400

        if len(user["password"]) < 6:
            return jsonify({"error": "The Password is too short"}), 400