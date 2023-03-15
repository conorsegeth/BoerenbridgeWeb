from flask import Flask, render_template, request, abort
from flask_socketio import SocketIO, join_room, leave_room
from game import GameRoom, Player, GameState
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
    max_players = int(data["max_players"])
    bot_type = None if data["bot_type"] == "None" else data["bot_type"]
    step_size = data["step_size"]
    reverse = data["reverse"]

    # Check if room already exists
    exists = False
    for room in game_rooms:
        if room == room_id:
            exists = True

    room = GameRoom(room_id, {
        "max_players": max_players, 
        "bot_type": bot_type,
        "step_size": step_size,
        "reverse": reverse
        })
    game_rooms[room_id] = room
    
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
            if len(game_rooms[room].players) >= game_rooms[room].settings["max_players"]:
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

    socketio.emit(
        "settings", {
            "max_players": game_rooms[room_id].settings["max_players"],
            "bot_type": game_rooms[room_id].settings["bot_type"],
            "step_size": game_rooms[room_id].settings["step_size"],
            "reverse": game_rooms[room_id].settings["reverse"]
            }, to=room_id)

@socketio.on('usernames request')
def send_player_names(data):
    room_id = data["room_id"]

    usernames = []
    for player_id in game_rooms[room_id].players:
        player = game_rooms[room_id].players[player_id]
        usernames.append(player.username)
    
    socketio.emit("usernames", {"usernames": usernames}, to=room_id)

@socketio.on("attempt start")
def attempt_start(data):
    room_id = data["room_id"]
    username = data["username"]

    # TODO: Send state info to client side
    if game_rooms[room_id].players[request.sid].is_admin == True:
        state = game_rooms[room_id].start_game()
        socketio.emit("update room", state.as_dict(), to=room_id)
        socketio.emit("start game", to=room_id)
        
    else:
        socketio.emit("not admin", to=request.sid)

@socketio.on("player move")
def player_move(data):
    room_id = data["room_id"]
    guess = data["move"]  # Can be guess or card choice

    state, valid = game_rooms[room_id].do_player_move(guess)
    
    if valid:
        socketio.emit("update room", state.as_dict(), to=room_id)
    else:
        socketio.emit("update room", state.as_dict(), to=room_id)
        socketio.emit("invalid move", to=request.sid)

# Somehow make it recognised who disconnected and stop that game
@socketio.on("bye")
def handle_disconnect(data):
    room_id = data["room_id"]
    pass

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0")
