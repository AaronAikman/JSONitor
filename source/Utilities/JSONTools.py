import json

class JSONConverter:
    def __init__(self, logger=None, JSONText=None):
        super().__init__()
        if JSONText:
            self.__content = JSONText
        self.__dict = self.getDict(JSONText) if JSONText else None
        self.sortKeys = False
        self.allowNaN = False
        self.logger = logger


    def getDict(self, j):
        """ Returns dict if json is valid, else logs
        """
        try:
            jResult = json.loads(j)
        except ValueError as vErr:
            if self.logger:
                self.logger.warn('Cannot update Tree View. JSON Invalid.  Error: {} Input: {}'.format(vErr, j))
            print('WARNING: Cannot update Tree View. JSON Invalid. See log for details.')
            return False
        return jResult


    def getJSONPretty(self, d):
        """ Return JSON that is pretty printed
        """
        return json.dumps(d, indent=4, sort_keys=self.sortKeys, allow_nan=self.allowNaN)


    def getJSONCompact(self, d):
        """ Returns JSON with no whitespace
        """
        return json.dumps(d, indent=None, separators=(',', ':'), sort_keys=self.sortKeys, allow_nan=self.allowNaN)


    def setSortKeys(self, b):
        if isinstance(b, bool):
            self.sortKeys = b


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
        """ Converts potential json strings to dict values
        """
        if isinstance(v, list):
            v = v[0]
        if isinstance(v, tuple):
            _, v = v
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

    def __splitListAlternating(self, arr):
        return (arr[::2], arr[1::2])

    def getDictFromLists(self, arr):
        ''' Converts list of lists produced by qt.itemList to a dict
        '''
        dic = {}
        if not len(arr) % 2:
            for i in range(len(arr)):
                # Handling potential key, vals
                if not i % 2:
                    primTup, sec = arr[i], arr[i+1]
                    primIsArrEl, prim = primTup
                    if primIsArrEl:
                        _, sec = self.__splitListAlternating(arr)
                        return [self.getDictFromLists(i) for i in sec]
                    else:
                        if isinstance(sec, list): # TODO figure out if this is needed
                            # if list has only one element, then process confirmed val accordingly
                            if len(sec) == 1:
                                dic[prim] = self.__filterValue(sec[0][1])
                            elif isinstance(sec[1], list):
                                # continue to search for dicts
                                dic[prim] = self.getDictFromLists(sec)
                            else:
                                dic[prim] = [self.__filterValue(y) for x,y in sec]
                        else:
                            dic[prim] = self.__filterValue(sec[1])
        else:
            # if not a set of pairs, return list immediately after checking values
            if len(arr) == 1:
                if not isinstance(arr[0][1], (list, tuple)):
                    return self.__filterValue(arr[0][1])
                else:
                    self.getDictFromLists(arr[0][1])
            return [self.__filterValue(x) for x in arr]
        return dic
