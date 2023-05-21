from collections.abc import Iterable
from game import GameRoom
from bots import RandomSearchBot, NNBot
import pandas as pd
import csv
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.optimizers import adam_v2, adadelta_v2
from tensorflow.python.keras.losses import mae
from concurrent.futures import ProcessPoolExecutor
from tensorflow.python.keras.models import load_model

def play_game(num_bots: int) -> None:
    settings = {
            "max_players": 7,
            "bot_type": None,
            "step_size": 1,
            "reverse": True
            }
    
    room = GameRoom('bruh', settings)

    for i in range(num_bots):
        bot = RandomSearchBot(f"RSBot{i + 1}", i + 1, 500, 13)
        room.add_player(bot)

    room.start_game()

    while room.engine.state.phase != 'game over':
        while room.engine.state.player_turn != 999:
            current_player = room.engine.state.get_player_from_turn()
            move = current_player.get_move(room.engine.get_player_perspective(current_player, room.engine.state))
            room.do_player_move(move)

        room.do_player_move(None)

def build_and_compile_regression_model():
    model = Sequential()
    model.add(Dense(550, input_shape=(377,), activation='relu'))
    model.add(Dense(550, activation='relu'))
    model.add(Dense(225, activation="relu"))
    model.add(Dense(1))

    model.compile(loss=mae, optimizer=adam_v2.Adam(learning_rate=0.001))
    return model

def train_regression_model(model):
    x = pd.read_csv("src/static/data.csv", header=None)
    y = x.pop(x.columns[-1])

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=112358)
    history = model.fit(x_train, y_train, epochs=30, batch_size=256, validation_split=0.1)

    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title(f'Loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='upper left')
    plt.show()

    # results = model.evaluate(x_test, y_test)
    # print(f"Loss: {results}")

    model.save("src/static/model3")

def build_and_compile_classification_model():
    model = Sequential()
    model.add(Dense(340, input_shape=(683,), activation='relu'))
    model.add(Dense(17, activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer=adam_v2.Adam(learning_rate=0.01), metrics=['accuracy'])
    return model

def train_classification_model(model):
    df = pd.read_csv("src/static/data2.csv", header=None)
    x = df.iloc[:, :683]
    y = df.iloc[:, -17:]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1)

    history = model.fit(x_train, y_train, epochs=50, batch_size=512, validation_split=0.1)

    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title(f'Loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='upper left')
    plt.savefig("loss_graph.png")
    plt.clf()

    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title(f'Accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'val'], loc='upper left')
    plt.savefig("accuracy_graph.png")
    plt.clf()

def task(arg):
    count = 0
    for i in range(arg):
        count += 1
        for i in range(3, 7):
            if i == 3:
                print(f"{count}: {i}")
                play_game(i)
            if i == 4:
                print(f"{count}: {i}")
                play_game(i)
            if i == 5:
                print(f"{count}: {i}")
                play_game(i)
            if i == 6:
                print(f"{count}: {i}")
                play_game(i)

if __name__ == '__main__':
    # with ProcessPoolExecutor(6) as exe:
    #     exe.map(task, range(1, 600))

    # model = build_and_compile_regression_model()
    # train_regression_model(model)

    x = pd.read_csv("src/static/data3.csv", header=None)
    y = x.pop(x.columns[-1])

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=112358)
    
    model = load_model('src/static/model')

    results = model.evaluate(x_test, y_test)
    print(f"Model Loss: {results}")

