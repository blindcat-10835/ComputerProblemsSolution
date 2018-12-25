# *-* coding:utf-8 -*-
from graphics import *
from random import randint

GRID_WIDTH = 40
COLUMN = 15
ROW = 15
INF = 999_999_999
RATIO = 1  # 进攻的系数(可调)：大于1 进攻型，小于1 防守型
DEPTH = 3  # 搜索深度，只能是单数。
CHESS_BOARD = [(i, j) for i in range(COLUMN + 1) for j in range(ROW + 1)]
# 整个棋盘的点
#
next_point = (5, 5)  # AI下一步最应该下的位置
BlackHuman = []  # 黑子 or 人类
WhiteAi = []  # 白子 or AI
All = []  # all


#   这里注意python的引用机制，不可以:
#   g_ChessBoard = [[0]*(COLUMN+1)]*(ROW+1)
g_ChessBoard = [[0] * (COLUMN + 1) for i in range(ROW + 1)]  # 0 为空 1黑 2白
# FIXME: 不确定是否需要这个，后期可再优化
g_LegalMoves = [(x, y)for y in range(COLUMN+1) for x in range(ROW+1)]
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))  # 4个方向


def tryMove(location: tuple,
            isWhite: bool):
    global g_ChessBoard, g_LegalMoves
    (x, y) = location
    g_ChessBoard[x][y] = 2 if isWhite else 1
    g_LegalMoves.remove((x, y))


def undoMove(location: tuple):
    global g_ChessBoard, g_LegalMoves
    (x, y) = location
    g_ChessBoard[x][y] = 0
    g_LegalMoves.append((x, y))


def evaluation()->int:
    '''
    根据此时的g_ChessBoard，计算局面评估函数，
    主视角应为White，Black 得分为负 
    '''
    return 0
    pass


def negamaxSearch(LastMove: tuple,
                  Depth: int,
                  Alpha: int,
                  Beta: int)->'int:Alpha':
    '''
    负值极大算法搜索 Alpha + beta剪枝
    :param is_ai: 是否是ai轮
    :param Depth: 搜索深度
    :return: Alpha or beta（需要补全）
    '''

    # 游戏是否结束 | | 探索的递归深度是否到边界
    if gameOver(LastMove) or Depth == 0:
        return evaluation()

    # 以下，生成合法的落子点
    #blank_list = list(set(CHESS_BOARD).difference(set(All)))
    global g_LegalMoves
    orderMoves()  # 搜索顺序排序  提高剪枝效率

    # TODO: 对每一个候选步进行递归并剪枝，将最后决策出的next_point赋值，将函数剩下部分补全
    BestMove = None
    isWhite = (Depth % 2 == 1)
    for Move in g_LegalMoves:
        tryMove(Move, isWhite)
        val = -negamaxSearch(Move, Depth - 1, -Beta, -Alpha)
        undoMove(Move)
        if val >= Beta:
            return Beta
        if val > Alpha:
            Alpha = val
            BestMove = Move
    if Depth == Depth and BestMove is not None:
        global next_point
        next_point = BestMove
    return Alpha
    # XXX: 把这一部分放到了前面的落子函数里面# .....
    # global next_point
    # next_point = blank_list[0]


def generateLegalMoves():
    '''
    此函数已经弃
    '''
    global g_LegalMoves
    g_LegalMoves = [(x, y) for y in range(COLUMN+1)
                    for x in range(ROW+1) if g_ChessBoard[x][y] == 0]


def orderMoves():
    '''

    '''
    global g_LegalMoves
    g_LegalMoves.sort(key=lambda x :abs(x[0]-(COLUMN/2))+abs(x[1]-(ROW/2)),reverse=True )
    # TODO：最后落子点周围？


def AI_step()->tuple:
    '''
    AI下一步棋判断
    :return: next_point
    '''
    global g_LegalMoves  # 合法着点已实时生成
    orderMoves()  # 合法着点排序以剪枝
    negamaxSearch(g_LegalMoves[0], DEPTH, -INF, INF)
    # return g_LegalMoves[randint(0, len(g_LegalMoves))]
    return next_point


def main_gamePVE():
    ''' 人机对战函数 '''
    Window = gobangWindow()
    global g_ChessBoard, g_LegalMoves
    StepCount = 0
    GameOver = False
    while not GameOver:
        if StepCount % 2 == 0:  # 黑子
            p = Window.getMouse()
            (x, y) = (round((p.getX()) / GRID_WIDTH), round((p.getY()) / GRID_WIDTH))
            if (g_ChessBoard[x][y] == 0):
                g_ChessBoard[x][y] = 1
                g_LegalMoves.remove((x, y))
                StepCount = StepCount + 1
                piece = Circle(Point(GRID_WIDTH * x, GRID_WIDTH * y), 16)
                piece.setFill('black')
                piece.draw(Window)
                GameOver = gameOver((x, y))

        elif StepCount % 2 == 1:  # 白子
            (x, y) = AI_step()
            if (g_ChessBoard[x][y] == 0):
                g_ChessBoard[x][y] = 2
                g_LegalMoves.remove((x, y))
                StepCount = StepCount + 1
                piece = Circle(Point(GRID_WIDTH * x, GRID_WIDTH * y), 16)
                piece.setFill('white')
                piece.draw(Window)
                GameOver = gameOver((x, y))

    if (StepCount % 2 == 1):
        message = Text(Point(100, 100), "Black win.")
    else:
        message = Text(Point(100, 100), "White win.")
    message.setFill("red")
    message.draw(Window)
    message = Text(Point(100, 120), "Click anywhere to quit.")
    message.setFill("red")
    message.draw(Window)
    Window.getMouse()
    Window.close()


def gobangWindow():
    ''' 绘制基本棋盘界面 '''
    Window = GraphWin("this is a gobang game",
                      GRID_WIDTH * COLUMN, GRID_WIDTH * ROW)
    Window.setBackground("yellow")
    i1 = 0

    while i1 <= GRID_WIDTH * COLUMN:
        l = Line(Point(i1, 0), Point(i1, GRID_WIDTH * COLUMN))
        l.draw(Window)
        i1 = i1 + GRID_WIDTH
    i2 = 0

    while i2 <= GRID_WIDTH * ROW:
        l = Line(Point(0, i2), Point(GRID_WIDTH * ROW, i2))
        l.draw(Window)
        i2 = i2 + GRID_WIDTH
    return Window


def gameOver(location: tuple)->bool:
    (m, n) = location
    global DIRECTIONS, g_ChessBoard
    for (x, y) in DIRECTIONS:
        tmp = [(m + (i - 4) * x, n + (i - 4) * y) for i in range(9)]
        tmp = [(i, j) for i, j in tmp if 0 <= i <= ROW and 0 <= j <= COLUMN]
        for i in range(len(tmp) - 4):
            ls = list(g_ChessBoard[tx][ty] for (tx, ty) in tmp[i:i + 5])
            assert ls.__len__() == 5
            if (all(x == 1 for x in ls)
                    or all(x == 2 for x in ls)):
                return True

    return False


def main_gamePVP():
    ''' 人人对战函数 '''
    Win = gobangWindow()
    global g_ChessBoard
    StepCount = 0
    GameOver = False
    while not GameOver:

        p = Win.getMouse()
        (x, y) = round(
            (p.getX()) / GRID_WIDTH), round((p.getY()) / GRID_WIDTH)
        if (StepCount % 2 == 0  # 黑子
                and g_ChessBoard[x][y] == 0):
            g_ChessBoard[x][y] = 1
            StepCount = StepCount + 1
            piece = Circle(Point(GRID_WIDTH * x, GRID_WIDTH * y), 16)
            piece.setFill('black')
            piece.draw(Win)
            GameOver = gameOver((x, y))

        elif (StepCount % 2 == 1  # 白子
              and g_ChessBoard[x][y] == 0):
            g_ChessBoard[x][y] = 2
            StepCount = StepCount + 1
            piece = Circle(Point(GRID_WIDTH * x, GRID_WIDTH * y), 16)
            piece.setFill('white')
            piece.draw(Win)
            GameOver = gameOver((x, y))

    if (StepCount % 2 == 1):
        message = Text(Point(100, 100), "Black win.")
    else:
        message = Text(Point(100, 100), "White win.")
    message.setFill("red")
    message.draw(Win)
    message = Text(Point(100, 120), "Click anywhere to quit.")
    message.setFill("red")
    message.draw(Win)
    Win.getMouse()
    Win.close()


if __name__ == '__main__':
    # main_gamePVP()
    main_gamePVE()
