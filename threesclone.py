# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 17:45:49 2017

@author: Andy

Based on: https://github.com/waltdestler/Threesus/blob/master
"""

# [1,2,3,6,12,24,48,96,192,384,768,1536,3072,6144,12288]

import numpy as np
import msvcrt as m
from enum import Enum
import random as r
from math import log, pow
import time

def wait():
    m.getch()

# CARD
class Card():
#    Vestiges of trying to make Card a ndarray. Was the wrong move.
#    """([('value', np.int16), ('uniqueID', np.int16)])"""
#    def __new__(cls, v, u):
#        obj = np.empty(2, dtype=[('value', np.int16), ('uniqueID', np.int16)])
#        obj.value = v
#        obj.uniqueID = u
#        return obj
#    def __array_finalize__(self, obj):
#        if obj is None: return
#        else: raise TypeError("Missing value or uniqueID")
#        
    def __init__(self, v, u):
        self.value = v
        self.uniqueID = u
    def score(self):
        """calculate the score"""
        if self.value == 0: return 0
        valueOver3 = self.value / 3
        print(valueOver3)
        exp = int(log(valueOver3, 2)) + 1
        print(exp)
        return int(pow(3, exp))
    def __eq__(self, other):
        """override default eq; test if have same value and uniqueID"""
        return (other is Card) and (self.value == other.value) and \
                (self.uniqueID == other.uniqueID)
    def __ne__(self, other):
        return not( (other is Card) and (self.value == other.value) and 
                (self.uniqueID == other.uniqueID) )
    def __hash__(self):
        hash = 17
        hash = hash*23 + hash(self.value)
        hash = hash*23 + hash(self.uniqueID)
        return hash
    def __str__(self):
        return str(self.value)
    def __repr__(self):
        return "{Value=" + str(self.value) + ",UID=" + str(self.uniqueID) + "}"
    def canMergeWith(self, other):
        if self.value == 1:
            return other.value == 2
        elif self.value == 2:
            return other.value == 1
        else:
            return self.value == other.value
    def getMergedWith(self, other):
        if self.value == 1:
            if other.value == 2:
                return Card(3, self.uniqueID)
            else:
                return None
        elif self.value == 2:
            if other.value == 1:
                return Card(3, self.uniqueID)
            else:
                return None
        else:
            if self.value == other.value:
                return Card(self.value * 2, self.uniqueID)
            else:
                return None


class Board:
    """Uses Q4/spreadsheet coordinates (right is positive, down is positive)"""
    def __init__(self, board=None):
        self.width = 4
        self.height = 4
        self.cards = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        if board is Board:
            self.copyFrom(board)
    def __getitem__(self, key):
        """key must be a 2 element tuple"""
        (row, col) = key
        if row>=self.width or row<0 or col>=self.height or col<0:
            return None
        return self.cards[row][col]
    def __setitem__(self, key, value):
        """key must be a 2 element tuple"""
        (row, col) = key
        self.cards[row][col] = value
    def __delitem__(self, key):
        if key is tuple:
            (row, col) = key
            self.cards[row][col] = 0
        else:
            self.cards[key] = np.zeros(self.width)
    def __str__(self):
        ret = ''
        for row in self.cards:
            for s in row:
                if (s is None):
                    ret += '0\t'
                else:
                    ret += str(s) 
                    ret += '\t'
            ret += '\n'
        return ret[:-1]
    def copyFrom(self, board):
        self.board = np.copy(self.cards)
    def getTotalScore(self):
        total = 0
        for row in self.cards:
            for card in row:
                total += card.score()
        return total
    def shift(self, direction, newCardCells):
        ret = False
        increment = self.getShift(direction)
        widthOrHeight = self.getShiftWidthOrHeight(direction);
        for startingCell in self.getShiftStartingCells(direction):
            shifted = self.shiftRowOrColumn(startingCell, increment, widthOrHeight)
            if shifted and newCardCells is not None:
                newCardCells.append(np.subtract(
                        startingCell, tuple((widthOrHeight-1)*x for x in increment)))
                ret = ret or shifted
        return ret

    def getShift(self, direction):
        if direction == "up":
            return (-1, 0)
        elif direction == "down":
            return (1, 0)
        elif direction == "left":
            return (0, -1)
        elif direction == "right":
            return (0, 1)
        else:
            return None
    def getShiftWidthOrHeight(self, direction):
        if direction == "left":
            return self.width
        elif direction == "right":
            return self.width
        elif direction == "up":
            return self.height
        elif direction == "down":
            return self.height
        else:
            return None
    def getShiftStartingCells(self, direction):
        """returns tuple (x, y) for all starting cells (the cells in the 
        direction of the shift"""
        if direction == "up":
            return [(0, y) for y in range(self.height)]
        elif direction == "down":
            return [(self.width-1, y) for y in range(self.height)]
        elif direction == "left":
            return [(x, 0) for x in range(self.width)]
        elif direction == "right":
            return [(x, self.height) for x in range(self.width)]
        else:
            return None
    def getCardMaxValue(self):
        big = 0
        for row in self.cards:
            for c in row:
                if c:
                    big = max(big, c.value)
        return big
    def shiftRowOrColumn(self, startingCell, increment, widthOrHeight):
        ret = False
        prevCell = startingCell
        curCell = tuple(np.subtract(startingCell, increment))
            
        for _ in range(widthOrHeight-1):
            curCard = self[curCell]
            if curCard is not None:
                prevCard = self[prevCell]
                if prevCard is None:
                    self[prevCell] = curCard
                    self[curCell] = None
                    ret = True
                else:
                    merged = curCard.getMergedWith(prevCard)
                    if merged is not None:
                        self[prevCell] = merged
                        self[curCell] = None
                        ret = True
            prevCell = curCell
            curCell = tuple(np.subtract(curCell, increment))
        return ret
    def getBoardLinearArray(self):
        return self.cards.flatten()
    def getBoardArray(self):
        return list(self.cards)

class Deck:
    def __init__(self, rand=None):
        self.INITIAL_CARD_VALUES = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]
        self.cardValues = []
        if rand is None:
            self.random = r.Random()
        elif rand is Deck:
            self.copyFrom(rand)
        else:
            self.random = rand
    def copyFrom(self, deck):
        self.cardValues = deck.cardValues[:]
    def drawNextCard(self):
        """Returns the number for the next card from the deck"""
        if not self.cardValues:
            self.rebuildDeck()
        ret = self.cardValues.pop()
        return ret
    def peekNextCard(self):
        if not self.cardValues:
            self.rebuildDeck()
        return self.cardValues[-1:]
    def getCountsOfCards(self):
        if not self.cardValues:
            self.rebuildDeck()
        ret = {}
        for value in self.cardValues:
            try:
                ret[value] = ret[value] + 1
            except KeyError:
                ret[value] = 1
        return ret
    def removeCard(self, cardValue):
        if not self.cardValues:
            self.rebuildDeck()
        self.cardValues.remove(cardValue)
    def rebuildDeck(self):
        if self.cardValues:
            raise Exception("Rebuilding Deck when deck not empty")
        self.cardValues = self.INITIAL_CARD_VALUES[:]
        self.random.shuffle(self.cardValues)

    
class Game:
    def __init__(self, rand=None):
        self.nextCardID = 0
        if rand is None:
            self.random = r.Random()
        else:
            self.random = rand
        self.deck = Deck(self.random)
        self.board = Board()
        self.prevBoard = Board(self.board)
        self.tempBoard = Board()
        self.nextBonusCard = None
        self.lastShiftTime = None
        self.lastShiftDirection = None
        self.totalTurns = 0
        self.initializeBoard()
    def __str__(self):
        return str(self.board)
    def getCurrentBoard(self):
        return self.board
    def getPreviousBoard(self):
        return self.prevBoard
    def getCurrentDeck(self):
        return self.deck
    def getNextCardHint(self):
        if self.nextBonusCard is None:
            nextCardValue = self.deck.peekNextCard()
        else:
            nextCardValue = self.nextBonusCard
            
        if nextCardValue == 1:
            return NextCardHint.One
        elif nextCardValue == 2:
            return NextCardHint.Two
        elif nextCardValue == 3:
            return NextCardHint.Three
        else:
            return NextCardHint.Bonus
    def getLastShiftTime(self):
        return self.lastShiftTime
    def setLastShiftTime(self, timee):
        """should be a time object"""
        self.lastShiftTime = timee
    def getLastShiftDirection(self):
        return self.lastShiftDirection
    def setLastShiftDirection(self, sd):
        self.lastShiftDirection = sd
    def getTotalTurns(self):
        return self.totalTurns 
    def setTotalTurns(self, turns):
        self.totalTurns = turns
    def shift(self, dir):
        self.tempBoard.copyFrom(self.board)
        newCardCells = []
        shifted = self.board.shift(dir, newCardCells)
        if shifted:
            newCardCell = self.random.choice(newCardCells)
            self.board[newCardCell] = self.drawNextCard()
            
            self.prevBoard.copyFrom(self.tempBoard)
            self.setLastShiftTime(time.clock())
            self.setLastShiftDirection(dir)
            self.totalTurns += 1
        return shifted
    def initializeBoard(self, n=9):
        for _ in range(n):
            cell = self.getRandomEmptyCell()
            self.board[cell] = self.drawNextCard(0)
    def getRandomEmptyCell(self):
        ret = (
                self.random.randint(0, self.board.width-1), 
                self.random.randint(0, self.board.height-1)   )
        while self.board[ret] is not None:
            ret = (
                    self.random.randint(0, self.board.width-1), 
                    self.random.randint(0, self.board.height-1)   )
        return ret
    def drawNextCard(self, BONUS_CARD_CHANCE = 1/21):
        if self.nextBonusCard is None:
            cardValue = self.deck.drawNextCard()
        
        maxCardValue = self.board.getCardMaxValue()
        if maxCardValue >= 48 and self.random.uniform(0,1) < self.BONUS_CARD_CHANCE:
            possibleBonusCards = [x for x in self.getPossibleBonusCards(maxCardValue)]
            self.nextBonusCard = self.random.choice(possibleBonusCards)
        else:
            self.nextBonusCard = None
        ncid = self.nextCardID 
        self.nextCardID += 1
        return Card(cardValue, ncid)
    def getPossibleBonusCards(maxCardValue):
        maxBonusCard = maxCardValue / 8
        val = 6
        while val <= maxBonusCard:
            yield val
            val *= 2
            
class NextCardHint(Enum):
    One = 1
    Two = 2
    Three = 3
    Bonus = 4
            
    
###################################################e############################          


#b = Board()
#b[2,3] = Card(6, 12)
#print(b[2,3])
#print(b)
#print(b.getTotalScore())

#cannot find way to make numpy work with objects without defining new datatypes
#in C type
#a = np.zeros(3, dtype=[('value', np.int16), ('uniqueID', np.int16)])
#a[2] = Card(12, 123)
#print a["value"]

#asdf = np.zeros(2)
#print asdf[5]

#print Card(2, 123).canMergeWith(Card(1, 124))
#print Card(3, 123).canMergeWith(Card(3, 124))



## BOARD 
#class Board:
#    BOARD_HEIGHT = 4
#    BOARD_WIDTH = 4
#    board = np.zeros( BOARD_HEIGHT, BOARD_WIDTH )
#
#def play(board, move):
#    cards = [1, 1, 2, 2, 3]
#    nextcard = random.choice(cards)
#    if move == 'left':
#        print "left"
#        newboard = shiftleft(board)
#        if np.array_equal(newboard, board):
#            newboard[random.randint(0,3)][3] = nextcard
#    elif move == 'right':
#        print "right"
#        newboard = shiftright(board)
#        if np.array_equal(newboard, board):
#            newboard[random.randint(0,3)][0] = nextcard
#    elif move == 'up':
#        print "up"
#        newboard = shiftup(board)
#        if np.array_equal(newboard, board):
#            newboard[3][random.randint(0,3)] = nextcard
#    elif move == 'down':
#        print 'down'
#        newboard = shiftdown(board)
#        if np.array_equal(newboard, board):
#            newboard[0][random.randint(0,3)] = nextcard
#    return newboard
#def shiftleft(board):
#    for row in board:
#        for index in range(row.size):
#            if (row[index] == 0):
#                for i in range(index, row.size-1):
#                    row[i] = row[i+1]
#                row[row.size-1] = 0
#                break
#            elif    not(index==row.size-1) and (((row[index] == row[index+1]) 
#                    and not(row[index]==1 and row[index+1]==1)
#                    and not(row[index]==2 and row[index-1]==2))
#                    or (row[index]+row[index+1]==3 and not(row[index]==0 and row[index+1]==0))):
#                row[index] = row[index] + row[index+1]
#                for i in range(index+1, row.size-1):
#                    row[i] = row[i+1]
#                row[row.size-1] = 0
#                break
#    return board
#def shiftright(board):
#    for row in board:
#        for index in range(row.size-1, -1, -1):
#            if (row[index] == 0):
#                for i in range(index, -1, -1):
#                    row[i] = row[i-1]
#                row[0] = 0
#                break
#            elif    not(index==row.size-1) and (((row[index] == row[index-1]) 
#                    and not(row[index]==1 and row[index-1]==1)
#                    and not(row[index]==2 and row[index-1]==2))
#                    or (row[index]+row[index-1]==3 and not(row[index]==0 and row[index-1]==0))):
#                row[index] = row[index] + row[index-1]
#                for i in range(index-1, 0, -1):
#                    row[i] = row[i-1]
#                row[0] = 0
#                break
#    return board
#def shiftup(board):
#    for col in board.T:
#        for index in range(col.size):
#            if (col[index] == 0):
#                for i in range(index, col.size-1):
#                    col[i] = col[i+1]
#                col[col.size-1] = 0
#                break
#            elif    not(index==col.size-1) and (((col[index] == col[index+1]) 
#                    and not(col[index]==1 and col[index+1]==1)
#                    and not(col[index]==2 and col[index-1]==2))
#                    or (col[index]+col[index+1]==3 and not(col[index]==0 and col[index+1]==0))):
#                col[index] = col[index] + col[index+1]
#                for i in range(index+1, col.size-1):
#                    col[i] = col[i+1]
#                col[col.size-1] = 0
#                break
#    return board
#def shiftdown(board):
#    for col in board.T:
#        for index in range(col.size-1, -1, -1):
#            if (col[index] == 0):
#                for i in range(index, -1, -1):
#                    col[i] = col[i-1]
#                col[0] = 0
#                break
#            elif    not(index==0) and (((col[index] == col[index-1]) 
#                    and not(col[index]==1 and col[index-1]==1)
#                    and not(col[index]==2 and col[index-1]==2))
#                    or (col[index]+col[index-1]==3 and not(col[index]==0 and col[index-1]==0))):
#                col[index] = col[index] + col[index-1]
#                for i in range(index-1, 0, -1):
#                    col[i] = col[i-1]
#                col[0] = 0
#                break
#    return board
#
#
#i = 0
#
#board[0][0] = 1
#board[0][1] = 2
#board[1][0] = 1
#board[1][1] = 1
#board[2][2] = 1
#board[3][3] = 1
##[[1 2 0 0]
## [1 1 0 0]
## [0 0 1 0]
## [0 0 0 1]]
#print "Start"
#print board
#print '\n'
#
#while(True):
#    moves = ['down', 'right']
#    board = play(board, random.choice(moves))
#    print board
#    print '\n'
#    time.sleep(1)
