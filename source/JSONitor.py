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
proper Undo stack
copy to clipboard
Feedback/email
select Occurence
select all Occurences
Ctrl up and down to scroll
ability to resize pane middle
*add line edit to panes for searching (itemModel.findItems)
*close window, ask save if any tab has unsaved changes
save tabs on close
*fix undo
set vars on tab switch to avoid having to get index all the time?
*undo stack for tree view
go to file

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
duplicate
insert
remove
sort

MORE
Unit tests (open files, store compact json, convert to tree view and back, check against compact json)
remove index from bookmarks when tab closed and shift other tab indices
Format Commenting
make sure var names are consistent/descriptive
http://jmespath.org/tutorial.html ?

NOTE
Shift Alt Drag to multi select



'''


import sys
import os
import json
import time
import logging
import getpass
import re

from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qsci import *

import qtawesome as qta
import pyperclip

import Utilities.JSONTools as jst


################
# Logger Setup #
################

# TODO Move logger to module?
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


        # Info
        self.pages = []
        self.textEditors = []
        self.lineEdits = []
        self.files = []
        self.itemModels = []
        self.treeViews = []
        self.undoButtons = []
        self.redoButtons = []
        self.searchBars = []

        # History
        self.recentlyClosedFiles = []
        self.recentlyAccessedTabs = []
        self.bookmarks = {}
        self.textHistory = []
        self.textHistoryIndex = None
        self.textHistoryMax = 50
        self.findNextInd = 0

        # Settings
        self.title = 'JSONitor (JSON Editor by Aaron Aikman)'
        self.autoUpdateViews = False
        self.findMatchCase = False
        self.findWholeWord = False
        self.autoCompleteBraces = True
        self.waitTime = 0.05
        self.sortKeys = False
        jsc.setSortKeys(self.sortKeys)
        self.doStyling = False
        self.statusMessageDur = 2
        self.errorDuration = 5
        self.warningDuration = 2.5

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
        self.actionUndo.triggered.connect(self.undoTextChange)
        self.actionRedo.triggered.connect(self.redoTextChange)
        self.actionFind.triggered.connect(self.setFocusToFind)
        self.actionFind_Next.triggered.connect(self.findNextInText)
        # self.actionFind.triggered.connect(self.highlightCurrentLine)
        # self.filepathLineEdit.returnPressed.connect(self.lineEditEnter)

        # Go options
        self.actionGo_to_Line.triggered.connect(self.goToLine)

        self.actionGo_to_Tab_1.triggered.connect(lambda: self.onTabGo(0))
        self.actionGo_to_Tab_2.triggered.connect(lambda: self.onTabGo(1))
        self.actionGo_to_Tab_3.triggered.connect(lambda: self.onTabGo(2))
        self.actionGo_to_Tab_4.triggered.connect(lambda: self.onTabGo(3))
        self.actionGo_to_Tab_5.triggered.connect(lambda: self.onTabGo(4))
        self.actionGo_to_Tab_6.triggered.connect(lambda: self.onTabGo(5))
        self.actionGo_to_Tab_7.triggered.connect(lambda: self.onTabGo(6))
        self.actionGo_to_Tab_8.triggered.connect(lambda: self.onTabGo(7))
        self.actionGo_to_Tab_9.triggered.connect(lambda: self.onTabGo(8))
        self.actionGo_to_Tab_10.triggered.connect(lambda: self.onTabGo(9))

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

        self.searchBarStyleSheet = ('''
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
        nameAttemptCount = 1
        tmpFileName = ('{}\\AutoSave\\tmp{}.json'.format(sourcePath, (nameAttemptCount))).replace('\\', '/')
        while tmpFileName in self.files:
            tmpFileName = ('{}\\AutoSave\\tmp{}.json'.format(sourcePath, (nameAttemptCount))).replace('\\', '/')
            nameAttemptCount += 1
        self.files.append(tmpFileName)
        lineEdit.setText(tmpFileName)
        if self.doStyling:
            lineEdit.setStyleSheet(self.lineEditStyleSheet)
        return lineEdit


    def createSearchBar(self):
        logger.debug('Creating Search bar')
        lineEdit = QLineEdit()
        lineEdit.setFixedWidth(140)
        lineEdit.setFont(self.__monoFont)
        lineEdit.textChanged.connect(self.findInText)
        lineEdit.returnPressed.connect(self.findInTextAndFocus)
        self.searchBars.append(lineEdit)
        if self.doStyling:
            lineEdit.setStyleSheet(self.searchBarStyleSheet)
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
        textEditor.selectionChanged.connect(self.textEditSelectionChanged)
        textEditor.cursorPositionChanged.connect(self.updateLineColInfo)

        # Drops
        textEditor.setAcceptDrops(True)

        # Multiline Editing
        textEditor.SendScintilla(textEditor.SCI_SETADDITIONALSELECTIONTYPING, 1)

        # textEditor.SendScintilla(textEditor.SCI_BRACEHIGHLIGHTINDICATOR, True)


        textEditor.setMarginSensitivity(0, True)
        textEditor.setMarginSensitivity(1, True)
        textEditor.marginClicked.connect(self.marginLeftClick)

        if self.doStyling:
            textEditor.setStyleSheet(self.textEditStyleSheet)

        self.textEditors.append(textEditor)

        return textEditor


    def createTreeView(self):
        logger.debug('Creating Tree View')
        # tree = json.loads(self.getTextEdit().text())
        sampleJSON = jsc.getDict(self.getTextEdit().text())

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
        self.treeViews.append(treeView)

        treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        treeView.customContextMenuRequested.connect(self.openContextMenu)
        # itemModel.setHorizontalHeaderLabels([self.tr("Tree View")])

        if self.doStyling:
            treeView.setStyleSheet(self.treeViewStyleSheet)

        return treeView


    def createToolButton(self, btnUse):
        logger.debug('Creating Tool Button')
        toolButton = QToolButton()
        # toolButton = QPButton()
        if btnUse == 'left':
            toolButton.setIcon(qta.icon('fa.arrow-circle-left'))
            toolButton.clicked.connect(self.updateTextFromTreeView)
            toolButton.setToolTip('Updates Text based upon Text View.\nNote that warnings will be produced in the status bar if the process fails. (Ctrl+U)')
        elif btnUse == 'right':
            toolButton.setIcon(qta.icon('fa.arrow-circle-right'))
            toolButton.clicked.connect(self.updateTreeViewFromText)
            toolButton.setToolTip('Updates Tree View based upon Text.\nNote that warnings will be produced in the status bar if the process fails. (Ctrl+I)')
        elif btnUse == 'autoUpdate':
            toolButton.setIcon(qta.icon('fa.circle-o-notch'))
            toolButton.setCheckable(True)
            toolButton.setChecked(self.autoUpdateViews)
            toolButton.clicked.connect(self.toggleAutoUpdateViews)
            toolButton.setToolTip('Auto Update - toggles the automatic update of text and tree views when one is edited.\n Note that warnings will be produced in the status bar if the process fails.')
        elif btnUse == 'format':
            toolButton.setIcon(qta.icon('fa.align-left'))
            toolButton.clicked.connect(self.formatText)
            toolButton.setToolTip('Pretty Print: Format Text View into pretty-printed JSON')
        elif btnUse == 'compact':
            toolButton.setIcon(qta.icon('fa.align-justify'))
            toolButton.clicked.connect(self.compactText)
            toolButton.setToolTip('Compact: Format Text View into compact JSON with no whitespace')
        elif btnUse == 'sortText':
            toolButton.setIcon(qta.icon('fa.sort-alpha-asc'))
            toolButton.clicked.connect(self.sortText)
            toolButton.setToolTip('Sort Text Alphabetically')
        elif btnUse == 'sortTree':
            toolButton.setIcon(qta.icon('fa.sort-alpha-asc'))
            toolButton.clicked.connect(self.sortTree)
            toolButton.setToolTip('Sort Tree View Alphabetically')
        elif btnUse == 'copy':
            toolButton.setIcon(qta.icon('fa.clipboard'))
            toolButton.clicked.connect(self.copyTextToClipboard)
            toolButton.setToolTip('Copy Text from Text Edit')
        elif btnUse == 'expand':
            toolButton.setIcon(qta.icon('fa.expand'))
            toolButton.clicked.connect(self.treeViewExpand)
            toolButton.setToolTip('Expand Tree View')
        elif btnUse == 'collapse':
            toolButton.setIcon(qta.icon('fa.compress'))
            toolButton.clicked.connect(self.treeViewCollapse)
            toolButton.setToolTip('Collapse Tree View')
        elif btnUse == 'save':
            toolButton.setIcon(qta.icon('fa.floppy-o'))
            toolButton.clicked.connect(self.saveFile)
            toolButton.setToolTip('Save (Ctrl+S')
        elif btnUse == 'open':
            toolButton.setIcon(qta.icon('fa.folder-open'))
            toolButton.clicked.connect(self.getFile)
            toolButton.setToolTip('Open File (Ctrl+O)')
        elif btnUse == 'new':
            toolButton.setIcon(qta.icon('fa.file'))
            toolButton.clicked.connect(self.newFile)
            toolButton.setToolTip('New File (Ctrl+N)')
        elif btnUse == 'undo':
            toolButton.setIcon(qta.icon('fa.undo'))
            toolButton.clicked.connect(self.undoTextChange)
            toolButton.setEnabled(False)
            self.undoButtons.append(toolButton)
            toolButton.setToolTip('Undo Text Change (Ctrl+Shift+Z)')
        elif btnUse == 'redo':
            toolButton.setIcon(qta.icon('fa.repeat'))
            toolButton.clicked.connect(self.redoTextChange)
            toolButton.setEnabled(False)
            self.redoButtons.append(toolButton)
            toolButton.setToolTip('Redo Text Change (Ctrl+Shift+Y)')
        elif btnUse == 'settings':
            toolButton.setIcon(qta.icon('fa.cog'))
            toolButton.clicked.connect(self.redoTextChange)
            toolButton.setToolTip('Settings (Ctrl+Comma)')
        elif btnUse == 'searchCase':
            toolButton.setIcon(qta.icon('ei.fontsize'))
            toolButton.setCheckable(True)
            toolButton.setChecked(self.findMatchCase)
            toolButton.clicked.connect(self.toggleFindMatchCase)
            toolButton.setToolTip('Match case when searching')
        elif btnUse == 'searchWholeWord':
            toolButton.setIcon(qta.icon('ei.font'))
            toolButton.setCheckable(True)
            toolButton.setChecked(self.findWholeWord)
            toolButton.clicked.connect(self.toggleFindWholeWord)
            toolButton.setToolTip('Match whole word when searching')

        return toolButton


    def createHorizSpacer(self):
        return QSplitter()


    def createPage(self, *contents):
        logger.debug('Creating page')
        page = QWidget()
        vbox = QVBoxLayout()
        toolbar = QHBoxLayout()
        hbox = QHBoxLayout()
        # TODO fix to allow for specific ordering
        for lyt, c in contents:
            if lyt == 'v':
                vbox.addWidget(c)
            elif lyt == 'h':
                hbox.addWidget(c)
            elif lyt == 't':
                toolbar.addWidget(c)
        vbox.addLayout(toolbar)
        vbox.addLayout(hbox)

        page.setLayout(vbox)
        return page


    def addPage(self, setFocusOn=True):
        logger.debug('Adding page')
        self.pages.append( self.createPage(
                                            ('v', self.createLineEdit()),
                                            ('t', self.createToolButton('settings')),
                                            ('t', self.createToolButton('new')),
                                            ('t', self.createToolButton('open')),
                                            ('t', self.createToolButton('save')),
                                            ('t', self.createToolButton('undo')),
                                            ('t', self.createToolButton('redo')),
                                            ('t', self.createToolButton('compact')),
                                            ('t', self.createToolButton('format')),
                                            ('t', self.createToolButton('sortText')),
                                            ('t', self.createToolButton('copy')),
                                            ('t', self.createHorizSpacer()),
                                            ('t', self.createToolButton('left')),
                                            ('t', self.createToolButton('autoUpdate')),
                                            ('t', self.createToolButton('right')),
                                            ('t', self.createHorizSpacer()),
                                            ('t', self.createSearchBar()),
                                            ('t', self.createToolButton('searchCase')),
                                            ('t', self.createToolButton('searchWholeWord')),
                                            ('t', self.createToolButton('expand')),
                                            ('t', self.createToolButton('collapse')),
                                            ('t', self.createToolButton('sortTree')),
                                            ('h', self.createTextEditor()),
                                            ('h', self.createTreeView()))
                                            )
        tabName = os.path.splitext(os.path.basename(self.lineEdits[-1].text()))[0]
        self.tabs.addTab( self.pages[-1] , tabName )
        self.tabs.setCurrentIndex( len(self.pages)-1 )
        if setFocusOn:
            self.getTextEdit().setFocus()


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
            self.openFile(filenames[0])


    def openFile(self, filename, setFocusOn=True):
        if filename in self.files:
            self.tabs.setCurrentIndex(self.files.index(filename))
        else:
            logger.debug('File not found in current tabs. Opening new tab.')
            self.addPage(setFocusOn=setFocusOn)
            self.lineEdits[self.tabInd()].setText(filename)
            if os.path.isfile(filename):
                with open(filename, 'r', encoding='utf-8-sig') as f:
                    data = f.read()
                    self.getTextEdit().setText(data)

                self.files[self.tabInd()] = filename
                logger.debug('Open Files: {}'.format(self.files))

                self.setWindowTitle('{} - {}'.format(self.title, os.path.basename(filename)))
                tabName = os.path.splitext(os.path.basename(self.lineEdits[self.tabInd()].text()))[0]
                self.tabs.setTabText(self.tabInd(), tabName)
                self.updateTreeViewFromText()
                self.statusMessage('Opened file: {}'.format(filename))
            else:
                self.statusMessage('The following file does not exist: {}'.format(filename), 2)

    def saveFile(self, doDialog = 0):
        tabInd = self.tabInd()
        filename = self.files[tabInd]
        if not filename:
            self.saveAs()
        fpText = self.lineEdits[tabInd].text()
        if doDialog:
            filename = QFileDialog.getSaveFileName(self, 'Save File', filter='*json')[0]
            if filename:
                self.lineEdits[tabInd].setText(filename)
        elif filename != fpText:
            if os.path.isfile(fpText):
                if self.quickPrompt('Save?', 'Do you want to OVERWRITE to the new filepath instead of the original?'):
                    filename = fpText
                else:
                    self.lineEdits[tabInd].setText(filename)
            else:
                if self.quickPrompt('Save?', 'Do you want to save to the new filepath instead of the original?'):
                    filename = fpText
                else:
                    self.lineEdits[tabInd].setText(filename)

        if filename:
            newText = str(self.textEditors[tabInd].text())
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))

            if os.access(os.path.dirname(filename), os.W_OK):
                with open(filename, 'w') as f:
                    f.write(newText)
                self.setWindowTitle('{} - {}'.format(self.title, os.path.basename(filename)))

                self.files[tabInd] = filename
                tabName = os.path.splitext(os.path.basename(self.lineEdits[tabInd].text()))[0]
                self.tabs.setTabText(tabInd, tabName)
                self.statusMessage('Saved file: {}'.format(filename))

                # Handling overwriting a file that is open in another tab
                if self.files.count(filename) > 1:
                    for ind, fName in enumerate(self.files):
                        if ind != tabInd:
                            if fName == filename:
                                self.onTabGo(ind)
                                self.onTabClose(force=True)
                self.onTabGo(tabInd)

            else:
                self.statusMessage('User does not have write permissions to save to {}'.format(filename), 2)


    def saveAs(self):
        self.saveFile(1)


    #################
    # Tab Functions #
    #################

    def onTabClose(self, force=False):
        if not force:
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
        del self.undoButtons[tabIndex]
        del self.redoButtons[tabIndex]
        del self.searchBars[tabIndex]


    def onTabGo(self, ind):
        # ind -= 1
        if (len(self.pages) - 1) > ind:
            self.tabs.setCurrentIndex(ind)


    def onTabReopen(self):
        logger.info('Attempting to reopen the last closed tab.')
        reopening = True
        while reopening:
            if self.recentlyClosedFiles:
                filename = self.recentlyClosedFiles[-1]
                if os.path.isfile(filename):
                    # Not setting focus to text edit in order to
                    # be able to continue to reopen closed tabs without switching focus
                    self.openFile(filename, setFocusOn=False)
                    self.statusMessage('Reopened {}'.format(filename))
                    reopening = False
                    del self.recentlyClosedFiles[-1]
                else:
                    del self.recentlyClosedFiles[-1]
            else:
                reopening = False


    def onTabChange(self):
        self.setWindowTitle('{} - {}'.format(self.title, self.tabs.tabText(self.tabInd())))
        self.recentlyAccessedTabs.append(self.tabInd())
        # keeping up to five last tabs in case of tab overwrites
        if len(self.recentlyAccessedTabs) > 5:
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
        self.bookmarks[ind] = [self.files[self.tabInd()], self.getTextEdit().getCursorPosition()]
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
            self.getTextEdit().setCursorPosition((pos-1), 0)
            self.getTextEdit().setFocus()
            self.statusMessage('Jumped to line {}'.format(pos-1))


    #########
    # Slots #
    #########

    @pyqtSlot()
    def getTextEditTextFromTree(self):
        try:
            tabInd = self.tabInd()
            itemModel = self.itemModels[tabInd]
            itemList = itemModel.itemList()
            txt = jsc.getJSONPretty(jsc.getDictFromLists(itemList))
            logger.debug('Text to populate Text View with is {}'.format(txt))
            self.textEditors[tabInd].setText(txt)
        except ValueError as vErr:
            logger.warning('Unable to retrieve JSON from Tree View because of ValueError: {}'.format(vErr))
            self.statusMessage('Unable to update Text based upon Tree View. Ensure that the Tree View would result in valid JSON. See log for details', 1, doLog=False)


    @pyqtSlot(str)
    def setTextEditText(self, txt):
        self.getTextEdit().setText(txt)


    @pyqtSlot(tuple)
    def setTextEditCursorPos(self, pos):
        logger.debug('Position to set text cursor is {}'.format(pos))
        self.getTextEdit().setCursorPosition(pos[0], pos[1])


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
        self.getTreeView().expandAll()


    @pyqtSlot(str, int)
    def statusMessage(self, msg, mode=0, doLog=True, dur=1):
        """
        Shows a message in the status bar and writes it to the log
        mode = [info, warning, error]
        dur = ms to show message in status bar for
        """
        dur = self.statusMessageDur if self.statusMessageDur else dur
        prefix = 'INFO: '
        if mode == 2:
            prefix = 'ERROR: '
            if doLog:
                logger.error(msg)
            dur = self.errorDuration
        elif mode == 1:
            prefix = 'WARNING: '
            if doLog:
                logger.warning(msg)
            dur = self.warningDuration
        else:
            if doLog:
                logger.info(msg)

        dur *= 1000
        self.statusbar.showMessage('{}{}'.format(prefix, msg), dur)


    ########
    # Tree #
    ########

    def treeViewExpand(self):
        self.getTreeView().expandAll()


    def treeViewCollapse(self):
        self.getTreeView().collapseAll()


    def treeViewChanged(self, itm):
        if self.autoUpdateViews:
            self.updateTextFromTreeView()
            # self.updateTreeViewFromText()


    def updateTreeViewFromText(self):
        tabIndex = self.tabInd()
        textEdit = self.textEditors[tabIndex]
        t = TreeViewUpdateThread(textEdit)
        t.itemModelClearSignal.connect(self.itemModelClear)
        t.itemModelPopulateSignal.connect(self.itemModelPopulate)
        t.treeViewExpandAllSignal.connect(self.treeViewExpandAll)
        t.statusSignal.connect(self.statusMessage)
        t.start()


    def getTreeItemAndInsert(self):
        itemModel = self.itemModels[self.tabInd()]
        treeView = self.getTreeView()
        indexes = treeView.selectedIndexes()
        ind = indexes[0]
        item = itemModel.itemFromIndex(ind)
        itemParent = item.parent()
        itemClone = item.clone()
        count = 1
        itemClone.setText('New ({})'.format(count))
        while itemModel.findItems(itemClone.text(), flags=Qt.MatchRecursive):
            itemClone.setText('New ({})'.format(count))
            count += 1
        itemParent.insertRow((item.row() + 1), itemClone)
        self.refreshTree()


    def getTreeItemAndAppend(self):
        itemModel = self.itemModels[self.tabInd()]
        treeView = self.getTreeView()
        indexes = treeView.selectedIndexes()
        ind = indexes[0]
        item = itemModel.itemFromIndex(ind)
        count = 1
        newItem = QStandardItem('New ({})'.format(count))
        while itemModel.findItems(newItem.text(), flags=Qt.MatchRecursive):
            newItem.setText('New ({})'.format(count))
            count += 1
        if item.hasChildren():
            if not item.child(0).isEditable():
                newItem.setEditable(False)
                newItem.setIcon(qta.icon('fa.list-ul'))
        item.appendRow(newItem)
        self.refreshTree()


    def getTreeItemAndRemove(self):
        itemModel = self.itemModels[self.tabInd()]
        treeView = self.getTreeView()
        indexes = treeView.selectedIndexes()
        ind = indexes[0]
        item = itemModel.itemFromIndex(ind)
        itemParent = item.parent()
        itemParent.removeRow(item.row())
        self.refreshTree()


    def getTreeItemAndDuplicate(self):
        itemModel = self.itemModels[self.tabInd()]
        treeView = self.getTreeView()
        indexes = treeView.selectedIndexes()
        ind = indexes[0]
        item = itemModel.itemFromIndex(ind)
        self.duplicateTreeItemChildren(item)


    def duplicateTreeItemChildren(self, sourceItem, targetItem=None):
        itemClone = sourceItem.clone()
        itemModel = self.itemModels[self.tabInd()]
        if targetItem:
            targetItem.appendRow(itemClone)
        else:
            count = 1
            while len(itemModel.findItems(itemClone.text(), flags=Qt.MatchRecursive)) > 0:
                itemClone.setText('{} ({})'.format(itemClone.text(), count))
                count += 1
            if sourceItem.parent():
                sourceItem.parent().insertRow((sourceItem.row() + 1),itemClone)
            else:
                itemModel.invisibleRootItem().insertRow((sourceItem.row() + 1),itemClone)
        if sourceItem.hasChildren():
            for row in range(sourceItem.rowCount()):
                child = sourceItem.child(row, 0)
                # if child.hasChildren():
                self.duplicateTreeItemChildren(child, itemClone)

        self.refreshTree()


    def openContextMenu(self, position):
        treeView = self.getTreeView()
        # indexes = treeView.selectedIndexes()
        # if len(indexes) > 0:

        #     level = 0
        #     index = indexes[0]
        #     while index.parent().isValid():
        #         index = index.parent()
        #         level += 1

        menu = QMenu()
        duplicateAction = menu.addAction(self.tr("Insert"))
        duplicateAction.triggered.connect(self.getTreeItemAndInsert)

        duplicateAction = menu.addAction(self.tr("Append"))
        duplicateAction.triggered.connect(self.getTreeItemAndAppend)

        duplicateAction = menu.addAction(self.tr("Duplicate"))
        duplicateAction.triggered.connect(self.getTreeItemAndDuplicate)

        duplicateAction = menu.addAction(self.tr("Remove"))
        duplicateAction.triggered.connect(self.getTreeItemAndRemove)

        # self.treeItemPosition = position
        # if level == 0:
        #     menu.addAction(self.tr("Edit person"))
        # elif level == 1:
        #     menu.addAction(self.tr("Edit object/container"))
        # elif level == 2:
        #     menu.addAction(self.tr("Edit object"))
        # else:
        #     menu.addAction(self.tr("Edit object"))

        menu.exec_(treeView.viewport().mapToGlobal(position))


    def refreshTree(self):
        self.treeViewChanged(itm=None)


    ########
    # Text #
    ########

    def findInText(self, searchText=None, findNext=False, findNextInd=0):
        # TODO option for select single/find next
        if not searchText:
            searchText = self.getSearchBar().text()
        textEdit = self.getTextEdit()
        text = textEdit.text()
        if not self.findMatchCase:
            searchText = searchText.lower()
            text = text.lower()

        foundAtLeastOne = False
        if searchText and searchText in text:
            if self.findWholeWord:
                searchRegex = re.compile(r"\b{st}\b".format(st = searchText))
            else:
                searchRegex = re.compile(r"{st}".format(st = searchText))
            for row, line in enumerate(text.split('\n')):
                grouping = searchRegex.finditer(line)
                if not grouping:
                    textEdit.SendScintilla(textEdit.SCI_CLEARSELECTIONS)
                else:
                    proceed = True
                    lastIndFound = 0
                    if findNext:
                        textEdit.SendScintilla(textEdit.SCI_CLEARSELECTIONS)
                    for ind, match in enumerate(grouping):
                        print(ind, findNextInd)
                        if findNext:
                            print(ind, findNextInd)
                            # textEdit.SendScintilla(textEdit.SCI_CLEARSELECTIONS)
                            proceed = True if ind == findNextInd else False
                        if proceed:
                            span = match.span()
                            start = textEdit.positionFromLineIndex(row, span[0])
                            end = textEdit.positionFromLineIndex(row, span[1])
                            self.setTextSelection(start, end, foundAtLeastOne)
                            foundAtLeastOne = True
                        lastIndFound = ind
                    # For restting find next if it is too high
                    if self.findNextInd > lastIndFound - 1:
                        self.findNextInd = -1
        else:
            textEdit.SendScintilla(textEdit.SCI_CLEARSELECTIONS)


    def findNextInText(self):
        self.findInText(findNext=True, findNextInd=self.findNextInd)
        self.findNextInd += 1


    def findInTextAndFocus(self):
        # TODO fix not using findmethod
        self.findInText()
        self.setFocusToTextEdit()


    def toggleFindMatchCase(self):
        self.findMatchCase = not self.findMatchCase
        self.findInText()


    def toggleFindWholeWord(self):
        self.findWholeWord = not self.findWholeWord
        self.findInText()


    # # text cursor functions
    # def getTextCursor(self):
    #     return self.getTextEdit().cursor()


    # def setTextCursorPos(self, value):
    #     tc = self.getTextCursor()
    #     tc.setPos(value, QTextCursor.KeepAnchor)
    #     self.getTextEdit().setCursor(tc)


    # def getTextCursorPos(self):
    #     return self.getTextCursor().position()


    # def getTextSelection(self):
    #     cursor = self.getTextCursor()
    #     return cursor.selectionStart(), cursor.selectionEnd()


    def setTextSelection(self, start, end, add=False):
        textEdit = self.getTextEdit()
        # offset = ed.positionFromLineIndex(0, 7)
        # textEdit.SendScintilla(textEdit.SCI_MULTIPLESELECTADDNEXT, start, end)
        if add:
            textEdit.SendScintilla(textEdit.SCI_ADDSELECTION, start, end)
        else:
            textEdit.SendScintilla(textEdit.SCI_SETSELECTION, start, end)
        # cursor = self.getTextCursor()
        # cursor.setPos(start[0], start[1])
        # cursor.setPos(end[0], end[1], QTextCursor.KeepAnchor)
        # textEdit.setCursorPosition(start[0], start[1])
        # TODO extra selections?
        # textEdit.setFocus()
        # self.getTextEdit().setCursorPosition(end[0], end[1], QTextCursor.KeepAnchor)
        # self.getTextEdit().setTextCursor(cursor)

    def clearTextSelection(self):
        textEdit = self.getTextEdit()
        textEdit.SendScintilla(textEdit.SCI_SETSELECTION)


    def updateTextFromTreeView(self):
        self.storeTextBackup()
        tabIndex = self.tabInd()
        itemModel = self.itemModels[tabIndex]
        t = TextUpdateThread(itemModel)
        t.textEditFromTreeSignal.connect(self.getTextEditTextFromTree)
        t.statusSignal.connect(self.statusMessage)
        t.start()


    def updateTextAutoBrace(self, txt, pos):
        self.storeTextBackup()
        t = TextAutoBraceThread(txt, pos)
        t.textEditSignal.connect(self.setTextEditText)
        t.textEditCursorPosSignal.connect(self.setTextEditCursorPos)
        t.start()


    def undoTextChange(self):
        if self.textHistory:
            if self.textHistoryIndex == (len(self.textHistory) - 1):
                if self.getTextEdit().text() != self.textHistory[self.textHistoryIndex]:
                    self.storeTextBackup(setIndex=False)
                    self.textHistoryIndex += 1
            self.textHistoryIndex -= 1
            self.getTextEdit().setText(self.textHistory[self.textHistoryIndex])
            self.setUndoRedoButtons()


    def redoTextChange(self):
        if self.textHistory:
            if self.textHistoryIndex < (len(self.textHistory) - 1):
                self.textHistoryIndex += 1
                self.getTextEdit().setText(self.textHistory[self.textHistoryIndex])
            self.setUndoRedoButtons()


    def setUndoRedoButtons(self):
        if self.textHistoryIndex < (len(self.textHistory) - 1):
            for redoButton in self.redoButtons:
                redoButton.setEnabled(True)
        else:
            for redoButton in self.redoButtons:
                redoButton.setEnabled(False)

        if self.textHistoryIndex:
            for undoButton in self.undoButtons:
                undoButton.setEnabled(True)
        else:
            for undoButton in self.undoButtons:
                undoButton.setEnabled(False)


    def storeTextBackup(self, setIndex=True):
        # TODO Store history for each tab
        # TODO set undo redo buttons enabled when switching tabs
        self.textHistory.append(self.getTextEdit().text())
        if len(self.textHistory) > self.textHistoryMax:
            del self.textHistory[0]
        if setIndex:
            self.textHistoryIndex = (len(self.textHistory) - 1)
            # self.setUndoRedoButtons()
            for redoButton in self.redoButtons:
                redoButton.setEnabled(False)
            for undoButton in self.undoButtons:
                undoButton.setEnabled(True)


    def setFocusToFind(self):
        searchBar = self.getSearchBar()
        searchBar.clear()
        # searchBar.setText('')
        searchBar.setFocus()


    def setFocusToTextEdit(self):
        self.getTextEdit().setFocus()


    def replaceStrIndex(self, text, index=0, replacement=''):
        return '{}{}{}'.format(text[:index], replacement, text[index+1:])


    def sortText(self):
        jsc.sortKeys = True
        self.formatText()
        jsc.sortKeys = False


    def formatText(self):
        self.storeTextBackup()
        textEdit = self.getTextEdit()
        dictText = jsc.getDict(textEdit.text())
        if dictText:
            prettyText = jsc.getJSONPretty(dictText)
            textEdit.setText(prettyText)


    def compactText(self):
        self.storeTextBackup()
        textEdit = self.getTextEdit()
        dictText = jsc.getDict(textEdit.text())
        if dictText:
            compactText = jsc.getJSONCompact(dictText)
            textEdit.setText(compactText)


    def textEditSelectionChanged(self):
        textEdit = self.getTextEdit()
        textEdit.SendScintilla(textEdit.SCI_CLEARSELECTIONS)

    def textEditChanged(self):
        tabName = '{}*'.format(os.path.splitext(os.path.basename(self.lineEdits[self.tabInd()].text()))[0])
        self.tabs.setTabText(self.tabInd(), tabName)
        self.setWindowTitle('{} - {}'.format(self.title, tabName))
        if self.autoUpdateViews:
            self.updateTreeViewFromText()

        # AutoTyping
        if self.autoCompleteBraces:
            textEdit = self.getTextEdit()
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


            autoContinued = False
            autoContinueOptions = ['}', ']', '"']
            autoReplaceOptions = ['{', '[', '"']

            # TODO fix this
            # Checking for all but " in order to remove end character when start character missing
            # for i in range(len(autoContinueOptions)-1):
            #     if autoContinueOptions[i] in textLines[p[0]][p[1]:]:
            #         if not autoReplaceOptions[i] in textLines[p[0]][:p[1]]:
            #             print('hi')
            #             textLines[p[0]] = textLines[p[0]].replace(autoContinueOptions[i], '')
            #             text = '\n'.join(textLines)
            #             p = tuple([p[0], (p[1])])
            #             self.updateTextAutoBrace(text, p)
            #             autoContinued = True


            if nextChar:
                if nextChar in autoContinueOptions:
                    print('l', lastTypedChar, 'n', nextChar)
                    print(textLines[p[0]].replace(' ', 'x'))
                    # if lastTypedChar not in autoReplaceOptions:
                    # if all([not x in autoReplaceOptions for x in textLines[p[0]]]):
                    #     print('hi')
                    #     textLines[p[0]] = self.replaceStrIndex(textLines[p[0]], p[1]+1, '')
                    #     text = '\n'.join(textLines)
                    #     p = tuple([p[0], (p[1] + 1)])
                    #     self.updateTextAutoBrace(text, p)
                    #     autoContinued = True
                    # else:
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

                if lastTypedChar in autoReplaceOptions:
                    proceed = True

                    replaceStr = lastTypedChar

                    if lastTypedChar == '{':
                        replaceStr = r'{}'
                    elif lastTypedChar == '[':
                        replaceStr = '[]'
                    elif lastTypedChar == '"':
                        # TODO fix inability to backspace first " if there are two in a row
                        replaceStr = '""'

                    textLines[p[0]] = self.replaceStrIndex(textLines[p[0]], p[1], replaceStr)

                    if lastTypedChar == '"':
                        # Do not add " if not appropriate
                        if textLines[p[0]].count(lastTypedChar) % 2:
                            proceed = False

                    if proceed:
                        text = '\n'.join(textLines)
                        p = tuple([p[0], (p[1] + 1)])
                        self.updateTextAutoBrace(text, p)



    ####################
    # Helper Functions #
    ####################

    def tabInd(self):
        return self.tabs.currentIndex()


    def getTextEdit(self):
        return self.textEditors[self.tabInd()]


    def getLineEdit(self):
        return self.lineEditors[self.tabInd()]


    def getTreeView(self):
        return self.treeViews[self.tabInd()]


    def getSearchBar(self):
        return self.searchBars[self.tabInd()]


    def toggleAutoUpdateViews(self):
        self.autoUpdateViews = not self.autoUpdateViews


    def copyTextToClipboard(self):
        pyperclip.copy(self.getTextEdit().text())


    def quickPrompt(self, title, message):
        reply = QMessageBox.question(self, title,
                        message, QMessageBox.Yes, QMessageBox.No)
        return reply == QMessageBox.Yes


    def sortTree(self):
        itemModel = self.itemModels[self.tabInd()]
        itemModel.sort(0)
        self.refreshTree()



    def updateLineColInfo(self):
        cursorLine, cursorCol = self.getTextEdit().getCursorPosition()
        self.lineColLabel.setText('Ln {}, Cl {}'.format(cursorLine + 1, cursorCol + 1))


    def lineEditEnter(self):
        # TODO maybe add a separate button for open
        filepathText = self.lineEdits[self.tabInd()].text()
        if filepathText:
            if os.path.isfile(filepathText):
                self.openFile(filepathText)
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


    # class CommandDelete(QUndoCommand):

    # def __init__(self, listWidget, item, row, description):
    #     super(CommandDelete, self).__init__(description)
    #     self.listWidget = listWidget
    #     self.string = item.text()
    #     self.row = row

    # def redo(self):
    #     item = self.listWidget.takeItem(self.row)
    #     del item

    # def undo(self):
    #     self.listWidget.insertItem(self.row, self.string)

    # def highlightCurrentLine(self):
        # pass
        # textEdit = self.getTextEdit()
        # offset = ed.positionFromLineIndex(0, 7)
        # textEdit.SendScintilla(textEditor.SCI_SETSELECTION, 1)

        # extraSelections = []

        # # if not self.isReadOnly():
        # selection = QTextEdit.ExtraSelection()

        # lineColor = QColor(Qt.yellow).lighter(160)

        # selection.format.setBackground(lineColor)
        # selection.format.setProperty(QTextFormat.FullWidthSelection, QVariant(True))
        # # selection.cursor = textEdit.cursor()
        # # selection.cursor.clearSelection()
        # extraSelections.append(selection)

        # textEdit.setExtraSelections(extraSelections)


class TextAutoBraceThread(QThread):
    textEditSignal = pyqtSignal(str)
    textEditCursorPosSignal = pyqtSignal(tuple)
    statusSignal = pyqtSignal(str, int)

    def __init__(self, txt, pos, waitTime=0.05):
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
        self.statusSignal.emit('Auto-completed braces/brackets', 0)


class TreeViewUpdateThread(QThread):
    itemModelClearSignal = pyqtSignal()
    itemModelPopulateSignal = pyqtSignal(dict)
    treeViewExpandAllSignal = pyqtSignal()
    statusSignal = pyqtSignal(str, int)

    def __init__(self, textEdit, waitTime=0.06):
        QThread.__init__(self)
        self.textEdit = textEdit
        self.waitTime = waitTime

    def __del__(self):
        self.wait()

    def run(self):
        time.sleep(self.waitTime)
        # TODO move this to slot?
        newDict = jsc.getDict(self.textEdit.text())
        if newDict:
            self.itemModelClearSignal.emit()
            self.itemModelPopulateSignal.emit(newDict)
            self.treeViewExpandAllSignal.emit()
            self.statusSignal.emit('Updated Text based upon Tree View', 0)
        else:
            self.statusSignal.emit('Unable to update Tree View based upon Text. Make sure the text is valid JSON.', 1)


class TextUpdateThread(QThread):
    textEditFromTreeSignal = pyqtSignal()
    statusSignal = pyqtSignal(str, int)

    def __init__(self, itemModel, waitTime = 0.05):
        QThread.__init__(self)
        self.itemModel = itemModel
        self.waitTime = waitTime

    def __del__(self):
        self.wait()

    def run(self):
        time.sleep(self.waitTime)
        self.textEditFromTreeSignal.emit()
        # try:
        #     itemList = self.itemModel.itemList()
        #     print(itemList)
        #     newJSON = jsc.getJSONPretty(jsc.getDictFromLists(itemList))
        #     self.textEditFromTreeSignal.emit(newJSON)
        #     self.statusSignal.emit('Updated Text based upon Tree View', 0)
        # except ValueError as vErr:
        #     logger.warning('Unable to retrieve JSON from Tree View because of ValueError: {}'.format(vErr))
        #     self.statusSignal.emit('WARNING: Unable to update Text based upon Tree View. Ensure that the Tree View would result in valid JSON. See log for details', 1)


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
                    childItem.setIcon(qta.icon('fa.list-ul'))
                    childItem.setFont(self.__fadeFont)
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
