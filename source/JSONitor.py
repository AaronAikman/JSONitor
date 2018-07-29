'''


TODO
TEXT EDIT
add drag and drop
copy/paste
recently closed files
add syntax highlighting
add comparison
add an About
logger
save temp files/autosave
Use json file for ui colors/settings
find and replace
Undo stack
copy to clipboard
Feedback/email
select Occurence
select all Occurences
Ctrl up and down to scroll
ability to resize pane middle

LINE EDIT
Up down arrows to search through dir
left right arrows to go up or down folders

JSON
fix decoder/filterValue?
conversion to (xml, csv, yaml)
validation
format/Beautify
Minimize/compact
use margin clicks for reordering elements

TREE VIEW
add lengths and indexing
json to tree
tree to json
arrow buttons for conversion
reorder
edit
duplicate
insert
remove
sort

NOTE
Shift Alt Drag to multi select



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

import Utilities.JSONTools as jst
import json

# TODO Move or strip down
jsc = jst.JSONConverter()

# import functools

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

class JSONitorWindow(QMainWindow):
    def __init__(self):
        # super(JSONitorWindow, self).__init__()
        super().__init__()
        uiFile = os.path.dirname(os.path.realpath(__file__)) + '\\JSONitor.ui'
        logger.debug('UI file is: {}'.format(uiFile))
        uic.loadUi(uiFile, self)

        self.currentFile = None

        # Info
        self.pages = []
        self.tEditors = []
        self.lineEdits = []
        self.files = []
        self.itemModels = []
        self.treeViews = []

        # History
        self.recentlyClosedFiles = []
        self.recentlyAccessedTabs = []
        self.bookmarks = {}


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
        self.actionUpdate_Tree_View.triggered.connect(self.updateTreeViewFromText)
        self.actionUpdate_Text.triggered.connect(self.updateTextFromTreeView)
        self.filepathLineEdit.returnPressed.connect(self.lineEditEnter)

        # Go options
        self.actionGo_to_Line.triggered.connect(self.goToLine)

        self.actionGo_to_Tab_1.triggered.connect(lambda: self.onTabGo(1))
        self.actionGo_to_Tab_2.triggered.connect(lambda: self.onTabGo(2))
        self.actionGo_to_Tab_3.triggered.connect(lambda: self.onTabGo(3))
        self.actionGo_to_Tab_4.triggered.connect(lambda: self.onTabGo(4))
        self.actionGo_to_Tab_5.triggered.connect(lambda: self.onTabGo(5))
        self.actionGo_to_Tab_6.triggered.connect(lambda: self.onTabGo(6))
        self.actionGo_to_Tab_7.triggered.connect(lambda: self.onTabGo(7))
        self.actionGo_to_Tab_8.triggered.connect(lambda: self.onTabGo(8))
        self.actionGo_to_Tab_9.triggered.connect(lambda: self.onTabGo(9))
        self.actionGo_to_Tab_10.triggered.connect(lambda: self.onTabGo(10))

        # Set Bookmarks
        self.actionSet_Bookmark_1 = QAction('Set Bookmark 1', self)
        self.actionSet_Bookmark_1.setShortcut('Ctrl+Shift+1')
        self.menuSet_Bookmark.addAction(self.actionSet_Bookmark_1)
        self.actionSet_Bookmark_1.triggered.connect(lambda: self.onBookmarkSet(1))

        self.actionSet_Bookmark_2 = QAction('Set Bookmark 2', self)
        self.actionSet_Bookmark_2.setShortcut('Ctrl+Shift+2')
        self.menuSet_Bookmark.addAction(self.actionSet_Bookmark_2)
        self.actionSet_Bookmark_2.triggered.connect(lambda: self.onBookmarkSet(2))

        self.actionSet_Bookmark_3 = QAction('Set Bookmark 3', self)
        self.actionSet_Bookmark_3.setShortcut('Ctrl+Shift+3')
        self.menuSet_Bookmark.addAction(self.actionSet_Bookmark_3)
        self.actionSet_Bookmark_3.triggered.connect(lambda: self.onBookmarkSet(3))

        self.actionSet_Bookmark_4 = QAction('Set Bookmark 4', self)
        self.actionSet_Bookmark_4.setShortcut('Ctrl+Shift+4')
        self.menuSet_Bookmark.addAction(self.actionSet_Bookmark_4)
        self.actionSet_Bookmark_4.triggered.connect(lambda: self.onBookmarkSet(4))

        self.actionSet_Bookmark_5 = QAction('Set Bookmark 5', self)
        self.actionSet_Bookmark_5.setShortcut('Ctrl+Shift+5')
        self.menuSet_Bookmark.addAction(self.actionSet_Bookmark_5)
        self.actionSet_Bookmark_5.triggered.connect(lambda: self.onBookmarkSet(5))

        self.actionSet_Bookmark_6 = QAction('Set Bookmark 6', self)
        self.actionSet_Bookmark_6.setShortcut('Ctrl+Shift+6')
        self.menuSet_Bookmark.addAction(self.actionSet_Bookmark_6)
        self.actionSet_Bookmark_6.triggered.connect(lambda: self.onBookmarkSet(6))

        self.actionSet_Bookmark_7 = QAction('Set Bookmark 7', self)
        self.actionSet_Bookmark_7.setShortcut('Ctrl+Shift+7')
        self.menuSet_Bookmark.addAction(self.actionSet_Bookmark_7)
        self.actionSet_Bookmark_7.triggered.connect(lambda: self.onBookmarkSet(7))

        self.actionSet_Bookmark_8 = QAction('Set Bookmark 8', self)
        self.actionSet_Bookmark_8.setShortcut('Ctrl+Shift+8')
        self.menuSet_Bookmark.addAction(self.actionSet_Bookmark_8)
        self.actionSet_Bookmark_8.triggered.connect(lambda: self.onBookmarkSet(8))

        self.actionSet_Bookmark_9 = QAction('Set Bookmark 9', self)
        self.actionSet_Bookmark_9.setShortcut('Ctrl+Shift+9')
        self.menuSet_Bookmark.addAction(self.actionSet_Bookmark_9)
        self.actionSet_Bookmark_9.triggered.connect(lambda: self.onBookmarkSet(9))

        self.actionSet_Bookmark_10 = QAction('Set Bookmark 10', self)
        self.actionSet_Bookmark_10.setShortcut('Ctrl+Shift+0')
        self.menuSet_Bookmark.addAction(self.actionSet_Bookmark_10)
        self.actionSet_Bookmark_10.triggered.connect(lambda: self.onBookmarkSet(10))

        # Get Bookmarks
        self.actionGo_Bookmark_1 = QAction('Go to Bookmark 1', self)
        self.actionGo_Bookmark_1.setShortcut('Alt+1')
        self.menuGo_Bookmark.addAction(self.actionGo_Bookmark_1)
        self.actionGo_Bookmark_1.triggered.connect(lambda: self.onBookmarkGo(1))

        self.actionGo_Bookmark_2 = QAction('Go to Bookmark 2', self)
        self.actionGo_Bookmark_2.setShortcut('Alt+2')
        self.menuGo_Bookmark.addAction(self.actionGo_Bookmark_2)
        self.actionGo_Bookmark_2.triggered.connect(lambda: self.onBookmarkGo(2))

        self.actionGo_Bookmark_3 = QAction('Go to Bookmark 3', self)
        self.actionGo_Bookmark_3.setShortcut('Alt+3')
        self.menuGo_Bookmark.addAction(self.actionGo_Bookmark_3)
        self.actionGo_Bookmark_3.triggered.connect(lambda: self.onBookmarkGo(3))

        self.actionGo_Bookmark_4 = QAction('Go to Bookmark 4', self)
        self.actionGo_Bookmark_4.setShortcut('Alt+4')
        self.menuGo_Bookmark.addAction(self.actionGo_Bookmark_4)
        self.actionGo_Bookmark_4.triggered.connect(lambda: self.onBookmarkGo(4))

        self.actionGo_Bookmark_5 = QAction('Go to Bookmark 5', self)
        self.actionGo_Bookmark_5.setShortcut('Alt+5')
        self.menuGo_Bookmark.addAction(self.actionGo_Bookmark_5)
        self.actionGo_Bookmark_5.triggered.connect(lambda: self.onBookmarkGo(5))

        self.actionGo_Bookmark_6 = QAction('Go to Bookmark 6', self)
        self.actionGo_Bookmark_6.setShortcut('Alt+6')
        self.menuGo_Bookmark.addAction(self.actionGo_Bookmark_6)
        self.actionGo_Bookmark_6.triggered.connect(lambda: self.onBookmarkGo(6))

        self.actionGo_Bookmark_7 = QAction('Go to Bookmark 7', self)
        self.actionGo_Bookmark_7.setShortcut('Alt+7')
        self.menuGo_Bookmark.addAction(self.actionGo_Bookmark_7)
        self.actionGo_Bookmark_7.triggered.connect(lambda: self.onBookmarkGo(7))

        self.actionGo_Bookmark_8 = QAction('Go to Bookmark 8', self)
        self.actionGo_Bookmark_8.setShortcut('Alt+8')
        self.menuGo_Bookmark.addAction(self.actionGo_Bookmark_8)
        self.actionGo_Bookmark_8.triggered.connect(lambda: self.onBookmarkGo(8))

        self.actionGo_Bookmark_9 = QAction('Go to Bookmark 9', self)
        self.actionGo_Bookmark_9.setShortcut('Alt+9')
        self.menuGo_Bookmark.addAction(self.actionGo_Bookmark_9)
        self.actionGo_Bookmark_9.triggered.connect(lambda: self.onBookmarkGo(9))

        self.actionGo_Bookmark_10 = QAction('Go to Bookmark 10', self)
        self.actionGo_Bookmark_10.setShortcut('Alt+0')
        self.menuGo_Bookmark.addAction(self.actionGo_Bookmark_10)
        self.actionGo_Bookmark_10.triggered.connect(lambda: self.onBookmarkGo(10))


        # menuSet_Bookmark


        # self.actionExit = QAction(('E&xit'), self)
        # self.actionExit.setShortcut(QKeySequence("Ctrl+Q"))
        # self.addAction(self.actionExit)
        # self.actionExit.triggered.connect(self.CloseSC)

        # self.filepathLineEdit.dropEvent.connect(self.lineEditEnter)
        # self.textEdit.textChanged.connect(self.asteriskTitle)
        # self.tabLayoutList = list(range(10))
        self.initUI()
        self.show()

    def initUI(self):
        self.title = 'JSONitor (JSON Editor by Aaron Aikman)'
        self.setWindowTitle(self.title)
        self.doStyling = False

        # Colors
        # backgroundColor = QColor()
        # backgroundColor.setNamedColor('#282821')
        # self.setAutoFillBackground(True)
        # p = self.palette()
        # p.setColor(self.backgroundRole(), backgroundColor)
        # p.setColor(self.backgroundRole(), Qt.gray)
        # self.filepathLineEdit.setStyleSheet('''
        #     QLineEdit {
        #         border: 2px solid rgb(63, 63, 63);
        #         color: rgb(255, 255, 255);
        #         background-color: rgb(128, 128, 128);
        #     }
        # ''')
        # # p.setColor(self.filepathLineEdit.backgroundRole(), backgroundColor)
        # self.setPalette(p)

        # Colors
        self.lineEditStyleSheet = ('''
            QLineEdit {
                border: 2px solid rgb(63, 63, 63);
                color: rgb(255, 255, 255);
                background-color: rgb(128, 128, 128);
            }
            ''')

        self.treeViewStyleSheet = ('''
            QTreeView {
                border: 2px solid rgb(63, 63, 63);
                color: rgb(255, 255, 255);
                background-color: rgb(128, 128, 128);
            }
            ''')

        self.textEditStyleSheet = ('''
            QsciScintilla {
                border: 2px solid rgb(63, 63, 63);
                color: rgb(255, 255, 255);
                background-color: rgb(128, 128, 128);
            }
            ''')




        # syntax.PythonHighlighter(self.textEdit.document())
        # self.__editor = QsciScintilla()
        # print(self.__editor)
        # self.__editor.setMarginType(0, QsciScintilla.NumberMargin)
        # self.__editor.setMarginWidth(0, "0000")
        # self.__editor.setMarginsForegroundColor(QColor("#ff888888"))

        # -------------------------------- #
        #     QScintilla editor setup      #
        # -------------------------------- #
        self.__monoFont = QFont('DejaVu Sans Mono')
        self.__monoFont.setPointSize(8)

        self.tabLayoutList = []
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.onTabChange)

        # Add tabs to widget
        self.gridLayout.addWidget(self.tabs)

        # Deleting Text Edit until I decide if I want it back
        self.gridLayout.removeWidget(self.textEdit)
        self.textEdit.deleteLater()
        self.textEdit = None

        # Deleting Line Edit until I decide if I want it back
        self.gridLayout.removeWidget(self.filepathLineEdit)
        self.filepathLineEdit.deleteLater()
        self.filepathLineEdit = None

        # Line Column Label
        self.lineColLabel = QLabel()
        self.lineColLabel.setText('Ln 0, Cl 0')
        self.lineColLabel.setAlignment(Qt.AlignRight)
        # self.statusbar.addWidget(self.lineColLabel)
        self.statusbar.addPermanentWidget(self.lineColLabel)





        self.addPage()

    ###################
    # Widget / Window #
    ###################

    def createLineEdit(self):
        lineEdit = QLineEdit()
        lineEdit.setFont(self.__monoFont)
        lineEdit.returnPressed.connect(self.lineEditEnter)
        self.lineEdits.append(lineEdit)
        # TODO fix this naming the wrong thing if a tab has been closed
        tmpFileName = ('{}\\AutoSave\\tmp{}.json'.format(sourcePath, (len(self.files) + 1))).replace('\\', '/')
        self.files.append(tmpFileName)
        lineEdit.setText(tmpFileName)
        if self.doStyling:
            lineEdit.setStyleSheet(self.lineEditStyleSheet)
        return lineEdit

    def createTextEditor(self):


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
        tEditor.setFont(self.__monoFont)

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
        # Set colors
        # self.__lexer.setColor(Qt.gray)
        # self.__lexer.setPaper(Qt.gray)
        self.__lexer.setDefaultFont(self.__monoFont)
        # self.__lexer.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        tEditor.setFolding(True)
        # self.__lexer.setFoldCompact(True)

        # self.__lexer = QsciLexerXML(tEditor)
        # self.__lexer = QsciLexerYAML(tEditor)

        tEditor.setAutoCompletionSource(QsciScintilla.AcsDocument)
        tEditor.setAutoCompletionThreshold(3)
        tEditor.setAutoCompletionCaseSensitivity(False)

        # 2. Install the lexer onto your editor
        tEditor.setLexer(self.__lexer)

        # tEditor.setFont(self.__monoFont)

        tEditor.textChanged.connect(self.asteriskTitle)
        tEditor.cursorPositionChanged.connect(self.updateLineColInfo)


        # Drops
        tEditor.setAcceptDrops(True)


        # Multiline Editing
        tEditor.SendScintilla(tEditor.SCI_SETADDITIONALSELECTIONTYPING, 1)
        # offset =tEditor.positionFromLineIndex(0, 7) # line-index to offset
        # tEditor.SendScintilla(tEditor.SCI_SETSELECTION, offset, offset)
        # # using the same offset twice selects no characters, hence a cursor

        # offset = tEditor.positionFromLineIndex(1, 5)
        # tEditor.SendScintilla(tEditor.SCI_ADDSELECTION, offset, offset)

        # offset = tEditor.positionFromLineIndex(2, 5)
        # tEditor.SendScintilla(tEditor.SCI_ADDSELECTION, offset, offset)

        if self.doStyling:
            tEditor.setStyleSheet(self.textEditStyleSheet)

        self.tEditors.append(tEditor)



        return tEditor

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


    def createTreeView(self):
        tree = json.loads(self.tEditors[self.tabInd()].text())

        itemModel = StandardItemModel()
        print(dir(itemModel))
        itemModel.populateTree(tree, itemModel.invisibleRootItem())
        self.itemModels.append(itemModel)

        treeView = QTreeView()
        treeView.setModel(itemModel)
        treeView.setHeaderHidden(True)
        treeView.setDragDropMode(QAbstractItemView.InternalMove)
        treeView.expandAll()
        # treeView.collapseAll()
        self.treeViews.append(treeView)

        # Colors
        # backgroundColor = QColor()
        # backgroundColor.setNamedColor('#282821')
        # treeView.setAutoFillBackground(True)
        # p = treeView.palette()
        # # print(dir(p.setColor))
        # # p.setColor(treeView.backgroundRole(), backgroundColor)
        # # p.setColor(treeView.role(), backgroundColor)
        # p.setColor(treeView.backgroundRole(), Qt.red)
        # treeView.setPalette(p)
        # treeView.setStyleSheet('''
        #     QTreeView {
        #         border: 2px solid rgb(63, 63, 63);
        #         color: rgb(255, 255, 255);
        #         background-color: rgb(128, 128, 128);
        #     }
        # ''')
        if self.doStyling:
            treeView.setStyleSheet(self.treeViewStyleSheet)


        return treeView


    def createPage(self, *contents):
        page = QWidget()
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        # TODO fix to allow for specific ordering
        for lyt, c in contents:
            if lyt == 'v':
                vbox.addWidget(c)
            else:
                hbox.addWidget(c)
        vbox.addLayout(hbox)

        page.setLayout(vbox)
        return page


    def addPage(self):
        self.pages.append( self.createPage( ('v', self.createLineEdit()), ('h', self.createTextEditor()), ('h', self.createTreeView())) )
        tabName = os.path.splitext(os.path.basename(self.lineEdits[-1].text()))[0]
        self.tabs.addTab( self.pages[-1] , tabName )
        self.tabs.setCurrentIndex( len(self.pages)-1 )


    def closeWindow(self):
        sys.exit()


    #################
    # File Handling #
    #################

    def newFile(self):
        self.addPage()

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
            self.addPage()
            self.lineEdits[self.tabInd()].setText(self.currentFile)
            with open(self.currentFile, 'r', encoding='utf-8-sig') as f:
                data = f.read()
                self.tEditors[self.tabInd()].setText(data)

            self.files[self.tabInd()] = self.currentFile
            logger.debug('Open Files: {}'.format(self.files))

            self.setWindowTitle('{} - {}'.format(self.title, os.path.basename(self.currentFile)))
            tabName = os.path.splitext(os.path.basename(self.lineEdits[self.tabInd()].text()))[0]
            self.tabs.setTabText(self.tabInd(), tabName)
            self.updateTreeViewFromText()


    def saveFile(self, doDialog = 0):
        # TODO fix infinite loop if you cancel save dialog
        # filename = self.currentFile
        filename = self.files[self.tabInd()]
        fpText = self.lineEdits[self.tabInd()].text()
        if doDialog:
            filename = QFileDialog.getSaveFileName(self, 'Save File')[0]
            if filename:
                self.currentFile = filename
                self.lineEdits[self.tabInd()].setText(self.currentFile)
        elif filename != fpText:
            if os.path.isfile(fpText):
                if self.quickPrompt('Save?', 'Do you want to OVERWRITE to the new filepath instead of the original?'):
                    filename = fpText
                    self.currentFile = filename
                else:
                    self.lineEdits[self.tabInd()].setText(self.currentFile)
            else:
                if self.quickPrompt('Save?', 'Do you want to save to the new filepath instead of the original?'):
                    filename = fpText
                    self.currentFile = filename
                else:
                    self.lineEdits[self.tabInd()].setText(self.currentFile)

        if filename:
            # newText = str(self.textEdit.toPlainText())
            newText = str(self.tEditors[self.tabInd()].text())
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
                # TODO add try in case can't make dir
            with open(filename, 'w') as f:
                f.write(newText)

            self.setWindowTitle('{} - {}'.format(self.title, os.path.basename(self.currentFile)))

            self.files[self.tabInd()] = self.currentFile
            tabName = os.path.splitext(os.path.basename(self.lineEdits[self.tabInd()].text()))[0]
            self.tabs.setTabText(self.tabInd(), tabName)
        else:
            self.saveAs()


    def saveAs(self):
        self.saveFile(1)


    #################
    # Tab Functions #
    #################

    def onTabClose(self):
        if self.tabs.tabText(self.tabInd())[-1] == '*':
            if self.quickPrompt('Save?', 'Do you want to save before closing the tab?'):
                self.saveFile()

        tabIndex = self.tabInd()
        self.recentlyClosedFiles.append(self.files[self.tabInd()])
        self.tabs.removeTab(tabIndex)

        del self.pages[tabIndex]
        del self.tEditors[tabIndex]
        del self.lineEdits[tabIndex]
        del self.files[tabIndex]
        del self.itemModels[tabIndex]
        del self.treeViews[tabIndex]


    def onTabGo(self, ind):
        ind -= 1
        if len(self.pages) > ind:
            self.tabs.setCurrentIndex(ind)


    def onTabReopen(self):
        reopening = True
        while reopening:
            if self.recentlyClosedFiles:
                if os.path.isfile(self.recentlyClosedFiles[-1]):
                    self.currentFile = self.recentlyClosedFiles[-1]
                    del self.recentlyClosedFiles[-1]
                    self.openFile()
                    self.statusMessage('Reopened {}'.format(self.currentFile))
                    reopening = False
                else:
                    del self.recentlyClosedFiles[-1]
            else:
                reopening = False


    def onTabChange(self):
        self.setWindowTitle('{} - {}'.format(self.title, self.tabs.tabText(self.tabInd())))
        self.recentlyAccessedTabs.append(self.tabInd())
        if len(self.recentlyAccessedTabs) > 2:
            del self.recentlyAccessedTabs[0]


    def onTabCycle(self):
        tabInd = self.recentlyAccessedTabs[-2]
        self.tabs.setCurrentIndex(tabInd)


    def onTabPrev(self):
        tabInd = self.tabInd()
        tabInd = (tabInd - 1) if tabInd > 0 else (len(self.pages) - 1)
        self.tabs.setCurrentIndex(tabInd)


    def onTabNext(self):
        tabInd = self.tabInd()
        tabInd = (tabInd + 1) if tabInd < (len(self.pages) - 1) else 0
        self.tabs.setCurrentIndex(tabInd)


    #############
    # Bookmarks #
    #############

    def onBookmarkSet(self, ind):
        self.bookmarks[ind] = [self.files[self.tabInd()], self.tEditors[self.tabInd()].getCursorPosition()]


    def onBookmarkGo(self, ind):
        filename, pos = self.bookmarks[ind]
        if filename in self.files:
            tabInd = self.files.index(filename)
            self.tabs.setCurrentIndex(tabInd)
            self.tEditors[tabInd].setCursorPosition(pos[0], pos[1])


    ##############
    # Go Options #
    ##############

    def goToLine(self):
        pos, ok = QInputDialog.getInt(self,"Go to Line","Enter line number")
        if ok:
            self.tEditors[self.tabInd()].setCursorPosition((pos-1), 0)
            self.tEditors[self.tabInd()].setFocus()


    ####################
    # Helper Functions #
    ####################

    def tabInd(self):
        return self.tabs.currentIndex()


    def updateTreeViewFromText(self):
        tabIndex = self.tabInd()
        itemModel = self.itemModels[tabIndex]
        itemModel.clear()
        itemModel.populateTree(json.loads(self.tEditors[tabIndex].text()) , itemModel.invisibleRootItem())
        self.treeViews[tabIndex].expandAll()


    def updateTextFromTreeView(self):
        tabIndex = self.tabInd()
        itemModel = self.itemModels[tabIndex]
        newJSON = json.dumps(jsc.getDictFromLists(itemModel.itemList()), indent=4, sort_keys=False)
        self.tEditors[tabIndex].setText(newJSON)


    def statusMessage(self, msg, dur=2):
        dur *= 1000
        self.statusbar.showMessage(msg, dur)
        logger.info(msg)


    def quickPrompt(self, title, message):
        reply = QMessageBox.question(self, title,
                        message, QMessageBox.Yes, QMessageBox.No)
        return reply == QMessageBox.Yes


    def asteriskTitle(self):
        tabName = '{}*'.format(os.path.splitext(os.path.basename(self.lineEdits[self.tabInd()].text()))[0])
        self.tabs.setTabText(self.tabInd(), tabName)
        self.setWindowTitle('{} - {}'.format(self.title, tabName))


    def updateLineColInfo(self):
        cursorLine, cursorCol = self.tEditors[self.tabInd()].getCursorPosition()
        self.lineColLabel.setText('Ln {}, Cl {}'.format(cursorLine + 1, cursorCol + 1))


    def lineEditEnter(self):
        # TODO make sure you can't lose your changes to current file
        # TODO maybe add a separate button for open
        filepathText = self.lineEdits[self.tabInd()].text()
        if filepathText:
            if os.path.isfile(filepathText):
                self.currentFile = filepathText
                self.openFile()
            else:
                self.saveFile()


    #######
    # REF #
    #######

    #     items = ("C", "C++", "Java", "Python")

    # item, ok = QInputDialog.getItem(self, "select input dialog",
    # "list of languages", items, 0, False)

    # if ok and item:
    #     self.le.setText(item)

    # def gettext(self):
    #     text, ok = QInputDialog.getText(self, 'Text Input Dialog', 'Enter your name:')
    #     if ok:
    #         self.le1.setText(str(text))

    # def getint(self):
    #     num,ok = QInputDialog.getInt(self,"integer input dualog","enter a number")

    #     if ok:
    #         self.le2.setText(str(num))

    # text cursor functions
    # def get_text_cursor(self):
    #     return self.TextEdit.textCursor()

    # def set_text_cursor_pos(self, value):
    #     tc = self.get_text_cursor()
    #     tc.setPosition(value, QtGui.QTextCursor.KeepAnchor)
    #     self.TextEdit.setTextCursor(tc)

    # def get_text_cursor_pos(self):
    #     return self.get_text_cursor().position()

    # def get_text_selection(self):
    #     cursor = self.get_text_cursor()
    #     return cursor.selectionStart(), cursor.selectionEnd()

    # def set_text_selection(self, start, end):
    #     cursor = self.get_text_cursor()
    #     cursor.setPosition(start)
    #     cursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
    #     self.TextEdit.setTextCursor(cursor)

    # if os.path.exists(filePath):
    #     #the file is there
    # elif os.access(os.path.dirname(filePath), os.W_OK):
    #     #the file does not exists but write privileges are given
    # else:
    #     #can not write there

class StandardItemModel(QStandardItemModel):
    def __init__(self, parent = None):
        super(StandardItemModel, self).__init__(parent)

    def itemList(self, parent = QModelIndex()):
        items = []
        for row in range(self.rowCount(parent)):
            idx = self.index(row, 0, parent)
            items.append(self.data(idx))
            if self.hasChildren(idx):
                items.append(self.itemList(idx))
        return items


    def populateTree(self, children, parent, sort=False):
        if sort:
            children = sorted(children)
        if isinstance(children, (dict, list)):
            for child in children:
                child_item = QStandardItem(str(child))
                parent.appendRow(child_item)
                # if isinstance(children, types.DictType):
                if isinstance(children, dict):
                    self.populateTree(children[child], child_item)
        else:
            child_item = QStandardItem(str(children))
            parent.appendRow(child_item)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JSONitorWindow()
    sys.exit(app.exec_())