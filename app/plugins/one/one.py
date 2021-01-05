from app.plugins.Plugin import Plugin


class One(Plugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('Plugin init ("one"):', args, kwargs)

    def fill_my_parameters(self, widget):
        pass

    def execute(self):
        addition = 5+4
        result = str(addition) + " " + "hello world"
        return result




