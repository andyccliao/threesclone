# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 17:45:49 2017

@author: Andy
"""

import numpy as np
import msvcrt as m
import time

def wait():
    m.getch()



board = np.array([[0,0,0,0],
         [0,0,0,0],
         [0,0,0,0],
         [0,0,0,0]])
    
asd = 0

def play(board, move):
    if move == 'left':
        print "playing left"
        board = shiftleft(board)
    elif move == 'right':
        board = shiftright(board)
    elif move == 'up':
        board = shiftleft(board)
    elif move == 'down':
        board = shiftleft(board)
    return board
def shiftleft(board):
    for row in board:
        for index in range(row.size):
            if (row[index] == 0):
                for i in range(index, row.size-1):
                    row[i] = row[i+1]
                row[row.size-1] = 0
                break
            elif (row[index] == row[index+1] or row[index]+row[index+1]==3):
                row[index] = row[index] + row[index+1]
                for i in range(index+1, row.size-1):
                    row[i] = row[i+1]
                row[row.size-1] = 0
    return board
def shiftright(board):
    for row in board:
        for index in range(row.size-1, -1):
            if (row[index] == 0):
                for i in range(index, -1):
                    row[i] = row[i-1]
                row[0] = 0
                break
            elif (row[index] == row[index+1] or row[index]+row[index+1]==3):
                row[index] = row[index] + row[index+1]
                for i in range(index+1, row.size-1):
                    row[i] = row[i+1]
                row[row.size-1] = 0
    return board

i = 0

board[0][0] = 1
board[1][1] = 1
board[2][2] = 1
board[3][3] = 1
print "Start"
print board
print '\n'

while(True):
    board = play(board, 'left')
    print board
    print '\n'
    time.sleep(1)
