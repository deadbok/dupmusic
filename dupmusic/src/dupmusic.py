'''
Scan a music collection for possible duplicates.

@since: Nov 17, 2012
@author: oblivion
'''
import sys
import scanner
import gui
from PyQt4 import QtCore, QtGui

__version__ = "0.2.0"

class Form(QtGui.QWidget):
    '''GUI application part.'''
    def __init__(self, parent=None):
        '''Init the main window.'''
        super(Form, self).__init__(parent)

        self.files = None

        self.gui = gui.Ui_Form()
        self.gui.setupUi(self)

        self.gui.pathEdit.setText('/media/7c06c506-b8da-48b2-a5b2-d6a5dabd2e2e/Music.mix')

        # Go click
        self.connect(self.gui.goButton, QtCore.SIGNAL('clicked()'), self.scan)
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
        self.gui.filesWidget.clear()
        if self.files != None:
            for dup in self.files[item.text()]:
                item = QDup(dup)
                self.gui.filesWidget.addItem(item)

    def updateDetailsBrowser(self, item):
        '''Update detailed file info'''
        if item == None:
            self.gui.detailsBrowser.setPlainText('')
        else:
            self.gui.detailsBrowser.setHtml('<p>Size: ' + str(item.size)
                                            + '<br />Ext: ' + item.extension
                                            + '<br />Unique path: '
                                            + item.uniqueName + '</p>')

    def scan(self):
        '''Scan a directory.'''
        self.gui.statusLabel.setText('Scanning...')
        self.gui.statusLabel.show()
        directory = self.gui.pathEdit.text()
        try:
            self.files = scanner.collect_files(directory)
            self.updateDupWidget()
        except OSError as exception:
            QtGui.QMessageBox.critical(self, 'Error!', str(exception))
        self.gui.statusLabel.setText('')



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

        self.setText(self.fullpath)


def main():
    app = QtGui.QApplication(sys.argv)
    form = Form()

    form.show()
    app.exec()


if __name__ == '__main__':
    main()
