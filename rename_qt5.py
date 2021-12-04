"""
Small UI program to (recursively) search a folder for files which fit a certain pattern and replace text in it (also the filename itself).

@Author: Florian W
"""
import sys, os, re
from typing import List
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget
from ui.win import Ui_Window


class Window(QWidget, Ui_Window):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.linePATH.setText(os.getcwd())

    def clear_log(self):
        """clears the QPlainTextEdit widget"""
        self.textLOG.clear()

    def log(self, text: str):
        """Appends text to the QPlainTextEdit widget

        Parameters
        ----------
        text : str
            text to append
        """
        self.textLOG.appendPlainText(text)
        self.textLOG.verticalScrollBar().setValue(self.textLOG.verticalScrollBar().maximum())

    def ask_path(self):
        """Opens a file dialog in which the user can select the starting path"""
        path = QFileDialog.getExistingDirectory(self, 'Select Folder', os.getcwd()).replace('/', '\\')

        if path not in ('', self.linePATH.text()):
            self.linePATH.setText(path)
            self.log(f'Path set to: {path}')

    def search_text(self, files: List[str]):
        """Searches for all matches of the entered string in the given files

        Parameters
        ----------
        files : List[str]
            files to be searched
        """
        search_for   = self.lineSEARCH.text()

        # check if the case should be matched
        flag = re.IGNORECASE
        if self.checkMATCH.isChecked():
            flag = 0

        content     = bytes
        match_count = 0
        for f in files:
            # check file name
            fname = f[f.rfind('\\'):]
            cnt = len(re.findall(search_for, fname, flags=flag))

            if cnt > 0:
                self.log(f'{cnt} matches in filename: {f}')

            # check file content
            # open the file as bytes so we dont have to consider the encodings
            with open(f, 'rb') as file:
                content = file.read()

            matches = len(re.findall(str.encode(search_for), content, flags=flag))
            match_count += matches

            self.log(f'{matches} matches in file: {f}')

        self.log(f'Found "{search_for}" {match_count} times in {len(files)} files.')

    def replace_text(self, files: List[str]):
        """Searches and replaces the entered strings in the files.

        Parameters
        ----------
        files : List[str]
            list of paths+filenames of the files to be searched
        """
        search_for   = self.lineSEARCH.text()
        replace_with = self.lineREPLACE.text()

        # check if the case should be matched
        flag = re.IGNORECASE
        if self.checkMATCH.isChecked():
            flag = 0

        content     = bytes
        new_content = bytes
        for f in files:
            # open the file as bytes so we dont have to consider the encodings
            with open(f, 'rb') as file:
                content = file.read()

            # replace the text via regex
            new_content = re.sub(str.encode(search_for), str.encode(replace_with), content, flags=flag)

            # new filname depends if the user selected "duplicate" or "overwrite"
            # if overwrite, filename stays the same
            new_filename = f
            if self.radioDUPLICATE.isChecked():
                # place "_REPLACED" before the filending
                pos = f.rfind('.')
                new_filename = f[:pos] + '_REPLACED' + f[pos:]

            # create or replace the file with the new contents
            with open(new_filename, 'wb') as file:
                file.write(new_content)

            # if user selected "rename filenames"
            if self.checkRENAME.isChecked():
                try:
                    # get filename
                    pos = new_filename.rfind('\\')
                    fname = f[:pos] + re.sub(search_for, replace_with, f[pos:], flags=flag)
                    # rename the file
                    os.rename(new_filename, fname)
                except FileExistsError as e:
                    # when the rename file already exists
                    self.log(f'{e.args[1]} -> {new_filename}')


    def get_matching_files(self, path: str):
        """Returns a list with path+filename to the files which fit the selected file-endings

        Parameters
        ----------
        path : str
            path to (recursively) search in

        Returns
        -------
        List[str]
            files which fit the criteria
        """
        file_list    = []
        file_endings = []

        # check the selected file endings
        if self.cTsv.isChecked():
            file_endings.append('.tsv')
        if self.cCsv.isChecked():
            file_endings.append('.csv')
        if self.cTxt.isChecked():
            file_endings.append('.txt')
        if self.cCustom.isChecked():
            fend = self.sCustom.text()
            # ending must start with a dot
            if len(fend)>0:
                if fend[0] != '.':
                    fend = '.'+fend
                file_endings.append(fend)

        # check files if they end with the given file endings
        if self.checkSUBFOLDERS.isChecked():
            self.log(f'Searching in {path} recursively')
            for root, _, file in os.walk(path):
                for f in file:
                    if f.endswith(tuple(file_endings)):
                        file_list.append(root+'\\'+f)
        else:
            self.log(f'Searching in {path}')
            for f in os.listdir(path):
                if f.endswith(tuple(file_endings)):
                    file_list.append(path+'\\'+f)

        for f in file_list:
            self.log(f'Found: {f}')
        self.log(f'Found {len(file_list)} files.')

        return file_list

    def search(self):
        path = self.linePATH.text()
        self.clear_log()

        files = self.get_matching_files(path)

        self.search_text(files)

    def search_and_replace(self):
        path = self.linePATH.text()
        self.clear_log()

        files = self.get_matching_files(path)

        self.replace_text(files)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    win = Window()
    win.show()

    app.exec()
    sys.exit()
