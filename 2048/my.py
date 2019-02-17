import curses


def main(stdscr):
    stdscr.addstr(1, 1, 'hello world')
    stdscr.getch()
    stdscr.refresh()
    curses.endwin()


if __name__ == '__main__':
    curses.wrapper(main)
