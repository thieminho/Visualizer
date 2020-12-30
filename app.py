import sys

from PyQt5.QtWidgets import QApplication

import gui.gui

mainWindow = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = gui.gui.App()
    sys.exit(app.exec_())
