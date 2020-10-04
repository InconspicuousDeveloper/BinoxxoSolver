#
# BINOXXO
# Ein Rätsel aus der Zeitung. Ähnlich wie Soduko.
# Hier müssen ein Feld mit O und X gefüllt werden.
# Es dürfen nicht mehr als zwei aufeinanderfolgende X oder O in einer Zeile oder
# Spalte erscheinen. In jeder Zeile und jeder Spalte müssen O und X gleich oft
# vorkommen.
#
# Dieses Programm löst es automatisch.
# Input ist eine csv Datei und output ist console.
#
# TODO Cell.getOppositeData(data) besser machen (evtl 'state' allgemein ändern)
# TODO https://docs.python.org/3/howto/logging.html

#################
#### Imports ####
#################

import sys
import os
import csv
import logging

#################
#### Klassen ####
#################

class Cell: # Eine Zelle
    _dirs = ['left', 'up', 'right', 'down'] # Mögliche Richtungen
    _lenDirs = len(_dirs) # Anzahl der Richtungen (für schnelleren Zugriff)
    _hlfDirs = int(_lenDirs / 2) # Die Hälfte, das sind dann die gegenüberliegenden Seiten
    _states = ['?', 'o', 'x', 'None'] # Möglichen Zustände

    @staticmethod
    def getDirection(direction) -> int: # Gibt die Richtung als Index zurück (für Cell._dirs)
        if type(direction) is not int:
            return Cell._dirs.index(direction)
        return direction

    @staticmethod
    def getOppositeDir(direction) -> int: # Gibt die gegensätzliche Richtung als Index zurück (für Cell._dirs)
        direction = Cell.getDirection(direction)
        if direction < Cell._hlfDirs:
            return direction + Cell._hlfDirs
        return direction - Cell._hlfDirs

    @staticmethod
    def getState(state) -> int: # Gibt den Index vom 'State' zurück
        if type(state) is not int:
            return Cell._states.index(state)
        return state

    @staticmethod
    def getOppositeState(state) -> str: # Wenn X dann O und umgedreht, wenn keines von beiden '?'
        if state == Cell._states[1]:
            return Cell._states[2]
        if state == Cell._states[2]:
            return Cell._states[1]
        return state

    @staticmethod
    def transfomToData(data) -> str: # Hilfsmethode, alles was nicht 'o' oder 'x' ist '?'
        data = data.lower()
        if Cell._states[1] == data or Cell._states[2] == data:
            return data
        return Cell._states[0]

    @staticmethod
    def createCounterArry(length) -> []: # Hilfsmethode, erzeugt Array zum zählen von O und X
        res = [] # [{'x': 0, 'o': 0}] * length funktioniert nicht!
        while length > len(res):
            res.append({'x': 0, 'o': 0}) # 'o' und 'x'
        return res

    @staticmethod
    def isXorO(check) -> bool: # Prüft ob es O oder X ist
        return check == Cell._states[1] or check == Cell._states[2]

    @staticmethod
    def isEitherXorO(check) -> bool: # Prüft ein Array ob es nur O oder nur X ist
        length = len(check)
        if length <= 0:
            return False

        for i in range(length):
            if i == 0 and not Cell.isXorO(check[i]) or check[i] != check[i - 1]:
                return False
        return True

    def __init__(self, data=_states[0], neighbors=[]):
        self.data = Cell.transfomToData(data)
        self.neighbors = [None] * Cell._lenDirs

        # Zelle mit den Nachbarn verbinden
        for i in range(len(neighbors)):
            if i >= Cell._lenDirs:
                break
            if neighbors[i] is not None:
                neighbors[i].neighbors[i - Cell._hlfDirs] = self
            self.neighbors[i] = neighbors[i]

    def __str__(self):
        return self.data

    def __repr__(self):
        return self.data

    def dataIndex(self) -> int: # Gibt den State-Index der Zelle zurück
        return Cell._states.index(self.data)

    def checkDirection(self, direction, length=1) -> []: # Gibt ein Array der nächsten data zurück ('None' wenn kein Nachbar)
        direction = Cell.getDirection(direction)
        nextCell = self.neighbors[direction]

        if nextCell is None:
            return [Cell._states[-1]] * length
        if length <= 1:
            return [nextCell.data]
        return [nextCell.data] + nextCell.checkDirection(direction, length - 1)

    def checkOpposite(self, direction, length=1) -> []: # Genau wie checkDirection aber zusätzlich die entgegengesetzte Richtung
        direction = Cell.getDirection(direction)
        oppositeDir = Cell.getOppositeDir(direction)
        return self.checkDirection(direction, length) + self.checkDirection(oppositeDir, length)

    def isSolved(self) -> bool: # Prüft, ob es nicht mehr '?' ist
        return self.data != Cell._states[0]

    def solve(self) -> str: # Versucht die Zelle zu lösen
        if self.isSolved(): # Bereits gelöst
            return Cell._states[-1]

        # Lösungsstrategie
        # Wenn zwei Nachbarn auf einer Seite oder eine jeweils auf der gegenüberliegenden gleich sind
        # Dann ist diese Zelle das Gegenteil
        for direction in range(Cell._hlfDirs): # Überprüfe die gegenüberliegenden
            arr = self.checkOpposite(direction)
            if Cell.isEitherXorO(arr):
                self.data = Cell.getOppositeState(arr[0])
                return self.data

        for direction in range(Cell._lenDirs): # Überprüfe in eine Richtung
            arr = self.checkDirection(direction, 2)
            if Cell.isEitherXorO(arr):
                self.data = Cell.getOppositeState(arr[0])
                return self.data
        return Cell._states[0] # Nicht (gerade) lösbar

class Grid: # Ein Feld von Zellen (die gelöst werden müssen)
    def __init__(self, initialGrid):
        self.gridLen = len(initialGrid)
        assert self.gridLen > 2 and not self.gridLen % 2, 'Grid length of {} is too small or uneven!'.format(self.gridLen)

        self.cells = []
        self.row = Cell.createCounterArry(self.gridLen)
        self.col = Cell.createCounterArry(self.gridLen)
        self.maxSolved = pow(self.gridLen, 2) # Hilfsvariable
        self.maxCount = int(self.gridLen / 2) # Hilfsvariable
        self.unsolved = 0

        upIndex = Cell.getDirection('up')
        leftIndex = Cell.getDirection('left')

        for rowNmb in range(self.gridLen):
            assert len(grid[rowNmb]) == self.gridLen, '{}. row isnt the same length as the column!'.format(rowNmb + 1)
            self.cells.append([])

            for colNmb in range(self.gridLen):
                neighbors = [None] * Cell._lenDirs
                data = Cell.transfomToData(initialGrid[rowNmb][colNmb])

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
            res = Cell.getOppositeState(state)
            print("-- Fill row {} with state {} --".format(row, res))

            for col in range(self.gridLen):
                if not self.cells[row][col].isSolved():
                    self.cells[row][col].data = res
                    self.countXorO(row, col, res)

    def fillColWithOpposite(self, col, state): # Füllt wenn möglich eine Spalte auf
        if self.col[col][state] >= self.maxCount:
            res = Cell.getOppositeState(state)

            for row in range(self.gridLen):
                if not self.cells[row][col].isSolved():
                    self.cells[row][col].data = res
                    self.countXorO(row, col, res)


    def countXorO(self, row, col, res): # Zählt X/O hoch und unsolved runter und gibt zurück ob eine Linie fertig ist
        if Cell.isXorO(res):
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

####################
#### Funktionen ####
####################

# Endet das Programm
def endProgram(pText='', code=0):
    print(pText)
    # os.system('pause')
    sys.exit(code)

# Liest den Input und gibt das Feld zurück
def readCsvFile(filename='binoxxo.csv'):
    with open(filename, newline='') as csvFile:
        csvReader = csv.reader(csvFile)
        grid = []
        
        for row in csvReader:
            grid.append(row)
        return grid

def isO(cell):
    return cell.lower() == 'o'

def isX(cell):
    return cell.lower() == 'x'

#############################
#### Start des Programms ####
#############################

grid = readCsvFile()
#grid = [['1','2','3','x'],['1','o','3','4'],['1','2','o','4'],['x','2','3','4']]

playfield = Grid(grid)

playfield.print()
print('#### Start ####')
playfield.solve()

endProgram()


# Methoden zum herausfinden
# 1. Zählen ist x und o pro Zeile und Spalte 50/50 (ob schon eins 50% erreicht hat)
# 1 1 2 2 0 2 0 3 0   o
# 0 0 1 1 0 1 2 1 1 x
# . . . . . . x . . 1 0
# . . . . . o . o . 0 2
# . . o o . . . o . 0 3
# . . . . . . . . x 1 0
# . . . . . x . . . 1 0
# . o o . . . x . . 1 2
# . . . x . . . o . 1 1
# o . . . . o . . . 0 2
# . . x . . . . x . 2 0
# . . . o . . . . . 0 1

# wo 2 gleiche aufeinander folgen können auf jeden Fall das andere gesetzt werden
# . . . . . O x X O
# . . . . . o . o .
# . X o o X . . o .
# . . . . . . O X x
# . . . O . x . . .
# X o o X . . x . .
# . . . x . . . o .
# o . . O . o . . .
# . . x . . . . x .
# . . . o . . . . .

# wenn zwischen zwei gleichen eins frei ist, kann es auch gefüllt werden
# . . . . . o x x o
# . . . . . o X o .
# . x o o x . . o .
# . . . . . . o x x
# . . . o . x . . .
# x o o x . . x . .
# . . . x . . . o .
# o . . o X o . . .
# . . x X . . . x .
# . . . o . . . . .


# . . . . . . x . .
# . . . . . o . o .
# . . o o . . . o .
# . . . . . . . . x
# . . . . . x . . .
# . o o . . . x . .
# . . . x . . . o .
# o . . . . o . . .
# . . x . . . . x .
# . . . o . . . . .

