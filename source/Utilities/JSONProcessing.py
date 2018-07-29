import json

class JSONTools:
    def __init__(self, JSONText=None):
        super().__init__()
        if JSONText:
            self.__content = JSONText
        self.__dict = self.getDict(JSONText) if JSONText else None


    def getDict(self, j):
        return json.loads(j)


    def getJSON(self, d):
        return json.dumps(d)


    # def getElem(self):
    #     return [x for x in self.__dict]


    def getDepth(self, d, level=1):
        if not isinstance(d, dict) or not d:
            return level
        return max(self.getDepth(d[k], level + 1) for k in d)

    def getAllKeys(self, d, level=1, keys=[]):
        if not isinstance(d, dict) or not d:
            return level
        keys.append([k for k in d])
        # print(keys)
        # return max(self.getAllKeys(d[k], level + 1, keys) for k in d)
        [self.getAllKeys(d[k], level + 1, keys) for k in d]
        return keys


    def __isNumberOrNone(self, s):
        '''
        if s is an int or float, return that, else return None
        Must check if == None in order to avoid registing 0 as false
        '''
        try:
            return int(s)
        except (ValueError, TypeError):
            pass
        try:
            return float(s)
        except (ValueError, TypeError):
            return None

    def __filterValue(self, v):
        if v in ['None', 'null']:
            return None
        elif v in ['True', 'true']:
            return True
        elif v in ['False', 'false']:
            return False
        else:
            # Checking for number
            tryNum = self.__isNumberOrNone(v)
            if tryNum != None:
                return tryNum
            else:
                # String
                return v

    def getDictFromLists(self, arr):
        ''' Converts list of lists produced by qt.itemList to a dict
        '''
        dic = {}
        if not len(arr) % 2:
            for i in range(len(arr)):
                # Handling potential key, vals
                if not i % 2:
                    prim, sec = arr[i], arr[i+1]
                    # if list has only one element, then process confirmed val accordingly
                    if len(sec) == 1:
                        dic[prim] = self.__filterValue(sec[0])
                    else:
                        # continue to search for dicts
                        dic[prim] = self.getDictFromLists(sec)
        else:
            # if not a set of pairs, return list immediately after checking values
            return [self.__filterValue(x) for x in arr]
        return dic


#Testing

# testJSON = ('''{
#     "glossary": {
#         "title": "example glossary",
#         "GlossDiv": {
#         "title": "S",
#         "GlossList": {
#             "GlossEntry": {
#             "ID": "SGML",
#             "SortAs": "SGML",
#             "GlossTerm": "Standard Generalized Markup Language",
#             "Acronym": "SGML",
#             "Abbrev": "ISO 8879:1986",
#             "GlossDef": {
#                 "para": "A meta-markup language, used to create markup languages such as DocBook.",
#                 "GlossSeeAlso": [
#                 "GML",
#                 "XML"
#                 ]
#             },
#             "GlossSee": "markup"
#             }
#         }
#         }
#     }
# }
#     ''')
# j = JSONAsset(testJSON)
# print(j.getAllKeys(j.getDict()))