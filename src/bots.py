from collections.abc import Iterable
from game import Player, PlayerPerspective, Card, RuleChecker, GameEngine, GameState, GameRoom
import tensorflow as tf
from tensorflow.python.keras.models import load_model
import numpy as np
import uuid
import random
import csv

class Bot(Player):
    def __init__(self, username: str, player_number: int, is_admin=False) -> None:
        id = str(uuid.uuid4())
        super().__init__(id, username, player_number, is_admin)

    def is_bot(self) -> bool:
        return True

    def get_valid_moves(self, perspective: PlayerPerspective) -> Iterable:
        valid_moves = []
        if perspective.phase == "guessing":
            if len(perspective.guesses) == perspective.num_players - 1:
                guess_total = sum(perspective.guesses.values())
                cant_guess = perspective.num_cards - guess_total
                valid_moves = [i for i in range(perspective.num_cards + 1) if i != cant_guess]
            else:
                valid_moves = [i for i in range(perspective.num_cards + 1)]
        else:
            for move in perspective.player_hand:
                if RuleChecker().is_valid_move(move, perspective.player_hand, perspective.leader_move):
                    valid_moves.append(move)

        return valid_moves


class RandBot(Bot):
    def __init__(self, username: str, player_number: int, is_admin=False) -> None:
        super().__init__(username, player_number, is_admin)

    def get_move(self, perspective: PlayerPerspective):
        return random.choice(self.get_valid_moves(perspective))


class NNBot(Bot):
    def __init__(self, username: str, player_number: int, is_admin=False) -> None:
        super().__init__(username, player_number, is_admin)
        self.model = load_model("src/static/model")
    
    def _get_input_data(self, move: Card, perspective: PlayerPerspective) -> Iterable[int]:
        input_data = []
        for val in one_hot_encode_card(move):
            input_data.append(val)
        
        hand = [0 for i in range(13)]
        for i, card in enumerate(self.hand):
            hand[i] = card

        for card in hand:
            for val in one_hot_encode_card(card):
                input_data.append(val)

        if self.username in perspective.guesses:
            input_data.append(perspective.guesses[self.username])
        elif isinstance(move, int):
            input_data.append(move)

        for player in perspective.won_tricks:
            if player == self.username:
                input_data.append(perspective.won_tricks[player])
        
        input_data.append(perspective.num_players)

        played = [0 for i in range(7)]
        for i, card in enumerate(perspective.played_cards.keys()):
            played[i] = card
        
        for card in played:
            for val in one_hot_encode_card(card):
                input_data.append(val)

        if perspective.leader_move == None:
            perspective.leader_move = 0
        for val in one_hot_encode_card(perspective.leader_move):
            input_data.append(val)
        
        return input_data


    def get_move(self, perspective):
        best_pred = float('inf')
        best_move = None
        for move in self.get_valid_moves(perspective):
            input_data = np.array(self._get_input_data(move, perspective))
            reshaped = np.reshape(input_data, (1, 377))
            reshaped_tensor = tf.convert_to_tensor(reshaped)
            prediction = self.model(reshaped_tensor)
            if prediction < best_pred:
                best_pred = prediction
                best_move = move

        return best_move


class RandomSearchBot(Bot):
    def __init__(self, username: str, player_number: int, num_simulations: int, max_depth: int, is_admin=False) -> None:
        super().__init__(username, player_number, is_admin)
        self.num_simulations = num_simulations
        self.max_depth = max_depth

    def _create_regression_data(self, data: Iterable[any]) -> None:
        encoded = []
        for i in range(14):
            for val in one_hot_encode_card(data[i]):
                encoded.append(val)

        for i in range(14, 17):
            encoded.append(data[i])
        
        for i in range(17, 25):
            if data[i] == None: 
                data[i] = 0
            for val in one_hot_encode_card(data[i]):
                encoded.append(val)
        
        encoded.append(data[25])

        with open("src/static/data3.csv", "a", newline="") as fd:
            writer = csv.writer(fd)
            writer.writerow(encoded)


    def get_move(self, perspective: PlayerPerspective):
        best_move = None
        best_score = float('inf')
        for move in self.get_valid_moves(perspective):
            # Generate regression data
            # data = [0 for i in range(26)]

            # my_guess = None
            # for name in perspective.guesses:
            #     if self.username == name:
            #         my_guess = perspective.guesses[name]
            # my_won = None
            # for name in perspective.won_tricks:
            #     if self.username == name:
            #         my_won = perspective.won_tricks[name]
            # data[0] = move
            # for i, card in enumerate(self.hand):
            #     data[i + 1] = card
            # if isinstance(move, int):
            #     data[14] = move
            # else:
            #     data[14] = my_guess
            # data[15] = my_won
            # data[16] = perspective.num_players
            # for i, card in enumerate(perspective.played_cards):
            #     data[i + 17] = card
            # data[24] = perspective.leader_move
            
            total_score = 0
            for i in range(self.num_simulations):
                state = perspective.generate_determinization()
                new_state = self.simulate(state, move, self.max_depth)
                score = self.evaluate(new_state)
                total_score += score

            average_score = total_score / self.num_simulations

            # Generate regression data
            # data[25] = average_score
            if average_score < best_score:
                best_score = average_score
                best_move = move

            # Generate regression data            
            # self._create_regression_data(data)
        
        return best_move

    def simulate(self, state: GameState, move: Card, max_depth: int) -> GameState:
        '''
        Simulate a number of steps from the provided state starting with the provided move.
        '''
        engine = GameEngine(state)
        engine.play_step(move)

        sim_bot = RandBot('', 0)
        for i in range(max_depth):
            while engine.state.player_turn != 999:
                current_player = engine.state.get_player_from_turn()
                sim_bot.give_hand(current_player.hand)
                sim_bot.username = current_player.username
                engine.play_step(sim_bot.get_move(engine.get_player_perspective(current_player, engine.state)))

            won = engine.state.won_tricks
            if sum(engine.state.won_tricks.values()) == engine.state.num_cards:
                break
            engine.play_step(None)
        
        return engine.state
        
    def evaluate(self, state: GameState) -> float:
        for player in state.players:
            if player.username == self.username:
                won = state.won_tricks[player]
                guess = state.guesses[player]
        
        # guess / (tricks_played * total_tricks)
        tricks_played = state.num_cards - len(state.players[0].hand)
        expected_proportion = guess * (tricks_played / state.num_cards)
        return abs(won - expected_proportion)

def one_hot_encode_card(card: Card) -> Iterable[int]:
    if isinstance(card, int):
        return [0 for i in range(17)]
    
    encoded = []
    for i in range(13):
        encoded.append(1) if card.value.value == i + 1 else encoded.append(0)
    for j in range(4):
        encoded.append(1) if card.suit.value == j + 1 else encoded.append(0)
    
    return encoded
        
if __name__ == '__main__':
    settings = {
            "max_players": 4,
            "bot_type": None,
            "step_size": 1,
            "reverse": False
            }
    
    NNWins = 0
    RSWins = 0

    for i in range(50):
        room = GameRoom('bruh', settings)

        print(f"Game {i + 1} started!")
        for j in range(4):
            if (i + j) % 2 == 0:
                bot = NNBot(f"NNBot{j + 1}", j + 1)
            else:
                bot = RandomSearchBot(f"RSBot{j + 1}", j + 1, 10, 5)

            room.add_player(bot)

        room.start_game()

        while room.engine.state.phase != "game over":
            while room.engine.state.player_turn != 999:
                current_player = room.engine.state.get_player_from_turn()
                move = current_player.get_move(room.engine.get_player_perspective(current_player, room.engine.state))
                room.do_player_move(move)

            room.do_player_move(None)

        winner = list(room.engine.state.scores.keys())[0]
        if isinstance(winner, NNBot):
            NNWins += 1
        elif isinstance(winner, RandomSearchBot):
            RSWins += 1

    print(f"NN Wins: {NNWins}, RS Wins: {RSWins}")


    
