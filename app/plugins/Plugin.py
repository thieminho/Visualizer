
""" Interface used to implement new algorithms used in app to process data"""
class Plugin:

    def __init__(self, *args, **kwargs):
        pass

    def execute(self):
        """ Function used to execute algorithm on data"""
        pass

    def fill_my_parameters(self, widget):
        """ Function used to fill widget with QWidgets with custom parameters needed to run algorithm """
        pass
