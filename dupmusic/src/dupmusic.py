'''
Scan a music collection for possible duplicates.

@since: Nov 17, 2012
@author: oblivion
'''
import sys
import os
import datetime
import scanner
import gui
from PyQt4 import QtCore, QtGui

__version__ = "0.9.3"

class Form(QtGui.QWidget):
    '''GUI application part.'''
    def __init__(self, parent=None):
        '''Init the main window.'''
        super(Form, self).__init__(parent)
        # Duplicates
        self.files = None
        # Selected files
        self.selected = dict()

        # PyQt4 GUI
        self.gui = gui.Ui_Form()
        self.gui.setupUi(self)
        self.callbacks = 0

        self.gui.pathEdit.setText('.')

        # Go click
        self.connect(self.gui.goButton, QtCore.SIGNAL('clicked()'), self.scan)
        # Browse click
        self.connect(self.gui.browseButton, QtCore.SIGNAL('clicked()'), self.directoryBrowse)
        # Add click
        self.connect(self.gui.addButton, QtCore.SIGNAL('clicked()'), self.addFile)
        # Remove click
        self.connect(self.gui.removeButton, QtCore.SIGNAL('clicked()'), self.removeFile)
        # Delete click
        self.connect(self.gui.deleteButton, QtCore.SIGNAL('clicked()'), self.deleteFiles)
        # Dup select
        self.connect(self.gui.dupWidget, QtCore.SIGNAL('currentItemChanged (QListWidgetItem *,QListWidgetItem *)'), self.updateFileWidget)
        # File select
        self.connect(self.gui.filesWidget, QtCore.SIGNAL('currentItemChanged (QListWidgetItem *,QListWidgetItem *)'), self.updateDetailsBrowser)

    def updateDupWidget(self):
        '''Update the dup list in the GUI.'''
        # Loop over each name
        for entry in self.files.keys():
            item = QtGui.QListWidgetItem(entry)
            self.gui.dupWidget.addItem(item)
        # Clear the details info
        self.updateDetailsBrowser(None)

    def updateFileWidget(self, item):
        '''Update file list.'''
        # Clear the list
        self.gui.filesWidget.clear()
        # Loop over duplicates if any files
        if self.files != None:
            for dup in self.files[item.text()]:
                # Cast to our binding class
                item = QDup(dup)
                self.gui.filesWidget.addItem(item)

    def updateDetailsBrowser(self, item):
        '''Update detailed file info'''
        if item == None:
            # Clear if none is selected
            self.gui.detailsBrowser.setPlainText('')
        else:
            self.gui.detailsBrowser.setHtml('<p>Size: ' + str(item.size)
                                            + '<br />Ext: ' + item.extension
                                            + '<br />Unique path: '
                                            + item.uniqueName
                                            + '<br />Duration: '
                                            + str(datetime.timedelta(seconds=item.duration)) + '</p>')

    def callback(self, filename):
        '''Callback from scanner with current file name.'''
        # Update label and repaint
        self.gui.statusLabel.setText(filename)
        # Don't repaint every time
        if self.callbacks == 0:
            self.gui.statusLabel.repaint()
        if self.callbacks == 10:
            self.callbacks = -1
        self.callbacks += 1

    def scan(self):
        '''Scan a directory.'''
        self.gui.statusLabel.setText('Scanning...')
        self.gui.statusLabel.repaint()
        self.gui.dupWidget.clear()
        self.gui.filesWidget.clear()
        self.gui.detailsBrowser.setPlainText('')
        self.gui.selectedWidget.clear()

        # Get path
        directory = self.gui.pathEdit.text()
        # Overwrite calback function
        scanner.callback = self.callback
        # Try scanning for duplicates
        try:
            self.files = scanner.collect_files(directory,
                                               self.gui.caseSense.checkState())
            self.updateDupWidget()
        except OSError as exception:
            QtGui.QMessageBox.critical(self, 'Error!', str(exception))
        self.gui.statusLabel.setText('Done.')

    def directoryBrowse(self):
        '''Browse for a directory.'''
        filename = QtGui.QFileDialog.getExistingDirectory(parent=self,
                                                          caption='Select directory.',
                                                          directory=self.gui.pathEdit.text(),
                                                          options=QtGui.QFileDialog.ShowDirsOnly)
        # Update edit widget
        self.gui.pathEdit.setText(filename)

    def addFile(self):
        '''Add a file to the selected list.'''
        try:
            item = self.gui.filesWidget.selectedItems()[0]
            if len(item.uniqueName) == 3:
                # Get filename if only extension is unique
                item.uniqueName = os.path.basename(item.fullpath)
            # Insert the item, the key is the unique part of the name
            self.selected[item.uniqueName] = item
            # Update the view
            self.updateSeletedWidget()
        except IndexError:
            pass

    def removeFile(self):
        '''Remove a file from the selected list.'''
        try:
            item = self.gui.selectedWidget.selectedItems()[0].text()
            del self.selected[item]
            # Update the view
            self.updateSeletedWidget()
        except IndexError:
            pass

    def deleteFiles(self):
        '''Delete all files in the selected list.'''
        # Get all items.
        items = self.gui.selectedWidget.findItems('*', QtCore.Qt.MatchWrap | QtCore.Qt.MatchWildcard)
        ret = QtGui.QMessageBox.warning(self, 'Warning!',
                                        'The files can not be restored.',
                                        QtGui.QMessageBox.Ok,
                                        QtGui.QMessageBox.Cancel,
                                        QtGui.QMessageBox.NoButton)
        if ret == QtGui.QMessageBox.Ok:
            for item in items:
                try:
                    os.remove(item.fullpath)
                except OSError as exception:
                    QtGui.QMessageBox.critical(self, 'Error!', str(exception))
        self.selected.clear()
        self.updateSeletedWidget()

    def updateSeletedWidget(self):
        '''Update the dup list in the GUI.'''
        self.gui.selectedWidget.clear()
        # Loop over each name
        for entry in self.selected.values():
            item = Selected(entry)
            self.gui.selectedWidget.addItem(item)


class Selected(scanner.Dup, QtGui.QListWidgetItem):
    '''Ties together data and listwidget items.'''
    def __init__(self, dup, parent=None):
        '''Init.'''
        scanner.Dup.__init__(self)
        QtGui.QListWidgetItem.__init__(self)

        self.fullpath = dup.fullpath
        self.size = dup.size
        self.extension = dup.extension
        self.uniqueName = dup.uniqueName
        self.duration = dup.duration

        self.setText(self.uniqueName)


class QDup(scanner.Dup, QtGui.QListWidgetItem):
    '''Ties together data and listwidget items.'''
    def __init__(self, dup, parent=None):
        '''Init.'''
        scanner.Dup.__init__(self)
        QtGui.QListWidgetItem.__init__(self)

        self.fullpath = dup.fullpath
        self.size = dup.size
        self.extension = dup.extension
        self.uniqueName = dup.uniqueName
        self.duration = dup.duration

        self.setText(self.fullpath)


def main():
    app = QtGui.QApplication(sys.argv)
    form = Form()

    form.show()
    app.exec()


if __name__ == '__main__':
    main()
