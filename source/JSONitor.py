'''


TODO
add drag and drop
add syntax highlighting
add comparison
add an About
logger
save temp files/autosave
Use json file for ui colors/settings
Add goto line
bookmarking
find and replace
conversion to (xml, csv, yaml)
Undo stack
validation
copy to clipboard
format/Beautify
Minimize/compact
Feedback/email
Tree view?
Form view?
use margin clicks for reordering elements



'''


import sys, os, re
# print(sys.version_info[0])
# import PyQt5
# help(PyQt5)
# from PyQt5 import uic
from PyQt5 import uic

# from PyQt5 import uic, QtWidgets
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *

# from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QFileDialog, QMessageBox
# from PyQt5.QtGui import QPainter, QColor, QPen
# from PyQt5.QtGui import QIcon
# from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *

# import syntax
import random

################
# Logger Setup #
################
import logging
import getpass

appTitle = 'JSONitor'

userName = getpass.getuser()

# Log File
sourcePath = os.path.dirname(os.path.realpath(__file__))
logFileName = '{}.log'.format(appTitle)
logFile = '{}/{}'.format(sourcePath, logFileName)


print('Logfile is {}'.format(logFile))
logger = logging.getLogger('{} Logger'.format(appTitle))
logger.setLevel(logging.INFO)
fh = logging.FileHandler(logFile)
fh.setLevel(logging.INFO)

# Version Number
versionNumber = '1.0.1'

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s {} - {} - %(levelname)s - %(message)s'.format(versionNumber, userName))
fh.setFormatter(formatter)

# reomoving prexisting handlers (NOTE may be unnecessary)
for lHand in logger.handlers:
    logger.removeHandler(lHand)
logger.addHandler(fh)

# NOTE May need to be set to 0 in order to prevent logging from bubbling up to maya's logger
# logger.propagate=1
logger.info('{} Initiated'.format(appTitle))


######
# UI #
######

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        # temp hard path
        uic.loadUi(r'F:\Database\Satchel\Works\Scripting\JSONitor\source\JSONitor.ui', self)

        self.currentFile = None


        # p = w.palette()
        # p.setColor(w.backgroundRole(), Qt.red)
        # w.setPalette(p)
        # self.palette = self.palette()
        # self.palette.setColor(Qt.red)
        # self.palette.setPalette(self.palette)

        self.actionOpen.triggered.connect(self.getFile)
        self.actionSave.triggered.connect(self.saveFile)
        self.actionSave_As.triggered.connect(self.saveAs)
        self.actionNew.triggered.connect(self.newFile)
        self.actionClose.triggered.connect(self.onTabClose)
        self.actionReopen_Tab.triggered.connect(self.onTabReopen)
        self.actionCycle_Tabs.triggered.connect(self.onTabCycle)
        self.actionPrevious_Tab.triggered.connect(self.onTabPrev)
        self.actionNext_Tab.triggered.connect(self.onTabNext)
        self.actionQuit.triggered.connect(self.closeWindow)
        # print(dir(self.filepathLineEdit))
        self.filepathLineEdit.returnPressed.connect(self.lineEditEnter)
        # self.filepathLineEdit.dropEvent.connect(self.lineEditEnter)
        # self.textEdit.textChanged.connect(self.asteriskTitle)
        # self.tabLayoutList = list(range(10))
        self.initUI()
        self.show()

    def initUI(self):
        self.title = 'JSONitor (JSON Editor by Aaron Aikman)'
        self.setWindowTitle(self.title)
        backgroundColor = QColor()
        backgroundColor.setNamedColor('#282821')
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), backgroundColor)
        p.setColor(self.backgroundRole(), Qt.gray)
        self.filepathLineEdit.setStyleSheet('''
            QLineEdit {
                border: 2px solid rgb(63, 63, 63);
                color: rgb(255, 255, 255);
                background-color: rgb(128, 128, 128);
            }
        ''')
        # p.setColor(self.filepathLineEdit.backgroundRole(), backgroundColor)
        self.setPalette(p)

        # syntax.PythonHighlighter(self.textEdit.document())
        # self.__editor = QsciScintilla()
        # print(self.__editor)
        # self.__editor.setMarginType(0, QsciScintilla.NumberMargin)
        # self.__editor.setMarginWidth(0, "0000")
        # self.__editor.setMarginsForegroundColor(QColor("#ff888888"))

        # -------------------------------- #
        #     QScintilla editor setup      #
        # -------------------------------- #
        self.__myFont = QFont('DejaVu Sans Mono')
        self.__myFont.setPointSize(8)

        self.tabLayoutList = []
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.onTabChange)

        # Add tabs to widget
        self.gridLayout.addWidget(self.tabs)

        # Deleting Text Edit until I decide if I want it back
        self.gridLayout.removeWidget(self.textEdit)
        self.textEdit.deleteLater()
        self.textEdit = None

        self.gridLayout.removeWidget(self.filepathLineEdit)
        self.filepathLineEdit.deleteLater()
        self.filepathLineEdit = None

        # Line Column Label
        self.lineColLabel = QLabel()
        self.lineColLabel.setText('Ln 0, Cl 0')
        self.lineColLabel.setAlignment(Qt.AlignRight)
        self.statusbar.addWidget(self.lineColLabel)


        # Info
        self.pages = []
        self.tEditors = []
        self.lineEdits = []
        self.files = []

        # History
        self.recentlyClosedFiles = []
        self.recentlyAccessedTabs = []
        self.add_page()


    def createLineEdit(self):
        lineEdit = QLineEdit()
        lineEdit.setFont(self.__myFont)
        lineEdit.returnPressed.connect(self.lineEditEnter)
        self.lineEdits.append(lineEdit)
        # TODO fix this naming the wrong thing if a tab has been closed
        tmpFileName = ('{}\\AutoSave\\tmp{}.json'.format(sourcePath, (len(self.files) + 1))).replace('\\', '/')
        self.files.append(tmpFileName)
        lineEdit.setText(tmpFileName)
        return lineEdit

    def create_textEditor(self):


        # ! Make instance of QSciScintilla class!
        # ----------------------------------------
        tEditor = QsciScintilla()
        tEditor.setText('''{
    "glossary": {
        "title": "example glossary",
        "GlossDiv": {
        "title": "S",
        "GlossList": {
            "GlossEntry": {
            "ID": "SGML",
            "SortAs": "SGML",
            "GlossTerm": "Standard Generalized Markup Language",
            "Acronym": "SGML",
            "Abbrev": "ISO 8879:1986",
            "GlossDef": {
                "para": "A meta-markup language, used to create markup languages such as DocBook.",
                "GlossSeeAlso": [
                "GML",
                "XML"
                ]
            },
            "GlossSee": "markup"
            }
        }
        }
    }
    }
    ''')
        tEditor.setUtf8(True)             # Set encoding to UTF-8
        tEditor.setFont(self.__myFont)

        # 1. Text wrapping
        # -----------------
        tEditor.setWrapMode(QsciScintilla.WrapWord)
        tEditor.setWrapVisualFlags(QsciScintilla.WrapFlagByText)
        tEditor.setWrapIndentMode(QsciScintilla.WrapIndentIndented)

        # 2. End-of-line mode
        # --------------------
        tEditor.setEolMode(QsciScintilla.EolWindows)
        tEditor.setEolVisibility(False)

        # 3. Indentation
        # ---------------
        tEditor.setIndentationsUseTabs(False)
        tEditor.setTabWidth(4)
        tEditor.setIndentationGuides(True)
        tEditor.setTabIndents(True)
        tEditor.setAutoIndent(True)

        # 4. Caret
        # ---------
        tEditor.setCaretForegroundColor(QColor("#ff0000ff"))
        tEditor.setCaretLineVisible(True)
        tEditor.setCaretLineBackgroundColor(QColor("#1f0000ff"))
        tEditor.setCaretWidth(2)

        # 5. Margins
        # -----------
        # Margin 0 = Line nr margin
        tEditor.setMarginType(0, QsciScintilla.NumberMargin)
        tEditor.setMarginWidth(0, "000")
        tEditor.setMarginsForegroundColor(QColor("#ff888888"))

        # self.__lexer = JSONLexer(tEditor)
        self.__lexer = QsciLexerJSON(tEditor)
        # print(dir(QsciLexerJSON))
        # Set colors
        # self.__lexer.setColor(Qt.gray)
        # self.__lexer.setPaper(Qt.gray)
        self.__lexer.setDefaultFont(self.__myFont)
        # self.__lexer.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        tEditor.setFolding(True)
        # print(help(self.__lexer.setProperty))
        # self.__lexer.setFoldCompact(True)

        # self.__lexer = QsciLexerXML(tEditor)
        # self.__lexer = QsciLexerYAML(tEditor)

        # print(dir(tEditor))
        # print(tEditor)
        tEditor.setAutoCompletionSource(QsciScintilla.AcsDocument)
        tEditor.setAutoCompletionThreshold(3)
        tEditor.setAutoCompletionCaseSensitivity(False)

        # 2. Install the lexer onto your editor
        tEditor.setLexer(self.__lexer)

        # tEditor.setFont(self.__myFont)

        tEditor.textChanged.connect(self.asteriskTitle)
        tEditor.cursorPositionChanged.connect(self.updateLineColInfo)


        # Drops
        tEditor.setAcceptDrops(True)


        # Multiline Editing
        # print(help(tEditor.cursorPositionChanged))
        tEditor.SendScintilla(tEditor.SCI_SETADDITIONALSELECTIONTYPING, 1)
        # offset =tEditor.positionFromLineIndex(0, 7) # line-index to offset
        # tEditor.SendScintilla(tEditor.SCI_SETSELECTION, offset, offset)
        # # using the same offset twice selects no characters, hence a cursor

        # offset = tEditor.positionFromLineIndex(1, 5)
        # tEditor.SendScintilla(tEditor.SCI_ADDSELECTION, offset, offset)

        # offset = tEditor.positionFromLineIndex(2, 5)
        # tEditor.SendScintilla(tEditor.SCI_ADDSELECTION, offset, offset)




        self.tEditors.append(tEditor)

        # print(dir(tEditor))
        return tEditor

        # print(dir(self.__editor))
        # Margin 1 = Symbol margin
        # self.__editor.setMarginType(1, QsciScintilla.SymbolMargin)
        # self.__editor.setMarginWidth(1, "00000")
        # sym_0 = QImage("green_dot.png").scaled(QSize(16, 16))
        # sym_1 = QImage("green_arrow.png").scaled(QSize(16, 16))
        # sym_2 = QImage("red_dot.png").scaled(QSize(16, 16))
        # sym_3 = QImage("red_arrow.png").scaled(QSize(16, 16))

        # self.__editor.markerDefine(sym_0, 0)
        # self.__editor.markerDefine(sym_1, 1)
        # self.__editor.markerDefine(sym_2, 2)
        # self.__editor.markerDefine(sym_3, 3)

        # self.__editor.setMarginMarkerMask(1, 0b1111)
        # print(dir(self.gridLayout))

        # TABS
                # Initialize tab screen







        # color_palette = self.text_editor.palette()
        # color_palette.setColor(QPalette.Text, Qt.white)
        # color_palette.setColor(QPalette.Base, backgroundColor)
        # self.text_editor.setPalette(color_palette)

        # default_font = self.text_editor.font()
        # default_font.setPointSize(9)
        # self.text_editor.setFont(default_font)

        # # self.setCentralWidget(self.text_editor)
        # self.setGeometry(500, 500, 500, 500)


    def getFile(self):

        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        # dlg.setFilter("JSON files (*.json)")
        filterList = ["JSON files (*.json)",
                    "XML files (*.xml)",
                    "YAML files (*.yaml)",
                    "TXT files (*.txt)",
                    "All files (*)"
                    ]
        dlg.setNameFilters(filterList)
        # filenames = QStringList()
        # filenames = []

        # if doDialog:
        #     if dlg.exec_():
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.currentFile = filenames[0]
            # self.filepathLineEdit.setText(self.currentFile)
            self.openFile()


    def openFile(self):
        if self.currentFile in self.files:
            self.tabs.setCurrentIndex(self.files.index(self.currentFile))
        else:
            logger.debug('File not found in current tabs. Opening new tab.')
            self.add_page()
            self.lineEdits[self.tabs.currentIndex()].setText(self.currentFile)
            with open(self.currentFile, 'r', encoding='utf-8-sig') as f:
                data = f.read()
                self.tEditors[self.tabs.currentIndex()].setText(data)

            self.files[self.tabs.currentIndex()] = self.currentFile
            print(self.files)

            self.setWindowTitle('{} - {}'.format(self.title, os.path.basename(self.currentFile)))
            tabName = os.path.splitext(os.path.basename(self.lineEdits[self.tabs.currentIndex()].text()))[0]
            self.tabs.setTabText(self.tabs.currentIndex(), tabName)


    def saveFile(self, doDialog = 0):
        # TODO fix infinite loop if you cancel save dialog
        # filename = self.currentFile
        filename = self.files[self.tabs.currentIndex()]
        fpText = self.lineEdits[self.tabs.currentIndex()].text()
        if doDialog:
            filename = QFileDialog.getSaveFileName(self, 'Save File')[0]
            if filename:
                self.currentFile = filename
                self.lineEdits[self.tabs.currentIndex()].setText(self.currentFile)
        elif filename != fpText:
            if os.path.isfile(fpText):
                if self.quickPrompt('Save?', 'Do you want to OVERWRITE to the new filepath instead of the original?'):
                    filename = fpText
                    self.currentFile = filename
                else:
                    self.lineEdits[self.tabs.currentIndex()].setText(self.currentFile)
            else:
                if self.quickPrompt('Save?', 'Do you want to save to the new filepath instead of the original?'):
                    filename = fpText
                    self.currentFile = filename
                else:
                    self.lineEdits[self.tabs.currentIndex()].setText(self.currentFile)

        if filename:
            # newText = str(self.textEdit.toPlainText())
            newText = str(self.tEditors[self.tabs.currentIndex()].text())
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
                # TODO add try in case can't make dir
            with open(filename, 'w') as f:
                f.write(newText)

            self.setWindowTitle('{} - {}'.format(self.title, os.path.basename(self.currentFile)))

            self.files[self.tabs.currentIndex()] = self.currentFile
            tabName = os.path.splitext(os.path.basename(self.lineEdits[self.tabs.currentIndex()].text()))[0]
            self.tabs.setTabText(self.tabs.currentIndex(), tabName)
        else:
            self.saveAs()


    def saveAs(self):
        self.saveFile(1)


    def quickPrompt(self, title, message):
        reply = QMessageBox.question(self, title,
                        message, QMessageBox.Yes, QMessageBox.No)
        return reply == QMessageBox.Yes


    def closeWindow(self):
        sys.exit()


    def onTabClose(self):
        if self.tabs.tabText(self.tabs.currentIndex())[-1] == '*':
            if self.quickPrompt('Save?', 'Do you want to save before closing the tab?'):
                self.saveFile()

        tabIndex = self.tabs.currentIndex()
        self.recentlyClosedFiles.append(self.files[self.tabs.currentIndex()])
        self.tabs.removeTab(tabIndex)

        del self.pages[tabIndex]
        del self.tEditors[tabIndex]
        del self.lineEdits[tabIndex]
        del self.files[tabIndex]


    def onTabReopen(self):
        reopening = True
        while reopening:
            if self.recentlyClosedFiles:
                if os.path.isfile(self.recentlyClosedFiles[-1]):
                    self.currentFile = self.recentlyClosedFiles[-1]
                    del self.recentlyClosedFiles[-1]
                    self.openFile()
                    reopening = False
                else:
                    del self.recentlyClosedFiles[-1]
            else:
                reopening = False


    def asteriskTitle(self):
        tabName = '{}*'.format(os.path.splitext(os.path.basename(self.lineEdits[self.tabs.currentIndex()].text()))[0])
        self.tabs.setTabText(self.tabs.currentIndex(), tabName)
        self.setWindowTitle('{} - {}'.format(self.title, tabName))


    def updateLineColInfo(self):
        cursorLine, cursorCol = self.tEditors[self.tabs.currentIndex()].getCursorPosition()
        self.lineColLabel.setText('Ln {}, Cl {}'.format(cursorLine + 1, cursorCol + 1))


    def onTabChange(self):
        self.setWindowTitle('{} - {}'.format(self.title, self.tabs.tabText(self.tabs.currentIndex())))
        self.recentlyAccessedTabs.append(self.tabs.currentIndex())
        if len(self.recentlyAccessedTabs) > 2:
            del self.recentlyAccessedTabs[0]


    def create_page(self, *contents):
        page = QWidget()
        vbox = QVBoxLayout()
        for c in contents:
            vbox.addWidget(c)

        page.setLayout(vbox)
        return page


    def create_new_page_button(self):
        btn = QPushButton('Create a new page!')
        btn.clicked.connect(self.add_page)
        return btn


    def add_page(self):
        self.pages.append( self.create_page( self.createLineEdit(), self.create_textEditor()) )
        tabName = os.path.splitext(os.path.basename(self.lineEdits[-1].text()))[0]
        self.tabs.addTab( self.pages[-1] , tabName )
        self.tabs.setCurrentIndex( len(self.pages)-1 )


    def onTabCycle(self):
        tabInd = self.recentlyAccessedTabs[-2]
        self.tabs.setCurrentIndex(tabInd)


    def onTabPrev(self):
        tabInd = self.tabs.currentIndex()
        tabInd = (tabInd - 1) if tabInd > 0 else (len(self.pages) - 1)
        self.tabs.setCurrentIndex(tabInd)


    def onTabNext(self):
        tabInd = self.tabs.currentIndex()
        tabInd = (tabInd + 1) if tabInd < (len(self.pages) - 1) else 0
        self.tabs.setCurrentIndex(tabInd)


    def lineEditEnter(self):
        # TODO make sure you can't lose your changes to current file
        # TODO maybe add a separate button for open
        filepathText = self.lineEdits[self.tabs.currentIndex()].text()
        if filepathText:
            if os.path.isfile(filepathText):
                self.currentFile = filepathText
                self.openFile()
            else:
                self.saveFile()

    # if os.path.exists(filePath):
    #     #the file is there
    # elif os.access(os.path.dirname(filePath), os.W_OK):
    #     #the file does not exists but write privileges are given
    # else:
    #     #can not write there


    def newFile(self):
        self.add_page()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())