from collections.abc import Iterable

class Player:
    def __init__(self, session_id: str, username: str, player_number: int, is_admin=False) -> None:
        self.session_id = session_id
        self.username = username
        self.player_number = player_number
        self.is_admin = is_admin

class GameRoom:
    def __init__(self, room_id: str) -> None:
        self.room_id = room_id
        self.players = {}
        self.state = "waiting for players"

    def add_player(self, player: Player) -> None:
        self.players[player.session_id] = player

    def get_player_session_ids(self):
        session_ids = []
        for sid in self.players:
            session_ids.append(sid)
        print(session_ids)
        return session_ids
