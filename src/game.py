from collections.abc import Iterable
from enum import Enum
import random
from math import floor
import time

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
    
    def get_name(self) -> str:
        return f"{self.value.name}_{self.suit.name}"
    
    def get_suit(self) -> Suit:
        if self.value == Value.JACK and self.suit == Suit.CLUBS:
            return Suit.SPADES
        else:
            return self.suit


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
    def __init__(self, players: Iterable[Player], settings: dict) -> None:
        self.players = players
        self.num_players = len(self.players)
        self.settings = settings
        self.phase = "guessing"
        self.guesses = {}
        self.won_tricks = {player: 0 for player in self.players}
        self.scores = {player: 0 for player in self.players}
        self.played_cards = {}
        self.leader_move = None
        self.player_turn = 1
        self.next_up = [player for player in self.players if player.player_number != self.player_turn]
        self.next_starting_turn = 2

        # TODO: Add bot to player list if bot type is specified
        if settings["bot_type"] is not None:
            self.num_players += 1
            pass
            
        # Deal initial cards to all players (max 13)
        deck = Deck()
        deck.shuffle()
        if self.num_players < 4:
            self.num_cards = 13
        else:
            self.num_cards = floor(len(self.deck.deck_lst) / self.num_players)
        
        for player in self.players:
            player.give_hand(deck.deal_cards(self.num_cards)) 
        
    def __repr__(self) -> str:
        state_str = f"Deck: {self.deck.deck_lst}\n Players: {self.players}\n Hand: {self.players[0].hand}\n Phase: {self.phase}\n Guesses: {self.guesses}\n Won Tricks: {self.won_tricks}\n Scores: {self.scores}\n Turn: {self.player_turn}, Next starting turn: {self.next_starting_turn}"
        return state_str
    
    def get_player_from_turn(self) -> Player:
        for player in self.players:
            if player.player_number == self.player_turn:
                return player

    def populate_next_up(self) -> None:
        self.next_up.clear()
        for i in range(len(self.players)):
            i += 1
            if i > len(self.players):
                i = 1
        self.next_up.append(self.players[self.player_turn + i])

    def increment_turn(self) -> None:
        self.player_turn += 1
        if self.player_turn > len(self.players):
            self.player_turn = 1

        if self.next_up:
            self.next_up.pop(0)

        #TODO: Add something to add players back to next_up list

    def trick_reset(self, new_leader) -> None:
        self.player_turn = new_leader.player_number
        self.played_cards.clear()
        self.leader_move = None
        self.populate_next_up()
    
    def game_reset(self) -> None:
        # Set the new player starting turn and increment the next counter
        self.player_turn = self.next_starting_turn

        self.next_starting_turn += 1
        if self.next_starting_turn > len(self.players):
            self.next_starting_turn = 1
        
        # Switch phase back to guessing
        self.phase = "guessing"

        # Deal new cards
        deck = Deck()
        deck.shuffle()
        self.num_cards -= int(self.settings["step_size"])
        if self.num_cards < 1:
            self.num_cards = 1
        for player in self.players:
            player.give_hand(deck.deal_cards(self.num_cards))
        
        # Clear already played cards
        self.played_cards.clear()
        
        # Set leader move back to None
        self.leader_move = None

        # Set guesses and won tricks back to defaults
        self.guesses.clear()
        self.won_tricks = {player: 0 for player in self.players}

        # Populate next up list
        self.populate_next_up()


    # Could definitely be more efficient
    def as_dict(self) -> dict:
        state_dict = {}

        score_dict = {}
        for player in self.scores:
            score_dict[player.username] = self.scores[player]
        state_dict["scores"] = score_dict

        guess_dict = {}
        for player in self.guesses:
            guess_dict[player.username] = self.guesses[player]
        state_dict["guesses"] = guess_dict

        won_dict = {}
        for player in self.won_tricks:
            won_dict[player.username] = self.won_tricks[player]
        state_dict["won_tricks"] = won_dict

        for player in self.players:
            if player.player_number == self.player_turn:
                state_dict["turn"] = player.username

        next_list = []
        if self.next_up:
            for player in self.next_up:
                next_list.append(player.username)
        state_dict["next_up"] = next_list

        hands_dict = {}
        for player in self.players:
            tmp_hand = []
            for card in player.hand:
                tmp_hand.append(card.get_name())
            hands_dict[player.username] = tmp_hand
        state_dict["hands"] = hands_dict

        played_list = []
        for card in self.played_cards:
            played_list.append(card.get_name())
        state_dict["played_cards"] = played_list

        state_dict["phase"] = self.phase
        
        return state_dict


class RuleChecker:
    def is_valid_guess(self, guess, state):
        if len(state.guesses) == len(state.players) - 1:
            guess_total = 0
            for player in state.guesses:
                guess_total += state.guesses[player]
            
            if guess_total + guess == state.num_cards:
                return False
        
        return True
    
    def is_valid_move(self, move, state):
        if not state.leader_move:
            return True
        
        current_player = state.get_player_from_turn()

        can_follow_suit = False
        for card in current_player.hand:
            if card.get_suit() == state.leader_move.get_suit():
                can_follow_suit = True

        if move.get_suit() == state.leader_move.get_suit():
            return True
        
        if can_follow_suit == False:
            return True

        return False


class Scorer:
    def get_winning_card(self, played_cards: Iterable[Card, Player], leader_card: Card) -> Card:
        hierarchy = [
            Value.TWO, Value.THREE, Value.FOUR, Value.FIVE, 
            Value.SIX, Value.SEVEN, Value.EIGHT, Value.NINE, 
            Value.TEN, Value.JACK, Value.QUEEN, Value.KING, 
            Value.ACE]
        hierarchy_spades = [
            Value.TWO, Value.THREE, Value.FOUR, Value.FIVE, 
            Value.SIX, Value.SEVEN, Value.EIGHT, Value.NINE, 
            Value.TEN, Value.QUEEN, Value.KING, Value.ACE,
            Value.JACK]
        
        winner = leader_card

        for card in played_cards:
            print(card)
            # Return jack of clubs if it is played
            if card.value == Value.JACK and card.suit == Suit.CLUBS:
                return card

            # Highest spade becomes winner
            elif winner.suit == Suit.SPADES and card.suit == Suit.SPADES:
                lead_val = hierarchy_spades.index(winner.value)
                val = hierarchy_spades.index(card.value)
                if val > lead_val:
                    winner = card
            
            # Spade becomes winner if it is not currently a spade
            elif card.suit == Suit.SPADES:
                winner = card
            
            # Highest card of suit becomes winner
            elif card.suit == winner.suit:
                lead_val = hierarchy.index(winner.value)
                val = hierarchy.index(card.value)
                if val > lead_val:
                    winner = card

        return winner

    def calculate_points(self, guesses, won_tricks, scores) -> Iterable[Player, int]:
        new_scores = {}
        for player in guesses:
            guess = guesses[player]
            won = won_tricks[player]
            score = scores[player]

            if won == guess:
                points = won + 10
                new_scores[player] = score + points
            else:
                points = -1 * abs(guess - won)
                new_scores[player] = score + points

        new_scores = dict(sorted(new_scores.items, key=lambda item: item[1], reverse=True))
        return new_scores


class GameEngine: 
    def __init__(self, players: Iterable[Player], settings: dict) -> None:
        self.state = GameState(players, settings)
        self.rule_checker = RuleChecker()
        self.scorer = Scorer()

    def is_final_move_game(self):
        empty_hands = 0
        for player in self.state.players:
            if not player.hand:
                empty_hands += 1
        
        if empty_hands == len(self.state.players):
            return True
        
        return False

    def play_step(self, move) -> GameState:
        if self.state.phase == "guessing":
            if move.isdigit():
                move = int(move)
                final_guess = True if len(self.state.guesses) == len(self.state.players) - 1 else False
                
                if self.rule_checker.is_valid_guess(move, self.state):  
                    current_player = self.state.get_player_from_turn()
                    self.state.guesses[current_player] = move

                    self.state.increment_turn()

                    if final_guess:
                        self.state.phase = "playing"

                    return self.state, True    
        else:
            move = move.split("_")
            move = Card(Value[move[0]], Suit[move[1]])
            
            first_move = True if len(self.state.played_cards) == 0 else False
            final_move_trick = True if len(self.state.played_cards) == len(self.state.players) - 1 else False

            if self.rule_checker.is_valid_move(move, self.state):
                current_player = self.state.get_player_from_turn()
                self.state.played_cards[move] = current_player

                if first_move:
                    self.state.leader_move = move
                
                # Remove card form players hand that was just played
                for card in current_player.hand[:]:
                    if card.get_name() == move.get_name():
                        current_player.hand.remove(card)      

                self.state.increment_turn()
                
                if final_move_trick:
                    winning_card = self.scorer.get_winning_card(self.state.played_cards, self.state.leader_move)
                    trick_winner = self.state.played_cards[winning_card]
                    self.state.won_tricks[trick_winner] += 1
                    self.state.trick_reset(trick_winner)

                final_move_game = self.is_final_move_game()
                if final_move_game:
                    scores = self.scorer.calculate_points(self.state.guesses, self.state.won_tricks, self.state.scores)
                    self.state.scores = scores
                    self.state.game_reset()

                return self.state, True
        
        return self.state, False



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
        players_lst = [self.players[sid] for sid in self.players]
        self.engine = GameEngine(players_lst, self.settings)
        return self.engine.state

    def do_player_move(self, move) -> GameState:
        return self.engine.play_step(move)

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
