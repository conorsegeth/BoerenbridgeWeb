from flask import Flask, render_template
from flask_socketio import SocketIO
from game import GameRoom, Player

app = Flask(__name__)
socketio = SocketIO(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/admin/<room_id>')
def room(room_id):
    pass

# SOCKET IO STUFF
game_rooms = []

@socketio.on("create room")
def create_game(data):
    room_id = data["room_id"]
    admin_name = data["admin_name"]
    game_room = GameRoom(room_id, [])
    player = Player(room_id, admin_name, 1, is_admin=True)
    game_room.players.append(player)
    game_rooms.append(game_room)
   


@socketio.on("join room")
def join_room(data):
    pass

@socketio.on("start game")
def start_game(data):
    pass 

@socketio.on("player move")
def player_move(data):
    pass