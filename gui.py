import sys, suggester
from PyQt5.QtWidgets import (QWidget, QToolTip, QAction, qApp, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem,
                             QPushButton, QApplication, QDesktopWidget, QMainWindow, QFileDialog, QLabel)
from PyQt5.QtGui import QFont, QIcon
from music21 import converter
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self._suggester = suggester.Suggester()
        self._pickedfiles = []
        self._targetmidi = []
        self.inputlistview = None
        self.suggestionlistview = None
        self.target_lbl = None
        self.initUI()

    def initUI(self):

        targetButton = QPushButton('Select Target', self)
        targetButton.setToolTip('Select midi you want suggestions for')
        targetButton.resize(targetButton.sizeHint())
        targetButton.clicked.connect(self.picktargetmidi)

        self.inputlistview = QListWidget()
        self.inputlistview.itemPressed.connect(self.showmidi)

        inputlistview_lbl = QLabel(self)
        inputlistview_lbl.setText("Input MIDIs")
        inputlistview_lbl.adjustSize()

        suggestionlistview_lbl = QLabel(self)
        suggestionlistview_lbl.setText("Suggested segments")
        suggestionlistview_lbl.adjustSize()

        self.target_lbl = QLabel(self)
        self.target_lbl.setText("Please select target midi")
        self.target_lbl.adjustSize()

        self.suggestionlistview = QListWidget()

        suggestButton = QPushButton("Suggest", self)
        suggestButton.setToolTip('Suggest a continuation to target midi')
        suggestButton.clicked.connect(self.suggestmidi)
        saveButton = QPushButton("Save Suggestions", self)

        importAction = QAction(self.tr('Add MIDI file(s)'), self)
        importAction.setShortcut('Ctrl+O')
        importAction.setStatusTip('Add MIDI files to pool')
        importAction.triggered.connect(self.pickfiles)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.target_lbl)
        hbox.addWidget(targetButton)
        hbox.addWidget(suggestButton)
        hbox.addWidget(saveButton)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(inputlistview_lbl)
        vbox.addWidget(self.inputlistview)
        vbox.addLayout(hbox)
        vbox.addWidget(suggestionlistview_lbl)
        vbox.addWidget(self.suggestionlistview)


        cwidget = QWidget()
        cwidget.setLayout(vbox)

        self.setCentralWidget(cwidget)
        self.statusBar().showMessage('Ready')

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(importAction)

        self.center()
        self.setGeometry(150,20,100,100)
        self.setWindowTitle('Gnotestic')
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def pickfiles(self, point):
        dialog_result = QFileDialog.getOpenFileNames(self,
                                                     self.tr("Import Midi"), "", self.tr("Midi Files (*.mid *.midi)"))
        self._pickedfiles.extend(dialog_result[0])
        self.updatemidilist(dialog_result[0])

    def picktargetmidi(self, point):
        dialog_result = QFileDialog.getOpenFileName(self,
                                                    self.tr("Select Target Midi"), "", self.tr("Midi Files (*.mid *.midi)"))
        self._targetmidi = dialog_result[0]

    def updatemidilist(self, items):
        for item in items:
            witem = QListWidgetItem(item)
            self.inputlistview.addItem(witem)

    def showmidi(self, item):
        path = item.text()
        ms = converter.parse(path)
        ms.plot('pianoroll')

    def suggestmidi(self, point):
        #add midis to suggester
        if self._targetmidi and self.inputlistview.count():
            self._suggester.set_target_piece(self._targetmidi)
            for i in range(self.inputlistview.count()):
                self._suggester.add_midi(self.inputlistview.item(i).text())
        #update suggestion list
        self.suggestionlistview.clear()
        for suggestion in self._suggester.get_suggestions():
            self.suggestionlistview.addItem(QListWidgetItem(repr(suggestion)))




if __name__ == '__main__':

    app = QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())
