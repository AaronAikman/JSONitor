'''


TODO
TEXT EDIT
add drag and drop
copy/paste
recently closed files
add comparison
add an About
save temp files/autosave
Use json file for ui colors/settings
*find and replace
Undo stack
copy to clipboard
Feedback/email
select Occurence
select all Occurences
Ctrl up and down to scroll
ability to resize pane middle
*add line edit to panes for searching (itemModel.findItems)
close window, ask save if any tab has unsaved changes

LINE EDIT
Up down arrows to search through dir
left right arrows to go up or down folders

JSON
conversion to (xml, csv, yaml)?
*validation help
format/Beautify
Minimize/compact
use margin clicks for reordering elements
Add schema support?
compensate for NaN, Infinity, -Infinity?

TREE VIEW
expand/collapse buttons
add lengths and indexing
icons for types
arrow buttons for switching views
duplicate
insert
remove
sort

MORE
Unit tests (open files, store compact json, convert to tree view and back, check against compact json)
remove index from bookmarks when tab closed and shift other tab indices

NOTE
Shift Alt Drag to multi select



'''


import sys
import os
import json
import time
import logging
import getpass
import Utilities.JSONTools as jst

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *


################
# Logger Setup #
################

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

# TODO Check this
# reomoving prexisting handlers (NOTE may be unnecessary)
for lHand in logger.handlers:
    logger.removeHandler(lHand)
logger.addHandler(fh)

# TODO Check this
# NOTE May need to be set to 0 in order to prevent logging from bubbling up to maya's logger
# logger.propagate=1
logger.info('{} Initiated'.format(appTitle))


##################
# JSON CONVERTER #
##################

jsc = jst.JSONConverter(logger)


######
# UI #
######

class JSONitorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.currentFile = None

        # Info
        self.pages = []
        self.textEditors = []
        self.lineEdits = []
        self.files = []
        self.itemModels = []
        self.treeViews = []

        # History
        self.recentlyClosedFiles = []
        self.recentlyAccessedTabs = []
        self.bookmarks = {}

        # Settings
        self.title = 'JSONitor (JSON Editor by Aaron Aikman)'
        self.autoUpdateViews = False
        self.autoCompleteBraces = True
        self.waitTime = 0.05
        self.sortKeys = False
        jsc.setSortKeys(self.sortKeys)
        self.statusMessageDur = 2
        self.doStyling = False

        self.initUI()


    def initUI(self):
        logger.debug('Initializing UI')

        # UI File
        uiFile = os.path.dirname(os.path.realpath(__file__)) + '\\JSONitor.ui'
        logger.debug('UI file is: {}'.format(uiFile))
        uic.loadUi(uiFile, self)

        # Actions
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

        self.setWindowTitle(self.title)

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

        self.__monoFont = QFont('DejaVu Sans Mono')
        self.__monoFont.setPointSize(8)

        self.tabLayoutList = []
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.onTabChange)

        # Add tabs to widget
        self.gridLayout.addWidget(self.tabs)

        # Deleting temp widgets from Designer
        self.gridLayout.removeWidget(self.textEdit)
        self.textEdit.deleteLater()
        self.textEdit = None

        # Deleting temp widgets from Designer
        self.gridLayout.removeWidget(self.filepathLineEdit)
        self.filepathLineEdit.deleteLater()
        self.filepathLineEdit = None

        # Line Column Label
        self.lineColLabel = QLabel()
        self.lineColLabel.setText('Ln 0, Cl 0')
        self.statusbar.addPermanentWidget(self.lineColLabel)

        self.addPage()

        self.show()


    ###################
    # Widget / Window #
    ###################

    def createLineEdit(self):
        logger.debug('Creating Line Edit')
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
        logger.debug('Creating Text Editor')

        # Instance
        textEditor = QsciScintilla()

        # TODO Fix temp text
        tempText = '''{
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
    '''
        tempText = '{"root": {"1": ["A", "B", "C"], "2": {"test": "thing", "asfd": 23, "tesfdsat": null, "2-1": ["G", "H", 0.0, 0, null], "2-2": [true, false, "L"]}, "3": ["D", "E", "F"]}, "extra": null}'
        textEditor.setText(tempText)
        textEditor.setUtf8(True)             # Set encoding to UTF-8
        textEditor.setFont(self.__monoFont)

        # Text wrapping
        textEditor.setWrapMode(QsciScintilla.WrapWord)
        textEditor.setWrapVisualFlags(QsciScintilla.WrapFlagByText)
        textEditor.setWrapIndentMode(QsciScintilla.WrapIndentIndented)

        # End-of-line mode
        textEditor.setEolMode(QsciScintilla.EolWindows)
        textEditor.setEolVisibility(False)

        # Indentation
        textEditor.setIndentationsUseTabs(False)
        textEditor.setTabWidth(4)
        textEditor.setIndentationGuides(True)
        textEditor.setTabIndents(True)
        textEditor.setAutoIndent(True)

        # Caret
        textEditor.setCaretForegroundColor(QColor("#ff0000ff"))
        textEditor.setCaretLineVisible(True)
        textEditor.setCaretLineBackgroundColor(QColor("#1f0000ff"))
        textEditor.setCaretWidth(2)

        # Margins
        textEditor.setMarginType(0, QsciScintilla.NumberMargin)
        textEditor.setMarginWidth(0, "0000")
        textEditor.setMarginWidth(1, "0")
        textEditor.setMarginsForegroundColor(QColor("#ff888888"))

        # Lexer
        self.lexer = QsciLexerJSON(textEditor)
        self.lexer.setDefaultFont(self.__monoFont)
        textEditor.setFolding(True)

        # self.lexer = QsciLexerXML(textEditor)
        # self.lexer = QsciLexerYAML(textEditor)

        textEditor.setAutoCompletionSource(QsciScintilla.AcsDocument)
        textEditor.setAutoCompletionThreshold(3)
        textEditor.setAutoCompletionCaseSensitivity(False)

        textEditor.setLexer(self.lexer)

        # textEditor.setFont(self.__monoFont)

        textEditor.textChanged.connect(self.textEditChanged)
        textEditor.cursorPositionChanged.connect(self.updateLineColInfo)

        # Drops
        textEditor.setAcceptDrops(True)

        # Multiline Editing
        textEditor.SendScintilla(textEditor.SCI_SETADDITIONALSELECTIONTYPING, 1)

        textEditor.setMarginSensitivity(0, True)
        textEditor.setMarginSensitivity(1, True)
        textEditor.marginClicked.connect(self.marginLeftClick)

        if self.doStyling:
            textEditor.setStyleSheet(self.textEditStyleSheet)

        self.textEditors.append(textEditor)

        return textEditor


    def createTreeView(self):
        logger.debug('Creating Tree View')
        # tree = json.loads(self.textEditors[self.tabInd()].text())
        sampleJSON = jsc.getDict(self.textEditors[self.tabInd()].text())

        itemModel = StandardItemModel()
        if sampleJSON:
            itemModel.populateTree(sampleJSON, itemModel.invisibleRootItem())
        itemModel.itemChanged.connect(self.treeViewChanged)
        self.itemModels.append(itemModel)

        treeView = QTreeView()
        treeView.setModel(itemModel)
        treeView.setHeaderHidden(True)
        treeView.setDragDropMode(QAbstractItemView.InternalMove)
        treeView.expandAll()
        # treeView.collapseAll()
        self.treeViews.append(treeView)

        if self.doStyling:
            treeView.setStyleSheet(self.treeViewStyleSheet)

        return treeView


    def createPage(self, *contents):
        logger.debug('Creating page')
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
        logger.debug('Adding page')
        self.pages.append( self.createPage( ('v', self.createLineEdit()), ('h', self.createTextEditor()), ('h', self.createTreeView())) )
        tabName = os.path.splitext(os.path.basename(self.lineEdits[-1].text()))[0]
        self.tabs.addTab( self.pages[-1] , tabName )
        self.tabs.setCurrentIndex( len(self.pages)-1 )
        self.textEditors[self.tabInd()].setFocus()


    def closeWindow(self):
        logger.debug('Closing JSONitor')
        if self.tabs.tabText(self.tabInd())[-1] == '*':
            if self.quickPrompt('Save?', 'Do you want to save before closing JSONitor?'):
                self.saveFile()
        sys.exit()


    #################
    # File Handling #
    #################

    def newFile(self):
        self.addPage()
        self.statusMessage('New tab')

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

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.currentFile = filenames[0]
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
                self.textEditors[self.tabInd()].setText(data)

            self.files[self.tabInd()] = self.currentFile
            logger.debug('Open Files: {}'.format(self.files))

            self.setWindowTitle('{} - {}'.format(self.title, os.path.basename(self.currentFile)))
            tabName = os.path.splitext(os.path.basename(self.lineEdits[self.tabInd()].text()))[0]
            self.tabs.setTabText(self.tabInd(), tabName)
            self.updateTreeViewFromText()
            self.statusMessage('Opened file: {}'.format(self.currentFile))


    def saveFile(self, doDialog = 0):
        # TODO fix infinite loop if you cancel save dialog
        filename = self.files[self.tabInd()]
        fpText = self.lineEdits[self.tabInd()].text()
        if doDialog:
            # TODO set default to json
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
            newText = str(self.textEditors[self.tabInd()].text())
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
                # TODO add try in case can't make dir
            with open(filename, 'w') as f:
                f.write(newText)

            self.setWindowTitle('{} - {}'.format(self.title, os.path.basename(self.currentFile)))

            self.files[self.tabInd()] = self.currentFile
            tabName = os.path.splitext(os.path.basename(self.lineEdits[self.tabInd()].text()))[0]
            self.tabs.setTabText(self.tabInd(), tabName)
            self.statusMessage('Saved file: {}'.format(filename))
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
        del self.textEditors[tabIndex]
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
        self.bookmarks[ind] = [self.files[self.tabInd()], self.textEditors[self.tabInd()].getCursorPosition()]
        self.statusMessage('Set bookmark {}'.format(ind))


    def onBookmarkGo(self, ind):
        filename, pos = self.bookmarks[ind]
        if filename in self.files:
            tabInd = self.files.index(filename)
            self.tabs.setCurrentIndex(tabInd)
            self.textEditors[tabInd].setCursorPosition(pos[0], pos[1])
            self.statusMessage('Jumped to bookmark {}'.format(ind))


    ##############
    # Go Options #
    ##############

    def goToLine(self):
        pos, ok = QInputDialog.getInt(self,"Go to Line","Enter line number")
        if ok:
            self.textEditors[self.tabInd()].setCursorPosition((pos-1), 0)
            self.textEditors[self.tabInd()].setFocus()
            self.statusMessage('Jumped to line {}'.format(pos-1))


    ###########
    # Setters #
    ###########

    @pyqtSlot(str)
    def setTextEditText(self, txt):
        logger.debug('Text to populate Text View with is {}'.format(txt))
        self.textEditors[self.tabInd()].setText(txt)


    @pyqtSlot(tuple)
    def setTextEditCursorPos(self, pos):
        logger.debug('Position to set text cursor is {}'.format(pos))
        self.textEditors[self.tabInd()].setCursorPosition(pos[0], pos[1])


    @pyqtSlot()
    def itemModelClear(self):
        logger.debug('Clearing Item Model')
        self.itemModels[self.tabInd()].clear()


    @pyqtSlot(dict)
    def itemModelPopulate(self, dic):
        logger.debug('Dict to populate Tree View with is {}'.format(dic))
        itemModel = self.itemModels[self.tabInd()]
        itemModel.populateTree(dic, itemModel.invisibleRootItem())


    @pyqtSlot()
    def treeViewExpandAll(self):
        logger.debug('Expanding Tree View')
        self.treeViews[self.tabInd()].expandAll()


    ####################
    # Helper Functions #
    ####################

    def tabInd(self):
        return self.tabs.currentIndex()


    def updateTreeViewFromText(self):
        tabIndex = self.tabInd()
        textEdit = self.textEditors[tabIndex]
        t = TreeViewUpdateThread(textEdit)
        t.itemModelClearSignal.connect(self.itemModelClear)
        t.itemModelPopulateSignal.connect(self.itemModelPopulate)
        t.treeViewExpandAllSignal.connect(self.treeViewExpandAll)
        t.statusSignal.connect(self.statusMessage)
        t.start()


    def updateTextFromTreeView(self):
        tabIndex = self.tabInd()
        itemModel = self.itemModels[tabIndex]
        t = TextUpdateThread(itemModel)
        t.textEditSignal.connect(self.setTextEditText)
        t.statusSignal.connect(self.statusMessage)
        t.start()


    def updateTextAutoBrace(self, txt, pos):
        t = TextAutoBraceThread(txt, pos)
        t.textEditSignal.connect(self.setTextEditText)
        t.textEditCursorPosSignal.connect(self.setTextEditCursorPos)
        t.start()


    def treeViewChanged(self, itm):
        if self.autoUpdateViews:
            self.updateTextFromTreeView()
            self.updateTreeViewFromText()


    @pyqtSlot(str)
    def statusMessage(self, msg, dur=2):
        dur = self.statusMessageDur if self.statusMessageDur else dur
        dur *= 1000
        self.statusbar.showMessage(str(msg), dur)
        logger.info(msg)


    def quickPrompt(self, title, message):
        reply = QMessageBox.question(self, title,
                        message, QMessageBox.Yes, QMessageBox.No)
        return reply == QMessageBox.Yes


    def replaceStrIndex(self, text, index=0, replacement=''):
        return '{}{}{}'.format(text[:index], replacement, text[index+1:])


    def textEditChanged(self):
        tabName = '{}*'.format(os.path.splitext(os.path.basename(self.lineEdits[self.tabInd()].text()))[0])
        self.tabs.setTabText(self.tabInd(), tabName)
        self.setWindowTitle('{} - {}'.format(self.title, tabName))
        if self.autoUpdateViews:
            self.updateTreeViewFromText()

        # AutoTyping
        if self.autoCompleteBraces:
            textEdit = self.textEditors[self.tabInd()]
            p = textEdit.getCursorPosition()
            text = textEdit.text()
            lastTypedChar = ''
            nextChar = None
            textLines = []
            for ind, line in enumerate(text.split('\n')):
                textLines.append(line)
                if ind == p[0]:
                    if p[1] > 0:
                        lastTypedChar = line[p[1]:(p[1]+1)]
                        nextChar = line[(p[1]+1):(p[1]+2)]

            # TODO fix bug where you can backspace there characters
            autoContinued = False
            autoContinueOptions = ['}', ']', '"']
            if nextChar:
                if nextChar in autoContinueOptions:
                    proceed = False
                    if lastTypedChar == '}' and nextChar == '}':
                        proceed = True
                    elif lastTypedChar == ']' and nextChar == ']':
                        proceed = True
                    elif lastTypedChar == '"' and nextChar == '"':
                        proceed = True
                    if proceed:
                        textLines[p[0]] = self.replaceStrIndex(textLines[p[0]], p[1], '')
                        text = '\n'.join(textLines)
                        p = tuple([p[0], (p[1] + 1)])
                        self.updateTextAutoBrace(text, p)
                        autoContinued = True

            if not autoContinued: # Avoiding double typing
                autoReplaceOptions = ['{', '[', '"']
                if lastTypedChar in autoReplaceOptions:
                    replaceStr = lastTypedChar
                    if lastTypedChar == '{':
                        replaceStr = r'{}'
                    elif lastTypedChar == '[':
                        replaceStr = '[]'
                    elif lastTypedChar == '"':
                        replaceStr = '""'

                    textLines[p[0]] = self.replaceStrIndex(textLines[p[0]], p[1], replaceStr)
                    text = '\n'.join(textLines)
                    p = tuple([p[0], (p[1] + 1)])
                    self.updateTextAutoBrace(text, p)


    def updateLineColInfo(self):
        cursorLine, cursorCol = self.textEditors[self.tabInd()].getCursorPosition()
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


    def marginLeftClick(self, margin_nr, line_nr, state):
        print("Margin clicked (left mouse btn)!")
        print(" -> margin_nr: " + str(margin_nr))
        print(" -> line_nr:   " + str(line_nr))
        print(" -> state:   " + str(state))
        print("")

        # if state == Qt.ControlModifier:
        #     # Show green dot.
        #     self.__editor.markerAdd(line_nr, 0)

        # elif state == Qt.ShiftModifier:
        #     # Show green arrow.
        #     self.__editor.markerAdd(line_nr, 1)

        # elif state == Qt.AltModifier:
        #     # Show red dot.
        #     self.__editor.markerAdd(line_nr, 2)

        # else:
        #     # Show red arrow.
        #     self.__editor.markerAdd(line_nr, 3)

    # ''''''

    # def __margin_right_clicked(self, margin_nr, line_nr, state):
    #     print("Margin clicked (right mouse btn)!")
    #     print(" -> margin_nr: " + str(margin_nr))
    #     print(" -> line_nr:   " + str(line_nr))
    #     print("")


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


class TextAutoBraceThread(QThread):
    textEditSignal = pyqtSignal(str)
    textEditCursorPosSignal = pyqtSignal(tuple)
    statusSignal = pyqtSignal(str)

    def __init__(self, txt, pos, waitTime=0.1):
        QThread.__init__(self)
        self.txt = txt
        self.pos = pos
        self.waitTime = waitTime

    def __del__(self):
        self.wait()

    def run(self):
        time.sleep(self.waitTime)
        self.textEditSignal.emit(self.txt)
        self.textEditCursorPosSignal.emit(self.pos)
        self.statusSignal.emit('Auto-completed braces/brackets')


class TreeViewUpdateThread(QThread):
    itemModelClearSignal = pyqtSignal()
    itemModelPopulateSignal = pyqtSignal(dict)
    treeViewExpandAllSignal = pyqtSignal()
    statusSignal = pyqtSignal(str)

    def __init__(self, textEdit, waitTime=0.1):
        QThread.__init__(self)
        self.textEdit = textEdit
        self.waitTime = waitTime

    def __del__(self):
        self.wait()

    def run(self):
        time.sleep(self.waitTime)
        newDict = jsc.getDict(self.textEdit.text())
        if newDict:
            self.itemModelClearSignal.emit()
            self.itemModelPopulateSignal.emit(newDict)
            self.treeViewExpandAllSignal.emit()
            self.statusSignal.emit('Updated Text based upon Tree View')
        else:
            logger.error('Unable to retrieve JSON from Text because Text is not valid JSON')
            self.statusSignal.emit('WARNING: Unable to update Tree View based upon Text. Make sure the text is valid JSON.')


class TextUpdateThread(QThread):
    textEditSignal = pyqtSignal(str)
    statusSignal = pyqtSignal(str)

    def __init__(self, itemModel, waitTime = 0.05):
        QThread.__init__(self)
        self.itemModel = itemModel
        self.waitTime = waitTime

    def __del__(self):
        self.wait()

    def run(self):
        time.sleep(self.waitTime)
        try:
            newJSON = jsc.getJSONPretty(jsc.getDictFromLists(self.itemModel.itemList()))
            self.textEditSignal.emit(newJSON)
            self.statusSignal.emit('Updated Text based upon Tree View')
        except ValueError as vErr:
            logger.error('Unable to retrieve JSON from Tree View because of ValueError: {}'.format(vErr))
            self.statusSignal.emit('WARNING: Unable to update Text based upon Tree View. Ensure that the Tree View would result in valid JSON. See log for details')


class StandardItemModel(QStandardItemModel):
    def __init__(self, parent = None):
        super(StandardItemModel, self).__init__(parent)
        self.__fadeFont = QFont('DejaVu Sans Mono')
        # self.__fadeFont.setPointSize(8)
        self.__fadeFont.setItalic(True)

    def itemList(self, parent=QModelIndex(), col=0):
        items = []
        for row in range(self.rowCount(parent)):
            ind = self.index(row, 0, parent)
            # To test for array elements
            isArrEl = not self.itemFromIndex(ind).isEditable()
            items.append((isArrEl, self.data(ind)))
            if self.hasChildren(ind):
                items.append(self.itemList(ind, col=(col+1)))
        return items


    def populateTree(self, children, parent, sort=False):
        if sort:
            children = sorted(children)
        if isinstance(children, (dict, list)):
            for ind, child in enumerate(children):
                # Handling lists
                if isinstance(children, list) and any([isinstance(x, dict) for x in children]): # TODO optimize
                    childItem = QStandardItem(str(ind))
                    childItem.setEditable(False)
                    childItem.setFont(self.__fadeFont)
                    # TODO use setIcon to show array
                    parent.appendRow(childItem)
                    self.populateTree(child, childItem)
                else:
                    childItem = QStandardItem(str(child))
                    parent.appendRow(childItem)
                if isinstance(children, dict):
                    self.populateTree(children[child], childItem)
        else:
            childItem = QStandardItem(str(children))
            parent.appendRow(childItem)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JSONitorWindow()
    sys.exit(app.exec_())
