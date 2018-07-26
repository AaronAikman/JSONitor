'''


TODO add drag and drop
TODO add syntax highlighting
TODO add tabs
TODO add comparison
TODO add an About
TODO logger
TODO save temp files
TODO Add close window shortcut
TODO Use json file for ui colors/settings
TODO Add goto line
TODO Asterisk in title if not saved

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
        self.initUI()
        self.show()

    def initUI(self):
        self.setWindowTitle('JSONitor - JSON Editor')
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
        self.__editor.setText("This\n")         # Line 1
        self.__editor.append("is\n")            # Line 2
        self.__editor.append("a\n")             # Line 3
        self.__editor.append("QScintilla\n")    # Line 4
        self.__editor.append("test\n")          # Line 5
        self.__editor.append("program\n")       # Line 6
        self.__editor.append("to\n")            # Line 7
        self.__editor.append("illustrate\n")    # Line 8
        self.__editor.append("some\n")          # Line 9
        self.__editor.append("basic\n")         # Line 10
        self.__editor.append("program\n")       # Line 6
        self.__editor.append("to\n")            # Line 7
        self.__editor.append("illustrate\n")    # Line 8
        self.__editor.append("some\n")          # Line 9
        self.__editor.append("basic\n")         # Line 10
        self.__editor.append("functions.")      # Line 11
        self.__editor.setLexer(None)
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

        self.__lexer = JSONLexer(self.__editor)

        # 2. Install the lexer onto your editor
        self.__editor.setLexer(self.__lexer)

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
        # print(dir(self))
        self.gridLayout.addWidget(self.__editor)
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

        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.currentFile = filenames[0]
            self.filepathLineEdit.setText(self.currentFile)

            with open(self.currentFile, 'r', encoding='utf-8-sig') as f:
                data = f.read()
                # print(data)
                self.textEdit.setText(data)


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
            newText = str(self.textEdit.toPlainText())
            with open(filename, 'w') as f:
                f.write(newText)
        else:
            self.saveAs()

    def saveAs(self):
        self.saveFile(1)

    def quickPrompt(self, title, message):
        reply = QMessageBox.question(self, title,
                        message, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        else:
            return False

    def closeWindow(self):
        sys.exit()


    def newFile(self):
        if self.quickPrompt('Save?', 'Do you want to save before proceeding?'):
            self.saveFile()
        self.textEdit.clear()
        self.filepathLineEdit.clear()
        self.currentFile = None



class JSONLexer(QsciLexerCustom):

    def __init__(self, parent):
        super(JSONLexer, self).__init__(parent)

        # Default text settings
        # ----------------------
        self.setDefaultColor(QColor("#ff000000"))
        self.setDefaultPaper(QColor("#ffffffff"))
        self.setDefaultFont(QFont("Consolas", 14))

        # Initialize colors per style
        # ----------------------------
        self.setColor(QColor("#ff000000"), 0)   # Style 0: black
        self.setColor(QColor("#ff7f0000"), 1)   # Style 1: red
        self.setColor(QColor("#ff0000bf"), 2)   # Style 2: blue
        self.setColor(QColor("#ff007f00"), 3)   # Style 3: green

        # Initialize paper colors per style
        # ----------------------------------
        self.setPaper(QColor("#ffffffff"), 0)   # Style 0: white
        self.setPaper(QColor("#ffffffff"), 1)   # Style 1: white
        self.setPaper(QColor("#ffffffff"), 2)   # Style 2: white
        self.setPaper(QColor("#ffffffff"), 3)   # Style 3: white

        # Initialize fonts per style
        # ---------------------------
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), 0)   # Style 0: Consolas 14pt
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), 1)   # Style 1: Consolas 14pt
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), 2)   # Style 2: Consolas 14pt
        self.setFont(QFont("Consolas", 14, weight=QFont.Bold), 3)   # Style 3: Consolas 14pt

    ''''''

    def language(self):
        return "JSON"
    ''''''

    def description(self, style):
        if style == 0:
            return "myStyle_0"
        elif style == 1:
            return "myStyle_1"
        elif style == 2:
            return "myStyle_2"
        elif style == 3:
            return "myStyle_3"
        ###
        return ""
    ''''''

    def styleText(self, start, end):
        # 1. Initialize the styling procedure
        # ------------------------------------
        self.startStyling(start)

        # 2. Slice out a part from the text
        # ----------------------------------
        text = self.parent().text()[start:end]

        # 3. Tokenize the text
        # ---------------------
        p = re.compile(r"[*]\/|\/[*]|\s+|\w+|\W")

        # 'token_list' is a list of tuples: (token_name, token_len)
        token_list = [ (token, len(bytearray(token, "utf-8"))) for token in p.findall(text)]

        # 4. Style the text
        # ------------------
        # 4.1 Check if multiline comment
        multiline_comm_flag = False
        editor = self.parent()
        if start > 0:
            previous_style_nr = editor.SendScintilla(editor.SCI_GETSTYLEAT, start - 1)
            if previous_style_nr == 3:
                multiline_comm_flag = True
            ###
        ###
        # 4.2 Style the text in a loop
        for i, token in enumerate(token_list):
            if multiline_comm_flag:
                self.setStyling(token[1], 3)
                if token[0] == "*/":
                    multiline_comm_flag = False
                ###
            ###
            else:
                if token[0] in ["for", "while", "return", "int", "include"]:
                    # Red style
                    self.setStyling(token[1], 1)

                elif token[0] in ["(", ")", "{", "}", "[", "]", "#"]:
                    # Blue style
                    self.setStyling(token[1], 2)

                elif token[0] == "/*":
                    multiline_comm_flag = True
                    self.setStyling(token[1], 3)

                else:
                    # Default style
                    self.setStyling(token[1], 0)
                ###
            ###
        ###

    ''''''

''' end Class '''



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())