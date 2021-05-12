from operator import methodcaller

from flask import Flask, url_for, jsonify, request
from markupsafe import escape
import pymongo
from pymongo import MongoClient
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

app.secret_key = b'\xbeBA\x18\xfb\xb2^\x1b\xeb\xd3\x89>qd\xd2\x94'
# Database
cluster = MongoClient("mongodb+srv://liadhazoot5:123Qwe123=@cluster0.8vdue.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = cluster["VolleyBeach"]
user_collection = db["user"]
player_collection = db["players"]
games_collection = db["games"]

# Routes
from user import routes
from game import routes

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return 'indcxxxxx'

if __name__ == '__main__':
    app.run(debug=True)
