var socket = io();

var username = null;
var room_id = null;

document.getElementById("create-room-form").addEventListener("submit", function(event) {
    event.preventDefault();
    username = document.getElementById("player-name").value;
    room_id = document.getElementById("room-id-input").value;

    if (username && room_id) {
        socket.emit("create room", { room_id: room_id, admin_name: username });
    }
});

socket.on("exists", function(data) {
    window.location.href = window.location.href + "/" + room_id
});
socket.on("pre-existing", function(data) {
    alert("A game with that code already exists!")
});
