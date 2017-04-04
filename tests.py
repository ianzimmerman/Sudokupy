import unittest
from sudoku import Sudoku

text = ['003020600',
        '900305001',
        '001806400',
        '008102900',
        '700000008',
        '006708200',
        '002609500',
        '800203009',
        '005010300']
    
s = Sudoku([[int(c) for c in r] for r in text])


class TestSudoku(unittest.TestCase):
    def setUp(self):
        pass
                
    def test_import(self):
        self.assertIsInstance(s.puzzle, list)
        self.assertEqual(len(s.puzzle), 9)
        self.assertEqual(len(s.puzzle[0]), 9)
    
    def test_size(self):
        self.assertEqual(s._grid_size, 9)
        self.assertEqual(s._box_size, 3)
    
    def test_value(self):
        self.assertEqual(s._cells[12].value, 3)
    
    def test_row(self): 
        self.assertEqual([c.value for c in s.row(s._cells[12])], list(map(int, '900305001')))
    
    def test_col(self):
        self.assertEqual([c.value for c in s.col(s._cells[12])], list(map(int, '038107620')))
    
    def test_box(self):
        self.assertEqual([c.value for c in s.box(s._cells[12])], list(map(int, '020305806')))
    
    def test_coords(self):
        self.assertEqual(s.index_from_coords(2,6), 24)
        self.assertEqual(s.coords_from_index(24), s.Coords(2,6))
        self.assertEqual(s.box_from_coords(2,6), s.Coords(0,2))
        self.assertEqual(s.box_from_index(24), s.Coords(0,2))
    
    def test_availability(self):
        self.assertEqual(s._cells[13].available, [4,7])


if __name__ == '__main__':  
    unittest.main()