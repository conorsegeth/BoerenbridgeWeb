var socket = io()

var username = null;
var room_id = null;

document.getElementById("join-room-form").addEventListener("submit", function(event) {
    event.preventDefault()
    username = document.getElementById("player-name").value;
    room_id = document.getElementById("room-id-input").value;

    if (username && room_id) {
        socket.emit("join room", { room_id: room_id, username: username });
    }
});

socket.on("exists", function(data) {
    window.location.href = window.location.href + "room" + "/" + room_id
    
});
socket.on("nonexistent", function(data) {
    alert("That game does not exist.")

});