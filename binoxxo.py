# binoxxo.py

_directions = ['left', 'up', 'right', 'down'] # Mögliche Richtungen
_lenDirs = len(_directions) # Anzahl der Richtungen (für schnelleren Zugriff)
_hlfDirs = int(_lenDirs / 2) # Die Hälfte, das sind dann die gegenüberliegenden Seiten
_states = ['?', 'o', 'x', 'None'] # Möglichen Zustände

def getDirection(direction) -> int: # Gibt die Richtung als Index zurück, wenn nicht bereits eine Zahl
    if type(direction) is not int:
        return _directions.index(direction)
    return direction

def getOppositeDir(direction) -> int: # Gibt die gegensätzliche Richtung als Index zurück
    direction = getDirection(direction)
    if direction < _hlfDirs:
        return direction + _hlfDirs
    return direction - _hlfDirs

def validateDirection(direction) -> str: # Für die Vollständigkeit...
    direction = direction.lower()
    if direction in _directions:
        return direction
    return _directions[0]

def getState(state) -> int: # Gibt den Index vom 'State' zurück
    if type(state) is not int:
        return _states.index(state)
    return state

def getOppositeState(state) -> str: # Wenn X dann O und umgedreht, wenn keines von beiden '?'
    if state == _states[1]:
        return _states[2]
    if state == _states[2]:
        return _states[1]
    return state

def validateState(state) -> str: # Hilfsmethode, alles was nicht 'x' oder 'o' wird zu '?'
    state = state.lower()
    if isXorO(state):
        return state
    return _states[0]

def isXorO(check) -> bool: # Prüft ob es x oder O ist
    return check in _states[1:3]

def isEitherXorO(check) -> bool: # Prüft ein Array ob es nur O oder nur X ist
    length = len(check)
    if length <= 0:
        return False

    for i in range(length):
        if i == 0 and not isXorO(check[i]) or check[i] != check[i - 1]:
            return False
    return True

def createCounterArry(length) -> list: # Hilfsmethode, erzeugt Array zum zählen von X und O
    res = []
    while length > len(res):
        res.append({_states[1]: 0, _states[2]: 0}) # 'x' und 'o'
    return res

class Cell: # Eine Zelle
    def __init__(self, data=_states[0], neighbors=[]):
        self.data = validateState(data)
        self.neighbors = [None] * _lenDirs

        # Zelle mit den Nachbarn verbinden
        for i in range(len(neighbors)):
            if i >= _lenDirs:
                break
            if neighbors[i] is not None:
                neighbors[i].neighbors[i - _hlfDirs] = self
            self.neighbors[i] = neighbors[i]

    def __str__(self):
        return self.data

    def __repr__(self):
        return self.data

    def dataIndex(self) -> int: # Gibt den State-Index der Zelle zurück
        return _states.index(self.data)

    def checkDirection(self, direction, length=1) -> list: # Gibt ein Array der nächsten data zurück ('None' wenn kein Nachbar)
        direction = getDirection(direction)
        nextCell = self.neighbors[direction]

        if nextCell is None:
            return [_states[-1]] * length
        if length <= 1:
            return [nextCell.data]
        return [nextCell.data] + nextCell.checkDirection(direction, length - 1)

    def checkOpposite(self, direction, length=1) -> list: # Genau wie checkDirection aber zusätzlich die entgegengesetzte Richtung
        direction = getDirection(direction)
        oppositeDir = getOppositeDir(direction)
        return self.checkDirection(direction, length) + self.checkDirection(oppositeDir, length)

    def isSolved(self) -> bool: # Prüft, ob es nicht mehr '?' ist
        return self.data != _states[0]

    def solve(self) -> str: # Versucht die Zelle zu lösen
        if self.isSolved(): # Bereits gelöst
            return _states[-1]

        # Lösungsstrategie
        # Wenn zwei Nachbarn auf einer Seite oder eine jeweils auf der gegenüberliegenden gleich sind
        # Dann ist diese Zelle das Gegenteil
        for direction in range(_hlfDirs): # Überprüfe die gegenüberliegenden
            arr = self.checkOpposite(direction)
            if isEitherXorO(arr):
                self.data = getOppositeState(arr[0])
                return self.data

        for direction in range(_lenDirs): # Überprüfe in eine Richtung
            arr = self.checkDirection(direction, 2)
            if isEitherXorO(arr):
                self.data = getOppositeState(arr[0])
                return self.data
        return _states[0] # Nicht (gerade) lösbar


class Grid: # Ein Feld von Zellen (die gelöst werden müssen)
    def __init__(self, initialGrid):
        self.gridLen = len(initialGrid)
        assert self.gridLen > 2 and not self.gridLen % 2, 'Grid length of {} is too small or uneven!'.format(self.gridLen)

        self.cells = []
        self.row = createCounterArry(self.gridLen)
        self.col = createCounterArry(self.gridLen)
        self.maxSolved = pow(self.gridLen, 2) # Hilfsvariable
        self.maxCount = int(self.gridLen / 2) # Hilfsvariable
        self.unsolved = 0

        upIndex = getDirection('up')
        leftIndex = getDirection('left')

        for rowNmb in range(self.gridLen):
            assert len(self.cells[rowNmb]) == self.gridLen, '{}. row isnt the same length as the column!'.format(rowNmb + 1)
            self.cells.append([])

            for colNmb in range(self.gridLen):
                neighbors = [None] * _lenDirs
                data = validateState(initialGrid[rowNmb][colNmb])

                # Die bereits vorhanden Nachbarn
                if rowNmb > 0:
                    neighbors[upIndex] = self.cells[rowNmb-1][colNmb]
                if colNmb > 0:
                    neighbors[leftIndex] = self.cells[rowNmb][colNmb-1]

                cell = Cell(data, neighbors)

                # Zählen und dann hinzufügen
                if cell.isSolved():
                    self.row[rowNmb][cell.data] += 1
                    self.col[colNmb][cell.data] += 1
                else:
                    self.unsolved += 1
                self.cells[rowNmb].append(cell)

    def __str__(self):
        return 'Length: {}'.format(len(self.cells))

    def __repr__(self):
        return self.cells
    
    def print(self): # Gibt das Feld aus
        for row in self.cells:
            print(row)

    def printRowCounter(self): # TODO
        for row in self.row:
            print(row)

    def printColCounter(self): # TODO
        for col in self.col:
            print(col)

    def fillRowWithOpposite(self, row, state): # Füllt wenn möglich eine Reihe auf
        if self.row[row][state] >= self.maxCount:
            res = getOppositeState(state)
            print("-- Fill row {} with state {} --".format(row, res))

            for col in range(self.gridLen):
                if not self.cells[row][col].isSolved():
                    self.cells[row][col].data = res
                    self.countXorO(row, col, res)

    def fillColWithOpposite(self, col, state): # Füllt wenn möglich eine Spalte auf
        if self.col[col][state] >= self.maxCount:
            res = getOppositeState(state)

            for row in range(self.gridLen):
                if not self.cells[row][col].isSolved():
                    self.cells[row][col].data = res
                    self.countXorO(row, col, res)


    def countXorO(self, row, col, res): # Zählt X/O hoch und unsolved runter und gibt zurück ob eine Linie fertig ist
        if isXorO(res):
            self.row[row][res] += 1
            self.col[col][res] += 1
            self.unsolved -= 1

            self.fillRowWithOpposite(row, res)
            self.fillColWithOpposite(col, res)
    
    def getSolvedRate(self) -> float: # Gibt wie an, viel der Felder bereits gelöst sind
        return 100 - (100 * self.unsolved / self.maxSolved)

    def solve(self): # Löst das Feld
        if self.unsolved <= 0: # Shortcut
            print('Already solved.')
            self.print()
            return

        iteration = 1
        lastRate = 0.0
        rate = 0.0

        while self.unsolved > 0:
            for row in range(self.gridLen):
                for col in range(self.gridLen):
                    res = self.cells[row][col].solve()
                    self.countXorO(row, col, res)

            lastRate = rate
            rate = self.getSolvedRate()

            print('{}. Iteration {} % solved'.format(iteration, rate))
            self.print()
            iteration += 1
            
            if rate <= lastRate:
                print('Cant solve anymore!')
                print('-- Row --')
                self.printRowCounter()
                print('-- Col --')
                self.printColCounter()
                break
            if rate >= 100:
                print('Solved!')