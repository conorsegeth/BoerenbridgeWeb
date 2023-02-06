from collections.abc import Iterable

class Player:
    def __init__(self, socket_id: str, username: str, player_number: int, is_admin=False) -> None:
        self.socket_id = socket_id
        self.username = username
        self.player_number = player_number
        self.is_admin = is_admin

class GameRoom:
    def __init__(self, room_id: str, players: Iterable[Player]) -> None:
        self.room_id = room_id
        self.players = players
