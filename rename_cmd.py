"""
Small UI program to (recursively) search a folder for files which fit a certain pattern and replace text in it (also the filename itself).

@Author: Florian W
"""
import os, re
from typing import List


def search_text(files: List[str], search_for: str, ignore_case: bool=True):
    """Searches for all matches of the entered string in the given files

    Parameters
    ----------
    files : List[str]
        files to be searched
    """
    # check if the case should be matched
    flag = 0
    if ignore_case:
        flag = re.IGNORECASE

    content     = bytes
    match_count = 0
    for f in files:
        # check file name
        fname = f[f.rfind('\\'):]
        cnt = len(re.findall(search_for, fname, flags=flag))

        if cnt > 0:
            print(f'{cnt} matches in filename: {f}')

        # check file content
        # open the file as bytes so we dont have to consider the encodings
        with open(f, 'rb') as file:
            content = file.read()

        matches = len(re.findall(str.encode(search_for), content, flags=flag))
        match_count += matches

        print(f'{matches} matches in file: {f}')

    print(f'Found "{search_for}" {match_count} times in {len(files)} files.')

def replace_text(files: List[str], search_for: str, replace_with: str, ignore_case: bool=True, duplicate_files: bool=False, rename_file_names: bool=True):
    """Searches and replaces the entered strings in the files.

    Parameters
    ----------
    files : List[str]
        list of paths+filenames of the files to be searched
    """
    # check if the case should be matched
    flag = 0
    if ignore_case:
        flag = re.IGNORECASE

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
        if duplicate_files:
            # place "_REPLACED" before the filending
            pos = f.rfind('.')
            new_filename = f[:pos] + '_REPLACED' + f[pos:]

        # create or replace the file with the new contents
        with open(new_filename, 'wb') as file:
            file.write(new_content)

        # if user selected "rename filenames"
        if rename_file_names:
            try:
                # get filename
                pos = new_filename.rfind('\\')
                fname = f[:pos] + re.sub(search_for, replace_with, f[pos:], flags=flag)
                # rename the file
                os.rename(new_filename, fname)
            except FileExistsError as e:
                # when the rename file already exists
                print(f'{e.args[1]} -> {new_filename}')

def get_matching_files(path: str, file_endings: List[str]=None, search_recursively: bool=False):
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
    if file_endings == None:
        file_endings = ['.tsv']

    # check files if they end with the given file endings
    if search_recursively:
        for root, _, file in os.walk(path):
            for f in file:
                if f.endswith(tuple(file_endings)):
                    file_list.append(root+'\\'+f)
    else:
        for f in os.listdir(path):
            if f.endswith(tuple(file_endings)):
                file_list.append(path+'\\'+f)

    return file_list


if __name__ == '__main__':
    path = input('Enter path:')

    if os.path.isdir(path) is False:
        print('Path does not exist!')
        quit()

    file_endings     = input('Enter File-Endings (default .tsv) like ".tsv, .csv, .dat":')
    search_recursive = input('Search recursively? default NO (Y/N):')
    search_for       = input('Search for:')
    ignore_case      = input('Ignore case? default YES (Y/N):')

    file_endings     = file_endings.split(', ')
    search_recursive = True  if search_recursive.lower() == 'y' else False
    ignore_case      = False if ignore_case.lower()      == 'n' else True

    files = get_matching_files(path, file_endings, search_recursive)
    search_text(files, search_for, ignore_case)

    try:
        replace_with = input(f'Enter text to replace "{search_for}" with:')
        duplicate    = input(f'Duplicate files? Else overwrite (Y/N):')
        duplicate    = True if duplicate.lower() == 'y' else False
        replace_text(files, search_for, replace_with, ignore_case, duplicate)
    except KeyboardInterrupt:
        print('\nOperation canceled')
