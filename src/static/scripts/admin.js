var socket = io();

document.getElementById("create-room-form").addEventListener("submit", function(event) {
    event.preventDefault();
    var name = document.getElementById("player-name").value;
    var room_id = document.getElementById("room-id-input").value;

    if (name && room_id) {
        socket.emit("create room", { room_id: room_id, admin_name: name });
    }
});
