#! /usr/bin/env python3
import curses
import curses.panel
import random
import sys
import select
from time import sleep

def quit_curses(stdscr):
    stdscr.clear()
    curses.echo()
    curses.curs_set(True)
    curses.nocbreak()
    curses.endwin()

def update_ball(stdscr, ball, paddleLeft, paddleRight, flag):
    stdscr.addstr(ball['y'], ball['x'], ' ')
    ball['x'] += ball['dx']
    ball['y'] += ball['dy']

    if (ball['y'] == 0 or ball['y'] == curses.LINES - 1):
        ball['dy'] = -ball['dy']

    if (ball['x'] == paddleLeft['x']+1):
        if (ball['y'] in paddleLeft['y']):
            ball['dx'] = -ball['dx']
            paddleLeft['score'] += 1
        else:
            if flag == True:
                ball['inPlay'] = 0
                paddleRight['win'] = True
            else:
                ball['dx'] = -ball['dx']
    elif (ball['x'] == paddleRight['x']-1):
        if (ball['y'] in paddleRight['y']):
            ball['dx'] = -ball['dx']
            paddleRight['score'] += 1
        else:
            ball['inPlay'] = 0
            if flag == True:
                paddleLeft['win'] = True
        
    if (ball['inPlay'] != 0):
        stdscr.addstr(ball['y'], ball['x'], 'O')
    
    return ball


def update_paddle(pad, paddle, stdscr, keyDown, keyUp):
    oldPaddleY = paddle['y'][:]
    
    try:
        move = pad.window().getch()
        if (move == ord(keyDown) and paddle['y'][0] < curses.LINES - 1):
            for i in range(len(paddle['y'])):
                paddle['y'][i] += 2
        elif (move == ord(keyUp) and paddle['y'][2] > 0):
            for i in range(len(paddle['y'])):
                paddle['y'][i] -= 2
        elif (move == ord('q')):
            quit_curses(stdscr)
            quit()
        else:
            pass    
    except curses.error:
        pass
    
    try:
        pad.move(paddle['y'][2], paddle['x'])
    except:
        pass
    curses.panel.update_panels()

def net_calc_paddle(net, paddle, ball):
    dist = [abs(ball['y'] - paddle['y'][2])]
    
    result = net.serial_activate(dist)
    return round(result[0])

def move_paddle(move, pad, paddle):
    oldPaddleY = paddle['y'][:]
    
    try:
        if (move == 0 and paddle['y'][0] < curses.LINES - 1):
            for i in range(len(paddle['y'])):
                paddle['y'][i] += 2
        elif (move == 1 and paddle['y'][2] > 0):
            for i in range(len(paddle['y'])):
                paddle['y'][i] -= 2
        else:
            pass    
    except curses.error:
        pass
    
    try:
        pad.move(paddle['y'][2], paddle['x'])
    except:
        pass
    curses.panel.update_panels()

def draw_pad(padWin):
    for i in range(0, 5):
        padWin.addch(i, 0, '#')

def new_paddle_panel(length, posY, posX):    
    padWin = curses.newwin(length, 1, posY, posX)
    padWin.timeout(0)
    draw_pad(padWin)
    paddlePanel = curses.panel.new_panel(padWin)
    paddlePanel.top()
    return paddlePanel

def init_curses():
    stdscr=curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.clear()
    # stdscr.nodelay(1)
    curses.start_color()
    curses.use_default_colors ()
    curses.init_pair (1, curses.COLOR_WHITE, -1)
    curses.init_pair (2, curses.COLOR_RED, -1)
    curses.curs_set(False) # Turn off the cursor, we won't be needing it.
    return stdscr

def init_paddle(x,y):
    paddle = {'x':0, 'y':[0, 0, 0], 'score':0, 'win':False}      # a dict of attributes about paddle
    paddle['x'] = x                      # Starting x and y of the paddle
    paddle['y'] = y 
    return paddle 

def main(net, flag, keyup, keydown, wins):
    
    stdscr = init_curses()
    
    ball = {'x':0, 'y':0,                # A dict of attributes about the ball
            'dx':0, 'dy':0,
            'inPlay':0}

    ball['x'] = curses.COLS // 2         # Ball's initial X position.
    ball['y'] = curses.LINES // 2        # Starts at screen center.
    ball['dx'] = random.choice([-1, 1])  # The ball's slope components
    ball['dy'] = random.choice([-1, 1])
    ball['inPlay'] = 1                   # Status of game
    
    paddleLeft = init_paddle(1, [curses.LINES // 2 + i for i in (2, 0, -2)])
    paddleRight = init_paddle(curses.COLS - 2, [curses.LINES // 2 + i for i in (2, 0, -2)])
    # if flag: 
        # stdscr.addstr( curses.COLS // 2-20, r, "Ready to play? Press a key to continue.", curses.color_pair(2))

        # stdscr.getch()
    stdscr.addch(ball['y'], ball['x'], 'O')
    
    paddlePanelLeft = new_paddle_panel(6, curses.LINES // 2, paddleLeft['x'])
    paddlePanelRight = new_paddle_panel(6, curses.LINES // 2, paddleRight['x'])
    
    update_paddle(paddlePanelLeft, paddleLeft, stdscr, 'r', 'w')
    
    stdscr.refresh()
    
    while ball['inPlay']:
        if not sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            ball = update_ball(stdscr, ball, paddleLeft, paddleRight, flag)
            
            mv = net_calc_paddle(net, paddleRight, ball)    
            stdscr.addstr(1, curses.COLS // 2 - 4, str(paddleLeft['score']) + ' ' + str(paddleRight['score']))
            stdscr.addstr(1, 3, str(wins[0]))
            stdscr.addstr(1, curses.COLS - 3, str(wins[1]))

            if paddleRight['score'] == 30 and flag == False:
                quit_curses(stdscr)
                return paddleRight['score']
            
            move_paddle(mv, paddlePanelRight, paddleRight)
            
            if flag == False:
                sleep(0.005)
            else:
                sleep(0.05)
        else:
            update_paddle(paddlePanelLeft, paddleLeft, stdscr,  keyup, keydown)
        stdscr.refresh() 
   
    paddlePanelLeft.hide()
    paddlePanelRight.hide()
    quit_curses(stdscr)
    if paddleRight['win']:
        wins[1] += 1
    elif paddleLeft['win']:
        wins[0] += 1
    return paddleRight['score'], wins 

    # stdscr.refresh()
    # # sleep(2)
    # stdscr.addstr(curses.LINES // 2 + 1, curses.COLS // 2 - 7,
                  # "Your Score Was: " + str(ball['score']))
    # stdscr.refresh()
    # # sleep(1)
    # stdscr.addstr(curses.LINES // 2 + 2, curses.COLS // 2 - 20,
                  # "Press q to quit or any other key to play again")
    # stdscr.refresh()
    # # sleep(1)   
    # curses.cbreak(True) 
    # curses.flushinp()
    # choice = stdscr.getch()
    # if choice == ord('q'):
        # quit_curses(stdscr)
    # else:
        # return curses.wrapper(main)


# if __name__ == "__main__":
    # curses.wrapper(main)
