from collections.abc import Iterable

class Player:
    def __init__(self, user_id: str, username: str, player_number: int, is_admin=False) -> None:
        self.user_id = user_id
        self.username = username
        self.player_number = player_number
        self.is_admin = is_admin

class GameRoom:
    def __init__(self, room_id: str) -> None:
        self.room_id = room_id
        self.players = {}
        self.state = "waiting for players"

    def add_player(self, player: Player) -> None:
        self.players[player.user_id] = player

    def get_player_uids(self) -> Iterable[str]:
        """
        Returns a list of player user ids that are in the room.
        """
        user_ids = []
        for playerID in self.players:
            user_ids.append(playerID)
        return user_ids

