class Plugin:
    def __init__(self, *args, **kwargs):
        print('Plugin init ("one"):', args, kwargs)

    def execute(self, a, b):
        addition = a + b
        result = str(addition) + " " + "hello world"
        return result




