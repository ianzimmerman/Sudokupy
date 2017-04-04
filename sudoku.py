from collections import Counter, namedtuple, defaultdict
from itertools import product, chain, combinations
from types import SimpleNamespace

import time

# todo: xwing

def same_attrs(iter, attr):
    check = [getattr(i, attr) for i in iter]
    if check:
        return check.count(check[0]) == len(check)
    else:
        return False

class Sudoku:
    def __init__(self, puzzle):
        '''
        puzzle is list() with n rows of n columns
        Missing values should be Zeroes
        e.g.:
        [
            [1,2,0,4,0,0,0,8,9],
            ... 7 Rows emitted ...,
            [0,0,7,0,5,4,0,2,1]
        ]
        '''
        
        self.Coords = namedtuple('Coords', 'r c')
        self.Cell = SimpleNamespace
        
        self.puzzle = puzzle
        
        self._valid = set(range(1, self._grid_size+1))
        
        self._cells = []
        for i in range(self._grid_size**2):
            coords = self.coords_from_index(i)
            new_cell = self.Cell(index=i, 
                                 row=coords.r, 
                                 col=coords.c,
                                 box=self.box_from_index(i),
                                 value=int(puzzle[coords.r][coords.c]),
                                 available=[])
            
            self._cells.append(new_cell)
                                  
        for cell in self._cells:
            cell.available = self.cell_availability(cell)
        
        self.box_cells = [self.Cell(box=self.box_from_coords(c[0],c[1])) for c in set(combinations([0,3,6]*2, 2))]
    
    @property
    def _grid_size(self):
        return len(self.puzzle[0])
    
    @property   
    def _box_size(self):
        return self._grid_size//3
    
    def coords_from_index(self, i):
        r = int(i//self._grid_size)
        c = int(i - r * self._grid_size)
        return self.Coords(r, c)
        
    def index_from_coords(self, r, c):
        return r * self._grid_size + c
    
    def box_from_coords(self, r, c):
        return self.Coords(int(r//3.0), int(c//3.0))
    
    def box_from_index(self, i):
        c = self.coords_from_index(i)
        return self.box_from_coords(c.r, c.c)
    
    def row(self, cell):
        row_start = cell.row*self._grid_size
        row_end = row_start + self._grid_size
        return self._cells[row_start:row_end]
    
    def col(self, cell):
        return self._cells[cell.col::self._grid_size]
        
    def box(self, cell):
        cells = []
        for n in range(self._box_size):
            r = cell.box.r * self._box_size + n
            row = self.row(self.Cell(row=r))
            
            c = cell.box.c * self._box_size
            
            cells.extend(row[c:c+self._box_size])
        
        return cells
    
    @property
    def vectors(self):
        return [self.row, self.col, self.box]
    
    def infer_vector(self, candidates):
        if same_attrs(candidates, 'col'):
            return self.col
        
        elif same_attrs(candidates, 'row'):
            return self.row
        
        elif same_attrs(candidates, 'box'):
            return self.box
        
        else:
            return None
    
    def cell_availability(self, cell):
        if cell.value != 0: 
            return []
        else:
            all_avail = self._valid.copy()
            for vector in self.vectors:
                all_avail -= {c.value for c in vector(cell)}
            
            return list(all_avail)
            
    def solve(self, cell, value):
        '''
        set cell value to solved item and then remove value from 
        candidate list for row, column, and box
        '''
        self._cells[cell.index].value = value
        self._cells[cell.index].available = []
        
        for vector in self.vectors:
            for c in vector(cell):
                if value in c.available: self._cells[c.index].available.remove(value)

    def update_candidates(self):
        '''
        iterate over rows, cols and boxes to do work
        '''
        
        tests = [self.reveal_hidden_singles,
                 self.reveal_naked_pairs,
                 self.reveal_pointing_pairs,
                 self.reveal_hidden_pairs]    
                 
        for n in range(self._grid_size):
            cell = self.Cell(row=n, col=n)
            for test in tests:
                test(self.row(cell))
                test(self.col(cell))
            
        for cell in self.box_cells:
            for test in tests:
                test(self.box(cell))
        
        # self.reveal_xwing()
                
    def solve_singles(self):
        '''
        check available candidates for each cell, if one candidate, solve
        and then recheck other cells
        '''
        self.update_candidates()
        for cell in self._cells:
            if len(cell.available) == 1:
                self.solve(cell, cell.available.pop()) 
                self.solve_singles()
    
    def reveal_hidden_singles(self, candidates):
        '''
        for each row / col / box if any value is only present once, even if 
        paired with another value, remove other candidates from cell
        
        does not solve the single! run solve_singles after to solve
        '''
        flat_list = chain.from_iterable([c.available for c in candidates])
        counts = [value for value, count in Counter(flat_list).items() 
                        if count == 1]
                        
        for candidate in candidates:
            for value in counts:
                if value in candidate.available: 
                    self._cells[candidate.index].available = [value,]

    def reveal_naked_pairs(self, candidates):
        for n in (2,3):
            pairs = [set(c.available) for c in candidates if len(c.available) == n]
            for pair in pairs:
                matches = [c for c in candidates if c.available and pair >= set(c.available)]
                if len(matches) == n:
                    non_pairs = [c for c in candidates if not pair >= set(c.available)]
                    for c in non_pairs:
                        for p in pair:
                            if p in c.available: self._cells[c.index].available.remove(p)
    
    def reveal_pointing_pairs(self, candidates):
        flat_list = chain.from_iterable([c.available for c in candidates])
        
        for n in (2,3):
            pairs = [value for value, count in Counter(flat_list).items() if count == n]
            
            for pair in pairs:
                matches = [c for c in candidates if pair in c.available]
                if len(matches) == n and same_attrs(matches, 'box'):
                    safe_index = [c.index for c in matches]
                    box = self.box(matches[0])
                    if box != candidates:
                        for cell in [c for c in box if c.index not in safe_index and pair in c.available]:
                            self._cells[cell.index].available.remove(pair)
                    else:
                        if same_attrs(matches, 'col'):
                            col = self.col(matches[0])
                            for cell in [c for c in col if c.index not in safe_index and pair in c.available]:
                                self._cells[cell.index].available.remove(pair)
                        
                        elif same_attrs(matches, 'row'):
                            row = self.row(matches[0])
                            for cell in [c for c in row if c.index not in safe_index and pair in c.available]:
                                self._cells[cell.index].available.remove(pair)

    def reveal_hidden_pairs(self, candidates):
        '''
        see hidden singles
        '''
        
        vector = self.infer_vector(candidates)
        
        def find_hidden_pairs(candidates, n):
            available = [c.available for c in candidates]
            all_available = list(chain.from_iterable(available))
            
            all_combos = chain.from_iterable([list(combinations(a, n)) for a in available])
            
            return [pair for pair, count in Counter(all_combos).items() 
                         if count == n 
                         and available.count(list(pair)) != n
                         and all(all_available.count(p) == n for p in pair)]
        
        for n in (2,3):
            pairs = find_hidden_pairs(candidates, n)
            while pairs: 
                pair = pairs.pop()
                matches = [c for c in candidates if all(p in c.available for p in pair)]
                if len(matches) == n:
                    for m in matches:
                        self._cells[m.index].available = list(pair)
                    
                #pairs = find_hidden_pairs(vector(candidates[0]), n)
    
    def reveal_xwing(self):
        '''
        for rows or cols only, doesnt work for boxes
        basically, if 2 rows/cols have the same single number as candidates to two boxes in teh same col/row
        you can eliminate it from the remainder of teh row.col
        '''
        for vector in (self.row, self.col):
            for n in range(self._grid_size):
                candidates = vector(self.Cell(row=n, col=n))
                available = chain.from_iterable(c.available for c in candidates)
                matches = [value for value, count in Counter(available).items() if count == 2]
                if matches: print(vector, matches)
            
    @property
    def value(self):
        return ''.join([str(c.value) for c in self.row(self.Cell(row=0))][:3])
    
    def validate(self):
        
        for n in range(self._grid_size):
            cell = self.Cell(row=n, col=n)
            row = [c.value for c in self.row(cell)]
            col = [c.value for c in self.col(cell)]
            if not (set(row) == set(col) == self._valid):
                return False
        
        
        for cell in self.box_cells:
            box = [c.value for c in self.box(cell)]
            if set(box) != self._valid:
                return False
        
        self.result = self.value
        return True
    
    def __repr__(self):
        rows = [' '.join([str(c.value) for c in self.row(self.Cell(row=n))]) for n in range(self._grid_size)]
        return '\n'.join(rows)


def main():          
    puzzles = range(50)
    solved = 0
    answer = 0
    
    start = time.time()
    for n in puzzles:
        p = Sudoku(lines[n*9:n*9+9])
        p.solve_singles()
        if p.validate():
            solved += 1
            print(n, p.value, '...')
            answer += int(p.value)
        else:
            print(p)
            for r in range(p._grid_size):
                print([c.available for c in p.row(p.Cell(row=r))])
            print()
            
    print('Solved: {}/{} in {:.2f}s'.format(solved, len(puzzles), time.time()-start))
    print(answer)


if __name__ == '__main__':
    lines = [[int(i) for i in line.strip()] for line in open('p096_sudoku.txt') 
                                        if line[0] != 'G']
    
    main()