from flask import Flask, render_template, request, abort, session
from flask_socketio import SocketIO, join_room
from game import GameRoom, Player
import os, uuid

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
        return room_id
    else:
        abort(404)


# SOCKET IO STUFF

@socketio.on('connect')
def handle_connect():
    user_id = str(uuid.uuid4())
    session['user_id'] = user_id

@socketio.on('test')
def testt():
    print(session.get('user_id'))

@socketio.on("create room")
def create_game(data):
    room_id = data["room_id"]
    admin_name = data["admin_name"]

    # Check if room already exists
    exists = False
    for room in game_rooms:
        if room == room_id:
            exists = True

    if exists:
        socketio.emit("pre-existing", to=request.sid)
    else:
        player = Player(session.get('user_id'), admin_name, 1, is_admin=True)
        game_room = GameRoom(room_id)
        game_room.add_player(player)
        game_rooms[room_id] = game_room

        session['room_id'] = room_id
        join_room(room_id)

        socketio.emit("exists", to=request.sid)
        socketio.emit("update room", {"room_id": room_id, "players": game_room.get_player_uids(), "state": game_room.state})

@socketio.on("join room")
def join_game(data):
    room_id = data["room_id"]
    username = data["username"]

    # Check if room exists
    exists = False
    for room in game_rooms:
        if room == room_id:
            exists = True
    
    if exists:
        current_room = game_rooms[room_id]
        player = Player(request.sid, username, len(current_room.players) + 1)
        current_room.add_player(player)

        session['room_id'] = room_id
        join_room(room_id)

        socketio.emit("exists", to=request.sid)
    else:
        socketio.emit("nonexistent", to=request.sid)

@socketio.on("players request")
def send_player_names():
    playerID = session.get('user_id')

    room_id = None
    player_names = []

    # Get room id attached to player and use to send updates about connected players
    for roomid in game_rooms:
        current_room = game_rooms[roomid]
        print(playerID, current_room.get_player_uids())
        if playerID in current_room.get_player_uids():
            room_id = current_room.room_id
            
            # Put player usernames in list
            for player in current_room.players:
                player_names.append(current_room.players[player].username)



    # Handle when this doesn't work  ??
    if not room_id or not player_names:
        pass
    else:
        socketio.emit("player names", {"usernames": player_names}, to=request.sid)

@socketio.on("start game")
def start_game(data):
    pass 

@socketio.on("player move")
def player_move(data):
    pass

if __name__ == '__main__':
    socketio.run(app, debug=True)