import unittest
from sudoku import Sudoku

text = ['043080250',
        '600000000',
        '000001094',
        '900004070',
        '000608000',
        '010200003',
        '820500000',
        '000000005',
        '034090710']
    
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
        self.assertEqual(s._cells[25].value, 9)
    
    def test_row(self): 
        self.assertEqual([c.value for c in s.row(s._cells[25])], list(map(int, '000001094')))
    
    def test_col(self):
        self.assertEqual([c.value for c in s.col(s._cells[25])], list(map(int, '509700001')))
    
    def test_box(self):
        self.assertEqual([c.value for c in s.box(s._cells[25])], list(map(int, '250000094')))
    
    def test_vectors(self):
        self.assertEqual(s.infer_vector(s.row(s._cells[25])), s.row)
        self.assertEqual(s.infer_vector(s.col(s._cells[25])), s.col)
        self.assertEqual(s.infer_vector(s.box(s._cells[25])), s.box)
    
    def test_coords(self):
        self.assertEqual(s.index_from_coords(2,6), 24)
        self.assertEqual(s.coords_from_index(24), s.Coords(2,6))
        self.assertEqual(s.box_from_coords(2,6), s.Coords(0,2))
        self.assertEqual(s.box_from_index(24), s.Coords(0,2))
    
    def test_availability(self):
        self.assertEqual(s._cells[80].available, [2,6,8])
    
    def test_validate(self):
        self.assertEqual(s.solve_singles(), None)
        self.assertEqual(s.validate(), True)
        self.assertEqual(s.value, '143')


if __name__ == '__main__':  
    unittest.main()