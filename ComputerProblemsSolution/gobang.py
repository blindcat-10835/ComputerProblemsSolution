# *-* coding:utf-8 -*-
from graphics import *
#from math import *
#import numpy as np

# 参数列表

GRID_WIDTH = 40
COLUMN = 15
ROW = 15

BlackHuman = []  # 黑子 or 人类
WhiteAi = []  # 白子 or AI
All = []  # all

list_all = []  # 整个棋盘的点
next_point = [14, 14]  # AI下一步最应该下的位置

ratio = 1  # 进攻的系数(可调)：大于1 进攻型，小于1 防守型
DEPTH = 3  # 搜索深度，只能是单数。

# 棋型的评估分数,1表示有子,0表示无子
# TODO:以下为举例用的棋形评估分数，可以自己扩展与改分
shape_score = [(50, (0, 1, 1, 0, 0)),
               (50, (0, 0, 1, 1, 0)),
               (200, (1, 1, 0, 1, 0)),
               (500, (0, 0, 1, 1, 1)),
               (500, (1, 1, 1, 0, 0)),
               (5000, (0, 1, 1, 1, 0)),
               (5000, (0, 1, 0, 1, 1, 0)),
               (5000, (0, 1, 1, 0, 1, 0)),
               (5000, (1, 1, 1, 0, 1)),
               (5000, (1, 1, 0, 1, 1)),
               (5000, (1, 0, 1, 1, 1)),
               (5000, (1, 1, 1, 1, 0)),
               (5000, (0, 1, 1, 1, 1)),
               (50000, (0, 1, 1, 1, 1, 0)),
               (99999999, (1, 1, 1, 1, 1))]


def ai_step():
    '''
    AI下一步棋判断
    :return: next_point
    '''
    negamax(True, DEPTH, -99999999, 99999999)
    return next_point[0], next_point[1]


def negamax(is_ai, depth, alpha, beta):
    '''
    负值极大算法搜索 alpha + beta剪枝
    :param is_ai: 是否是ai轮
    :param depth: 搜索深度
    :return: alpha or beta（需要补全）
    '''

    # 游戏是否结束 | | 探索的递归深度是否到边界
    if game_win(BlackHuman) or game_win(WhiteAi) or depth == 0:
        return evaluation(is_ai)

    blank_list = list(set(list_all).difference(set(All)))
    order(blank_list)   # 搜索顺序排序  提高剪枝效率
    # TODO: 对每一个候选步进行递归并剪枝，将最后决策出的next_point赋值，将函数剩下部分补全
    # .....
    global next_point
    next_point = blank_list[0]


def order(blank_list):
    '''
    离最后落子的邻居位置最有可能是最优点，策略优化，无需改动
    '''
    last_pt = All[-1]
    for item in blank_list:
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if (last_pt[0] + i, last_pt[1] + j) in blank_list:
                    blank_list.remove((last_pt[0] + i, last_pt[1] + j))
                    blank_list.insert(0, (last_pt[0] + i, last_pt[1] + j))


def has_neightnor(pt):
    '''
    查看某个位置是否有邻居，用于剪枝
    :param pt:
    :return:
    '''
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if (pt[0] + i, pt[1]+j) in All:
                return True
    return False


def evaluation(is_ai):
    '''
    评估函数，用于评估当前棋盘局势
    :param is_ai:是否是AI的评估
    :return:当前棋局博弈双方的总分
    '''

    total_score = 0

    if is_ai:
        我下的棋 = WhiteAi
        敌人下的棋 = BlackHuman
    else:
        我下的棋 = BlackHuman
        敌人下的棋 = WhiteAi

    # 算自己的得分
    score_all_arr = []  # 得分形状的位置，用于计算是否有有相交，如果有则得分翻倍
    my_score = 0
    for 棋子 in 我下的棋:
        my_score += cal_score(棋子, (0, 1), 敌人下的棋, 我下的棋, score_all_arr)
        my_score += cal_score(棋子, (1, 0), 敌人下的棋, 我下的棋, score_all_arr)
        my_score += cal_score(棋子, (1, 1), 敌人下的棋, 我下的棋, score_all_arr)
        my_score += cal_score(棋子, (-1, 1), 敌人下的棋, 我下的棋, score_all_arr)

    #  算敌人的得分，并减去
    score_all_arr_enemy = []
    enemy_score = 0
    for 棋子 in 敌人下的棋:
        enemy_score += cal_score(棋子, (0, 1), 我下的棋,
                                 敌人下的棋, score_all_arr_enemy)
        enemy_score += cal_score(棋子, (1, 0), 我下的棋,
                                 敌人下的棋, score_all_arr_enemy)
        enemy_score += cal_score(棋子, (1, 1), 我下的棋,
                                 敌人下的棋, score_all_arr_enemy)
        enemy_score += cal_score(棋子, (-1, 1), 我下的棋,
                                 敌人下的棋, score_all_arr_enemy)

    total_score = my_score - enemy_score*ratio*0.1

    return total_score


def cal_score(坐标: tuple(int, int), direction: tuple(int, int), enemy_list:list(tuple(int,int)), my_list:list(tuple(int,int)), score_all_arr):
    '''
    计算(m,n)点的指定方向上棋盘形状的评估分值
    :param m: x坐标值
    :param n: y坐标值
    :param x_decrict:指定x轴方向
    :param y_derice:指定y轴方向
    :param enemy_list:对手的棋局
    :param my_list:我方的棋局
    :param score_all_arr:得分形状的位置，用于计算是否有有相交，如果有则得分翻倍
    :return: 当前方向上的得分
    '''
    add_score = 0  # 加分项
    # 在一个方向上， 只取最大的得分项
    max_score_shape = (0, None)

    # 如果此方向上，该点已经有得分形状，不重复计算
    for item in score_all_arr:
        for pt in item[1]:
            if (坐标 == pt and direction == item[2]):
                return 0
    # TODO: 在落子点指定方向上查找形状，并根据shape_score计分，将最大的score值与其对应shape赋值给max_score_shape,在END前补齐代码
    # ......

    # END:

    # 计算两个形状相交， 如两个活3相交， 得分增加。一个子的除外，无需改动
    if max_score_shape[1] is not None:
        for item in score_all_arr:
            for pt1 in item[1]:
                for pt2 in max_score_shape[1]:
                    if pt1 == pt2 and max_score_shape[0] > 10 and item[0] > 10:
                        add_score += item[0] + max_score_shape[0]

        score_all_arr.append(max_score_shape)

    return add_score + max_score_shape[0]


def game_win(List):
    '''
    传入的list判断当前list是否已经连出五子
    :param list:需要判断的棋子列表
    :return: True or False
    '''
    for m in range(COLUMN):
        for n in range(ROW):

            if (n < ROW - 4
                    and (m, n) in List
                    and (m, n + 1) in List
                    and (m, n + 2) in List
                    and (m, n + 3) in List
                    and (m, n + 4) in List):
                return True
            elif (m < ROW - 4
                    and (m, n) in List
                    and (m + 1, n) in List
                    and (m + 2, n) in List
                    and (m + 3, n) in List
                    and (m + 4, n) in List):
                return True
            elif (m < ROW - 4
                    and n < ROW - 4
                    and (m, n) in List
                    and (m + 1, n + 1) in List
                    and (m + 2, n + 2) in List
                    and (m + 3, n + 3) in List
                    and (m + 4, n + 4) in List):
                return True
            elif (m < ROW - 4
                    and n > 3
                    and (m, n) in List
                    and (m + 1, n - 1) in List
                    and (m + 2, n - 2) in List
                    and (m + 3, n - 3) in List
                    and (m + 4, n - 4) in List):
                return True
    return False


def gobangwin():
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


def main_AI():
    ''' 人机对战函数 '''
    Window = gobangwin()

    for i in range(COLUMN+1):
        for j in range(ROW+1):
            list_all.append((i, j))

    change = 0
    GameOver = False
    while not GameOver:

        if change % 2 == 0:  # 黑子
            p = Window.getMouse()
            if not ((round((p.getX()) / GRID_WIDTH), round((p.getY()) / GRID_WIDTH)) in All):

                a = round((p.getX()) / GRID_WIDTH)
                b = round((p.getY()) / GRID_WIDTH)
                BlackHuman.append((a, b))
                All.append((a, b))

                piece = Circle(Point(GRID_WIDTH * a, GRID_WIDTH * b), 16)
                piece.setFill('black')
                piece.draw(Window)

                if game_win(BlackHuman):
                    message = Text(Point(100, 100), "black win.")
                    message.draw(Window)
                    GameOver = True
                change = change + 1

        elif change % 2 == 1:  # 白子
            pos = ai_step()

            if pos in All:
                message = Text(Point(200, 200), "不可用的位置" +
                               str(pos[0]) + "," + str(pos[1]))
                message.draw(Window)
                GameOver = 1

            WhiteAi.append(pos)
            All.append(pos)

            piece = Circle(Point(GRID_WIDTH * pos[0], GRID_WIDTH * pos[1]), 16)
            piece.setFill('white')
            piece.draw(Window)

            if game_win(WhiteAi):
                message = Text(Point(100, 100), "white win.")
                message.draw(Window)
                GameOver = True
            change = change + 1

    message = Text(Point(100, 120), "Click anywhere to quit.")
    message.draw(Window)
    Window.getMouse()
    Window.close()


def main_Human():
    ''' 人人对战函数 '''
    win = gobangwin()

    for i in range(COLUMN + 1):
        for j in range(ROW + 1):
            list_all.append((i, j))

    change = 0
    g = 0
    while g == 0:

        p = win.getMouse()

        if change % 2 == 0:  # 黑子
            if not ((round((p.getX()) / GRID_WIDTH), round((p.getY()) / GRID_WIDTH)) in All):

                a = round((p.getX()) / GRID_WIDTH)
                b = round((p.getY()) / GRID_WIDTH)
                BlackHuman.append((a, b))
                All.append((a, b))

                piece = Circle(Point(GRID_WIDTH * a, GRID_WIDTH * b), 16)
                piece.setFill('black')
                piece.draw(win)
                if game_win(BlackHuman):
                    message = Text(Point(100, 100), "black win.")
                    message.draw(win)
                    g = 1

                change = change + 1

        elif change % 2 == 1:  # 白子
            if not ((round((p.getX()) / GRID_WIDTH), round((p.getY()) / GRID_WIDTH)) in All):

                a = round((p.getX()) / GRID_WIDTH)
                b = round((p.getY()) / GRID_WIDTH)
                WhiteAi.append((a, b))
                All.append((a, b))

                piece = Circle(Point(GRID_WIDTH * a, GRID_WIDTH * b), 16)
                piece.setFill('white')
                piece.draw(win)
                if game_win(WhiteAi):
                    message = Text(Point(100, 100), "White win.")
                    message.draw(win)
                    g = 1

                change = change + 1

    message = Text(Point(100, 120), "Click anywhere to quit.")
    message.draw(win)
    win.getMouse()
    win.close()


if __name__ == '__main__':
    main_AI()
    # main_Human()
