'''


TODO
add drag and drop
add syntax highlighting
add tabs
add comparison
add an About
logger
save temp files/autosave
Use json file for ui colors/settings
Add goto line
Asterisk in title if not saved
fix layout
source folding
bookmarking
find and replace
conversion to (xml, csv, yaml)
Ln: Col: indicator
Undo stack
validation
copy to clipboard
format/Beautify
Minimize/compact
Feedback/email
Tree view?
Form view?



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
        self.actionClose.triggered.connect(self.closeWindow)
        # print(dir(self.filepathLineEdit))
        self.filepathLineEdit.returnPressed.connect(self.lineEditEnter)
        # self.filepathLineEdit.dropEvent.connect(self.lineEditEnter)
        self.textEdit.textChanged.connect(self.asteriskTitle)
        # self.tabLayoutList = list(range(10))
        self.initUI()
        self.show()

    def initUI(self):
        self.title = 'JSONitor - JSON Editor'
        self.setWindowTitle(self.title)
        backgroundColor = QColor()
        backgroundColor.setNamedColor('#282821')
        self.setAutoFillBackground(True)
        p = self.palette()
        # p.setColor(self.backgroundRole(), Qt.gray)
        p.setColor(self.backgroundRole(), backgroundColor)
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
        # ! Make instance of QSciScintilla class!
        # ----------------------------------------
        self.__editor = QsciScintilla()
        self.__editor.setText('''{
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
        self.__editor.setUtf8(True)             # Set encoding to UTF-8
        self.__editor.setFont(self.__myFont)

        # 1. Text wrapping
        # -----------------
        self.__editor.setWrapMode(QsciScintilla.WrapWord)
        self.__editor.setWrapVisualFlags(QsciScintilla.WrapFlagByText)
        self.__editor.setWrapIndentMode(QsciScintilla.WrapIndentIndented)

        # 2. End-of-line mode
        # --------------------
        self.__editor.setEolMode(QsciScintilla.EolWindows)
        self.__editor.setEolVisibility(False)

        # 3. Indentation
        # ---------------
        self.__editor.setIndentationsUseTabs(False)
        self.__editor.setTabWidth(4)
        self.__editor.setIndentationGuides(True)
        self.__editor.setTabIndents(True)
        self.__editor.setAutoIndent(True)

        # 4. Caret
        # ---------
        self.__editor.setCaretForegroundColor(QColor("#ff0000ff"))
        self.__editor.setCaretLineVisible(True)
        self.__editor.setCaretLineBackgroundColor(QColor("#1f0000ff"))
        self.__editor.setCaretWidth(2)

        # 5. Margins
        # -----------
        # Margin 0 = Line nr margin
        self.__editor.setMarginType(0, QsciScintilla.NumberMargin)
        self.__editor.setMarginWidth(0, "000")
        self.__editor.setMarginsForegroundColor(QColor("#ff888888"))

        # self.__lexer = JSONLexer(self.__editor)
        self.__lexer = QsciLexerJSON(self.__editor)
        # print(dir(QsciLexerJSON))
        # Set colors
        # self.__lexer.setColor(Qt.gray)
        # self.__lexer.setPaper(Qt.gray)
        self.__lexer.setDefaultFont(self.__myFont)

        # self.__lexer = QsciLexerXML(self.__editor)
        # self.__lexer = QsciLexerYAML(self.__editor)

        # print(dir(self.__editor))
        # print(self.__editor)
        self.__editor.setAutoCompletionSource(QsciScintilla.AcsDocument)
        self.__editor.setAutoCompletionThreshold(3)
        self.__editor.setAutoCompletionCaseSensitivity(False)

        # 2. Install the lexer onto your editor
        self.__editor.setLexer(self.__lexer)

        # self.__editor.setFont(self.__myFont)

        self.__editor.textChanged.connect(self.asteriskTitle)

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

        self.tabLayoutList = []
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.onTabChange)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(300,200)

        # Add tabs
        self.tabs.addTab(self.tab1,"Tab 1")
        self.tabs.addTab(self.tab2,"Tab 2")

        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.tabLayoutList.append(self.tab1.layout)
        # self.pushButton1 = QPushButton("PyQt5 button")
        self.tab1.layout.addWidget(self.__editor)
        self.tab1.setLayout(self.tab1.layout)

        # Create second tab
        self.tab2.layout = QVBoxLayout(self)
        self.tabLayoutList.append(self.tab2.layout)
        # self.tab2.layout.addWidget(self.__editor)
        self.tab2.setLayout(self.tab2.layout)

        # Add tabs to widget
        self.gridLayout.addWidget(self.tabs)
        # self.setLayout(self.layout)




        # self.gridLayout.addWidget(self.__editor)

        # Deleting Text Edit until I decide if I want it back
        self.gridLayout.removeWidget(self.textEdit)
        self.textEdit.deleteLater()
        self.textEdit = None

        self.next_item_is_table = False
        self.pages = []
        self.add_page()



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
            self.filepathLineEdit.setText(self.currentFile)
            self.openFile()


    def openFile(self):
        with open(self.currentFile, 'r', encoding='utf-8-sig') as f:
            data = f.read()
            # print(data)
            self.__editor.setText(data)

        self.setWindowTitle('{} {}'.format(self.title, self.currentFile))


    def saveFile(self, doDialog = 0):
        filename = self.currentFile
        fpText = self.filepathLineEdit.text()
        if doDialog:
            filename = QFileDialog.getSaveFileName(self, 'Save File')[0]
            self.currentFile = filename
            self.filepathLineEdit.setText(self.currentFile)
        elif filename != fpText:
            if os.path.isfile(fpText):
                if self.quickPrompt('Save?', 'Do you want to OVERWRITE to the new filepath instead of the original?'):
                    filename = fpText
                    self.currentFile = filename
                else:
                    self.filepathLineEdit.setText(self.currentFile)
            else:
                if self.quickPrompt('Save?', 'Do you want to save to the new filepath instead of the original?'):
                    filename = fpText
                    self.currentFile = filename
                else:
                    self.filepathLineEdit.setText(self.currentFile)

        if filename:
            # newText = str(self.textEdit.toPlainText())
            newText = str(self.__editor.text())
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
                # TODO add try in case can't make dir
            with open(filename, 'w') as f:
                f.write(newText)
            self.setWindowTitle('{} {}'.format(self.title, self.currentFile))
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

    def asteriskTitle(self):
        if self.currentFile:
            self.setWindowTitle('JSONitor - JSON Editor {}*'.format(self.currentFile))

    def onTabChange(self):
        # print(dir(self.tabs))
        # print(self.tabs.currentIndex())
        # print(self.tabLayoutList)
        # ind = self.tabs.currentIndex()
        # self.tabLayoutList[ind].addWidget(self.__editor)
        # print(self.tabs.currentWidget().layout.addWidget(self.__editor))
        pass

    def create_page(self, *contents):
        page = QWidget()
        vbox = QVBoxLayout()
        for c in contents:
            vbox.addWidget(c)

        page.setLayout(vbox)
        return page

    def create_table(self):
        rows, columns = random.randint(2,5), random.randint(1,5)
        table = QTableWidget( rows, columns )
        for r in range(rows):
            for c in range(columns):
                table.setItem( r, c, QTableWidgetItem( str( random.randint(0,10) ) ) )
        return table

    def create_list(self):
        list = QListWidget()
        columns = random.randint(2,5)
        for c in range(columns):
            QListWidgetItem( str( random.randint(0,10) ), list )

        return list

    def create_new_page_button(self):
        btn = QPushButton('Create a new page!')
        btn.clicked.connect(self.add_page)
        return btn

    def add_page(self):
        if self.next_item_is_table:
            self.pages.append( self.create_page( self.create_table(), self.create_new_page_button() ) )
            self.next_item_is_table = False
        else:
            self.pages.append( self.create_page( self.create_list(), self.create_new_page_button() ) )
            self.next_item_is_table = True

        self.tabs.addTab( self.pages[-1] , 'Page %s' % len(self.pages) )
        self.tabs.setCurrentIndex( len(self.pages)-1 )


    def onTabCycle(self):
        self.tabs.setCurrentIndex(self.tabs.currentIndex()+1)

    def lineEditEnter(self):
        filepathText = self.filepathLineEdit.text()
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
        if self.quickPrompt('Save?', 'Do you want to save before proceeding?'):
            self.saveFile()
        self.textEdit.clear()
        self.filepathLineEdit.clear()
        self.currentFile = None






if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())