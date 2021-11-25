
import sys, os
from typing import List
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget


class Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('win.ui', self)

        self.linePATH.setText(os.getcwd())

    def log(self, text: str):
        self.textLOG.appendPlainText(text)
        self.textLOG.verticalScrollBar().setValue(self.textLOG.verticalScrollBar().maximum())

    def ask_path(self):
        path = QFileDialog.getExistingDirectory(self, 'Select Folder', os.getcwd()).replace('/', '\\')

        if path not in ('', self.linePATH.text()):
            self.linePATH.setText(path)
            self.log(f'Path set to: {path}')

    def get_matching_files(self, path: str) -> List[str]:
        file_list    = []
        file_endings = []

        if self.cTsv.isChecked():
            file_endings.append('.tsv')
        if self.cCsv.isChecked():
            file_endings.append('.csv')
        if self.cTxt.isChecked():
            file_endings.append('.txt')
        if self.cCustom.isChecked():
            fend = self.sCustom.text()
            if len(fend)>0:
                if fend[0] != '.':
                    fend = '.'+fend
                file_endings.append(fend)

        if self.checkSUBFOLDERS.isChecked():
            for root, _, file in os.walk(path):
                for f in file:
                    if f.endswith(tuple(file_endings)):
                        file_list.append(root+'\\'+f)
        else:
            for f in os.listdir(path):
                if f.endswith(tuple(file_endings)):
                    file_list.append(path+'\\'+f)

        for f in file_list:
            self.log(f'Found: {f}')
        self.log(f'Found {len(file_list)} Files.')

        return file_list

    def search(self):
        path = self.linePATH.text()
        print(self.get_matching_files(path))

    def search_and_replace(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    win = Window()
    win.show()

    app.exec()
    sys.exit()
