
import sys, os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget

class Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('win.ui', self)

        self.linePATH.setText(os.getcwd())

    def get_path(self):
        path = QFileDialog.getExistingDirectory(self, 'test', os.getcwd())

        if path not in ('', self.linePATH.text()):
            self.linePATH.setText(path)
            self.textLOG.appendPlainText(f'Path set to: {path}')

    def search_and_replace(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    win = Window()
    win.show()

    app.exec()
    sys.exit()
