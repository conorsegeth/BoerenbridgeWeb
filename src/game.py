from collections.abc import Iterable
from enum import Enum
import random
from copy import deepcopy
from math import floor


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
        val = self.value.name[:1] + self.value.name[1:].lower()
        suit = self.suit.name[:1] + self.suit.name[1:].lower()
        return str(val + " of " + suit)
    
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
        self.card_names = [card.get_name for card in self.deck_lst]
    
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

    def is_bot(self) -> bool:
        return False
    
    def get_move(self, perspective):
        pass


class GameState:
    def __init__(self, players: Iterable[Player], settings: dict) -> None:
        self.players = [None for player in players]
        for player in players:
            self.players[player.player_number - 1] = player
        self.num_players = len(self.players)
        
        self.settings = settings
        if self.settings:
            self.settings["step_size"] = int(self.settings["step_size"])
        
        self.phase = "guessing"
        
        self.guesses = {}
        self.won_tricks = {player: 0 for player in self.players}
        self.scores = {player: 0 for player in self.players}
        
        self.leader_move = None
        self.played_cards = {}
        self.seen_cards = []
        
        self.player_turn = 1
        self.next_up = [player for player in self.players if player.player_number != self.player_turn]
        self.next_starting_turn = 2
        
        self.ones_rounds = 0
        self.starting = None
        
        self.message = ["Game has started!"]
        
    def __repr__(self) -> str:
        state_str = f"Players: {self.players}\n Hand: {self.players[0].hand}\n Phase: {self.phase}\n Guesses: {self.guesses}\n Won Tricks: {self.won_tricks}\n Scores: {self.scores}\n Turn: {self.player_turn}, Next starting turn: {self.next_starting_turn}"
        return state_str
    
    def get_player_from_turn(self) -> Player:
        for player in self.players:
            if player.player_number == self.player_turn:
                return player

    def populate_next_up(self) -> None:
        self.next_up.clear()
        idx = self.player_turn - 1
        for i in range(len(self.players) - 1):
            idx += 1
            if idx > len(self.players) - 1:
                idx = 0

            self.next_up.append(self.players[idx])

    def increment_turn(self) -> None:
        self.player_turn += 1
        if self.player_turn > len(self.players):
            self.player_turn = 1

        if self.next_up:
            self.next_up.pop(0)

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

        # End game if cards are already at 13
        if self.num_cards == 13 and self.ones_rounds == self.num_players:
            self.phase = "game over"

        # Add to ones count
        if self.num_cards == 1:
            self.ones_rounds += 1

        # Reverse step size if reverse setting is true
        if self.ones_rounds == self.num_players and self.settings["reverse"] == True and self.settings["step_size"] > 0:
            self.settings["step_size"] *= -1

        # Change number of cards
        self.num_cards -= self.settings["step_size"]
        if self.num_cards < 1:
            self.num_cards = 1
        elif self.num_cards > 13:
            self.num_cards = 13
        
        # Set starting turn (to organise cards) if there is 1 card
        if self.num_cards == 1:
            self.starting = self.player_turn

        # End game if there are not enough cards to deal to all players
        if self.num_cards * self.num_players > 52:
            self.phase = "game over"
        else:
            # Deal new cards
            deck = Deck()
            deck.shuffle()
            for player in self.players:
                player.give_hand(deck.deal_cards(self.num_cards))
        
        # Handle game over if ones rounds complete & no reverse
        if self.ones_rounds == self.num_players and self.settings["reverse"] == False:
            self.phase = "game over"

        # Clear already played cards and seen cards
        self.played_cards.clear()
        self.seen_cards.clear()
        
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

        state_dict["turn"] = None
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

        state_dict["num_cards"] = self.num_cards

        state_dict["starting"] = None
        for player in self.players:
            if player.player_number == self.starting:
                state_dict["starting"] = player.username

        state_dict["message"] = self.message

        return state_dict


class PlayerPerspective():
    def __init__(self, player: Player, state: GameState) -> None:
        self.settings = state.settings

        self.player_name = player.username
        self.player_hand = player.hand

        self.num_players = state.num_players
        self.player_numbers = {player.username: player.player_number for player in state.players}
        self.hand_lengths = {player.username: len(player.hand) for player in state.players}

        self.phase = state.phase

        self.num_cards = state.num_cards

        self.guesses = {player.username: state.guesses[player] for player in state.guesses}
        self.won_tricks = {player.username: state.won_tricks[player] for player in state.won_tricks}
        self.scores = {player.username: state.scores[player] for player in state.scores}

        self.leader_move = state.leader_move
        self.played_cards = {card: state.played_cards[card].username for card in state.played_cards}
        self.seen_cards = state.seen_cards

        self.player_turn = state.player_turn
        self.next_starting_turn = state.next_starting_turn

        self.ones_rounds = state.ones_rounds

    def _remove_seen_cards(self, deck: Deck, seen_cards: Iterable[Card]) -> Deck:
        for card in deck.deck_lst[:]:
            for seen_card in seen_cards:
                if seen_card.get_name() == card.get_name():
                    deck.deck_lst.remove(card)
        return deck

    def generate_determinization(self) -> GameState:
        deck = Deck()
        deck = self._remove_seen_cards(deck, self.seen_cards + self.player_hand)
        deck.shuffle()
        
        players = []
        for player_name in self.player_numbers:
            player = Player(None, player_name, self.player_numbers[player_name])
            if player.username == self.player_name:
                player.give_hand(deepcopy(self.player_hand))
            else:
                player.give_hand(deck.deal_cards(self.hand_lengths[player_name]))
            players.append(player)

        # Don't know if all these deepcopies are needed but ah well
        # It is needed for seen_cards, DONT REMOVE

        state = GameState(players, self.settings)
        state.phase = deepcopy(self.phase)
        state.num_cards = deepcopy(self.num_cards)
        state.guesses = {player: self.guesses[player.username] for player in state.players if player.username in self.guesses}
        state.won_tricks = {player: self.won_tricks[player.username] for player in state.players}
        state.scores = {player: self.scores[player.username] for player in state.players}
        state.leader_move = self.leader_move
        
        for card in self.played_cards:
            for player in state.players:
                if player.username == self.played_cards[card]:
                    state.played_cards[card] = player
        
        state.seen_cards = deepcopy(self.seen_cards)
        state.player_turn = deepcopy(self.player_turn)
        state.next_starting_turn = deepcopy(self.next_starting_turn)
        state.ones_rounds = deepcopy(self.ones_rounds)

        return state


class RuleChecker:
    def is_valid_guess(self, guess, state):
        if len(state.guesses) == len(state.players) - 1:
            guess_total = 0
            for player in state.guesses:
                guess_total += state.guesses[player]
            
            if guess_total + guess == state.num_cards:
                return False
        
        return True
    
    def is_valid_move(self, move: Card, hand: Iterable[Card], leader_move: Card) -> bool:
        if not leader_move:
            return True

        can_follow_suit = False
        for card in hand:
            if card.get_suit() == leader_move.get_suit():
                can_follow_suit = True

        if move.get_suit() == leader_move.get_suit():
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

        new_scores = dict(sorted(new_scores.items(), key=lambda item: item[1], reverse=True))
        return new_scores


class GameEngine: 
    def __init__(self, state: GameState) -> None:
        self.state = state
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

    def deal_initial_cards(self) -> None:
        deck = Deck()
        deck.shuffle()

        if self.state.num_players < 4:
            self.state.num_cards = 13
        else:
            self.state.num_cards = floor(len(deck.deck_lst) / self.state.num_players)

        for player in self.state.players:
            player.give_hand(deck.deal_cards(self.state.num_cards)) 

    def get_player_perspective(self, player: Player, state: GameState) -> PlayerPerspective:
        return PlayerPerspective(player, state)

    def play_step(self, move: Card | int) -> GameState:
        if self.state.phase == "guessing":
            final_guess = True if len(self.state.guesses) == len(self.state.players) - 1 else False
            
            if self.rule_checker.is_valid_guess(move, self.state):  
                current_player = self.state.get_player_from_turn()
                self.state.guesses[current_player] = move

                self.state.increment_turn()

                if final_guess:
                    self.state.phase = "playing"
                    self.state.populate_next_up()

                self.state.message = [f"{current_player.username} guessed {move}."]

                return self.state, True
        else:
            # Handle trick or game reset when move is None
            if move == None:
                if self.state.players[0].hand:
                    winning_card = self.scorer.get_winning_card(self.state.played_cards, self.state.leader_move)
                    trick_winner = self.state.played_cards[winning_card]
                    
                    self.state.message = [f"{trick_winner.username} won with the {winning_card}"]
                    
                    self.state.trick_reset(trick_winner)
                else:
                    old_scores = self.state.scores.copy()

                    scores = self.scorer.calculate_points(self.state.guesses, self.state.won_tricks, self.state.scores)
                    self.state.scores = scores         
                    
                    winning_card = self.scorer.get_winning_card(self.state.played_cards, self.state.leader_move)
                    trick_winner = self.state.played_cards[winning_card]

                    low_name = 'low_name'
                    high_name = 'high_name'
                    highest = -999
                    lowest = 999
                    for player in self.state.scores:
                        points = self.state.scores[player] - old_scores[player]
                        if points > highest: 
                            highest = points
                            high_name = player.username
                        elif points < lowest:
                            lowest = points
                            low_name = player.username
                    if random.random() > 0.5:
                        self.state.message = [f"{trick_winner.username} won with the {winning_card}", f"{high_name} got the most points, going up by {highest}!"]
                    else:
                        self.state.message = [f"{trick_winner.username} won with the {winning_card}", f"{low_name} lost the most points, losing {abs(lowest)} :("]

                    self.state.game_reset()

                return self.state, True

            # Convert move to str if it is not already
            if isinstance(move, Card):
                move = move.get_name()

            move = move.split("_")
            move = Card(Value[move[0]], Suit[move[1]])

            first_move = True if len(self.state.played_cards) == 0 else False

            if self.rule_checker.is_valid_move(move, self.state.get_player_from_turn().hand, self.state.leader_move):
                current_player = self.state.get_player_from_turn()
                self.state.played_cards[move] = current_player
                self.state.seen_cards.append(move)

                if first_move:
                    self.state.leader_move = move
                
                # Remove card form players hand that was just played
                for card in current_player.hand[:]:
                    if card.get_name() == move.get_name():
                        current_player.hand.remove(card)      

                self.state.increment_turn()
                
                final_move_trick = True if len(self.state.played_cards) == len(self.state.players) else False
                if final_move_trick:
                    winning_card = self.scorer.get_winning_card(self.state.played_cards, self.state.leader_move)
                    trick_winner = self.state.played_cards[winning_card]

                    self.state.won_tricks[trick_winner] += 1

                    self.state.player_turn = 999
                
                self.state.message = [f"{current_player.username} played the {move}."]

                return self.state, True
        
        return self.state, False


class GameRoom:
    def __init__(self, room_id: str, settings: dict) -> None:
        self.room_id = room_id
        self.players = {}
        self.settings = settings
        self.started = False

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

    def get_player_from_sid(self, sid) -> Player:
        return self.players[sid]
    
    def start_game(self) -> GameState:
        self.started = True
        players_lst = [self.players[sid] for sid in self.players]
        state = GameState(players_lst, self.settings)
        self.engine = GameEngine(state)
        self.engine.deal_initial_cards()
        return self.engine.state

    def do_player_move(self, move) -> GameState:
        return self.engine.play_step(move)

if __name__ == '__main__':
    pass