import numpy as np
import sys
from IPython.display import clear_output
import re
import time
from copy import deepcopy
import random
import itertools
import cv2
import os
    
DIMENSION = 9
# can rotate all pieces with np.rot90(m, k=1)

# m 	Array of two or more dimensions. 
# k 	Number of times the array is rotated by 90 degrees. 


pieces = [
        np.array([[1, 1],
                  [1, 1]]), # 0

        np.array([[0, 1, 0],
                  [1, 1, 1]]), # 1

        np.array([[0, 1, 1],
                  [1, 1, 0]]), # 2

        np.array([[0, 1, 0],
                  [0, 1, 0],
                  [1, 1, 1]]), # 3

        np.array([[1, 1, 1, 1]]), # 4

        np.array([[1, 1, 1]]), # 5

        np.array([[0, 1],
                  [1, 1]]), # 6

        np.array([[1, 0, 0],
                  [1, 1, 1]]), # 7

        np.array([[1, 0, 0],
                  [1, 0, 0],
                  [1, 1, 1]]), # 8
        
        np.array([[1, 1]]), # 9
    
        np.array([[1, 0, 0],
                  [0, 1, 0],
                  [0, 0, 1]]), # 10
    
        np.array([[1, 0],
                  [0, 1]]), # 11

        np.array([[1]]) #12

    ]

class GameState():
    def __init__(self, board=None, pcs=None, lose=None, checkLost=None, points=None):
        self.board = np.zeros((9,9), dtype = int)
        
        # assign random piece indices
        p = np.random.rand(3)
        
        pr = []
        y_off = 0
        # make piece orientation random
        for i in p:
            rotated = np.rot90(pieces[int(round(i*(len(pieces)-1)))], k=int(round(np.random.rand()*5)))
            piece_object = Piece(piece=rotated,placed = 0, gs = self)
            pr.append(piece_object)
         
        # piece is object with a piece and a flag if placed
        self.pcs = pr
        self.lose = False
        self.checkLost = True
        self.points = 0
        
    def copy(self):
        return deepcopy(self)
        
    
    def placed3(self):
        # create 3 new pieces
        p = np.random.rand(3)
        
        pr = []
        y_off = 0
        # make piece orientation random
        for i in p:
            rotated = np.rot90(pieces[int(round(i*(len(pieces)-1)))], k=int(round(np.random.rand()*5)))
            piece_object = Piece(piece=rotated,placed = 0, gs = self)
            pr.append(piece_object)
         
        # piece is object with a piece and a flag if placed
        self.pcs = pr
        
    def drawBoard(self, HIGH_SCORE):
        game_screen = np.zeros((876,1158,3))
        blank = np.ones((64,64,3))
        BLUE=(0,0,255)
        CHARCOAL = (56,56,56)
        WHITE = (255,255,255)
        blue = np.ones((64,64,3))*BLUE
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (40, 656)
        org2 = (40, 696)
        fontScale = 1
        thickness = 2
        y_offset = 5
        
        # draw board
        for i in range(9):
            x_offset = 5
            for j in range(9):
                if self.board[i][j] == 1:
                    block = blue
                else:
                    block = blank
                game_screen[(64*i)+y_offset:(64*(i+1))+y_offset,(64*j)+x_offset:(64*(j+1))+x_offset,:] = block
                x_offset += 5
            y_offset += 5
        
        for i in range(4):
            game_screen[:626,i*(64*3+13):i*(64*3+13)+9,:] = np.zeros((626,9,3))    
        
        for j in range(4):
            game_screen[j*(64*3+13):j*(64*3+13)+9,:626,:] = np.zeros((9,626,3))
            
        piece_offset= 0
        y_offset = 5
        x_offset = 5
        # draw pieces
        for p in self.pcs:
            if p.placed == 0:
                r,c = p.shape
                for i in range(r):
                    x_offset = 5 
                    for j in range(c):
                        if p.piece[i][j] == 1:
                            game_screen[20 + piece_offset + (64*i)+y_offset:20 + piece_offset + (64*(i+1))+y_offset,636 + (64*j)+x_offset:636 + (64*(j+1))+x_offset,:] = blue
                        x_offset += 5
                    y_offset += 5
            piece_offset += p.shape[0]*64 + 30
        
        game_screen = cv2.putText(game_screen, 'Points: '+ str(self.points), org, font, fontScale, WHITE, thickness, cv2.LINE_AA)
        game_screen = cv2.putText(game_screen, 'HIGH SCORE: '+ str(HIGH_SCORE), org2, font, fontScale, WHITE, thickness, cv2.LINE_AA)

        cv2.imshow('Game Screen',game_screen)
        key = cv2.waitKey(50)        # Timed wait, allows the screen to be seen as the AI moves really fast
        if key == ord('q'):
            cv2.destroyAllWindows()
            sys.exit()
        cv2.destroyAllWindows()
        
    def drawBoardLost(self, HIGH_SCORE):
        game_screen = np.zeros((876,1158,3))
        blank = np.ones((64,64,3))
        BLUE=(0,0,255)
        CHARCOAL = (56,56,56)
        WHITE = (255,255,255)
        blue = np.ones((64,64,3))*BLUE
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (40, 656)
        org2 = (40, 696)
        fontScale = 1
        thickness = 2
        y_offset = 5
        
        # draw board
        for i in range(9):
            x_offset = 5
            for j in range(9):
                if self.board[i][j] == 1:
                    block = blue
                else:
                    block = blank
                game_screen[(64*i)+y_offset:(64*(i+1))+y_offset,(64*j)+x_offset:(64*(j+1))+x_offset,:] = block
                x_offset += 5
            y_offset += 5
        
        for i in range(4):
            game_screen[:626,i*(64*3+13):i*(64*3+13)+9,:] = np.zeros((626,9,3))    
        
        for j in range(4):
            game_screen[j*(64*3+13):j*(64*3+13)+9,:626,:] = np.zeros((9,626,3))
            
        piece_offset= 0
        y_offset = 5
        x_offset = 5
        # draw pieces
        for p in self.pcs:
            if p.placed == 0:
                r,c = p.shape
                for i in range(r):
                    x_offset = 5 
                    for j in range(c):
                        if p.piece[i][j] == 1:
                            game_screen[20 + piece_offset + (64*i)+y_offset:20 + piece_offset + (64*(i+1))+y_offset,636 + (64*j)+x_offset:636 + (64*(j+1))+x_offset,:] = blue
                        x_offset += 5
                    y_offset += 5
            piece_offset += p.shape[0]*64 + 30
        
        game_screen = cv2.putText(game_screen, 'Points: '+ str(self.points), org, font, fontScale, WHITE, thickness, cv2.LINE_AA)
        game_screen = cv2.putText(game_screen, 'HIGH SCORE: '+ str(HIGH_SCORE), org2, font, fontScale, WHITE, thickness, cv2.LINE_AA)
        
        game_screen = cv2.putText(game_screen, 'Oh no, I have lost.', (100,400), font, 3, (0,255,0), 8, cv2.LINE_AA)

        cv2.imshow('Game Screen',game_screen)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    def printBoard(self):
        print(self.board)
        
    def printPieces(self):
        # iterate through pieces and only print the ones not placed
        # return a list with indices of pieces not placed 
        piece_list = []
        for idx, i in enumerate(self.pcs):
            if i.placed == 0:
                piece_list.append(idx)
                print(idx, '\n', i.piece)
        return piece_list
    
    def printAllPieces(self):
        # iterate through pieces and only print the ones not placed
        # return a list with indices of pieces not placed 
        piece_list = []
        for idx, i in enumerate(self.pcs):
            piece_list.append(idx)
            print(idx, '\n', i.piece)
        return piece_list

class Piece(): 
    def __init__(self, piece, placed, gs):
        self.piece = piece
        self.placed = placed
        self.gs = gs
        self.shape = self.piece.shape
        r,c = self.shape
        self.drag_center = (0,0)
        
        
    def place_piece(self,mouse_end):
        # first check board to check mouse_end is not already placed
        if mouse_end[0] >= DIMENSION or mouse_end[1] >= DIMENSION:
            return
        if self.gs.board[mouse_end[0]][mouse_end[1]] == 1 and self.piece[self.drag_center[0]][self.drag_center[1]] == 1:
            return
        else:
            temp_board = self.gs.board.copy()
            # check board to see if rest of piece is valid
            r,c = self.piece.shape
            for y in range(r):
                for x in range(c):
                    if self.piece[y][x] == 1:
                        block_x = x-self.drag_center[1]
                        block_y = y-self.drag_center[0]
                        if (block_y + mouse_end[0]) < 0 or (block_y + mouse_end[0]) > 8:
                            self.failed_place(temp_board)
                            return False
                        if (block_x + mouse_end[1]) < 0 or (block_x + mouse_end[1]) > 8:
                            self.failed_place(temp_board)
                            return False
                        if self.gs.board[block_y + mouse_end[0]][block_x + mouse_end[1]] == 1:
                            self.failed_place(temp_board)
                            return False
                        else:
                            # set piece in board
                            self.gs.board[block_y + mouse_end[0]][block_x + mouse_end[1]] = 1
            
            # if pass through check, place
            self.placed = 1
            self.gs.checkLost = True
            self.gs.points += self.piece.sum()
            return True
            

    def failed_place(self,board):
        self.gs.board = board

                


def checkSudoku(gs):
    multiplier = 1
    temp_board = gs.board.copy()
    
    # 3 structures to keep track of which rows columns and blocks to clear
    clear_r = np.zeros(9)
    clear_c = np.zeros(9)
    clear_b = np.zeros((3,3))
    
    # create the sums of rows, columns and blocks
    rows = temp_board.sum(axis=1)
    cols = temp_board.sum(axis=0)  
    H,W = 3,3 # block-size
    m,n = temp_board.shape
    block_matrix = temp_board.reshape(H,m//H,W,n//W).sum(axis=(1,3))
    
    # iterate through the 9 different rows, columns and blocks and mark if need to be cleared
    for i in range(9):
        if rows[i] == 9:
            clear_r[i]=1
        if cols[i] == 9:
            clear_c[i]=1
        if block_matrix[i//3][i%3] == 9:
            clear_b[i//3][i%3]=1
            
    # set multiplier
    multiplier += clear_r.sum() + clear_c.sum() + clear_b.sum() 
    
    # clear board
    for i in range(9):
        if clear_r[i]==1:
            gs.board[i] = np.zeros(9)
        if clear_c[i]==1:
            gs.board[:,i] = np.zeros(9)
        if clear_b[i//3][i%3]==1:
            gs.board[3*(i//3):3*(i//3)+3,3*(i%3):3*(i%3)+3] = np.zeros((3,3))
            
    if clear_r.sum() + clear_c.sum() + clear_b.sum() > 0:
        gs.checkLost = False

    num_blocks = temp_board.sum() - gs.board.sum()

    return multiplier, num_blocks

def calculatePoints(multiplier, num_blocks):
    return num_blocks*multiplier

def checkLostGame(gs):
    # iterate through every location on board that is empty and try to place each piece
    row_idx = 0
    col_idx = 0
    for row_idx, row in enumerate(gs.board):
        for col_idx, block in enumerate(row):
            if block == 0:
                for piece in gs.pcs:
                    gs.lose = False
                    gs.lose = attemptPlace(row_idx, col_idx, piece,gs)
                    if not gs.lose:
                        return



def attemptPlace(row_idx, col_idx, piece,gs):
    # iterate through each possible drag center of piece, then check: if using that drag center, can I place the piece?
    r,c = piece.shape
    for dcy in range(r):
        for dcx in range(c):
            if piece.piece[dcy][dcx] == 1:
                # for each drag center
                valid = checkPiece(gs,piece,row_idx,col_idx,dcy,dcx)
                if valid:
                    # can place, gs.lose = False
                    #print('valid placement at: ', row_idx, col_idx,'\n', piece,'\n','drag center: ',dcy,dcx,'\n')
                    return False
                #print('invalid placement at: ', row_idx, col_idx,'\n', piece,'\n','drag center: ',dcy,dcx,'\n')
    return True

def checkPiece(gs,piece, row_idx, col_idx,dcy=0, dcx=0):
    # given a drag center and a location on the board, does piece fit?
    r,c = piece.shape
    for y in range(r):
        for x in range(c):
            if piece.piece[y][x] == 1:
                # check to see if the rest of piece is valid
                block_x = x-dcx
                block_y = y-dcy
                if (block_y + row_idx) < 0 or (block_y + row_idx) > 8:
                    # cant place
                    return False
                if (block_x + col_idx) < 0 or (block_x + col_idx) > 8:
                    # cant place
                    return False
                if gs.board[block_y + row_idx][block_x + col_idx] == 1:
                    # cant place
                    return False
    return True

def loseSequence(gs):
    gs.printBoard()
    gs.printPieces()
    print('Final Points: ',gs.points)
    return False

def main_player():
    gs = GameState()
    running = True
    coord_regex = re.compile('\(?\d,\d\)?')
    while running:
        checkLostGame(gs)
        new3 = True
        for piece in gs.pcs:
            if piece.placed == 0:
                new3 = False
        if new3:
            gs.placed3()
        multiplier, num_blocks = checkSudoku(gs)
        gs.points += calculatePoints(multiplier, num_blocks)
        print('Points: ', gs.points)
        gs.printBoard()
        piece_list = gs.printPieces()
        piece_number = int(input('Enter piece index to place: '))
        if piece_number not in piece_list:
            print('Invalid index')
            clear_output(wait=True)
            continue
        board_location = input('Enter x,y coordinate on board to place piece \nPlacement based on top left of piece')
        if coord_regex.match(board_location):
            x,y = board_location.replace("(","").replace(")","").split(',')
            gs.pcs[piece_number-1].place_piece((int(x),int(y)))
        else:
            print('Not a correct board location')
            clear_output(wait=True)
            
        print('\n')
        clear_output(wait=True)
        
def run_cc(image):
    numLabels, labels, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity = 4)
    return numLabels, labels, stats, centroids

def better_evaluation(gs):
    board = gs.board.copy()
    imboard = np.zeros((DIMENSION,DIMENSION,3))
    imboard[:,:,0] = board*255
    imboard[:,:,1] = board*255
    imboard[:,:,2] = board*255
    imboard = np.array(imboard, dtype=np.uint8)
    imboard = cv2.cvtColor(imboard, cv2.COLOR_BGR2GRAY)
    numLabels, labels, stats, centroids = run_cc(imboard)
    gs.points -= numLabels
    imboard = cv2.cvtColor(np.array(np.ones((imboard.shape[0],imboard.shape[1],3))*255,dtype=np.uint8), cv2.COLOR_BGR2GRAY) - imboard
    numLabels, labels, stats, centroids = run_cc(imboard)
    for i in range(1, numLabels):
        subtraction = 1/stats[i][-1]
        gs.points -= subtraction
    gs.points -= numLabels
    return gs.points

def ai_move(gs):
    all_scores = {}
    action_dict = {}
    pieces_dict = {idx: piece for idx, piece in enumerate(gs.pcs)}
    permutations_list = list(itertools.permutations(list(range(len(gs.pcs))), len(gs.pcs)))
    random.shuffle(permutations_list)
    for po_idx, piece_order in enumerate(permutations_list):
        # for every piece order place a piece that gives highest score
        coords = [(i,j) for i in range(DIMENSION) for j in range(DIMENSION)]
        random.shuffle(coords)
        action_dict[po_idx]= {}
        scores = {}
        copied_gs = gs.copy()
        for idx in piece_order:
            for x,y in coords:
                # try every location in the board and record the points from performing the action
                temp_gs = copied_gs.copy()
                flag = temp_gs.pcs[idx].place_piece((x,y))
                if flag:
                    multiplier, num_blocks = checkSudoku(temp_gs)
                    temp_gs.points += calculatePoints(multiplier, num_blocks)
                    temp_gs.points = better_evaluation(temp_gs)
                    all_scores[(po_idx,idx,x,y)] = temp_gs.points
                    scores[(po_idx,idx,x,y)] = temp_gs.points
            # get the location with the best score # TODO fix max key
            if not scores:
                break
            max_key = max(scores, key=scores.get)
            copied_gs.pcs[max_key[1]].place_piece((max_key[2],max_key[3]))
            multiplier, num_blocks = checkSudoku(copied_gs)
            copied_gs.points += calculatePoints(multiplier, num_blocks)

            action_dict[po_idx][idx] = (max_key[2],max_key[3])
    if not all_scores:
        return None, None
    max_key = max(all_scores, key=all_scores.get)
    permutations_list[max_key[0]]
    return permutations_list[max_key[0]], action_dict[max_key[0]]

def HS_config(score):
    try:
        os.remove("score.config")
        f = open("score.config", "w")
        f.write(str(score))
        f.close()
    except:
        f = open("score.config", "w")
        f.write(str(score))
        f.close()
                
def main_brute_force():
    try:
        f = open("score.config", "r")
        HIGH_SCORE = float(f.read())
    except:
        HIGH_SCORE = 0
    gs = GameState()
    running = True
    high_score = 0
    coord_regex = re.compile('\(?\d,\d\)?')
    while running:
        order= None
        moves = None
        if gs.lose:
            clear_output(wait=True)
            running = loseSequence(gs)
            HS_config(HIGH_SCORE)
            gs.drawBoardLost(HIGH_SCORE)
            break
        checkLostGame(gs)
        new3 = True
        for piece in gs.pcs:
            if piece.placed == 0:
                new3 = False
        if new3:
            gs.placed3()
            checkLostGame(gs)
            if gs.lose:
                clear_output(wait=True)
                running = loseSequence(gs)
                HS_config(HIGH_SCORE)
                gs.drawBoardLost(HIGH_SCORE)
                break
        else:
            multiplier, num_blocks = checkSudoku(gs)
            gs.points += calculatePoints(multiplier, num_blocks)
            if gs.points > HIGH_SCORE:
                HIGH_SCORE = gs.points
            
            # print('Points: ', gs.points)
            
            # gs.printBoard()
            # piece_list = gs.printPieces()
            
            order, moves = ai_move(gs)
            if not order:
                clear_output(wait=True)
                running = loseSequence(gs)
                HS_config(HIGH_SCORE)
                gs.drawBoardLost(HIGH_SCORE)
                break
            for idx in order:
                gs.drawBoard(HIGH_SCORE)
                gs.pcs[idx].place_piece((moves[idx][0],moves[idx][1]))
                multiplier, num_blocks = checkSudoku(gs)
                gs.points += calculatePoints(multiplier, num_blocks)
                
            clear_output(wait=True)

if __name__ == '__main__':
    main_brute_force()