from flask import Flask, render_template, request, abort
from flask_socketio import SocketIO, join_room
from game import GameRoom, Player

app = Flask(__name__)
socketio = SocketIO(app, logger=True)

game_rooms = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/admin/<room_id>')
def admin_start(room_id):
    if room_id in game_rooms:
        return room_id
    else:
        abort(404)

@app.route('/room/<room_id>')
def room(room_id):
    if room_id in game_rooms:
        return room_id
    else:
        abort(404)


# SOCKET IO STUFF

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
        player = Player(request.sid, admin_name, 1, is_admin=True)
        game_room = GameRoom(room_id)
        game_room.add_player(player)
        game_rooms[room_id] = game_room

        join_room(room_id)

        socketio.emit("update room", {"room_id": room_id, "players": game_room.playerIDs, "state": game_room.state})
        socketio.emit("exists", to=request.sid)

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
        player = Player(request.sid, username, len(current_room.playerIDs) + 1)
        current_room.add_player(player)

        join_room(room_id)

        socketio.emit("exists", to=request.sid)
    else:
        socketio.emit("nonexistent", to=request.sid)

@socketio.on("start game")
def start_game(data):
    pass 

@socketio.on("player move")
def player_move(data):
    pass

if __name__ == '__main__':
    socketio.run(app, debug=True)