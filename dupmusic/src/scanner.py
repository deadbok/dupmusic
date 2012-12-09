'''
Functions to scan directories for duplicates.

@since: 2 Dec 2012
@author: oblivion
'''
import os
from hsaudiotag import auto

def listdirs(directory):
    '''list files in directory and sub directories.'''
    # Get entries in current directory
    files = os.listdir(directory)
    ret = list()

    if files != None:
        for filename in files:
            fullpath = os.path.join(directory, filename)
            # Insert name in the start of the list
            ret.insert(0, fullpath)
            if os.path.isdir(fullpath):
                ret.extend(listdirs(fullpath))
        return(ret)
    else:
        return(list())


class Dup(object):
    '''A duplicate file.'''
    def __init__(self):
        '''Init.'''
        self.fullpath = ''
        self.size = 0
        self.extension = ''
        self.uniqueName = ''
        self.duration = ''

    def set(self, filename):
        self.fullpath = filename
        self.size = os.path.getsize(filename)
        (_, self.extension) = os.path.splitext(filename)
        # Meta-data
        if not os.path.isdir(filename):
            tag = auto.File(filename)
            self.duration = tag.duration

def callback(parent=None, filename=''):
    print(filename)

def collect_files(directory, case_sensitive=True):
    '''Create a list of possibly duplicate files.'''
    files = listdirs(directory)
    # Use a set to detect duplicates
    unique_files = set()
    unique_files.add('.')
    dups = dict()
    firsts = dict()

    # Run through all files
    for filename in files:
        # Ignore directories
        if not os.path.isdir(filename):
            callback(filename)
            # Remove extension
            (noext, _) = os.path.splitext(filename)
            # Remove path
            if case_sensitive:
                name = os.path.basename(noext).strip()
            else:
                name = os.path.basename(noext).strip().lower()

            # Check if the name is known
            if name in unique_files:
                # Save data
                dup = Dup()
                dup.set(filename)

                # If we are the first
                if name not in dups:
                    dups[name] = list()
                    # Add first occurrence
                    first = Dup()
                    first.set(firsts[name])
                    dups[name].append(first)
                # Add duplicate
                dups[name].append(dup)
            else:
                # First occurrence
                unique_files.add(name)
                # Save data in dictionary of first occurrences
                firsts[name] = filename
    # Find unique part
    for dup_list in dups.values():
        # Get common part
        paths = list()
        for dup in dup_list:
            paths.append(dup.fullpath)
        common = os.path.commonprefix(paths)
        # Remove common part
        for dup in dup_list:
            dup.uniqueName = dup.fullpath.replace(common, '')


    return(dups)


