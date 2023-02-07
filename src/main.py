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

@app.route('/<room_id>')
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

    player = Player(request.sid, admin_name, 1, is_admin=True)
    game_room = GameRoom(room_id)
    game_room.add_player(player)
    game_rooms[room_id] = game_room

    join_room(room_id)

    socketio.emit("update room", {"room_id": room_id, "players": game_room.players, "state": game_room.state})

@socketio.on("join room")
def join_game(data):
    room_id = data["room_id"]
    username = data["username"]

    print(data)

    current_room_id = None
    if game_rooms:
        for room in game_rooms:
            if room == room_id:
                current_room_id = room

    if current_room_id:
        current_room = game_rooms[current_room_id]
        num_players = len(current_room.players)
        player = Player(request.sid, username, num_players + 1)
        current_room.add_player(player)
    
        join_room(current_room_id)

        socketio.emit("update room", {"room_id": current_room_id, "players": current_room.players, "state": current_room.state})
        socketio.emit("exists", {"esists": True}, to=request.sid)
    else:
        socketio.emit("nonexistent", {"nonexistent": True}, to=request.sid)


@socketio.on("start game")
def start_game(data):
    pass 

@socketio.on("player move")
def player_move(data):
    pass

if __name__ == '__main__':
    socketio.run(app, debug=True)