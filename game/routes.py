from flask import Flask, session,jsonify
from game.models import Game
from home import app
import datetime
from datetime import date
from home import games_collection


@app.route('/players/addPlayerToGame', methods=['POST'])
def addPlayerToGame():
    g = Game()
    return g.add_player_to_game()

@app.route('/players/getGames', methods=['GET'])
def getGames():
    g = Game()
    return jsonify(g.get_games())

@app.route('/players/getPlayersInCurrentGame', methods=['GET'])
def getPlayersInCurrentGame():
    g = Game()
    return jsonify(g.get_players_in_current_game("username"))

@app.route('/players/checkIfPlayerExist', methods=['POST'])
def checkIfPlayerExist():
    g = Game()
    return jsonify(g.check_if_player_exist())

@app.route('/players/createTeams', methods=['POST'])
def createTeams():
    g = Game()
    return jsonify(g.create_team_api())

@app.route('/players/getGame', methods=['GET'])
def getGame():
    g = Game()
    return jsonify(g.api_get_cur_game())