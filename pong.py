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

    if (ball['x'] == paddleLeft['x']):
        if (ball['y'] in paddleLeft['y']):
            ball['dx'] = -ball['dx']
            paddleLeft['score'] += 1
        else:
            if flag == True:
                ball['inPlay'] = 0
            else:
                ball['dx'] = -ball['dx']
    elif (ball['x'] == paddleRight['x']-1):
        if (ball['y'] in paddleRight['y']):
            ball['dx'] = -ball['dx']
            paddleRight['score'] += 1
        else:
            ball['inPlay'] = 0
        
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

def new_paddle(length, posY, posX):    
    padWin = curses.newwin(length, 1, posY, posX)
    padWin.timeout(0)
    draw_pad(padWin)
    paddlePanel = curses.panel.new_panel(padWin)
    paddlePanel.top()
    return paddlePanel
    

def main(net, flag, keyup, keydown):
    stdscr=curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.clear()
    stdscr.nodelay(1)
    curses.start_color()
    curses.use_default_colors ()
    curses.init_pair (1, curses.COLOR_WHITE, -1)
    curses.curs_set(False) # Turn off the cursor, we won't be needing it.

    ball = {'x':0, 'y':0,                # A dict of attributes about the ball
            'dx':0, 'dy':0,
            'inPlay':0}

    ball['x'] = curses.COLS // 2         # Ball's initial X position.
    ball['y'] = curses.LINES // 2        # Starts at screen center.
    ball['dx'] = random.choice([-1, 1])  # The ball's slope components
    ball['dy'] = random.choice([-1, 1])
    ball['inPlay'] = 1                   # Status of game
    
    paddleLeft = {'x':0, 'y':[0, 0, 0], 'score':0}      # a dict of attributes about paddle
    paddleLeft['x'] = 0                      # Starting x and y of the paddle
    paddleLeft['y'] = [curses.LINES // 2 + i for i in (2, 0, -2)]
                                         # lowest to highest, visually
    paddleRight = {'x':0, 'y':[0, 0, 0], 'score':0}      # a dict of attributes about paddle
    paddleRight['x'] = curses.COLS - 2      # Starting x and y of the paddle
    paddleRight['y'] = [curses.LINES // 2 + i for i in (2, 0, -2)]
    
    stdscr.addch(ball['y'], ball['x'], 'O')
    paddlePanelLeft = new_paddle(6, curses.LINES // 2, 0)
    paddlePanelRight = new_paddle(6, curses.LINES // 2, curses.COLS - 2)
    update_paddle(paddlePanelLeft, paddleLeft, stdscr, 'r', 'w')
    
    stdscr.refresh()
    
    while ball['inPlay']:
        if not sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            ball = update_ball(stdscr, ball, paddleLeft, paddleRight, flag)
            mv = net_calc_paddle(net, paddleRight, ball)
            
            stdscr.addstr(1, curses.COLS // 2 - 4, str(paddleLeft['score']) + ' ' + str(paddleRight['score']))
            
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
    return paddleRight['score']

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
