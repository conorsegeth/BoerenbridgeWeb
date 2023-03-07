var socket = io();

function get_cookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  };

let username = get_cookie("username");
let path_arr = window.location.pathname.split('/');
let room_id = path_arr[path_arr.length - 1];
socket.emit("joined", {username: username, room_id: room_id});

let settings = {}
socket.on("settings", function(data) {
    settings["max_players"] = data.max_players;
    settings["bot_type"] = data.bot_type;
    settings["step_size"] = data.step_size;
    settings["reverse"] = data.reverse;
});

var usernames_request = setInterval(function() {
    socket.emit("usernames request", {room_id: room_id});
}, 1000);

let tmp_list = [];
socket.on("usernames", function(data) {
    const usernames = data.usernames
    let list = document.getElementById("player-list");

    usernames.forEach((name) => {
        var has_name = tmp_list.includes(name)
        if (!has_name) {
            tmp_list.push(name)
            let li = document.createElement("li");
            li.innerText = name;
            li.className = "player-list-items"
            list.appendChild(li);
        }
    });
});

document.getElementById("start-btn").onclick = function() {
    socket.emit("attempt start", {room_id: room_id, username: username})
}

socket.on("start game", function() {
    document.getElementById("container").style.display = "none";
    document.getElementById("grid-container").style.display = "grid";
    clearInterval(usernames_request);
});

socket.on("not admin", function() {
    alert("Only the admin can start the game!")
})

function unload() {
    socket.emit("bye", {room_id: room_id});
};
