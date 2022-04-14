from data.model.Base import Base

class UserGame(Base):
    table_name = "user_game"
    coloum = {
        "user_id": "",
        "game_id": ""
    }
    def __init__(self, **kwargs):
        super(UserGame, self).__init__(**kwargs)
