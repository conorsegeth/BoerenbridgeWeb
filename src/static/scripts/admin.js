var socket = io();

var username = null;
var room_id = null;

if (document.getElementById("create-room-form")) {
    document.getElementById("create-room-form").addEventListener("submit", function(event) {
        event.preventDefault();
        username = document.getElementById("player-name").value;
        room_id = document.getElementById("room-id-input").value;
    
        if (username && room_id) {
            socket.emit("create room", { room_id: room_id, admin_name: username });
        }
    });
}

socket.on("exists", function(data) {
    // window.location.href = window.location.href + "/" + room_id
    var new_url = '/admin/' + room_id
    window.location.replace(new_url)
});
socket.on("pre-existing", function(data) {
    alert("A game with that code already exists!")
});

setInterval(function() {
    socket.emit("test") // players request
}, 1000);

let tmp_list = [];
socket.on("player names", function(data) {
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





