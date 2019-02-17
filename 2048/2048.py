import curses
from collections import defaultdict
from random import randrange
from random import choice

actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']
letter_codes.extend([curses.KEY_UP, curses.KEY_LEFT, curses.KEY_DOWN, curses.KEY_RIGHT])
actions_dict = dict(zip(letter_codes, actions * 2 + actions[0:4]))
color_pair = {
    'NEW': 1,
    'BIG': 2
}


def transpose(field):
    '''
    将矩阵转置
    :param field: 格式(('a','b', 'c'), (1, 2, 3))
    :return:
    '''
    return [list(row) for row in zip(*field)]


def invert(field):
    '''
    矩阵逆转
    :param field:
    :return:
    '''
    return [row[::-1] for row in field]


class GameField:
    def __init__(self, height=2, width=2, win=2048):
        self.height = height  # 高
        self.width = width  # 宽
        self.win_value = 2048  # 过关分数
        self.score = 0  # 当前分数
        self.highscore = 0  # 最高分
        # self.reset()  # 棋盘重置

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

    def isgameover(self):
        """
        判断游戏是否成功或失败
        :return:  True 成功， False 失败， None 进行中
        """
        for row in self.field:
            if 0 in row:
                return False

        movealbe = False
        for direction in actions[0:4]:
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
            check['Left'](invert(field))

        check['Up'] = lambda field: \
            check['Left'](transpose(field))

        check['Down'] = lambda field: \
            check['Right'](transpose(field))

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
        moves['Right'] = lambda field: invert(moves['Left'](invert(field)))
        moves['Up'] = lambda field: transpose(moves['Left'](transpose(field)))
        moves['Down'] = lambda field: transpose(moves['Right'](transpose(field)))
        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True

    def draw(self, stdscr, states):
        stdscr.clear()
        stdscr.addstr('Score:' + str(self.score)+"\n")
        x = 8  # 小方格宽度，单位为字符
        y = 4  # 小方格高度，单位为字符
        crosschar = '+'  # 交叉点
        xchar = '-'  # 横线
        ychar = '|'  # 竖线
        for j in range(self.height * y + 1):
            for i in range(self.width * x + 1):
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
                    if self.field[row][col] != 0:
                        if self.field[row][col] < 0:
                            self.field[row][col] *= -1
                            printpair = color_pair['NEW']
                        elif self.field[row][col] >= 64:
                            printpair = color_pair['BIG']
                        printchar = str(self.field[row][col])
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
                        stdscr.addstr(printj, printi, printchar, curses.color_pair(printpair))
                    else:
                        stdscr.addstr(printj, printi, printchar)
        stdscr.addstr('\n')
        if states == 'Gameover':
            stdscr.addstr('     (R)Restart (Q)Exit\n')
        else:
            stdscr.addstr('(W)Up (S)Down (A)Left (D)Right\n')
        # stdscr.getch()


def main(stdscr):
    gamefield = GameField()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    stdscr.keypad(True)

    def init():
        gamefield.reset()
        return 'Game'

    def not_game(state):
        responses = defaultdict(lambda: state)
        responses['Restart'] = 'Init'
        responses['Exit'] = 'Exit'
        return responses['Restar']

    def game():
        # 画出当前棋盘状态
        # 读取用户输入得到action
        gamefield.draw(stdscr, state)
        action = get_user_action()
        if action == 'Restart':
            return "Init"
        elif action == 'Exit':
            return "Exit"
        else:
            gamefield.move(action)
            if gamefield.isgameover():
                return 'Gameover'

        return 'Game'

    def get_user_action():
        '''
        获取键盘操作
        :param keyboard:
        :return:
        '''
        char = 'N'
        while char not in actions_dict:
            char = stdscr.getch()
        return actions_dict[char]

    state_actions = {
        'Init': init,
        'Win': lambda: not_game('Win'),
        'Gameover': lambda: not_game('Gameover'),
        'Game': game
    }
    state = 'Init'
    while state != 'Exit':
        statefuc = state_actions[state]
        if statefuc is None:
            pass
        else:
            state = statefuc()

    curses.endwin()


if __name__ == '__main__':
    curses.wrapper(main)
    # main(None)
