import pcbnew

active_pcb = pcbnew.GetBoard()

class LedPlacer():

    def __init__(self, pcb: pcbnew.BOARD=active_pcb):
        self.pcb = pcb

        # constants based on led_mapper_850.kicad_sch
        # rows and columns refer to position on pcb, not in schematic,
        # though the schematic is on the same grid except discontinuities where diagonals are missing
        # for example, D69 is in column 23 and not column 24
        self.num_rows = 12  # actual num rows is 11.5; last row contains only 23 LEDs
        self.num_cols = 46

        # constants based on pixel_loc_analysis.xlsx
        # LEDs lie on a hexagonal grid composed of equilateral triangles with side length equal to self.spacing_um
        # this script is intended to generate the top left rhombus -- the other 2 can be obtained through copy/paste/transformations/edits
        self.spacing_um = 1400.0
        self.row_shift_um = -self.spacing_um / 2  # rows shift left as we go down
        self.col_width_um = self.spacing_um
        self.row_height_um = (self.spacing_um ** 2 - self.row_shift_um ** 2) ** 0.5  # equilateral triangle height

    def led_ref(self, row: int, col: int) -> str:
        '''Get the refdes of an LED given its position in the grid.
        
        This method will break if the schematic is changed.

        :param int row: The row of the LED in the rectangular grid, from top (row 1) to bottom (row 12)
        :param int col: The column of the LED in the rectangular grid, from left (col 1) to right (col 46)
        :return int: LED refdes
        '''
        return f'/D{self.led_id(row, col):02}'

    def led_id(self, row: int, col: int) -> int:
        '''Get the id of an LED given its position in the grid.
        
        This method will break if the schematic is changed.

        :param int row: The row of the LED in the rectangular grid, from top (row 1) to bottom (row 12)
        :param int col: The column of the LED in the rectangular grid, from left (col 1) to right (col 46)
        :return int: LED id
        '''
        assert 1 <= row <= self.num_rows, "row outside grid!"
        assert 1 <= col <= self.num_cols, "column outside grid!"
        half_cols = self.num_cols / 2
        assert not (row == self.num_rows and col > half_cols), \
            f"final row (row {self.num_rows}) is only half-full, with LEDs from col 1 - {half_cols}!"

        row_idx = row - 1
        return row_idx * self.num_cols + col
