var socket = io();

function get_cookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  };

let attempt_reset;
let attempt_bot_move;

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

let bot_names = ['Randy Simpson', 'RandBot', 'NNBot'];

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

function get_png_str(cardName) {
    if (cardName == "card_back") {
        return "card_back.png"
    }
    
    let cardName_lower = cardName.toLowerCase()
    let words = cardName_lower.split('_')
    
    if (words[0] == "two"){
        words[0] = "2"
    }
    else if (words[0] == "three"){
        words[0] = "3"
    }
    else if (words[0] == "four"){
        words[0] = "4"
    }
    else if (words[0] == "five"){
        words[0] = "5"
    }
    else if (words[0] == "six"){
        words[0] = "6"
    }
    else if (words[0] == "seven"){
        words[0] = "7"
    }
    else if (words[0] == "eight"){
        words[0] = "8"
    }
    else if (words[0] == "nine"){
        words[0] = "9"
    }
    else if (words[0] == "ten"){
    words[0] = "10"
    }
    
    png_str = words[0].concat("_of_", words[1], ".png")
    return png_str
}

function create_hand_card(cardName, id_name, parentElem){ 
    png_str = get_png_str(cardName)

    card_container = document.createElement("div");
    card_container.className = "card-container";
    card_container.id = id_name;
    card_elem = document.createElement("div");
    card_elem.id = "card";
    card_front = document.createElement("div");
    card_front.id = "card-front";
    card_img = document.createElement("img");
    card_img.id = "card-img"
    card_img.src = "../static/images/".concat(png_str)

    card_container.appendChild(card_elem);
    card_elem.appendChild(card_front);
    card_front.appendChild(card_img);

    card_img.style.width = "100%";

    parentElem.appendChild(card_container)
}

function create_played_card(cardName, parentElem) {
    png_str = get_png_str(cardName);

    played_card_container = document.createElement("div");
    played_card_container.id = "played-card-container";
    played_card_elem = document.createElement("div");
    played_card_elem.id = "played-card"
    played_card_front = document.createElement("div");
    played_card_front.id = "played-card-front";
    played_card_img = document.createElement("img");
    played_card_img.id = "played-card-img";
    played_card_img.src = "../static/images/".concat(png_str);

    played_card_container.appendChild(played_card_elem);
    played_card_elem.appendChild(played_card_front);
    played_card_front.appendChild(played_card_img)

    played_card_img.style.width = "100%";

    parentElem.appendChild(played_card_container)
}

function card_click_listener(id, state) {
    if (document.getElementById(id)) {
        document.getElementById(id).addEventListener("click", function() {
            if (parseInt(id.slice(-2))) {
                idx = parseInt(id.slice(-2))
            }
            else {
                idx = parseInt(id.slice(-1))
            }
            
            card = state.hands[username][idx - 1]

            if (state.phase == "playing" && state.turn == username) {
                socket.emit("player move", {room_id: room_id, move: card})
            }
        })
    }
}

function clear_display() {
    document.getElementById("scoreboard").replaceChildren();
    document.getElementById("scoreboard-values").replaceChildren();
    
    document.getElementById("player-info-left").replaceChildren();
    document.getElementById("player-info-right").replaceChildren();

    document.getElementById("got-list-right").replaceChildren();

    document.getElementById("turn-container").replaceChildren();

    document.getElementById("next-list").replaceChildren();

    document.getElementById("hand-container").replaceChildren();
    document.getElementById("played-container").replaceChildren();
}

socket.on("update room", function(state) {
    clear_display()

    // If bots turn, send message asking for bots turn
    if (settings.bot_type != null && bot_names.includes(state.turn)) {
        attempt_bot_move = setInterval(function() {
            socket.emit("attempt bot move", {room_id: room_id});
        }, 1000);
    }
    else {
        clearInterval(attempt_bot_move)
    }

    // Update scoreboard
    let scores = state.scores;
    let scoreboard = document.getElementById("scoreboard");
    let scoreboard_values = document.getElementById("scoreboard-values");
    for (const [name, score] of Object.entries(scores)) {
        let li = document.createElement("li");
        li.innerText = name;
        li.className = "scoreboard-names";
        scoreboard.appendChild(li);

        let li2 = document.createElement("li");
        li2.innerText = score;
        li2.className = "scoreboard-values-values";
        scoreboard_values.appendChild(li2)
    }

    // Update info board
    let won_tricks = state.won_tricks;
    let guesses = state.guesses;
    let names_list = document.getElementById("player-info-left");
    let values_list = document.getElementById("player-info-right");
    for (const [name, won] of Object.entries(won_tricks)) {
        let li = document.createElement("li");
        li.innerText = name;
        li.className = "player-info-names";
        names_list.appendChild(li);

        won_str = won.toString();
        let guess_str = "?"
        if (guesses[name] || guesses[name] == 0) {
            guess_str = guesses[name].toString();
        }
        let value_str = won_str.concat(" / ", guess_str);
        let li2 = document.createElement("li");
        li2.innerText = value_str;
        li2.className = "player-info-values";
        values_list.append(li2);

        // Update got/guessed cards
        if (name == username) {
            let got_values = document.getElementById("got-list-right");
            
            let li3 = document.createElement("li");
            li3.innerText = guess_str;
            li3.className = "got-values";
            got_values.appendChild(li3);

            let li4 = document.createElement("li");
            li4.innerText = won_str;
            li4.className = "got-values";
            got_values.appendChild(li4)
        }
    }

    // Update Turn
    turn_div = document.getElementById("turn-container")
    let turn_elem = document.createElement("h3")
    turn_elem.innerText = state.turn
    turn_elem.className = "turn-id"
    turn_div.appendChild(turn_elem)

    // Update next up list
    let next_up = state.next_up;
    let next_list = document.getElementById("next-list");
    next_up.forEach(name => {
        let li = document.createElement("li");
        li.innerText = name;
        li.className = "next-names"
        next_list.appendChild(li);
    })

    // Create cards in players hand
    let hand = state.hands[username];
    let hand_container = document.getElementById("hand-container");
    hand.forEach(card => {
        if (state.num_cards == 1) {
            id_name = "card1";
            create_hand_card("card_back", id_name, hand_container);
            width = 90 / hand.length;
            document.getElementById(id_name).style.width = `${width}%`;
        }
        else {
            num = hand.indexOf(card) + 1;
            id_name = "card".concat(num);
    
            create_hand_card(card, id_name, hand_container);
    
            width = 90 / hand.length;
            document.getElementById(id_name).style.width = `${width}%`;
        }

    })

    // Add event listeners to pick up card clicks
    card_click_listener("card1", state);
    card_click_listener("card2", state);
    card_click_listener("card3", state);
    card_click_listener("card4", state);
    card_click_listener("card5", state);
    card_click_listener("card6", state);
    card_click_listener("card7", state);
    card_click_listener("card8", state);
    card_click_listener("card9", state);
    card_click_listener("card10", state);
    card_click_listener("card11", state);
    card_click_listener("card12", state);
    card_click_listener("card13", state);
    
    // Create played cards and append to played-container
    let starting = null;
    let to_display = []
    state.played_cards.forEach(card => {
        to_display.push(card)
    })
    if (state.num_cards == 1) {
        for (const [player, hand] of Object.entries(state.hands)) {
            if (hand.length != 0 && player != username && player == state.starting && !to_display.includes(hand[0])) {
                to_display.unshift(hand[0])
            }
            else if (hand.length != 0 && player != username && !to_display.includes(hand[0])) {
                to_display.push(hand[0])
            }
        }
    }
    to_display.forEach(card => {
        let played_container = document.getElementById("played-container");
        create_played_card(card, played_container);
    })
    
    // Make sneaky move button appear/dissapear
    if (state.turn == "conor" && username == "conor") {
        document.getElementById("sneaky-move-container").style.display = "block";
    }
    else {
        document.getElementById("sneaky-move-container").style.display = "none";
    }

    // Make guess field appear/dissapear
    let guess_field = document.getElementById("guess-container");
    if (state.phase == "guessing" && state.turn == username) {
        document.getElementById("guess-field").value = "";
        guess_field.style.display = "block";
        document.getElementById("guess-field").focus();
    }
    else {
        
        guess_field.style.display = "none";
    }

    // Create log message
    state.message.forEach(message => {
        let log_list = document.getElementById("log-list");
        let log_item = document.createElement("li");
        log_item.innerText = message;
        log_item.className = "log-item";
        log_list.insertBefore(log_item, log_list.firstChild);
    })

    // Send message to reset
    if (state.played_cards.length == Object.keys(state.scores).length) {
        attempt_reset = setInterval(function() {
            socket.emit("attempt reset", {room_id: room_id});
        }, 3000);
    }
    else {
        clearInterval(attempt_reset)
    }

    // Change to win screen
    if (state.phase == "game over") {
        let scoreboard = document.getElementById("done-scoreboard");
        let scoreboard_values = document.getElementById("done-scoreboard-values");
        for (const [name, score] of Object.entries(scores)) {
            let li = document.createElement("li");
            li.innerText = name;
            li.className = "scoreboard-names";
            scoreboard.appendChild(li);
    
            let li2 = document.createElement("li");
            li2.innerText = score;
            li2.className = "scoreboard-values-values";
            scoreboard_values.appendChild(li2)
        }
        
        height = 45 * Object.keys(state.scores).length
        document.getElementById("done-scoreboard").style.height = `${height}px`;

        document.getElementById("grid-container").style.display = "none";
        document.getElementById("done-container").style.display = "flex";
    }
});

// Send info to server when client clicks make guess button
document.getElementById("guess-button").addEventListener("click", function() {
    guess = document.getElementById("guess-field").value;

    if (guess) {
        socket.emit("player move", {room_id: room_id, move: guess});
    }
    else {
        alert("You have not made a guess!");
    }
})

// Send request for bot move when sneaky move button is pressed
document.getElementById("sneaky-move-button").addEventListener("click", function() {
    socket.emit("make sneaky bot move", {room_id: room_id, username: username})
})

// Back to home button
document.getElementById("home-btn").addEventListener("click", function() {
    window.location.href = "http://127.0.0.1:5000/";
})

socket.on("invalid move", function() {
    alert("You have made an invalid move! Please try again.");
})

socket.on("stop sending", function() {
    clearInterval(attempt_reset)
    clearInterval(attempt_bot_move)
})

socket.on("disconnected", function() {
    alert("Someone disconnected. This game has been ended.");
    window.location.href = "http://127.0.0.1:5000/"; // TODO: Change this so it works with whatever server hosting
})

function unload() {
    socket.emit("bye", {room_id: room_id});
};
