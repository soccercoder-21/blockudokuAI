import numpy as np
import pygame, sys
from pygame.locals import *

WIDTH = HEIGHT = 576
    
DIMENSION = 9
    
SQ_SIZE = HEIGHT // DIMENSION
    
MAX_FPS = 15
WHITE=(255,255,255)
BLUE=(0,0,255)
RED = (255, 0, 0)
BLACK = (0,0,0)

pausetimerevent = pygame.USEREVENT + 1
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
                  [0, 1]]) # 11
    
    ]

class GameState():
    def __init__(self, screen, all_sprites):
        self.board = np.zeros((9,9), dtype = int)
        
        # assign random piece indices
        p = np.random.rand(3)
        
        pr = []
        y_off = 0
        # make piece orientation random
        for i in p:
            rotated = np.rot90(pieces[int(round(i*11))], k=int(round(np.random.rand()*11)))
            piece_object = Piece(piece=rotated,clicked=0,placed = 0, y_off = y_off, gs = self)
            all_sprites.add(piece_object)
            pr.append(piece_object)
            y_off += (1+rotated.shape[0])*SQ_SIZE
         
        # piece is object with a piece and a flag if placed
        self.pcs = pr
        self.lose = False
        self.checkLost = True
        self.points = 0
    
    def placed3(self):
        # create 3 new pieces
        p = np.random.rand(3)
        
        pr = []
        y_off = 0
        # make piece orientation random
        for i in p:
            rotated = np.rot90(pieces[int(round(i*11))], k=int(round(np.random.rand()*11)))
            piece_object = Piece(piece=rotated,clicked=0,placed = 0, y_off = y_off, gs = self)
            all_sprites.add(piece_object)
            pr.append(piece_object)
            y_off += (1+rotated.shape[0])*SQ_SIZE
         
        # piece is object with a piece and a flag if placed
        self.pcs = pr

class Piece(pygame.sprite.Sprite): 
    def __init__(self, piece, clicked, placed, y_off, gs):
        pygame.sprite.Sprite.__init__(self)
        self.piece = piece
        self.clicked = clicked
        self.placed = placed
        self.y_off = y_off
        self.gs = gs
        self.shape = self.piece.shape
        r,c = self.shape
        
        self.image = pygame.Surface((c*(SQ_SIZE-2),r*(SQ_SIZE-2)),pygame.SRCALPHA, 32)
        self.image.convert_alpha()

        if self.placed == 0:
            for y in range(r):
                for x in range(c):
                    if piece[y][x] == 1:
                        self.image.fill(BLUE,(x*SQ_SIZE,y*SQ_SIZE,SQ_SIZE-2, SQ_SIZE-2))
                    
        self.rect = self.image.get_rect()       
        self.rect.x = (DIMENSION+1)*SQ_SIZE
        self.rect.y = self.y_off
        self.drag_center = (0,0)
        
        

        
    def move(self, rel_x, rel_y):
        self.rect.x += rel_x
        self.rect.y += rel_y
        
    def place_piece(self, mouse_end):
        # first check board to check mouse_end is not already placed
        if self.gs.board[mouse_end[0]][mouse_end[1]] == 1:
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
                            return
                        if (block_x + mouse_end[1]) < 0 or (block_x + mouse_end[1]) > 8:
                            self.failed_place(temp_board)
                            return 
                        if self.gs.board[block_y + mouse_end[0]][block_x + mouse_end[1]] == 1:
                            self.failed_place(temp_board)
                            return 
                        else:
                            # set piece in board
                            self.gs.board[block_y + mouse_end[0]][block_x + mouse_end[1]] = 1
            
            # if pass through check, place
            self.placed = True
            self.gs.checkLost = True
            self.gs.points += self.piece.sum()
            
            for p in self.gs.pcs:
                if p.placed:
                    self.gs.pcs.remove(p)

    def failed_place(self,board):
        self.gs.board = board

        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            location = pygame.mouse.get_pos() # returns x,y location of the mouse
            # if mouse press is on board disregard
            if location[0]< SQ_SIZE*(DIMENSION+1):
                return
            elif location[1] < self.y_off:
                return
            elif location[1] > (self.y_off + (1+self.piece.shape[0])*SQ_SIZE):
                return
                
            mx, my = location[0]//SQ_SIZE, location[1]//SQ_SIZE
            y_offset = self.y_off//SQ_SIZE
            r,c = self.piece.shape
            for i in range(r):
                for j in range(c):
                    if self.piece[i][j] == 1:
                        if mx == ((DIMENSION+1) + j):
                            if my == y_offset + i:
                                #drag from piece at ij as center
                                #piece_draging = True
                                #mouse_x, mouse_y = event.pos
                                # get piece object function
                                #offset_x = rectangle.x - mouse_x
                                #offset_y = rectangle.y - mouse_y
                                self.clicked = 1
                                self.drag_center = i,j
                        # if this ends then not the first piece so update to next y piece
        
        elif event.type == pygame.MOUSEBUTTONUP:
            location = pygame.mouse.get_pos()
            if self.clicked: # for the clicked piece
                #ensure that mouse is within board
                if location[0] > SQ_SIZE*(DIMENSION) or location[1] > SQ_SIZE*(DIMENSION):
                    self.placed = 0 # not placed
                if location[0] < SQ_SIZE*(DIMENSION) and location[1] < SQ_SIZE*(DIMENSION):
                    # inside the board
                    # figure out which square on board the mouse ended
                    mx, my = location[0]//SQ_SIZE, location[1]//SQ_SIZE
                    mouse_end = (my,mx)
                    self.place_piece(mouse_end)
                
                if not self.placed:
                    self.rect.x = (DIMENSION+1)*SQ_SIZE
                    self.rect.y = self.y_off
                if self.placed:
                    self.kill()
                    
                self.clicked = 0
        elif event.type == pygame.MOUSEMOTION:
            if self.clicked:
                self.move(event.rel[0], event.rel[1])
                
def drawGameState(screen,gs):
    drawBoard(screen)
    drawPlaced(screen,gs.board)

def drawBoard(screen):
    sudoku_x_offset = 0
    sudoku_y_offset = 0
    for r in range(DIMENSION):
        if (r%3) == 0:
                sudoku_y_offset += 3
                
        for c in range(DIMENSION):
            if (c%3) == 0:
                sudoku_x_offset += 3
            pygame.draw.rect(screen, BLACK, (c*SQ_SIZE+sudoku_x_offset,r*SQ_SIZE+sudoku_y_offset, SQ_SIZE+6, SQ_SIZE+6))
            pygame.draw.rect(screen, WHITE, (c*SQ_SIZE+1+sudoku_x_offset,r*SQ_SIZE+1+sudoku_y_offset, SQ_SIZE-2, SQ_SIZE-2))
            
        sudoku_x_offset = 0

def drawPlaced(screen,board):
    sudoku_x_offset = 0
    sudoku_y_offset = 0
    for r in range(DIMENSION):
        if (r%3) == 0:
                sudoku_y_offset += 3
                
        for c in range(DIMENSION):
            if (c%3) == 0:
                sudoku_x_offset += 3
            if board[r][c] == 1:
                pygame.draw.rect(screen, BLUE, (c*SQ_SIZE+1+sudoku_x_offset,r*SQ_SIZE+1+sudoku_y_offset, SQ_SIZE-2, SQ_SIZE-2))
        sudoku_x_offset = 0


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
                    gs.lost = False
                    gs.lost = attemptPlace(row_idx, col_idx, piece.piece,gs)
                    if not gs.lost:
                        #print('check lost game result: ', gs.lost,'\n')
                        return
                    #print('invalid placement at: ', row_idx,col_idx,'\n',piece.piece,'\n')

    #print('check lost game result: ', gs.lost,'\n')


def attemptPlace(row_idx, col_idx, piece,gs):
    # iterate through each possible drag center of piece, then check: if using that drag center, can I place the piece?
    r,c = piece.shape
    for dcy in range(r):
        for dcx in range(c):
            if piece[dcy][dcx] == 1:
                # for each drag center
                valid = checkPiece(gs,dcy,dcx,piece,row_idx,col_idx)
                if valid:
                    # can place, gs.lose = False
                    #print('valid placement at: ', row_idx, col_idx,'\n', piece,'\n','drag center: ',dcy,dcx,'\n')
                    return False
                #print('invalid placement at: ', row_idx, col_idx,'\n', piece,'\n','drag center: ',dcy,dcx,'\n')
    return True

def checkPiece(gs, dcy, dcx, piece, row_idx, col_idx):
    # given a drag center and a location on the board, does piece fit?
    r,c = piece.shape
    for y in range(r):
        for x in range(c):
            if piece[y][x] == 1:
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


def main():
    pygame.init()
    
    DISPLAY=pygame.display.set_mode((896,800))
    DISPLAY.fill(WHITE)
    
    # set the pygame window name 
    pygame.display.set_caption('Game Window') 
      
    # create a font object. 
    # 1st parameter is the font file 
    # which is present in pygame. 
    # 2nd parameter is size of the font 
    font = pygame.font.Font('freesansbold.ttf', 20)
    losefont = pygame.font.Font('freesansbold.ttf', 80)
    global all_sprites 
    all_sprites = pygame.sprite.Group()

    gs = GameState(DISPLAY, all_sprites)
    running = True
    lose_message_time = 2000
    high_score = 0
    while running:
        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    checkLostGame(gs)
                if event.key == pygame.K_q:
                    gs.lost = True

            for o in gs.pcs:
                o.handle_event(event)

        if not gs.pcs:
            gs.placed3()
            gs.checkLost = True
        
        
        multiplier, num_blocks = checkSudoku(gs)
        
        if gs.checkLost:
            checkLostGame(gs)
            gs.checkLost = False
        
        DISPLAY.fill(WHITE)
        drawGameState(DISPLAY,gs)
        all_sprites.update()
        all_sprites.draw(DISPLAY)
        
        gs.points += calculatePoints(multiplier, num_blocks)
        if gs.points > high_score:
            high_score = gs.points
        hscore = "High Score: " + str(high_score)
        score = "Score: " + str(gs.points)
        
        # create a text suface object, 
        # on which text is drawn on it. 
        text = font.render(score, True, BLACK) 
        htext = font.render(hscore, True, BLACK)
      
        # create a rectangular object for the 
        # text surface object 
        textRect = text.get_rect()  
        htextRect = htext.get_rect()
        # set the center of the rectangular object. 
        textRect.center = (288, 676)
        htextRect.center = (288, 626)
        DISPLAY.blit(text, textRect)
        DISPLAY.blit(htext, htextRect)
        
        if gs.lost:
            #print('lost')
            losetext = losefont.render('YOU LOST!!!!', True, BLACK) 
            temp_surface = pygame.Surface(losetext.get_size())
            temp_surface.fill((192, 192, 192))
            temp_surface.blit(losetext, (0, 0))
            DISPLAY.blit(temp_surface,(148,300))
            # prompt restart
            while lose_message_time > 0:
                lose_message_time -=1
                pygame.display.update()
            all_sprites = pygame.sprite.Group()
            gs = GameState(DISPLAY, all_sprites)
            lose_message_time =2000

        pygame.display.update()

if __name__ == '__main__':
    main()