var socket = io();

var room_id = null;
var username = null;

document.getElementById("create-room-form").addEventListener("submit", function(event) {
    event.preventDefault();
    username = document.getElementById("player-name").value;
    room_id = document.getElementById("room-id-input2").value;

    if (username && room_id) {
        document.cookie = `username=${username}; path=/`;

        var num_players = document.getElementById("num-players").value;
        var bot_type = document.getElementById("bot-type").value;
        var deck_size = document.getElementById("deck-size").value;
        var step_size = document.getElementById("step-size").value;
        var reverse = document.getElementById("reverse").checked;

        socket.emit("create room", { 
            room_id: room_id, 
            num_players: num_players, 
            bot_type: bot_type, 
            deck_size: deck_size, 
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

// setInterval(function() {
//     socket.emit("test") // players request
// }, 1000);

// let tmp_list = [];
// socket.on("player names", function(data) {
//     const usernames = data.usernames
//     let list = document.getElementById("player-list");

//     usernames.forEach((name) => {
//         var has_name = tmp_list.includes(name)
//         if (!has_name) {
//             tmp_list.push(name)
//             let li = document.createElement("li");
//             li.innerText = name;
//             li.className = "player-list-items"
//             list.appendChild(li);
//         }
//     });
// });





