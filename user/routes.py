from flask import Flask, session
from home import app
from user.models import User


@app.route('/user/signup', methods=['POST'])
def signup():
    return User().signup()


@app.route('/user/login', methods=['POST'])
def login():
    return User().login()


@app.route('/Post/signout', methods=['POST'])
def signout():
    session.clear()


@app.route('/Post/test', methods=['POST'])
def post():
    return "User().signup()"
