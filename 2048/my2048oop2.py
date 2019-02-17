# import curses
from random import randrange
from random import choice
from collections import defaultdict


class Grid:
    def __init__(self, height=2, width=2, win=2048):
        self.height = height  # 高
        self.width = width  # 宽
        self.win_value = 2048  # 过关分数
        self.score = 0  # 当前分数
        self.highscore = 0  # 最高分
        self.reset()

    def reset(self):
        '''
        重置棋盘
        :return:
        '''
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        self.spawn()
        self.spawn()

    def spawn(self):
        '''
        在棋盘空闲位置中，随机选取一个位置，随机生成一个2 或者 4 的数字,新数字使用负数标记，在绘画的时候将负数改成正数
        :return:
        '''
        new_element = 4 if randrange(100) > 89 else 2
        (i, j) = choice([(i, j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_element * -1

    def transpose(self, field):
        '''
        将矩阵转置
        :param field: 格式(('a','b', 'c'), (1, 2, 3))
        :return:
        '''
        return [list(row) for row in zip(*field)]

    def invert(self, field):
        '''
        矩阵逆转
        :param field:
        :return:
        '''
        return [row[::-1] for row in field]

    def isgameover(self):
        """
        判断游戏是否成功或失败
        :return:  True 成功， False 失败， None 进行中
        """
        for row in self.field:
            if 0 in row:
                return False

        movealbe = False
        for direction in Action.actions[0:4]:
            if self.move_is_possible(direction):
                movealbe = True
                break;
        if movealbe:
            pass
        else:
            print('d')

        movealbe = False
        for direction in Action.actions[0:4]:
            if self.move_is_possible(direction):
                movealbe = True
                break;
        if movealbe:
            return False
        else:
            return True

    def move_is_possible(self, direction):
        def row_is_left_movable(row):
            def change(i):  # true if there'll be change in i-th tile
                if row[i] == 0 and row[i + 1] != 0:  # Move
                    return True
                if row[i] != 0 and row[i + 1] == row[i]:  # Merge
                    return True
                return False

            return any(change(i) for i in range(len(row) - 1))

        check = {}
        check['Left'] = lambda field: \
            any(row_is_left_movable(row) for row in field)

        check['Right'] = lambda field: \
            check['Left'](self.invert(field))

        check['Up'] = lambda field: \
            check['Left'](self.transpose(field))

        check['Down'] = lambda field: \
            check['Right'](self.transpose(field))

        if direction in check:
            return check[direction](self.field)
        else:
            return False

    def move(self, direction):
        def move_row_left(row):

            def tighten(row):
                """
                把零散的非零单元挤到一块
                :param row:
                :return:
                """
                new_row = [i for i in row if i != 0]
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row

            def merge(row):
                """
                对邻近元素进行合并
                :param row:
                :return:
                """
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        new_row.append(2 * row[i])
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        if i + 1 < len(row) and row[i] == row[i + 1]:
                            pair = True
                            new_row.append(0)
                        else:
                            new_row.append(row[i])
                return new_row

            return tighten(merge(tighten(row)))

        # 通过对矩阵进行转置于逆转，可以直接从左移得到其余三个方向的移动操作
        moves = dict()
        moves['Left'] = lambda field: [move_row_left(row) for row in field]
        moves['Right'] = lambda field: self.invert(moves['Left'](self.invert(field)))
        moves['Up'] = lambda field: self.transpose(moves['Left'](self.transpose(field)))
        moves['Down'] = lambda field: self.transpose(moves['Right'](self.transpose(field)))
        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True


class Action:
    UP = 'Up'
    LEFT = 'Left'
    RIGHT = 'Right'
    DOWN = 'Down'
    RESTART = 'Restart'
    EXIT = 'Exit'
    actions = [UP, LEFT, DOWN, RIGHT, RESTART, EXIT]
    letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']
    actions_dict = dict(zip(letter_codes, actions * 2))

    def __init__(self, stdscr):
        self.stdscr = stdscr

    def getaction(self):
        keycode = input("输入")
        keycode = ord(keycode)
        while keycode not in self.actions_dict:
            keycode = input("输入")
            keycode = ord(keycode)
        return self.actions_dict[keycode]


class Screen:
    INFOR = '(W)Up (S)Down (A)Left (D)Right\n'
    GAME_OVER_INFO = "     GAME OVER   (R)Restart (Q)Exit\n"
    color_pair = {
        'NEW': 1,
        'BIG': 2
    }

    def __init__(self, stdscr, grid):
        self.stdscr = stdscr
        self.grid = grid


    def draw(self, states):
        print('Score:' + str(self.grid.score),'State:',states)
        x = 8  # 小方格宽度，单位为字符
        y = 4  # 小方格高度，单位为字符
        crosschar = '+'  # 交叉点
        xchar = '-'  # 横线
        ychar = '|'  # 竖线
        for j in range(self.grid.height * y + 1):
            for i in range(self.grid.width * x + 1):
                row = j // y
                col = i // x
                printchar = None
                printj = j + 1  # 打印坐标
                printi = i + 1  # 打印坐标
                printpair = None
                if i % x == 0 and j % y == 0:
                    # 绘制交叉点
                    printchar = crosschar

                elif j == (row * y + (row + 1) * y) / 2 and i == (col * x + (col + 1) * x) / 2:
                    # 绘制字符
                    # printchar = str(self.field[row][col])
                    if self.grid.field[row][col] != 0:
                        if self.grid.field[row][col] < 0:
                            self.grid.field[row][col] *= -1
                            printpair = self.color_pair['NEW']
                        elif self.grid.field[row][col] >= 64:
                            printpair = self.color_pair['BIG']
                        printchar = str(self.grid.field[row][col])
                        printi = printi - len(printchar) // 2
                elif i % x == 0:
                    # 绘制竖线
                    printchar = ychar
                elif j % y == 0:
                    # 绘制横线
                    printchar = xchar
                if printchar:
                    # color_pair
                    if printpair:
                        print('color', printpair)
                        # self.stdscr.addstr(printj, printi, printchar, curses.color_pair(printpair))
                    else:
                        pass
                        # self.stdscr.addstr(printj, printi, printchar)
        for c in self.grid.field:
            print(c)
        if states == GameManager.GAMEOVER:
            print(self.GAME_OVER_INFO)
        # else:
        #     print(self.INFOR)
        # stdscr.getch()
        print('*' * 30)


class GameManager:
    INIT = 'init'
    GAMEOVER = 'gameover'
    GAME = 'game'
    EXIT = 'exit'

    def __init__(self, stdscr=None):
        self.grid = Grid()
        self.stdscr = stdscr
        self.screen = Screen(stdscr, self.grid)
        self.action = Action(stdscr)
        self.state = GameManager.INIT

    def startgame(self):
        while self.state != GameManager.EXIT:
            if self.state == GameManager.GAMEOVER:
                print('game over')
            self.screen.draw(self.state)
            self.state = getattr(self, 'state_' + self.state)()

    def state_init(self):
        self.grid.reset()
        return GameManager.GAME

    def state_gameover(self):
        response = {Action.RESTART: GameManager.INIT, Action.EXIT: GameManager.EXIT}
        action = self.action.getaction()
        while action not in response.keys():
            action = self.action.getaction()
        return response[action]

    def state_game(self):
        # 画出当前棋盘状态
        # 读取用户输入得到action
        action = self.get_user_action()
        if action == Action.RESTART:
            return GameManager.INIT
        elif action == Action.EXIT:
            return GameManager.EXIT
        else:
            self.grid.move(action)
            if self.grid.isgameover():
                return GameManager.GAMEOVER

        return GameManager.GAME

    def get_user_action(self):
        '''
        获取键盘操作
        :param keyboard:
        :return:
        '''
        return self.action.getaction()


if __name__ == '__main__':
    game = GameManager()
    game.startgame()
