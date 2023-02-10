function openNav() {
    document.getElementById("infoSidebar").style.width = "600px";
}

function closeNav() {
    document.getElementById("infoSidebar").style.width = "0";
}

function openWin() {
    document.getElementById("settingsModal").style.display = "block";
}

function closeWin() {
    document.getElementById("settingsModal").style.display = "none";
}

// Socket-IO
var socket = io()

var room_dict = {};

// Fix whatever going on here
socket.on("update room", function(data) {
    var room_id = data.room_id;
    var players = data.players;
    var state = data.state;

    room_dict[room_id] = {"players": players, "state": state}
});