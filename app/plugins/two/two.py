from app.plugins.Plugin import Plugin


class Two(Plugin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('Plugin init ("two"):', args, kwargs)

    def execute(self):
        return 5-4