from data.db import execute as db_execute
from data.model.Base import Base


class GameExpiry(Base):
    table_name = "game_expiry"
    coloum = {
        "game_name": "",
        "channel": "",
        "login_expiry_date": None,
        "pay_expiry_date": None,
    }

    def __init__(self, **kwargs):
        super(GameExpiry, self).__init__(**kwargs)
