import numpy as np
import random
import copy
import sys
import re

def read_input_data(filename): 
    with open(filename,'r') as f:
        content = f.readlines()
        content = [x.strip() for x in content] 
    
        puzzle = np.chararray((len(content),len(content[0]))) # assume non-empty file
        
        for i in range(len(content)):
            for j in range(len(content[i])):
                puzzle[i][j] = content[i][j]   
    return puzzle

def print_board(board):
    for i in range(board.shape[0]+1):
        if i < board.shape[0]:
            print ' '*16,
            for j in range(board.shape[1]):
                print board[i,j],
            print '|'+str(8-i)
        else: 
            print ' '*17+'- - - - - - - -'
            print ' '*17+'A B C D E F G H'
            print '\n'
  
def change_board(board, action, team):
    if team:
        board[action[0][0]][action[0][1]] = "_"
        board[action[1][0]][action[1][1]] = "W"
    else:
        board[action[0][0]][action[0][1]] = "_"
        board[action[1][0]][action[1][1]] = "B"

def translate(s):
    s = s.replace(' ',"")
    act = []
    for el in s.split(','):
        act.append([vertical_key[el[1]],horizontal_key[el[0]]])
    return act

# Check the state if game is still playing
def is_gaming(board):
    if any(board[0] == "W"):
        print "You Won!"
        return False
    elif any(board[len(board)-1] == "B"):
        print "You lose!"
        return False
    elif getNumBlack(board) == 0:
        print "You Won!"
        return False
    elif getNumWhite(board) == 0:
        print "You lose!"
        return False
    else: 
        return True

# Play the game
def play_game(orig_board, player1_strat, player2_strat, player1_heur, player2_heur):
    
    board = np.copy(orig_board)
    turn = True # If true it's white's turn
    black_num = getNumBlack(board)
    white_num = getNumWhite(board)
        
    while (is_gaming(board)):

        print_board(board)

        if (turn):
            while (1):
                s = raw_input('Choose your piece and target location, e.g. A2,A3\n')
                s = s.replace(' ','')
                if (re.match('^[A-H]{1}[1-8]{1},[A-H]{1}[1-8]{1}$', s)):
                    pass
                else:
                    print 'Please enter your entry in the correct format, e.g. A2,A3'
                    continue
                action = translate(s)
                if board[action[0][0]][action[0][1]] != 'W':
                    print "TOUCH ONLY YOUR OWN PIECES! WTF?"
                    continue
                if action[0][0] - action[1][0] == 1 and abs(action[0][1]-action[1][1]) == 0:
                    if board[action[1][0]][action[1][1]] == 'B':
                        print "YOU CAN'T EAT THAT!"
                        continue
                if action[0][0] - action[1][0] == 1 and abs(action[0][1]-action[1][1]) <= 1:
                    break
                else:
                    print "Illegal move"
                    continue

            change_board(board, action, turn)
        else:
            print 'Opponent\'s turn...'
            if (player2_strat == "minimax"):
                action = minimax(board, turn, black_num, white_num, player2_heur)
            else:
                action = alpha_beta(board, turn, black_num, white_num, player2_heur)
            change_board(board, action, turn)

        turn = not turn

    print_board(board) # Print final state of the board
        
        # print "black_num:", getNumBlack(board), "white_num:", getNumWhite(board)

# minimax algorithm. Team signifies if you are controlling black or white
def minimax(board, team, black_num, white_num, heuristic):
    # So when 2nd argument is True, you are max, if false, you are min
    list_actions = actions(board, True, team)
    max_val = -9999999
    index = -1
    
    for idx, action in enumerate(list_actions):
        temp_board = result(action, board, True ,team, black_num, white_num)
        val = min_value(temp_board, 2, team, black_num, white_num, heuristic)
        max_val = max(max_val, val)
        if max_val == val:
            index = idx
    
    return list_actions[index]

def max_value(board, depth, team, black_num, white_num, heuristic):
    # print "depth: ", depth
    if depth == 0 or black_num == 0 or white_num == 0 or terminal_test(board, depth, team):
        return choose_heuristic(heuristic, board, team, black_num, white_num) # Subject to change depending on the heur.
    v = -999999
    # print "board for max", board
    for action in actions(board, True, team):
        temp_board = result(action, board, True, team, black_num, white_num) # should update black_num & white_num
        v = max(v, min_value(temp_board, depth-1, team, black_num, white_num, heuristic))
    return v

def min_value(board, depth, team, black_num, white_num, heuristic):
    if depth == 0 or black_num == 0 or white_num == 0 or terminal_test(board, depth, team):
        return choose_heuristic(heuristic, board, team, black_num, white_num) # Subject to change depending on the heur
    v = 999999
    for action in actions(board, False, team):
        temp_board = result(action, board, False, team, black_num, white_num)
        v = min(v, max_value(temp_board, depth-1, team, black_num, white_num, heuristic))
    return v

def terminal_test(board, depth, team):
    if any(board[0] == "W"):
        return True
    elif any(board[len(board)-1] == "B"):
        return True
    else: 
        return False

def result(action, board, player_type, team, black_num, white_num):
    temp_board = np.copy(board)
    
    if team:
        if player_type:
            temp_board[action[0][0]][action[0][1]] = "_"
            if (temp_board[action[1][0]][action[1][1]] == "B"):
                black_num -= 1
            temp_board[action[1][0]][action[1][1]] = "W"
        else:
            temp_board[action[0][0]][action[0][1]] = "_"
            if (temp_board[action[1][0]][action[1][1]] == "W"):
                white_num -= 1
            temp_board[action[1][0]][action[1][1]] = "B"
    else:
        if player_type:
            temp_board[action[0][0]][action[0][1]] = "_"
            if temp_board[action[1][0]][action[1][1]] == "W":
                white_num -= 1
            temp_board[action[1][0]][action[1][1]] = "B"
        else: 
            temp_board[action[0][0]][action[0][1]] = "_"
            if temp_board[action[1][0]][action[1][1]] == "B":
                black_num -= 1
            temp_board[action[1][0]][action[1][1]] = "W"
    return temp_board
    
def getNumBlack(board):
    return sum(sum(board=='B'))
    
def getNumWhite(board):
    return sum(sum(board=='W'))

# Oh god... This will be complicated
def actions(board, player_type, team):
    
    global one_counter # team = True
    global two_counter # team = False
    
    if team:
        if player_type:
            possible_moves = white_moves(board)
        else:
            possible_moves = black_moves(board)
    else:
        if player_type:
            possible_moves = black_moves(board)
        else:
            possible_moves = white_moves(board)
        
    return possible_moves
        
# Checks to see what are possible black moves and returns a list of those moves as nodes
def black_moves(board):
    black_coord = zip(np.where(board == "B")[0], np.where(board == "B")[1])
    actions = []
    
    for piece in black_coord:
        if (piece[0]+1 < board.shape[0]):
            if (board[piece[0]+1][piece[1]] == "_"):
                actions.append([(piece[0], piece[1]), (piece[0]+1, piece[1])])
    
        if (piece[1]-1 >= 0 and piece[0]+1 < board.shape[0]):
            if (board[piece[0]+1][piece[1]-1] == "_" or board[piece[0]+1][piece[1]-1] == "W"):
                actions.append([(piece[0], piece[1]), (piece[0]+1, piece[1]-1)])
            
        if (piece[1]+1 < board.shape[1] and piece[0]+1 < board.shape[0]):
            if (board[piece[0]+1][piece[1]+1] == "_" or board[piece[0]+1][piece[1]+1] == "W"):
                actions.append([(piece[0], piece[1]), (piece[0]+1, piece[1]+1)])
    return actions

# Checks to see what are possible white moves and returns a list of those moves as nodes
def white_moves(board):
    white_coord = zip(np.where(board == "W")[0], np.where(board == "W")[1])
    # print "Right before white_coord", board
    # print "white_coord", white_coord
    actions = []
    
    for piece in white_coord:
        if (piece[0]-1 >= 0):
            if (board[piece[0]-1][piece[1]] == "_"):
                actions.append([(piece[0], piece[1]), (piece[0]-1, piece[1])])
    
        if (piece[1]-1 >= 0 and piece[0]-1 >= 0):
            if (board[piece[0]-1][piece[1]-1] == "_" or board[piece[0]-1][piece[1]-1] == "B"):
                actions.append([(piece[0], piece[1]), (piece[0]-1, piece[1]-1)])
        
        if (piece[1]+1 < board.shape[1] and piece[0]-1 >= 0):
            if (board[piece[0]-1][piece[1]+1] == "_" or board[piece[0]-1][piece[1]+1] == "B"):
                actions.append([(piece[0], piece[1]), (piece[0]-1, piece[1]+1)])
    
    return actions

def choose_heuristic(heuristic, board, team, black_num, white_num):
    if heuristic == "defense_heuristic1":
        return defense_heuristic1(board, team, black_num, white_num)
    elif heuristic == "offensive_heuristic1":
        return offensive_heuristic1(board, team, black_num, white_num)
    elif heuristic == "defense_heuristic2":
        return defense_heuristic2(board, team, black_num, white_num)
    else:
        return offensive_heuristic2(board, team, black_num, white_num)

# Dumb defensive heuristic
def defense_heuristic1(board, team, black_num, white_num):
    rand = random.random()
    if (team):
        return 2*getNumWhite(board) + rand
    else:
        return 2*getNumBlack(board) + rand

# Dumb offensive heuristic
def offensive_heuristic1(board, team, black_num, white_num):
    rand = random.random()
    if (team):
        return 2*(30 - getNumBlack(board)) + rand
    else:
        return 2*(30 - getNumWhite(board)) + rand

def offensive_heuristic2(board, team, black_num, white_num):
    rand = random.random()
    if (team):
        # Based on offensive_heuristic1 but set up a multiplier for pieces closer to the goal
        dist = np.where(board == "W")[0][0]
        return  (len(board)-1-dist) * 2*(30 - getNumBlack(board)) + rand
    else:
        dist = np.where(board == "B")[0][-1]
        return dist * 2*(30 - getNumWhite(board)) + rand
    
def defense_heuristic2(board, team, black_num, white_num):
    rand = random.random()
    if (team):
        # Based on offensive_heuristic1 but set up a multiplier for pieces closer to the goal
        dist = np.where(board == "W")[0][0]
        return  (len(board)-1-dist) * 2*getNumWhite(board) + rand
    else:
        dist = np.where(board == "B")[0][-1]
        return dist * 2*getNumBlack(board) + rand

# minimax algorithm. Team signifies if you are controlling black or white
def alpha_beta(board, team, black_num, white_num, heuristic): 
    # So when 2nd argument is True, you are max, if false, you are min
    list_actions = actions(board, True, team)
    max_val = -999999
    index = -1
    
    for idx, action in enumerate(list_actions):
        temp_board = result(action, board, True ,team, black_num, white_num)
        val = ab_min_value(temp_board, -999999, 999999, 3, team, black_num, white_num, heuristic)
        max_val = max(max_val, val)
        if max_val == val:
            index = idx
    
    return list_actions[index]

def ab_max_value(board, alpha, beta, depth, team, black_num, white_num, heuristic):
    if depth == 0 or black_num == 0 or white_num == 0 or terminal_test(board, depth, team):
        return choose_heuristic(heuristic, board, team, black_num, white_num) # Subject to change depending on the heur.
    v = -999999
    for action in actions(board, True, team):
        temp_board = result(action, board, True, team, black_num, white_num)
        v = max(v, ab_min_value(temp_board, alpha, beta, depth-1, team, black_num, white_num, heuristic))
        if (v >= beta):
            return v
        alpha = max(alpha, v)
    return v

def ab_min_value(board, alpha, beta, depth, team, black_num, white_num, heuristic):
    if depth == 0 or black_num == 0 or white_num == 0 or terminal_test(board, depth, team):
        return choose_heuristic(heuristic, board, team, black_num, white_num) # Subject to change depending on the heur
    v = 999999
    for action in actions(board, False, team):
        temp_board = result(action, board, False, team, black_num, white_num)
        v = min(v, ab_max_value(temp_board, alpha, beta, depth-1, team, black_num, white_num, heuristic))
        if (v <= alpha):
            return v
        beta = min(beta, v)
    return v

### Start of Initialization ###
board = read_input_data("8x8.txt")
horizontal_key = dict()
vertical_key = dict()
for ci, i in enumerate(['A','B','C','D','E','F','G','H']):
    horizontal_key[i] = ci
for ci, i in enumerate(['8','7','6','5','4','3','2','1']):
    vertical_key[i] = ci
### End of Initialization ###

# Introduction 
welcome = '''
 __        __   _                                                 
 \ \      / /__| | ___ ___  _ __ ___   ___                        
  \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \                       
  _\ V  V /  __/ | (_| (_) | | | | | |  __/                       
 | |\_/\_/ \___|_|\___\___/|_| |_| |_|\___|                       
 | __/ _ \                                                        
 | || (_) |                                                       
  \__\___/             _    _   _                           _     
 | __ ) _ __ ___  __ _| | _| |_| |__  _ __ ___  _   _  __ _| |__  
 |  _ \| '__/ _ \/ _` | |/ / __| '_ \| '__/ _ \| | | |/ _` | '_ \ 
 | |_) | | |  __/ (_| |   <| |_| | | | | | (_) | |_| | (_| | | | |
 |____/|_|  \___|\__,_|_|\_\\__|_| |_|_|  \___/ \__,_|\__, |_| |_|
                                                      |___/       
'''
print welcome
print '-----------------------------------------------------------'
print 'Choose your Opponent\'s Vision Ability'
print '1. Expert (Minimax)'
print '2. Prophet (Alpha-beta)\n'

# Choose Opponent
c = 0

while (1):
    s = raw_input('Enter 1 or 2: ')
    s = s.replace(' ','')
    if (re.match('^[1-2]{1}$', s)):
        break
    else:
        c += 1
        if c < 10:
            print 'CAN YOU NOT READ?\n'
        else:
            print "You can't read. Get off the computer right now. Goodbye.\n"
            sys.exit()

if int(s.replace(" ","")) == 1:
    opponent =  "an Expert"
    vision = 'minimax'
else:
    opponent = "a Prophet"
    vision = 'alpha_beta'

print '\nYou chose to play against', opponent, '\n'
print '-----------------------------------------------------------'
# Choose your opponent strength and tactic
strategy = {1:"offensive_heuristic1",2:"offensive_heuristic2",
            3:"defense_heuristic1",4:"defense_heuristic2"}

print '''What strategy should your opponent use?
1. Offensive (Eat everyone!)
2. Offensive on steroids
3. Defensive (Go away!)
4. Defensive on steroids
'''

c = 0

while (1):
    s = raw_input('Enter a number from 1 to 4: ')
    s = s.replace(' ','')
    if (re.match('^[1-4]{1}$', s)):
        break
    else:
        c += 1
        if c < 10:
            print 'CAN YOU NOT READ?\n'
        else:
            print "You can't read. Get off the computer right now. Goodbye.\n"
            sys.exit()

print '\nYour opponent is going to use', strategy[int(s)]

# Game begins
print '-----------------------------------------------------------'
print '''
 .---.   .--.  .-.   .-..----.   .----. .----..---. .-..-. .-. .----.
/   __} / {} \ |  `.'  || {_     | {}  }| {_ /   __}| ||  `| |{ {__  
\  {_ }/  /\  \| |\ /| || {__    | {}  }| {__\  {_ }| || |\  |.-._} }
 `---' `-'  `-'`-' ` `-'`----'   `----' `----'`---' `-'`-' `-'`----' 
''' 
play_game(board, "alpha_beta", vision, "offensive_heuristic2", strategy)
