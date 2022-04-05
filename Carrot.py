"""
Carrot module. 🥕yay🥕
"""

import json
from io import TextIOWrapper


class CarrotError(BaseException): pass # base exception


class BaseCarrot:

    # === magic === #

    def __init__(self, file: TextIOWrapper, sep: str = ',', _doParse = True) -> None:
        """
        Base class for all Carrot instances.
        """

        self.file: TextIOWrapper = file
        self.sep = sep

        self.columns: list = None
        self.lines: list = None

        if _doParse: self.parse()
        self.isOk = self.verify_integrity()
    
    def __str__(self) -> str:
        """
        Yes.
        """
        return {'columns': self.columns, 'lines': self.lines}

    # === Utilities === #

    def parse(self) -> None:
        """
        Parse the content of the csv file into readable object.
        """

        self.lines = list(map(lambda l: tuple(l.split(self.sep)), self.file.read().rstrip().split('\n')))
        self.columns = self.lines.pop(0)
    
    def verify_integrity(self, _ErrorValue: str = None) -> bool:
        """
        Verify if all the lines have the same length than the first one.
        Returns True if test passed else False or an error value.
        """

        lengths = list(map(len, self.lines))

        if len(list(filter((len(self.columns)).__ne__, lengths))): return False if _ErrorValue is None else _ErrorValue
        return True

    def display(self, seps = (' | ', '\n')) -> None:
        """
        Display the content of the csv.
        """

        formated_cols = seps[0].join(self.columns)

        print('\033[1m', formated_cols)
        print('-' * len(formated_cols), '\033[0m')
        print(seps[1].join(map(seps[0].join, self.lines)))
    
    def _column_id(self, columnName: str) -> int:
        """
        Returns the id associated to a column (it's just its place in the list).
        """

        if not columnName in self.columns: raise CarrotError('Couldn\'t find this column. Weird.')
        return self.columns.index(columnName)

    def submit(self, sep = None) -> None:
        """
        Update the content of the file.
        """

        sep = self.sep if sep is None else sep

        raw = sep.join(self.columns) + '\n'.join([sep.join(line) for line in self.lines])

        self.file.write(raw)

    # === Read methods === #

    def find(self, column_name: str, data: str) -> tuple:
        """
        Returns the first name it finds from a given column.
        """

        column_id = self._column_id(column_name)

        for line in self.lines:
            if line[column_id] == data: return line
        
        return None
    
    def findAll(self, column_name: str, data: str) -> list:
        """
        Attempts to find matching names from a column.
        """

        column_id = self._column_id(column_name)

        matchs = []

        for line in self.lines:
            if line[column_id] == data: matchs.append(line)

        return matchs if len(matchs) else None
    
    def getColumn(self, column_name: str) -> list:
        """
        Attempts to get all the properties matching a column.
        """
        
        if column_name in self.columns: column_id = self.columns.index(column_name)
        else: raise CarrotError('Couldn\'t find this column. Weird.')

        return [line[column_id] for line in self.lines]

    # === Write methods === #

    def add(self, *args, _submit = True) -> None:
        """
        Adds a row to the csv file.
        """

        if len(args) < len(self.columns): raise CarrotError('Hum, there is missing columns, isn\'t it?')
        if len(args) > len(self.columns): raise CarrotError('Woops, there is too much columns!')

        self.lines.append('\n' + self.sep.join(args))

        if _submit: self.submit()
    
    def set(self, column: str, columnMatch: str, newValue: str, _submit = True) -> None:
        """
        Set the value of a slot.
        """

        column_id = self._column_id

        for line in self.lines:
            if line[column_id] == str(columnMatch):
                line[column_id] = newValue
                break
        
        if _submit: self.submit()
    
    def setAll(self, column: str, columnMatch: str, newValue: str, _submit = True) -> None:
        """
        Set the value for all mathing slots.
        """

        column_id = self._column_id

        for line in self.lines:
            if line[column_id] == str(columnMatch):
                line[column_id] = newValue
        
        if _submit: self.submit()
    
    def addColumn(self, name: str, defaultValue: str = 'UNDEF', _submit = True) -> None:
        """
        Adds a column.
        """

        self.columns.append(name)

        for line in self.lines: line = (*line, defaultValue)

        if _submit: self.submit()
    
    def removeColumn(self, column, _submit = True) -> None:
        """
        Removes a column.
        """

        column_id = self._column_id(column)

        self.columns.pop(column_id)

        for line in self.lines: line.pop(column_id)

        if _submit: self.submit()

    # === Advanced methods === #

    def toList(self) -> list:
        """
        Returns the csv file formated as a python list.
        The first line of the ouput will be the columns.
        Each line is a tuple containing the elements.
        """

        return self.columns + self.lines

    def toDict(self) -> dict:
        """
        Returns the csv file formated as a python dictionnary.
        (In facts it's a list but with dictionarries in it.)
        """

        out = [{col:line[i] for i, col in enumerate(self.columns)} for line in self.lines]

        return out

    def toJSON(self) -> str:
        """
        Returns the csv file formated as a JSON string of the type:
        {
            'columns': (col1, col2, col3),
            'content': [
                {'val1': value, 'val2': value, 'val3': value},
                {'val1': value, 'val2': value, 'val3': value},
                {'val1': value, 'val2': value, 'val3': value},
                etc.
            ]
        }
        """

        out = {'columns': self.columns, 'content': self.toDict()}

        return json.dumps(out)


class Carrot(BaseCarrot):
    def __init__(self, file: TextIOWrapper, sep: str = ',', _doParse=True) -> None:
        """
        Create a new Carrot instance.
        Arguments:
            file: output of the open() function on a file.
            sep: the separator of the csv file. Default is comma.
        """

        super().__init__(file, sep, _doParse)


class New(BaseCarrot):
    def __init__(self, name: str) -> None:
        """
        Create a new Carrot instance by creating a new file.
        """
        
        super().__init__(file = open(str(name), 'w+'))


class From(BaseCarrot):
    def __init__(self, path: str) -> None:
        """
        Make Carrot open a csv file.
        """

        super().__init__(file = open(str(path), 'r+'))


if __name__ == '__main__': exit('Oh, hi, you!')