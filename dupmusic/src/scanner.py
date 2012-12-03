'''
Functions to scan directories for duplicates.

@since: 2 Dec 2012
@author: oblivion
'''
import os

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

def collect_files(directory):
    '''Create a list of possibly duplicate files.0'''
    files = listdirs(directory)
    # Use a set to detect duplicates
    unique_files = set()
    dups = dict()
    firsts = dict()

    # Run through all files
    for filename in files:
        # Ignore directories
        if not os.path.isdir(filename):
            # Remove extension
            (noext, _) = os.path.splitext(filename)
            # Remove path
            name = os.path.basename(noext).strip().lower()
            if name in unique_files:
                # Save data
                dup = Dup()
                dup.fullpath = filename
                dup.size = os.path.getsize(filename)
                (_, dup.extension) = os.path.splitext(filename)

                # If we are the first
                if name not in dups:
                    dups[name] = list()
                    # Add first occurrence
                    dups[name].append(firsts[name])
                # Add duplicate
                dups[name].append(dup)
            else:
                # First occurrence
                unique_files.add(name)
                # Save data for later
                first = Dup()
                first.fullpath = filename
                first.size = os.path.getsize(filename)
                (_, first.extension) = os.path.splitext(filename)
                # Save data in dictionary of first occurrences
                firsts[name] = first
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


