# *-* coding:utf-8 -*-
from graphics import *
# from random import randint

#棋盘相关
GRID_WIDTH = 40
COLUMN = 15
ROW = 15

#搜索相关
INF = 999_999_999
RATIO = 1  # 进攻的系数(可调)：大于1 进攻型，小于1 防守型
DEPTH = 3  # 搜索深度，只能是单数。
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))  # 4个方向

SCORE_DICT = {
# '''
# {'0': 'empty',
#  '+': 'me',
#  '-': 'enermy',
#  '?': '+0',
#  '*': '+0-',
#  }
#  '''
    '+++++': INF,

    '0++++0': INF-1,  # 活4

    '-++++0': INF//3,  # 死4
    '+++0+': INF//3,
    '+0+++': INF//3,
    '++0++': INF//3,

    '+++00': INF//3,  # 活3
    '0+++0': INF//3,
    '00+++': INF//3,

    '++0+': 5000,  # 死3

    '0++0': 200,  # 活2

    }
#棋势评估表，根据预设的小字典SCORE_DICT,
#生成包含所有情形的大字典g_ScoreDict
g_ScoreDict = {}

# 棋盘状态
g_ChessBoard = [[0] * (COLUMN + 1) for i in range(ROW + 1)]  
BLACK = 1
WHITE = -1
EMPTY = 0

#双方落子步骤
g_AllSteps = []  # type:list(tuple (int, int))
# 
# isWhiteTurn= len(g_AllSteps)%2==1

#合法落子点/棋盘剩余空点

#   这里注意python的引用机制，不可以:
#   g_ChessBoard = [[0]*(COLUMN+1)]*(ROW+1)
g_LegalMoves = [(x, y)for y in range(COLUMN+1) for x in range(ROW+1)]

g_NextMove = (7, 7)
#


def generateScoreDict():
    '''
    根据预设的小字典SCORE_DICT,
    生成包含所有情形的大字典g_ScoreDict
    dict.key：长度为6的str，表示所有可能的情形，
        其中'0-+'分别代表'空敌我'
    dict.value:得分
    '''
    def TenToThree(x: int)->str:
        '''
        把十进制转为3进制字符串
        '''
        num, rem = divmod(x, 3)
        s = [rem]
        while num != 0:
            num, rem = divmod(num, 3)
            s.append(rem)
        return ''.join(str(i) for i in s[::-1])

    # 一个方向上长度为6的区间共有3**6 种情形，
    ls_shape = [f'{int(TenToThree(i)):06}' for i in range(3 ** 6)]
    ls_shape = [i.translate(i.maketrans('12', '-+')) for i in ls_shape]

    global g_ScoreDict,SCORE_DICT
    ls_score = []
    for i in ls_shape:
        t = 0
        if i.count('-') >= 2:
            t = 0
        else:
            for x, y in SCORE_DICT.items():
                if x in i and t <= y:
                    t = y
        ls_score.append(t)
    g_ScoreDict = dict(zip(ls_shape, ls_score))


def tryMove(location: tuple,
            ):
    global g_ChessBoard, g_LegalMoves, g_AllSteps
    (x, y) = location
    # 黑先，已落子数为奇数，则为白方落子
    isWhiteTurn = (len(g_AllSteps) % 2 == 1)
    g_ChessBoard[x][y] = WHITE if isWhiteTurn else BLACK
    g_LegalMoves.remove(location)
    g_AllSteps.append(location)


def undoMove():
    global g_ChessBoard, g_LegalMoves, g_AllSteps
    (x, y) = g_AllSteps.pop()
    g_ChessBoard[x][y] = EMPTY
    g_LegalMoves.append((x, y))


def evaluation()->float:
    '''
    根据此时的g_ChessBoard，g_AllSteps计算局面评估函数，
    返回局面得分 float
    '''
    global DIRECTIONS, g_ScoreDict, g_ChessBoard, g_AllSteps
    if (gameOver()):
        return INF
    # 这里是要评价已落下的子，所以偶数时，是表示刚下了一步白棋，
    # 而不同于其他部分表示轮到白棋下而白棋未落子
    isWhiteTurn = (len(g_AllSteps) % 2 == 0)
    print(isWhiteTurn)
    t_dict = {
        # 白方回合，则白子为己'+',黑子为敌'-'
        # 黑方回合，则黑子为己'+',白子为敌'-'
        True:
        {
            EMPTY: '0',
            BLACK: '-',
            WHITE:'+',
        },
        False:
        {
            EMPTY: '0',
            BLACK: '+',
            WHITE: '-',
        }
    }
    TotalScore = 0
    (m, n) = g_AllSteps[-1]
    for (x, y) in DIRECTIONS:
        tmp = [(m + (i - 4) * x, n + (i - 4) * y) for i in range(9)]
        tmp = [(i, j) for i, j in tmp if 0 <= i <= ROW and 0 <= j <= COLUMN]
        for i in range(len(tmp) - 5):
            ls = ''
            for (tx, ty) in tmp[i:i + 6]:
                ls += t_dict[isWhiteTurn][g_ChessBoard[tx][ty]]
            if TotalScore < g_ScoreDict[ls]:
                TotalScore = g_ScoreDict[ls]
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

    # isWhiteTurn = (len(g_AllSteps) % 2 == 1)

    # 游戏是否结束 | | 探索的递归深度是否到边界
    if gameOver()or Depth == 0:
        return evaluation()
    orderMoves()  # 搜索顺序排序  提高剪枝效率
    CurrentScore = -INF
    BestMove = None

    global g_LegalMoves
    for Move in g_LegalMoves:
        tryMove(Move)
        Score = -negamaxSearch(Depth - 1, -Beta, -Alpha)
        undoMove()
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
    GameOver = False
    isWhiteTurn = False
    (x, y) = (0, 0)
    while not GameOver:
        isWhiteTurn = (len(g_AllSteps) % 2 == 1)
        if not isWhiteTurn:  # 黑子
            p = Window.getMouse()
            (x, y) = (round((p.getX()) / GRID_WIDTH), round((p.getY()) / GRID_WIDTH))
        else:  # 白子
            if len(g_AllSteps) >= 2:
                (x, y) = AI_step()
            else:
                orderMoves()
                (x, y) = g_LegalMoves[0]
            assert g_ChessBoard[x][y] == EMPTY, 'AI_step 生成错误！'
        if g_ChessBoard[x][y] == EMPTY:  # 有效落子点
            tryMove((x, y))
            piece = Circle(Point(GRID_WIDTH * x, GRID_WIDTH * y), 16)
            piece.setFill('white' if isWhiteTurn else 'black')
            piece.draw(Window)
            GameOver = gameOver()

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


def gameOver() -> bool:
    global DIRECTIONS, g_ChessBoard, g_AllSteps

    (m, n) = g_AllSteps[-1]
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
    (x, y) = (0, 0)
    while not GameOver:
        isWhiteTurn = (len(g_AllSteps) % 2 == 1)
        p = Window.getMouse()
        (x, y) = round(
            (p.getX()) / GRID_WIDTH), round((p.getY()) / GRID_WIDTH)

        if g_ChessBoard[x][y] == EMPTY:  # 有效落子点
            tryMove((x, y))
            print(evaluation()) if len(g_AllSteps) >= 2 else 0
            piece = Circle(Point(GRID_WIDTH * x, GRID_WIDTH * y), 16)
            piece.setFill('white' if isWhiteTurn else 'black')
            StepCount = StepCount + 1
            piece.draw(Window)
            GameOver = gameOver()

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
    generateScoreDict()
    main_gamePVP()
    # main_gamePVE()
