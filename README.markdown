# JSONitor
#### by Aaron Aikman

## Summary


A JSON Editor for manipulating JSON files in text and tree views.

## Preview
![PreviewImage](https://imgur.com/00NUuRO.jpg)

## Getting started

### EXE

It is recommend to simply copy `JSONitor.exe` to where you would like to store the executable and generated info file.  From there, you may double click to run the exe.

### Python Install

If preferred or if they above method does not work, you may install
module requirements (PyQt5, Qscintilla, QtAwesome, and Pyperclip) by changing to the source folder and running:

    pip3 install -r requirements.txt

Once the requirements are installed, you can run JSONitor using Python 3 in the source folder.

    python3 JSONitor.py

The application window should appear.

## Usage

Has many functions of a regular text editor, but also features a tree view which can be edited and transferred back to JSON in the text view.

#### Tree View Basics
![TreeViewBasics](https://imgur.com/Lxs1yfD.gif)

Right-click to access the Tree View context menu
Double-click to edit an item

Click the left-pointing arrow at top middle of the window to update the Text View based upon the Tree View

#### Text View Basics
![TextViewBasics](https://imgur.com/GGml7zf.gif)

AutoSyntax (on by default) will add braces, brackets and quotes for you

Click the right-pointing arrow at top middle of the window to update the Tree View based upon the Text View

#### Auto Update Tree View
![AutoUpdateTreeView](https://imgur.com/FMQf8DR.gif)

Click the cycle icon at top middle of the window to enable Auto Updating of Text and Tree Views (note that this process may be slow for large files when typing in Text View)

#### Find and Edit
![FindAndEdit](https://imgur.com/Gl88wy0.gif)

Press Ctrl+F to focus the find bar

Start typing the find entries in the Text View

Press Return to find the next match

Press Ctrl+Shift+F to select all matches in the Text View

Press Ctrl+Return to focus the Text View

#### Bookmarks and Tabs
![BookmarksAndTabs](https://imgur.com/V1zHp8w.gif)

Tabs may be accessed specifially using Ctrl+(0-9)

Tabs may by cycled using Ctrl+Tab

Tabs may be navigated using Ctrl+(PageUp, PageDown)

Bookmarks may be set using Ctrl+Shift+(0-9)

Bookmarks may be accessed using Alt+(0-9)

#### Text Formating Options
![TextFormatingOptions](https://imgur.com/qh5JvG2.gif)

Click the buttons or using the JSON menu to format your text to compact, pretty-printed, or sorted

#### Auto Update and Undo
![AutoUpdateAndUndo](https://imgur.com/jq4QdS6.gif)

Undos and Redo stack based upon updates from the Tree View per tab

#### Auto Syntax and Settings
![AutoSyntaxAndSettings](https://imgur.com/32COdrn.gif)

Press Ctrl+, to open the JSONSettings.json file

Make a change and save the file to update your settings

Note that the file must be valid JSON

#### Go to Line
![GoToLine](https://imgur.com/3SQ6It8.gif)

Press Ctrl+G to open a dialog to go to a line

#### Close Tab and Reopen Tab
![CloseTabReopenTab](https://imgur.com/pss4Gcv.gif)

Press Ctrl+W to close a tab

Press Ctrl+Shift+T to reopen closed tabs

### Additional Features
Save All

Save On Close

Remembering Open Tabs

Remembering Window Sizes



## Debugging

### Log File
The log file, created in whichever folder JSONitor is run from, provides information about JSONitor processes.

### Issues
If you encounter any errors in the code, please file an issue on github: [https://github.com/AaronAikman/JSONitor/issues](https://github.com/AaronAikman/JSONitor/issues).

### Basic Troubleshooting
For a fresh run, you may try deletting the JSONitorSetting.json and JSONitorHistory.json files, and running again.

## Author

* Author: Aaron Aikman
* Email: aaronaikman [4t] aol dot com
* Repository: [http://github.com/AaronAikman/JSONitor](http://github.com/AaronAikman/JSONitor)

## Version

* Version: 1.0.2
* Release Date: 2018-08-04

## Revision History

### Version 1.0.2

* Release Date: 2018-08-04
* Changes: Fixed SaveAs error

### Version 1.0.1

* Release Date: 2018-08-04