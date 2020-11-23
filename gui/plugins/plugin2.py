class Plugin:
    def __init__(self, *args, **kwargs):
        print('Plugin init ("two"):', args, kwargs)

    def execute(self, a, b):
        return a-b