var socket = io();

var room_id = null;
var username = null;

document.getElementById("create-room-form").addEventListener("submit", function(event) {
    event.preventDefault();
    username = document.getElementById("player-name").value;
    room_id = document.getElementById("room-id-input2").value;

    if (username && room_id) {
        document.cookie = `username=${username}; path=/`;

        var max_players = document.getElementById("max-players").value;
        var bot_type = document.getElementById("bot-type").value;
        var step_size = document.getElementById("step-size").value;
        var reverse = document.getElementById("reverse").checked;

        socket.emit("create room", { 
            room_id: room_id, 
            max_players: max_players, 
            bot_type: bot_type, 
            step_size: step_size,
            reverse: reverse,
        });
    }
});

socket.on("exists", function(data) {
    // window.location.href = window.location.href + "/" + room_id
    var new_url = '/room/' + room_id
    window.location.replace(new_url)
});
socket.on("pre-existing", function(data) {
    alert("A game with that code already exists!")
});

socket.on("no spaces", function() {
    alert("You can't put spaces in the game code.")
})
