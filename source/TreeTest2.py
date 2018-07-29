import sys

import json

from PyQt5 import QtGui, QtCore, QtWidgets

import Utilities.JSONTools as jst

class StandardItemModel(QtGui.QStandardItemModel):
    def __init__(self, parent = None):
        super(StandardItemModel, self).__init__(parent)

    def itemList(self, parent = QtCore.QModelIndex()):
        items = []
        for row in range(self.rowCount(parent)):
            idx = self.index(row, 0, parent)
            items.append(self.data(idx))
            if self.hasChildren(idx):
                items.append(self.itemList(idx))
        return items


    def _populateTree(self, children, parent, sort=False):
        if sort:
            children = sorted(children)
        if isinstance(children, (dict, list)):
            for child in children:
                child_item = QtGui.QStandardItem(str(child))
                parent.appendRow(child_item)
                # if isinstance(children, types.DictType):
                if isinstance(children, dict):
                    self._populateTree(children[child], child_item)
        else:
            child_item = QtGui.QStandardItem(str(children))
            parent.appendRow(child_item)

    # def populate(self):
    #     for row in range(0, 10):
    #         parentItem = self.invisibleRootItem()
    #         for col in range(0, 4):
    #             item = QtGui.QStandardItem("item (%s, %s)" % (row, col))
    #             parentItem.appendRow(item)
    #             parentItem = item


    # def isNumberOrNone(self, s):
    #     '''
    #     if s is an int or float, return that, else return None
    #     Must check if == None in order to avoid registing 0 as false
    #     '''
    #     try:
    #         return int(s)
    #     except (ValueError, TypeError):
    #         pass
    #     try:
    #         return float(s)
    #     except (ValueError, TypeError):
    #         return None

    # def filterValue(self, v):
    #     if v in ['None', 'null']:
    #         return None
    #     elif v in ['True', 'true']:
    #         return True
    #     elif v in ['False', 'false']:
    #         return False
    #     else:
    #         # Checking for number
    #         tryNum = self.isNumberOrNone(v)
    #         if tryNum != None:
    #             return tryNum
    #         else:
    #             # String
    #             return v

    # def dictFromLists(self, arr):
    #     ''' Converts list of lists produced by qt.itemList to a dict
    #     '''
    #     dic = {}
    #     if not len(arr) % 2:
    #         for i in range(len(arr)):
    #             # Handling potential key, vals
    #             if not i % 2:
    #                 prim, sec = arr[i], arr[i+1]
    #                 # if list has only one element, then process confirmed val accordingly
    #                 if len(sec) == 1:
    #                     dic[prim] = self.filterValue(sec[0])
    #                 else:
    #                     # continue to search for dicts
    #                     dic[prim] = self.dictFromLists(sec)
    #     else:
    #         # if not a set of pairs, return list immediately after checking values
    #         return [self.filterValue(x) for x in arr]
    #     return dic





class MainForm(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)


        tree = {'root': {
                    "1": ["A", "B", "C"],
                    "2": {
                        "test" : "thing",
                        "asfd" : 23,
                        "tesfdsat" : None,
                        "2-1": ["G", "H", 0.0, 0, None],
                        "2-2": [True, False, "L"]},
                    "3": ["D", "E", "F"]},
                    'extra': None
        }
        # print(tree)
        print(json.dumps(tree))

        testJSON = ('''{
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
        # print(testJSON)
        # tree = json.loads(testJSON)
        print(tree)
        # self.model.populate()
        # self.model._populateTree(tree, root_model.invisibleRootItem())
        # print(dir(self.view))

        self.model = StandardItemModel()
        self.model._populateTree(tree, self.model.invisibleRootItem())

        self.view = QtWidgets.QTreeView()
        self.view.setModel(self.model)
        self.view.setHeaderHidden(True)
        self.view.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.view.expandAll()
        # self.view.collapseAll()

        self.setCentralWidget(self.view)

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = MainForm()
    form.show()
    app.exec_()

    # print(form.model.itemList())
    jsc = jst.JSONConverter()
    print(jsc.getDictFromLists(form.model.itemList()))

if __name__ == '__main__':
    main()