var socket = io();

var username = null;
var room_id = null;

document.getElementById("join-room-form").addEventListener("submit", function(event) {
    event.preventDefault()
    username = document.getElementById("player-name").value;
    room_id = document.getElementById("room-id-input1").value;

    if (username && room_id) {
        socket.emit("join room", { room_id: room_id, username: username });
        document.cookie = `username=${username}; path=/`;
    }
});

socket.on("exists", function() {
    //window.location.href = window.location.href + "room" + "/" + room_id
    var new_url = '/room/' + room_id
    window.location.replace(new_url)
});

socket.on("nonexistent", function() {
    alert("That game does not exist.")
});

socket.on("full", function() {
    alert("That game is full.")
});

socket.on("started", function() {
    alert("That game has already started.")
})

socket.on("name taken", function() {
    alert("That name has been taken!")
})
