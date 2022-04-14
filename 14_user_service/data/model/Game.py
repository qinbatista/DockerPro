from data.model.Base import Base

class Game(Base):
    table_name = "game"
    coloum = {
        "id": "",
        "name": ""
    }
    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)