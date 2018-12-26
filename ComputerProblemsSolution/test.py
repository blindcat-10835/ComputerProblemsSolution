# *-* coding:utf-8 -*-
from graphics import *
# from random import randint


GRID_WIDTH = 40
COLUMN = 15
ROW = 15
INF = 999_999_999
RATIO = 1  # 进攻的系数(可调)：大于1 进攻型，小于1 防守型
DEPTH = 3  # 搜索深度，只能是单数。
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))  # 4个方向


#   这里注意python的引用机制，不可以:
#   g_ChessBoard = [[0]*(COLUMN+1)]*(ROW+1)
g_ChessBoard = [[0] * (COLUMN + 1) for i in range(ROW + 1)]  # 0 为空 1黑 -1白
g_AllSteps = []  # type:list(tuple (int, int)) 所有棋子的落子顺序
g_LegalMoves = [(x, y)for y in range(COLUMN+1) for x in range(ROW+1)]
g_NextMove = (7, 7)

SCORE_DICT = {
    (0, 1, 1, 0, 0): 50,
    (0, 0, 1, 1, 0): 50,
    (1, 1, 0, 1, 0): 200,
    (0, 1, 0, 1, 1): 200,
    (0, 1, 1, 1, 0): 200,
    (1, 1, 1, 0, 0): 500,
    (0, 0, 1, 1, 1): 500,
    (1, 1, 1, 0, 1): 5000,
    (1, 1, 0, 1, 1): 5000,
    (1, 0, 1, 1, 1): 5000,
    (1, 1, 1, 1, 0): 5000,
    (0, 1, 1, 1, 1, 0): 5000,
    (1, 1, 1, 1, 1): INF,

}


def tryMove(location: tuple,
            isWhite: bool):
    global g_ChessBoard, g_LegalMoves, g_AllSteps
    (x, y) = location
    g_ChessBoard[x][y] = -1 if isWhite else 1
    g_LegalMoves.remove(location)
    g_AllSteps.append(location)


def undoMove(location: tuple):
    global g_ChessBoard, g_LegalMoves, g_AllSteps
    (x, y) = location
    g_ChessBoard[x][y] = 0
    g_LegalMoves.append((x, y))
    g_AllSteps.pop()


def evaluation()->float:
    '''
    根据此时的g_ChessBoard，g_AllSteps计算局面评估函数，
    返回局面得分 float
    '''
    global DIRECTIONS, SCORE_DICT, g_ChessBoard, g_AllSteps
    TotalScore = 0
    isWhiteTurn = (len(g_AllSteps) % 2 == 1)

    (m, n) = g_AllSteps[-1]
    for (x, y) in DIRECTIONS:
        tmp = [(m + (i - 4) * x, n + (i - 4) * y) for i in range(9)]
        tmp = [(i, j) for i, j in tmp if 0 <= i <= ROW and 0 <= j <= COLUMN]
        for i in range(len(tmp) - 4):
            ls = tuple(-g_ChessBoard[tx][ty] if isWhiteTurn else
                       g_ChessBoard[tx][ty] for (tx, ty) in tmp[i:i + 5])
            if ls in SCORE_DICT.keys():
                TotalScore += SCORE_DICT[ls]
                # 此方向只取一个就好了
                break
    (m, n) = g_AllSteps[-2]
    for (x, y) in DIRECTIONS:
        tmp = [(m + (i - 4) * x, n + (i - 4) * y) for i in range(9)]
        tmp = [(i, j) for i, j in tmp if 0 <= i <= ROW and 0 <= j <= COLUMN]
        for i in range(len(tmp) - 4):
            ls = tuple( g_ChessBoard[tx][ty] if isWhiteTurn else
                       -g_ChessBoard[tx][ty] for (tx, ty) in tmp[i:i + 5])
            # assert ls.__len__() == 5
            if ls in SCORE_DICT.keys():
                TotalScore -= SCORE_DICT[ls]
                break
    return TotalScore


def negamaxSearch(
        Depth: int,
        Alpha: int,
        Beta: int)->'int:Alpha':
    '''
    负值极大算法搜索 Alpha + beta剪枝
    :param is_ai: 是否是ai轮
    :param Depth: 搜索深度
    :return: Alpha or beta（需要补全）
    '''

    isWhite = (Depth % 2 == 1)
    # 游戏是否结束 | | 探索的递归深度是否到边界
    global g_AllSteps
    if gameOver(g_AllSteps[-1])or Depth == 0:
        return evaluation()
    orderMoves()  # 搜索顺序排序  提高剪枝效率
    CurrentScore = -INF
    BestMove = None
    isWhite = (Depth % 2 == 1)
    global g_LegalMoves
    for Move in g_LegalMoves:
        tryMove(Move, isWhite)
        Score = -negamaxSearch(Depth - 1, -Beta, -Alpha)
        undoMove(Move)
        if Score >= CurrentScore:
            CurrentScore = Score
            BestMove = Move
            if Score >= Alpha:
                Alpha = Score
            if Score >= Beta:
                break

    if Depth == DEPTH and BestMove is not None:
        global g_NextMove
        g_NextMove = BestMove
    return CurrentScore


def orderMoves():
    '''
    以最后落子点周围进行排序
    '''
    global g_LegalMoves, g_AllSteps
    LastMove = g_AllSteps[-1]
    g_LegalMoves.sort(key=lambda x: abs(
        x[0]-LastMove[0])+abs(x[1]-LastMove[1]))


def AI_step()->tuple:
    '''
    AI下一步棋判断
    :return: next_point
    '''
    global g_LegalMoves, g_NextMove  # 合法着点已实时生成
    orderMoves()  # 合法着点排序以剪枝
    val = negamaxSearch(DEPTH, -INF, INF)
    print(val, g_NextMove)
    return g_NextMove


def main_gamePVE():
    ''' 人机对战函数 '''
    Window = gobangWindow()
    global g_ChessBoard, g_LegalMoves, g_AllSteps
    StepCount = 0
    GameOver = False
    isWhiteTurn = False
    (x, y) = (0, 0)
    while not GameOver:
        isWhiteTurn = (StepCount % 2 == 1)
        if not isWhiteTurn:  # 黑子
            p = Window.getMouse()
            (x, y) = (round((p.getX()) / GRID_WIDTH), round((p.getY()) / GRID_WIDTH))
        else:  # 白子
            if StepCount >= 2:
                (x, y) = AI_step()
            else:
                orderMoves()
                (x, y) = g_LegalMoves[0]
            assert g_ChessBoard[x][y] == 0, 'AI_step 生成错误！'
        if g_ChessBoard[x][y] == 0:  # 有效落子点
            tryMove((x, y), isWhiteTurn)
            piece = Circle(Point(GRID_WIDTH * x, GRID_WIDTH * y), 16)
            piece.setFill('white' if isWhiteTurn else 'black')
            StepCount = StepCount + 1
            piece.draw(Window)
            GameOver = gameOver((x, y))

    message = Text(Point(100, 100),
                   "White" if isWhiteTurn else "Black"+" win.")
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
                    or all(x == -1 for x in ls)):
                return True

    return False


def main_gamePVP():
    ''' 人人对战函数 '''
    Window = gobangWindow()
    global g_ChessBoard
    StepCount = 0
    GameOver = False
    isWhiteTurn = False
    (x, y) = (0, 0)
    while not GameOver:
        isWhiteTurn = (StepCount % 2 == 1)
        p = Window.getMouse()
        (x, y) = round(
            (p.getX()) / GRID_WIDTH), round((p.getY()) / GRID_WIDTH)

        if g_ChessBoard[x][y] == 0:  # 有效落子点
            tryMove((x, y), isWhiteTurn)
            print(evaluation())
            piece = Circle(Point(GRID_WIDTH * x, GRID_WIDTH * y), 16)
            piece.setFill('white' if isWhiteTurn else 'black')
            StepCount = StepCount + 1
            piece.draw(Window)
            GameOver = gameOver((x, y))

    message = Text(Point(100, 100),
                   "White" if isWhiteTurn else "Black"+" win.")
    message.setFill("red")
    message.draw(Window)
    message = Text(Point(100, 120), "Click anywhere to quit.")
    message.setFill("red")
    message.draw(Window)
    Window.getMouse()
    Window.close()


if __name__ == '__main__':
    main_gamePVP()
    # main_gamePVE()
