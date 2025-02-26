# ============================================================================ #
# lay_out_pcb.py
#
# Jonah Lee
# CCAT Prime 2025
#
# Lay out PCB. 
# KiCAD script to place LEDs for 850GHz LED mapping
# ============================================================================ #

import pcbnew
from math import cos, sin, radians

active_pcb = pcbnew.GetBoard()

class LedPlacer():

    def __init__(self, network: int, pcb: pcbnew.BOARD=active_pcb):

        valid_networks = {1, 2, 3, 4}
        assert network in valid_networks, f"network must be one of: {valid_networks}"
        self.network = network  # charlieplexed network id

        self.connector_ref = f'J{self.network}'

        self.pcb = pcb

        layertable = {}

        for i in range(1000):
            name = pcb.GetLayerName(i)
            if name != "BAD INDEX!":
                layertable[name]=i

        self.layertable: int = layertable
        self.front_copper_layer: int = self.layertable['F.Cu']
        self.back_copper_layer: int = self.layertable['B.Cu']
        self.edgecut: int = self.layertable['Edge.Cuts']

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
        self.row_shift_um = -self.spacing_um / 2  # rows shift left for increasing rows for top right rhombus
        self.col_width_um = self.spacing_um
        # equilateral triangle height, positive means we go down with increasing rows for top right rhombus
        self.row_height_um = (self.spacing_um ** 2 - self.row_shift_um ** 2) ** 0.5
        
        if self.network == 1:
            self.reference_led = 'D1'  # set top left LED as reference position
            self.reference_x_um = 0.0
            self.reference_y_um = 0.0
        if self.network == 2:
            self.reference_led = 'D530'  # set top left LED as reference position
            self.reference_x_um = 200e3
            self.reference_y_um = 0.0
        if self.network == 3:
            self.reference_led = 'D1059'  # set top left LED as reference position
            self.reference_x_um = 0.0
            self.reference_y_um = 200e3
        if self.network == 4:
            self.reference_led = 'D1588'  # set top left LED as reference position
            self.reference_x_um = 200e3
            self.reference_y_um = 200e3
        

        self.default_via_width_nm = int(0.6*10**6)
        self.default_via_drill_nm = int(0.3*10**6)
        self.default_via_type = pcbnew.VIATYPE_THROUGH
        self.via_offset_um = 12  # Adjustment to center via vertically between rows. I don't know why this is needed.

        self.track_width_nm = int(0.2*10**6)

        self.connector_via_dist_um = 2000

    def do_for_each_position(self, func_apply) -> None:
        """Iterate over each point in the 11.5 x 46 hex grid and call func_apply for each, passing in relevant arguments
        
        :param Callable func_apply: Is called for each LED given a dict containing:
        - row: int, ranging from 1-12
        - row_idx: int, ranging from 0-11
        - col: int, ranging from 1-46
        - col_idx: int, ranging from 0-45
        - x_um: float, x position of grid point in um
        - y_um: float, y position of grid point in um
        - led_fp: pcbnew.FOOTPRINT, footprint of the given LED
        """
        for row_idx in range(self.num_rows):
            row = row_idx + 1
    
            for col_idx in range(self.num_cols):
                col = col_idx + 1

                pos_data: dict = {
                    'row': row,
                    'col': col,
                    'row_idx': row_idx,
                    'col_idx': col_idx
                }

                # last row is half full
                if (row == self.num_rows and col > self.num_cols // 2): continue

                ref = self.led_ref(row, col)

                fp: pcbnew.FOOTPRINT = self.pcb.FindFootprintByReference(ref)
                assert fp is not None, f"footprint with refdes: '{ref}' not found!"
                pos_data['led_fp'] = fp

                if ref == self.reference_led:
                    pos_data['x_um'] = self.reference_x_um
                    pos_data['y_um'] = self.reference_y_um
                else:
                    pos_data['x_um'] = self.reference_x_um + col_idx * self.col_width_um + row_idx * self.row_shift_um
                    pos_data['y_um'] = self.reference_y_um + row_idx * self.row_height_um

                func_apply(pos_data)

    def place_leds(self, orientation_deg=0) -> None:
        def place_led(pos_data):
            self.set_microns(pos_data['led_fp'], pos_data['x_um'],  pos_data['y_um'])
            pos_data['led_fp'].SetOrientationDegrees(orientation_deg)
        self.do_for_each_position(place_led)

        pcbnew.Refresh()
    
    def place_pad1_vias(self) -> None:
        # designed for orientation_deg = 0
        
        pad1_vias = {}  # pad1_vias[row_idx][col_idx]

        # place a via for each LED pad 1
        def place_pad1_via(pos_data):

            fp: pcbnew.FOOTPRINT = pos_data['led_fp']
            pad1: pcbnew.PAD = fp.FindPadByNumber(1)
            net: int = pad1.GetNetCode()
            
            via: pcbnew.PCB_VIA = self.place_new_via(
                pos_data['x_um'] - self.spacing_um / 2,
                pos_data['y_um'] + self.row_height_um / 2 - self.via_offset_um,
                net
            )
            if pos_data['row_idx'] in pad1_vias.keys():
                pad1_vias[pos_data['row_idx']][pos_data['col_idx']] = via
            else:
                pad1_vias[pos_data['row_idx']] = {pos_data['col_idx']: via}
        self.do_for_each_position(place_pad1_via)

        # route each LED pad 1 (cathode) to its via
        def route_pad1_to_via(pos_data):
            fp: pcbnew.FOOTPRINT = pos_data['led_fp']
            pad1: pcbnew.PAD = fp.FindPadByNumber(1)
            via: pcbnew.PCB_VIA = pad1_vias[pos_data['row_idx']][pos_data['col_idx']]
            
            track: pcbnew.PCB_TRACK = pcbnew.PCB_TRACK(self.pcb)
            track.SetStart(pad1.GetCenter())
            track.SetEnd(via.GetCenter())
            track.SetWidth(self.track_width_nm)
            track.SetLayer(self.front_copper_layer)
            self.pcb.Add(track)
        self.do_for_each_position(route_pad1_to_via)

        pcbnew.Refresh()
    
    def place_pad2_vias(self) -> None:
        # designed for orientation_deg = 60
        
        pad2_vias = {}  # pad1_vias[row_idx][col_idx]

        # place a via for each LED pad 1
        def place_pad2_via(pos_data):

            fp: pcbnew.FOOTPRINT = pos_data['led_fp']
            pad1: pcbnew.PAD = fp.FindPadByNumber(2)
            net: int = pad1.GetNetCode()

            # vector from footprint centre to via center, before rotation
            x_offset = self.spacing_um / 2  # point to positive x (to the right), since this is for pad 2
            y_offset = self.row_height_um / 2 - self.via_offset_um

            # rotate by 60 deg.
            rot_x_offset =  cos(radians(60.)) * x_offset + sin(radians(60.)) * y_offset
            rot_y_offset = -sin(radians(60.)) * x_offset + cos(radians(60.)) * y_offset
            
            via: pcbnew.PCB_VIA = self.place_new_via(
                pos_data['x_um'] + rot_x_offset,
                pos_data['y_um'] + rot_y_offset,
                net
            )
            if pos_data['row_idx'] in pad2_vias.keys():
                pad2_vias[pos_data['row_idx']][pos_data['col_idx']] = via
            else:
                pad2_vias[pos_data['row_idx']] = {pos_data['col_idx']: via}
        self.do_for_each_position(place_pad2_via)

        # route each LED pad 1 (cathode) to its via
        # def route_pad2_to_via(pos_data):
        #     fp: pcbnew.FOOTPRINT = pos_data['led_fp']
        #     pad1: pcbnew.PAD = fp.FindPadByNumber(2)
        #     via: pcbnew.PCB_VIA = pad2_vias[pos_data['row_idx']][pos_data['col_idx']]
            
        #     track: pcbnew.PCB_TRACK = pcbnew.PCB_TRACK(self.pcb)
        #     track.SetStart(pad1.GetCenter())
        #     track.SetEnd(via.GetCenter())
        #     track.SetWidth(self.track_width_nm)
        #     track.SetLayer(self.front_copper_layer)
        #     self.pcb.Add(track)
        # self.do_for_each_position(route_pad2_to_via)

        pcbnew.Refresh()

    def place_connector_vias(self) -> None:
        """Route each pad on the connector to a nearby via.
        
        Since Networks need to be tiled tightly, it is easiest to put tracks
        to the connector on the two sparsely-populated inner layers.
        """
        j1_fp: pcbnew.FOOTPRINT = self.pcb.FindFootprintByReference(self.connector_ref)
        for padnum in range(1, 13):
            # pad 1-12, left side
            pad: pcbnew.PAD = j1_fp.FindPadByNumber(padnum)
            via_x_um = (pad.GetCenter().x - pad.GetSizeX() / 2) / 1000 - self.connector_via_dist_um
            via_y_um = pad.GetCenter().y / 1000
            via: pcbnew.PCB_VIA = self.place_new_via(via_x_um, via_y_um, pad.GetNetCode())
            # self.add_track(pad, via, layer=self.back_copper_layer)
        for padnum in range(13, 25):
            # pad 13-24, left side
            pad: pcbnew.PAD = j1_fp.FindPadByNumber(padnum)
            pad: pcbnew.PAD = j1_fp.FindPadByNumber(padnum)
            via_x_um = (pad.GetCenter().x + pad.GetSizeX() / 2) / 1000 + self.connector_via_dist_um
            via_y_um = pad.GetCenter().y / 1000
            via: pcbnew.PCB_VIA = self.place_new_via(via_x_um, via_y_um, pad.GetNetCode())
            # self.add_track(pad, via, layer=self.back_copper_layer)

        pcbnew.Refresh()

    def route_columns(self) -> None:
        """Route tracks for vertical columns across for LED pad 2 (anode)"""
        for col_idx in range(self.num_cols):
            col = col_idx + 1

            if 1 <= col <= 12 or 35 <= col <= 46:
                # left & right rectangular sections -- simply route all the way down
                start_row = 1
                end_row = 12 if col <= 23 else 11
                start_pad: pcbnew.PAD = self.led_footprint(start_row, col).FindPadByNumber(2)
                end_pad: pcbnew.PAD = self.led_footprint(end_row, col).FindPadByNumber(2)
                self.add_track(start_pad, end_pad)
            if 13 <= col <= 22:
                # triangle top left half
                start_row = 1
                end_row = 24 - col  # as we go to the right, we end further up
                start_pad: pcbnew.PAD = self.led_footprint(start_row, col).FindPadByNumber(2)
                end_pad: pcbnew.PAD = self.led_footprint(end_row, col).FindPadByNumber(2)
                self.add_track(start_pad, end_pad)
            if 14 <= col <= 23:
                # triangle section 1 bottom left half
                start_row = 25 - col  # as we go to the right, we start further up
                end_row = 12  # left half has full height
                start_pad: pcbnew.PAD = self.led_footprint(start_row, col).FindPadByNumber(2)
                end_pad: pcbnew.PAD = self.led_footprint(end_row, col).FindPadByNumber(2)
                self.add_track(start_pad, end_pad)
            if 24 <= col <= 33:
                # triangle top right half
                start_row = 1
                end_row = 35 - col  # as we go to the right, we end further up
                start_pad: pcbnew.PAD = self.led_footprint(start_row, col).FindPadByNumber(2)
                end_pad: pcbnew.PAD = self.led_footprint(end_row, col).FindPadByNumber(2)
                self.add_track(start_pad, end_pad)
            if 26 <= col <= 34:
                # triangle section 1 bottom right half
                start_row = 36 - col  # as we go to the right, we start further up
                end_row = 11  # left half has full height
                start_pad: pcbnew.PAD = self.led_footprint(start_row, col).FindPadByNumber(2)
                end_pad: pcbnew.PAD = self.led_footprint(end_row, col).FindPadByNumber(2)
                self.add_track(start_pad, end_pad)

        pcbnew.Refresh()

    def place_column_vias(self):
        """place vias for pad 2 at the bottom of each column"""
        for col_idx in range(self.num_cols):
            col = col_idx + 1
            bottom_row = 12 if col <= 23 else 11
            bottom_fp: pcbnew.FOOTPRINT = self.led_footprint(bottom_row, col)
            fp_pos_um: pcbnew.VECTOR2I = bottom_fp.GetPosition() / 1000
            bottom_pad2: pcbnew.PAD = bottom_fp.FindPadByNumber(2)
            net: int = bottom_pad2.GetNetCode()

            via: pcbnew.PCB_VIA = self.place_new_via(
                fp_pos_um.x,
                fp_pos_um.y + self.row_height_um / 2 - self.via_offset_um,
                net
            )

            self.add_track(bottom_pad2, via)
        
        pcbnew.Refresh()

    def add_track(self, start_item: pcbnew.BOARD_ITEM, end_item: pcbnew.BOARD_ITEM, layer=None) -> None:
        if layer is None: layer = self.front_copper_layer
        if start_item == end_item: return
        track: pcbnew.PCB_TRACK = pcbnew.PCB_TRACK(self.pcb)
        track.SetStart(start_item.GetCenter())
        track.SetEnd(end_item.GetCenter())
        track.SetWidth(self.track_width_nm)
        track.SetLayer(layer)
        self.pcb.Add(track)

    def set_microns(self, item: pcbnew.EDA_ITEM, x_um: float, y_um: float) -> None:
        item.SetPosition(pcbnew.VECTOR2I_MM(x_um / 1000, y_um / 1000))

    def led_footprint(self, row: int, col: int) -> pcbnew.FOOTPRINT:
        return self.pcb.FindFootprintByReference(self.led_ref(row, col))

    def led_ref(self, row: int, col: int) -> str:
        '''Get the refdes of an LED given its position in the grid.
        
        This method will break if the schematic is changed.

        :param int row: The row of the LED in the rectangular grid, from top (row 1) to bottom (row 12)
        :param int col: The column of the LED in the rectangular grid, from left (col 1) to right (col 46)
        :return int: LED refdes
        '''
        network_offset = (self.network - 1) * 529
        return f'D{self.led_id(row, col) + network_offset}'

    def led_id(self, row: int, col: int) -> int:
        '''Get the id of an LED given its position in the grid.
        
        This method will break if the schematic is changed.

        :param int row: The row of the LED in the rectangular grid, from top (row 1) to bottom (row 12)
        :param int col: The column of the LED in the rectangular grid, from left (col 1) to right (col 46)
        :return int: LED id
        '''
        assert 1 <= row <= self.num_rows, "row outside grid!"
        assert 1 <= col <= self.num_cols, "column outside grid!"
        half_cols = self.num_cols // 2
        assert not (row == self.num_rows and col > half_cols), \
            f"final row (row {self.num_rows}) is only half-full, with LEDs from col 1 - {half_cols}!"

        row_idx = row - 1
        return row_idx * self.num_cols + col

    def place_new_via(self, x_um: float, y_um: float, net: int,
                      width: int=None, drill: int=None,
                      top_layer: int=None, bottom_layer: int=None,
                      via_type=None) -> pcbnew.PCB_VIA:
        if width is None: width = self.default_via_width_nm
        if drill is None: drill = self.default_via_drill_nm
        if top_layer is None: top_layer = self.front_copper_layer
        if bottom_layer is None: bottom_layer = self.back_copper_layer
        if via_type is None: via_type = self.default_via_type

        via = pcbnew.PCB_VIA(self.pcb)
        self.pcb.Add(via)
        self.set_microns(via, x_um, y_um)
        via.SetWidth(width)
        via.SetDrill(drill)
        via.SetViaType(via_type)
        via.SetLayerPair(top_layer, bottom_layer)
        via.SetNetCode(net)
        return via
