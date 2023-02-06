var socket = io()

document.getElementById("join-room-form").addEventListener("submit", function(event) {
    event.preventDefault()
    var name = document.getElementById("player-name").value;
    var room_id = document.getElementById("room-id-input").value;

    if (name && room_id) {
        socket.emit("join room", { room_id: room_id, username: name });
    }
});
