# *-* coding:utf-8 -*-
from graphics import *
from random import randint
GRID_WIDTH = 40
COLUMN = 15
ROW = 15
CHESS_BOARD = [(i, j) for i in range(COLUMN + 1) for j in range(ROW + 1)]
# 整个棋盘的点
#
next_point = (5, 5)  # AI下一步最应该下的位置
BlackHuman = []  # 黑子 or 人类
WhiteAi = []  # 白子 or AI
All = []  # all

ChessBoard = [[0]*(COLUMN+1) for i in range(ROW+1)]  # 0 为空 1黑 2白
RATIO = 1  # 进攻的系数(可调)：大于1 进攻型，小于1 防守型
DEPTH = 3  # 搜索深度，只能是单数。
Directions = ((0, 1), (1, 0), (1, 1), (1, -1))  # 4个方向


def gobangWin():
    ''' 绘制基本棋盘界面 '''
    win = GraphWin("this is a gobang game",
                   GRID_WIDTH * COLUMN, GRID_WIDTH * ROW)
    win.setBackground("yellow")
    i1 = 0

    while i1 <= GRID_WIDTH * COLUMN:
        l = Line(Point(i1, 0), Point(i1, GRID_WIDTH * COLUMN))
        l.draw(win)
        i1 = i1 + GRID_WIDTH
    i2 = 0

    while i2 <= GRID_WIDTH * ROW:
        l = Line(Point(0, i2), Point(GRID_WIDTH * ROW, i2))
        l.draw(win)
        i2 = i2 + GRID_WIDTH
    return win


def gameOver(location: tuple)->bool:
    (m, n) = location
    global Directions, ChessBoard
    for (x, y) in Directions:
        tmp = [(m + (i - 4) * x, n + (i - 4) * y) for i in range(9)]
        tmp = [(i, j) for i, j in tmp if 0 <=
               i <= ROW and 0 <= j <= COLUMN]
        for i in range(len(tmp) - 4):
            ls = list(ChessBoard[tx][ty] for (tx, ty) in tmp[i:i + 5])
            assert ls.__len__() == 5
            if (all(x == 1 for x in ls)
                    or all(x == 3 for x in ls)):
                return True

    return False


def main_Human():
    ''' 人人对战函数 '''
    win = gobangWin()
    global ChessBoard
    change = 0
    GameOver = False
    while not GameOver:

        p = win.getMouse()
        (a, b) = round(
            (p.getX()) / GRID_WIDTH), round((p.getY()) / GRID_WIDTH)
        if change % 2 == 0:  # 黑子
            if (ChessBoard[a][b] == 0):
                ChessBoard[a][b] = 1
                change = change + 1
                piece = Circle(Point(GRID_WIDTH * a, GRID_WIDTH * b), 16)
                piece.setFill('black')
                piece.draw(win)
                GameOver = gameOver((a, b))
        elif change % 2 == 1:  # 白子
            if (ChessBoard[a][b] == 0):
                ChessBoard[a][b] = 2
                change = change + 1

                piece = Circle(Point(GRID_WIDTH * a, GRID_WIDTH * b), 16)
                piece.setFill('white')
                piece.draw(win)
                GameOver = gameOver((a, b))

    if (change % 2 == 1):
        message = Text(Point(100, 100), "black win.")
    else:
        message = Text(Point(100, 100), "White win.")
    message.setFill("red")
    message.draw(win)
    message = Text(Point(100, 120), "Click anywhere to quit.")
    message.setFill("red")
    message.draw(win)
    win.getMouse()
    win.close()


if __name__ == '__main__':
    main_Human()
