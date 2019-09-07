''' Implement an AI to play tetris '''
from random import Random
from te_settings import Direction
from te_settings import MAXROW, MAXCOL
from collections import deque

class AutoPlayer():
    def __init__(self, controller):
        self.controller = controller
        self.rand = Random()
        self.last_gamestate = 0
        self.moves = deque([])
        self.x = 0

    def next_move(self, gamestate):
        if self.no_moves(self.moves) == True:
            self.moves = self.get_moves(gamestate, 2)[1]
            
        self.do_move(gamestate, self.moves)

    def get_moves(self, gamestate, rec): 
        best_score = None
        best_moves = None

        expected_blocks = self.count_blocks(gamestate.get_tiles()) + self.count_blocks(gamestate.get_next_block_tiles())
    
        lst = []
        for x_move in range(-10, 10):
            for r_move in range(-1, 3):
                curr_gamestate = gamestate.clone(True)
                (curr_moves, mock_tiles) = self.simulate_moves(curr_gamestate, x_move, r_move)

                if (curr_moves == None):
                    continue

                curr_score = self.compute_score(curr_gamestate.get_tiles(), mock_tiles)
                
                if (rec > 1):
                    lst.append((-curr_score, x_move, r_move))
                    continue
            
                if (best_score is None or curr_score > best_score):
                    best_score = curr_score
                    best_moves = curr_moves
        
        if (rec == 1):
            return (best_score, best_moves)
        
        lst.sort()
        for i in range (0, min(5, len(lst))):
            curr_gamestate = gamestate.clone(True)
            (curr_moves, _) = self.simulate_moves(curr_gamestate, lst[i][1], lst[i][2])
            
            curr_score = self.get_moves(curr_gamestate, rec - 1)[0]
            if (best_score is None or curr_score > best_score):
                    best_score = curr_score
                    best_moves = curr_moves
            
            
        return (best_score, best_moves)

    def simulate_moves(self, curr_gamestate, x_move, r_move):
        curr_moves = self.values_to_moves(x_move, r_move)

        curr_moves_copy = curr_moves.copy()

        last_pos = curr_gamestate.get_falling_block_position()[0]
        while (self.no_moves(curr_moves) == 0):
            if (self.do_move(curr_gamestate, curr_moves) == 0):
                return (None, None)
            if (curr_gamestate.get_falling_block_position()[0] == last_pos):
                return (None, None)
            
            last_pos = curr_gamestate.get_falling_block_position()[0]

        
        curr_moves = curr_moves_copy
        while (True):
            curr_moves.append((0, 0))
            mock_tiles = self.zero_drop(curr_gamestate)

            if (curr_gamestate.update() == 1):
                return (curr_moves, mock_tiles)
        
        return (None, None)

    def init_matrix(self, n, m):
        mat = []
        for i in range(0, n):
            row = []
            for j in range(0, m):
                row.append(0)
            mat.append(row)
        return mat

    def zero_drop(self, gamestate):
        mat = self.init_matrix(MAXROW, MAXCOL)
        block_tiles = gamestate.get_falling_block_tiles()
        tiles = gamestate.get_tiles()

        for _x in range(0, MAXROW):
            for _y in range(0, MAXCOL):
                if (tiles[_x][_y] != 0):
                    mat[_x][_y] = 1

        pos = gamestate.get_falling_block_position()
        landed = False
        for _x in range(0, len(block_tiles)):
            for _y in range(0, len(block_tiles)):
                if (block_tiles[_x][_y] == 0):
                    continue
        
                mat[pos[1]+_x][pos[0]+_y] = 1

        return mat

    def no_moves(self, curr_moves):
        if (curr_moves):
            return False
        else:
            return True

    def do_move(self, gamestate, curr_moves):
        (f, s) = curr_moves[0]
        curr_moves.popleft()

        if (f != 0):
            gamestate.move(self.dir(f))
        if (s != 0):
            gamestate.rotate(self.dir(s))
        return not gamestate.update()

    def dir(self, x):
        if (x == 1):
            return Direction.RIGHT
        if (x == -1):
            return Direction.LEFT
        return None

    def values_to_moves(self, x_move, r_move):
        res = deque([])
        while x_move != 0 or r_move != 0:
            f = 0
            if x_move < 0:
                f = -1
            elif x_move > 0:
                f = 1
            x_move -= f

            s = 0
            if r_move > 0:
                s = 1
            elif r_move < 0:
                s = -1
            r_move -= s

            res.append((f, s))
        
        return res

    def count_blocks(self, tiles):
        res = 0
        for _x in range(0, len(tiles)):
            for _y in range(0, len(tiles[_x])):
                if (tiles[_x][_y] != 0):
                    res += 1

        return res 
        
    def compute_score(self, tiles, tiles_aux):
        lowest = self.get_lowest(tiles)
        cnt_holes = self.number_of_holes(tiles, lowest) #min
        total_heights = self.total_heights(tiles_aux, self.get_lowest(tiles_aux)) #min
        flat = self.flat(tiles, lowest) #min
        lines = self.complete_lines(tiles_aux)
        #max_height = self.max_height(tiles, lowest)
        #rel_height = self.relative_height(tiles, lowest)

        w_flat = -18.4483
        w_holes = -35.663
        w_heights = -51.0066
        #w_relH = 15.8424
        #w_maxH = -8.6795
        w_lines = 76.0666
        
        '''
        if (total_heights > MAXCOL * 6 or max_height > 8):
            w_holes = -30.8576
            w_heights = -44.1337
        '''
        
        score = flat * w_flat + cnt_holes * w_holes + total_heights * w_heights + lines * w_lines
        return score

    def compare_tiles(self, tiles, real_tiles):
        for _x in range(0, MAXROW):
            for _y in range(0, MAXCOL):
                if (tiles[_x][_y] == 0 and real_tiles[_x][_y] != 0):
                    return False
                if (tiles[_x][_y] != 0 and real_tiles[_x][_y] == 0):
                    return False
                
        return True


    def get_lowest(self, tiles):
        lowest = []
        for _y in range(0, MAXCOL):
            lowest.append(MAXROW)
            for _x in range(0, MAXROW):
                if (tiles[_x][_y] != 0):
                    lowest[_y] = _x
                    break

        return lowest
    
    def max_height(self, tiles, lowest):
        res = -1
        for _y in range(0, MAXCOL):
            res = max(res, MAXROW - lowest[_y])
        
        return MAXROW - res

    def number_of_holes(self, tiles, lowest):
        holes = 0
        for _x in range(1, MAXROW):
            for _y in range(0, MAXCOL):
                if tiles[_x][_y] == 0 and lowest[_y] < _x:
                    holes += 1
        return holes

    def total_heights(self, tiles, lowest):
        res = 0
        for _y in range(0, MAXCOL):
            res += MAXROW - lowest[_y]
        
        return res
    
    def relative_height(self, tiles, lowest):
        mx = -1
        mn = MAXROW
        for _y in range(0, MAXCOL):
            mx = max(mx, MAXROW - lowest[_y])
            mn = min(mn, MAXROW - lowest[_y])
            
        return mx - mn

    def flat(self, tiles, lowest):
        res = 0
        for _y in range(1, MAXCOL):
            res += abs(lowest[_y] - lowest[_y-1])
        
        return res

    def complete_lines(self, tiles):
        res = 0
        for _x in range(0, MAXROW):
            complete_line = True
            for _y in range(0, MAXCOL):
                if (tiles[_x][_y] == 0):
                    complete_line = False
            
            if (complete_line):
                res += 1

        return res