import sys
from flask import Flask, jsonify, request, json, session
import uuid
from passlib.hash import pbkdf2_sha256
from home import player_collection
from home import games_collection
from home import user_collection
import datetime
from datetime import date


class Game:
    def is_same_week(self, date1, date2):
        d1 = datetime.datetime.strptime(date1, '%Y%m%d')
        d2 = datetime.datetime.strptime(date2, '%Y%m%d')
        d1 = d1 + datetime.timedelta(days=1)
        d2 = d2 + datetime.timedelta(days=1)

        return d1.isocalendar()[1] == d2.isocalendar()[1] and d1.year == d2.year

    # get the game id and insert to DB if dont Exist
    def get_game(self, cur_time, last_game):
        game = {
            "id": uuid.uuid4().hex,
            "gameId": (last_game["gameId"] + 1),
            "MVP": "?",
            "summary": "?",
            "time": cur_time,
            "players": []
        }
        if self.is_same_week(cur_time, last_game["time"]):
            return last_game
        else:
            print(game)
            games_collection.insert_one(game)
            return game

    def api_get_cur_game(self):
        last_game = {}
        game_cursor = games_collection.find().sort("gameId", -1).limit(1)
        for x in game_cursor:
            last_game = x
        last_game['_id'] = str(last_game['_id'])
        return last_game

    def get_players_in_current_game(self, arrayType):
        last_game = {}
        today = date.today()
        # dd/mm/YY
        join_date = today.strftime("%Y%m%d")
        game_cursor = games_collection.find().sort("gameId", -1).limit(1)
        for x in game_cursor:
            last_game = x
        if last_game:
            #print("######################################")
            #print("join date = ", join_date)
            game = self.get_game(join_date, last_game)

            game['_id'] = str(game['_id'])
            if arrayType == "username":
                return self.create_username_arry(game, "username")
            elif arrayType == "email":
                return self.create_username_arry(game, "email")
        else:
            return {"error": "no last game"}

    # return only the user name array
    def create_username_arry(self, game, arrayType):
        players = game["players"]
        player_username_array = []
        for player in players:
            if arrayType == "username":
                player_username_array.append(player["username"])
            elif arrayType == "email":
                player_username_array.append(player["email"])
        return player_username_array

    def get_user_from_email(self, email):
        return user_collection.find_one({"email": email})

    def add_player_to_game(self):
        today = date.today()
        # dd/mm/YY
        join_date = today.strftime("%Y%m%d")
        # user info
        request_data = json.loads(request.data)
        # user = self.get_user_from_email(request_data["email"])
        # game info
        game = {
            "id": uuid.uuid4().hex,
            "gameId": 1,
            "MVP": "?",
            "summary": "the game summary",
            "time": join_date,
            "players": []
        }
        # player DB
        player = {
            "_id": uuid.uuid4().hex,
            "username": request_data["firstName"] + " " + request_data["lastName"],
            "email": request_data["email"],
            "gameId": [],
        }
        last_game = {}
        # if there is no game at all
        if not games_collection.find_one():
            games_collection.insert_one(game)
            last_game = game
        else:
            game_cursor = games_collection.find().sort("gameId", -1).limit(1)
            for x in game_cursor:
                last_game = x

        game = self.get_game(join_date, last_game)
        # get only the username without email
        players_in_game = self.create_username_arry(game, "email")
        # check if the player in the player DB
        player_find = player_collection.find_one({"email": player["email"]})
        if not player_find:
            player_collection.insert_one(player)
        else:
            player = player_find
        if player:
            # check if the game exist else adding to DB return the last game
            # check if game exist
            # game = games_collection.find_one({"gameId": player["gameId"][-1]})
            # check if the player registerd
            # print("#################################################")
            # print(players_in_game)
            # print((player["email"] in players_in_game))
            # print(player["gameId"])
            # print((game["gameId"] in player["gameId"]))
            # remove player
            if (player["email"] in players_in_game) and player["gameId"] and (
                    game["gameId"] in player["gameId"]):
                # remove the game from player array
                player_games_id = player["gameId"]
                player_games_id.remove(player["gameId"][-1])
                player_collection.update_one({"email": player["email"]}, {"$set": {"gameId": player_games_id}})
                # remove the player from game
                game_players = game["players"]
                game_players.remove({"email": player["email"], "username": player["username"]})
                games_collection.update_one({"gameId": game["gameId"]}, {"$set": {"players": game_players}})
                return jsonify({"remove": player["username"]})
            # add player
            else:
                # print(game["gameId"])
                # print(player["gameId"])
                # print(player["email"])
                # print(game["players"])
                # print("##########################################################")
                # print((game["gameId"] not in player["gameId"]))
                # print((player["email"] not in players_in_game))
                if (game["gameId"] not in player["gameId"]) and (player["email"] not in players_in_game):
                    # adding to player the game
                    player_games_id = player["gameId"]
                    player_games_id.append(game["gameId"])
                    player_collection.update_one({"email": player["email"]}, {"$set": {"gameId": player_games_id}})

                    # adding to game the player
                    game_players = game["players"]
                    game_players.append({"email": player["email"], "username": player["username"]})
                    games_collection.update_one({"gameId": game["gameId"]},
                                                {"$set": {"players": game_players}})
                    return jsonify({"add": player["username"]})

        return jsonify({"error": "Something failed"}), 400

    def check_if_player_exist(self):
        request_data = json.loads(request.data)
        players = self.get_players_in_current_game("email")
        if request_data["email"] in players:
            return {"exist": "the user does in game"}
        else:
            return {"error": "The user does not in game"}

    def get_games(self):
        games = []
        game_cursor = games_collection.find().sort("gameId", -1)
        for game in game_cursor:
            game['_id'] = str(game['_id'])
            games.append(game)
        return games

    def create_teams(self, game, player_in_team):
        if not game or not player_in_team:
            return {"error": "Invalid Parameters"}
        import random
        players = game["players"].copy()
        teams = []
        team = []
        out = []
        number_of_players = len(players)
        number_of_teams = int(number_of_players) / int(player_in_team)
        if number_of_teams < 2:
            return {"error": "There are not enough players"}
        for i in range(int(number_of_teams)):
            for j in range(player_in_team):
                n = random.randint(0, len(players)-1)
                team.append(players[n])
                players.pop(n)

            teams.append(team.copy())
            team.clear()
        for player in players:
            out.append(player)
        final_teams = {
            "teams": teams,
            "out": out
        }
        return final_teams
    # get game info and number of players in team request_data["game"],request_data["player_in_team"]
    def create_team_api(self):
        request_data = json.loads(request.data)
        final_teams = self.create_teams(request_data["game"],int(request_data["playerInTeam"]))
        return final_teams