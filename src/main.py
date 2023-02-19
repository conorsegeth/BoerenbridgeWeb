from flask import Flask, render_template, request, abort
from flask_socketio import SocketIO, join_room
from game import GameRoom, Player
import os

SECRET_KEY = os.urandom(24)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app, logger=True)
socketio.init_app(app, cors_allowed_origins="*")

game_rooms = {}

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/admin/<room_id>')
def admin_start(room_id):
    if room_id in game_rooms:
        return render_template('admin_start.html')
    else:
        abort(404)

@app.route('/room/<room_id>')
def room(room_id):
    if room_id in game_rooms:
        return render_template('room.html')
    else:
        abort(404)


# SOCKET IO STUFF

@socketio.on("create room")
def create_game(data):
    room_id = data["room_id"]
    num_players = int(data["num_players"])
    bot_type = None if data["bot_type"] == "None" else data["bot_type"]
    deck_size = data["deck_size"]
    step_size = data["step_size"]
    reverse = data["reverse"]

    # Check if room already exists
    exists = False
    for room in game_rooms:
        if room == room_id:
            exists = True

    room = GameRoom(room_id, {
        "num_players": num_players, 
        "bot_type": bot_type,
        "deck_size": deck_size,
        "step_size": step_size,
        "reverse": reverse
        })
    game_rooms[room_id] = room
    print("settings", room.settings)
    
    if exists:
        socketio.emit("pre-existing", to=request.sid)
    else:
        socketio.emit("exists", to=request.sid)

@socketio.on("join room")
def join_game(data):
    room_id = data["room_id"]

    # Check if room exists
    exists = False
    for room in game_rooms:
        if room == room_id:
            print(len(game_rooms[room].players), game_rooms[room].settings["num_players"])
            if len(game_rooms[room].players) >= game_rooms[room].settings["num_players"]:
                socketio.emit("full", to=request.sid)
                return
            exists = True
    
    if exists:
        socketio.emit("exists", to=request.sid)
    else:
        socketio.emit("nonexistent", to=request.sid)

@socketio.on("joined")
def handle_join(data):
    room_id = data["room_id"]
    username = data["username"]

    room = game_rooms[room_id]
    if len(room.players) == 0:
        player = Player(request.sid, username, 1, is_admin=True)
    else:
        player = Player(request.sid, username, len(room.players) + 1)

    join_room(room_id)
    room.add_player(player)

@socketio.on('usernames request')
def send_player_names(data):
    room_id = data["room_id"]

    usernames = []
    for player_id in game_rooms[room_id].players:
        player = game_rooms[room_id].players[player_id]
        usernames.append(player.username)
    
    socketio.emit("usernames", {"usernames": usernames}, to=room_id)

@socketio.on("start game")
def start_game(data):
    pass 

@socketio.on("player move")
def player_move(data):
    pass

# Somehow make it recognised who disconnected and stop that game
@socketio.on("disconnect")
def handle_disconnect():
    pass

if __name__ == '__main__':
    socketio.run(app, debug=True)