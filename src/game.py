from collections.abc import Iterable
from enum import Enum
import random
from math import floor

random.seed(1)

class Suit(Enum):
    DIAMONDS = 1
    HEARTS = 2
    CLUBS = 3
    SPADES = 4

class Value(Enum):
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13


class Card:
    def __init__(self, value: Value, suit: Suit) -> None:
        self.value = value
        self.suit = suit
    
    def __repr__(self) -> str:
        return str(self.value.name + " of " + self.suit.name)


class Deck:
    def __init__(self) -> None:
        self.deck_lst = [Card(val, suit) for suit in (Suit) for val in (Value)]
    
    def shuffle(self) -> None:
        random.shuffle(self.deck_lst)
    
    def deal_cards(self, num_cards: int) -> Iterable[Card]:
        hand = []
        for i in range(num_cards):
            hand.append(self.deck_lst.pop(0))
        return hand
    
    def test(self, num_cards):
        hand = []
        for i in range(num_cards):
            hand.append(self.deck.pop(0))
        return hand


class Player:
    def __init__(self, session_id: str, username: str, player_number: int, is_admin=False) -> None:
        self.session_id = session_id
        self.username = username
        self.player_number = player_number
        self.is_admin = is_admin
    
    def __repr__(self) -> str:
        return f"{self.username} ({self.player_number})"

    def give_hand(self, hand: Iterable[Card]) -> None:
        self.hand = hand


class Bot(Player):
    def __init__(self, username: str, player_number: int, session_id=None) -> None:
        super().__init__(session_id, username, player_number)


class GameState:
    def __init__(self, deck: Deck, players: Iterable[Player], settings: dict) -> None:
        self.deck = deck
        self.players = players
        self.num_players = len(self.players)
        self.settings = settings
        self.phase = "guessing"
        self.guesses = {}
        self.won_tricks = {}
        self.scores = {player: 0 for player in self.players}
        self.player_turn = 1
        self.next_starting_turn = 2

        # TODO: Add bot to player list if bot type is specified
        if settings["bot_type"] is not None:
            self.num_players += 1
            pass
            
        # Deal initial cards to all players (max 13)
        deck.shuffle()
        if self.num_players < 4:
            num_cards = 13
        else:
            num_cards = floor(len(self.deck.deck_lst) / self.num_players)
        
        for player in self.players:
            player.give_hand(self.deck.deal_cards(num_cards)) 
        
    def __repr__(self) -> str:
        state_str = f"Deck: {self.deck.deck_lst}\n Players: {self.players}\n Hand: {self.players[0].hand}\n Phase: {self.phase}\n Guesses: {self.guesses}\n Won Tricks: {self.won_tricks}\n Scores: {self.scores}\n Turn: {self.player_turn}, Next starting turn: {self.next_starting_turn}"
        return state_str

class GameEngine: 
    # TODO: Continue after able to render states in browser
    def play_step(self, state: GameState) -> GameState:
        if state.phase == "guessing":
            final_guess = True if len(state.guesses) == state.num_players - 1 else False
            pass


class GameRoom:
    def __init__(self, room_id: str, settings: dict) -> None:
        self.room_id = room_id
        self.players = {}
        self.settings = settings
        self.state = "waiting for players"

    def add_player(self, player: Player) -> None:
        self.players[player.session_id] = player

    def get_player_sids(self) -> Iterable[str]:
        """
        Returns a list of player session ids that are in the room.
        """
        user_ids = []
        for playerID in self.players:
            user_ids.append(playerID)
        return user_ids
    
    def start_game(self) -> GameState:
        deck = Deck()
        players_lst = [self.players[sid] for sid in self.players]
        self.state = GameState(deck, players_lst, self.settings)
        print(self.state)


if __name__ == '__main__':
    deck = Deck()
    players = []
    for i in range(4):
        players.append(Player(None, f"player{i + 1}", i + 1))
    settings = {
        'max_players': len(players),
        'bot_type': None,
        'step_size': 1,
        'reverse': False}

    engine = GameEngine()

    game_state = GameState(deck, players, settings)
