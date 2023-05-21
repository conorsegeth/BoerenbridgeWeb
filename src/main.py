from flask import Flask, render_template, request, abort
from flask_socketio import SocketIO, join_room, leave_room
from game import GameRoom, Player
from bots import RandBot, RandomSearchBot, NNBot
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

    # Check if room id has spaces
    if len(room_id.split(" ")) > 1:
        socketio.emit("no spaces", to=request.sid)
        return

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
    
    if bot_type == 'NNBot':
        room.add_player(NNBot("NNBot", 2))
    elif bot_type == 'RSBot':
        room.add_player(RandomSearchBot("Randy Simpson", 2, 100, 15))
    elif bot_type == "rand":
        room.add_player(RandBot("RandBot", 2))

    game_rooms[room_id] = room
    
    if exists:
        socketio.emit("pre-existing", to=request.sid)
    else:
        socketio.emit("exists", to=request.sid)

@socketio.on("join room")
def join_game(data):
    room_id = data["room_id"]
    username = data["username"]

    # Check if room exists
    exists = True if room_id in game_rooms else False

    name_taken = False
    if exists:
        for id in game_rooms[room_id].players:
            if game_rooms[room_id].players[id].username == username:
                name_taken = True
        if name_taken:
            socketio.emit("name taken", to=request.sid)
            return

    if exists and len(game_rooms[room_id].players) >= game_rooms[room_id].settings["max_players"]:
        socketio.emit("full", to=request.sid)
        return

    elif exists and game_rooms[room_id].started == True:
        socketio.emit("started", to=request.sid)
        return
    
    if exists:
        socketio.emit("exists", to=request.sid)
    else:
        socketio.emit("nonexistent", to=request.sid)

@socketio.on("joined")
def handle_join(data):
    room_id = data["room_id"]
    username = data["username"]

    bot_names = ["RandBot", "Randy Simpson", "NNBot"]
    room = game_rooms[room_id]
    if len(room.players) == 0 or (len(room.players) == 1 and list(room.players.values())[0].username in bot_names):
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

    if game_rooms[room_id].players[request.sid].is_admin == True:
        state = game_rooms[room_id].start_game()
        socketio.emit("update room", state.as_dict(), to=room_id)
        socketio.emit("start game", to=room_id)
        
    else:
        socketio.emit("not admin", to=request.sid)

@socketio.on("player move")
def player_move(data):
    room_id = data["room_id"]
    move = data["move"]  # Can be guess or card choice

    if move.isdigit():
        move = int(move)

    state, valid = game_rooms[room_id].do_player_move(move)
    
    if valid:
        socketio.emit("update room", state.as_dict(), to=room_id)
    else:
        socketio.emit("update room", state.as_dict(), to=room_id)
        socketio.emit("invalid move", to=request.sid)

@socketio.on("attempt bot move")
def attempt_bot_move(data):
    room_id = data["room_id"]

    if game_rooms[room_id].players[request.sid].is_admin:
        socketio.emit("stop sending", to=room_id)

        engine = game_rooms[room_id].engine
        bot = engine.state.get_player_from_turn()
        move = bot.get_move(engine.get_player_perspective(bot, engine.state))
        new_state, valid = game_rooms[room_id].do_player_move(move)

        socketio.emit("update room", new_state.as_dict(), to=room_id)

@socketio.on("make sneaky bot move")
def make_sneaky_bot_move(data):
    room_id = data["room_id"]
    username = data["username"]

    room = game_rooms[room_id]
    engine = room.engine
    
    bot = NNBot(username, 0)
    bot.give_hand(room.get_player_from_sid(request.sid).hand)

    move = bot.get_move(engine.get_player_perspective(room.get_player_from_sid(request.sid), engine.state))
    new_state, valid = room.do_player_move(move)

    socketio.emit("update room", new_state.as_dict(), to=room_id)

@socketio.on("attempt reset")
def attempt_reset(data):
    room_id = data["room_id"]
    
    if game_rooms[room_id].players[request.sid].is_admin:
        state, valid = game_rooms[room_id].do_player_move(None)
        socketio.emit("update room", state.as_dict(), to=room_id)

@socketio.on("bye")
def handle_disconnect(data):
    room_id = data["room_id"]
    socketio.emit("disconnected", to=room_id)
    
    leave_room(room_id)
    
    if game_rooms[room_id].players[request.sid].is_admin:
        del game_rooms[room_id]

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0")
