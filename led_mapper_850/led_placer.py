# ============================================================================ #
# led_placer.py
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

class LedPlacer:

    def __init__(self, network: int, pcb: pcbnew.BOARD=active_pcb):

        valid_networks = {1, 2, 3, 4}
        assert network in valid_networks, f"network must be one of: {valid_networks}"
        self.network = network  # charlieplexed network id

        self.pcb = pcb

        self.layertable: dict[str, int] = self.get_layertable()
        self.front_copper_layer: int = self.layertable['F.Cu']
        self.inner_layer_1 = self.layertable['In1.Cu']
        self.inner_layer_2 = self.layertable['In2.Cu']
        self.back_copper_layer: int = self.layertable['B.Cu']

        # constants based on led_mapper_850.kicad_sch
        # rows and columns refer to position on pcb, not in schematic,
        # though the schematic is on the same grid except discontinuities where diagonals are missing
        # for example, D69 is in column 23 and not column 24
        self.num_rows = 12  # actual num rows is 11.5; last row contains only 23 LEDs
        self.num_cols = 46

        # constants based on pixel_loc_analysis.xlsx
        # LEDs lie on a hexagonal grid composed of equilateral triangles with side length equal to self.spacing_um
        self.spacing_um = 1400.0
        # below are magnitudes only, directions change for different networks
        self.row_shift_um = self.spacing_um / 2
        self.col_width_um = self.spacing_um
        self.row_height_um = (  self.spacing_um ** 2 - self.row_shift_um ** 2) ** 0.5

        self.reference_led, self.leds, self.reference_x_um, self.reference_y_um = self.get_leds()

        self.via_width_nm = int(0.6 * 10 ** 6)
        self.via_drill_nm = int(0.3 * 10 ** 6)
        self.via_type = pcbnew.VIATYPE_THROUGH
        self.via_offset_um = 12  # Adjustment to center via vertically between rows. I don't know why this is needed.
        self.track_width_nm = int(0.2*10**6)

        self.connector_ref = f'J{self.network}'
        self.connector_via_dist_um = 3000

        self.pad2_vias: dict[str, pcbnew.PCB_VIA] = {}  # map from led fp reference to pad 2 via

    # =====================================================
    # PLACEMENT METHODS - MODIFY THE PCB
    # =====================================================

    def place_leds(self) -> None:
        """Place LEDs in a 46x11.5 hexagonal grid"""
        for row_idx in range(self.num_rows):
            row = row_idx + 1
            for col_idx in range(self.num_cols):
                col = col_idx + 1

                # last row is half full
                if row == self.num_rows and col > self.num_cols // 2: continue

                ref = self.led_ref(row, col)
                fp: pcbnew.FOOTPRINT = self.pcb.FindFootprintByReference(ref)
                assert fp is not None, f"footprint with refdes: '{ref}' not found!"

                if ref == self.reference_led:
                    x_um = self.reference_x_um
                    y_um = self.reference_y_um
                else:
                    if self.network in (1, 3):
                        x_um = self.reference_x_um + col_idx * self.col_width_um - row_idx * self.row_shift_um
                        y_um = self.reference_y_um + row_idx * self.row_height_um
                    else:
                        x_um = self.reference_x_um - col_idx * self.col_width_um + row_idx * self.row_shift_um
                        y_um = self.reference_y_um - row_idx * self.row_height_um

                self.set_microns(fp, x_um, y_um)
                orientation_deg = 60
                fp.SetOrientationDegrees(orientation_deg)
        pcbnew.Refresh()

    def route_rows(self) -> None:
        """Route tracks for horizontal rows for LED pad 1"""
        for row_idx in range(self.num_rows):
            row = row_idx + 1
            track1_start = self.led_footprint(row, 1).FindPadByNumber(1)
            track1_end = self.led_footprint(row, 23).FindPadByNumber(1)
            self.add_track_between_items(track1_start, track1_end)
            if row != 12:
                track2_start = self.led_footprint(row, 24).FindPadByNumber(1)
                track2_end = self.led_footprint(row, 46).FindPadByNumber(1)
                self.add_track_between_items(track2_start, track2_end)
        pcbnew.Refresh()

    def place_pad2_vias(self, place_tracks=True) -> None:
        """Place vias and connect them with tracks to each LED pad 2 (cathode)"""
        # place a via for each LED pad 2
        for fp in self.leds:
            pad1: pcbnew.PAD = fp.FindPadByNumber(2)
            net: int = pad1.GetNetCode()
            # vector from footprint centre to via center, before rotation
            x_offset = self.spacing_um / 2  # point to positive x (to the right), since this is for pad 2
            y_offset = self.row_height_um / 2 - self.via_offset_um
            # Apply clockwise rotation transformation matrix. It looks like counter-clockwise rotation,
            # but since positive y is downwards, the plane is flipped.
            rotate_angle = 60
            rot_x_offset =  cos(radians(rotate_angle)) * x_offset + sin(radians(rotate_angle)) * y_offset
            rot_y_offset = -sin(radians(rotate_angle)) * x_offset + cos(radians(rotate_angle)) * y_offset
            # add via
            via: pcbnew.PCB_VIA = self.place_new_via(
                fp.GetPosition().x / 1000 + rot_x_offset,
                fp.GetPosition().y / 1000 + rot_y_offset,
                net
            )
            # add track
            if place_tracks: self.add_track_between_items(pad1, via)
            self.pad2_vias[fp.GetReference()] = via
        pcbnew.Refresh()

    def route_columns(self) -> None:
        """Route tracks for vertical columns across for LED pad 2 (cathode)"""
        for col_idx in range(self.num_cols):
            col = col_idx + 1

            if (1 <= col <= 12 or 35 <= col <= 46) and self.network == 1:
                # left & right rectangular sections -- simply route all the way down
                # since they go across ALL networks, only route from network 1
                start_row = 1
                end_row = 12 if col <= 23 else 11
                start_via: pcbnew.PCB_VIA = self.get_pad2_via(start_row, col)
                path_across_all: pcbnew.VECTOR2I = self.vector2i_um(-45 * self.row_shift_um, 45 * self.row_height_um)
                self.route_segmented_track(
                    start_via.GetCenter(),
                    [path_across_all],
                    self.back_copper_layer
                )
            if 13 <= col <= 22:
                # triangle top left half
                start_row = 1
                end_row = 24 - col  # as we go to the right, we end further up
                start_via: pcbnew.PCB_VIA = self.get_pad2_via(start_row, col)
                end_via: pcbnew.PCB_VIA = self.get_pad2_via(end_row, col)
                self.add_track_between_items(start_via, end_via, layer=self.back_copper_layer)
            if 14 <= col <= 23:
                # triangle section 1 bottom left half
                start_row = 25 - col  # as we go to the right, we start further up
                end_row = 12  # left half has full height
                start_via: pcbnew.PCB_VIA = self.get_pad2_via(start_row, col)
                end_via: pcbnew.PCB_VIA = self.get_pad2_via(end_row, col)
                self.add_track_between_items(start_via, end_via, layer=self.back_copper_layer)
            if 24 <= col <= 33:
                # triangle top right half
                start_row = 1
                end_row = 35 - col  # as we go to the right, we end further up
                start_via: pcbnew.PCB_VIA = self.get_pad2_via(start_row, col)
                end_via: pcbnew.PCB_VIA = self.get_pad2_via(end_row, col)
                self.add_track_between_items(start_via, end_via, layer=self.back_copper_layer)
            if 26 <= col <= 34:
                # triangle section 1 bottom right half
                start_row = 36 - col  # as we go to the right, we start further up
                end_row = 11  # left half has full height
                start_via: pcbnew.PCB_VIA = self.get_pad2_via(start_row, col)
                end_via: pcbnew.PCB_VIA = self.get_pad2_via(end_row, col)
                self.add_track_between_items(start_via, end_via, layer=self.back_copper_layer)
        pcbnew.Refresh()

    def stitch_columns(self) -> None:

        def stitch_diagonal(start_via: pcbnew.PCB_VIA):
            """Weave a track to connect vias on the back layer on the diagonal.

            Shape illustrated (roughly):
               /-
              /
            -/
            """

            track_start = start_via.GetCenter()
            direction = 1 if self.network in (1, 3) else -1

            self.route_segmented_track(
                track_start,
                [
                    self.vector2i_um(self.col_width_um / 2, 0) * direction,
                    self.vector2i_um(self.col_width_um, -2 * self.row_height_um) * direction,
                    self.vector2i_um(self.col_width_um / 2, 0) * direction
                ],
                layer=self.back_copper_layer
            )

        # stitch diagonals
        for col in range (13, 22 + 1):
            row = 25 - col
            start_via: pcbnew.PCB_VIA = self.get_pad2_via(row, col)
            stitch_diagonal(start_via)
        for col in range (25, 33 + 1):
            row = 36 - col
            start_via: pcbnew.PCB_VIA = self.get_pad2_via(row, col)
            stitch_diagonal(start_via)

        # stitch between networks
        down_and_right: pcbnew.VECTOR2I = self.vector2i_um(self.row_shift_um, self.row_height_um)
        down_and_left: pcbnew.VECTOR2I = self.vector2i_um(-self.row_shift_um, self.row_height_um)
        around_to_the_right: list[pcbnew.VECTOR2I] = [
            self.vector2i_um(self.row_shift_um / 2, self.row_height_um / 2),
            self.vector2i_um(-self.row_shift_um * 1.5, self.row_height_um * 1.5),
            self.vector2i_um(-self.col_width_um / 2, 0)
        ]
        around_to_the_left: list[pcbnew.VECTOR2I] = [
            self.vector2i_um(-self.row_shift_um / 2, 0),
            self.vector2i_um(-self.row_shift_um * 1.5, self.row_height_um * 1.5),
            self.vector2i_um(self.row_shift_um / 2, self.row_height_um / 2)
        ]
        if self.network in (1, 3):
            self.route_segmented_track(self.get_pad2_via(11, 13).GetCenter(), around_to_the_left, self.back_copper_layer)
            for col in range(13, 21 + 1):
                self.route_segmented_track(self.get_pad2_via(12, col).GetCenter(), [down_and_right], self.back_copper_layer)
            self.route_segmented_track(self.get_pad2_via(12, 22).GetCenter(), around_to_the_right, self.back_copper_layer)
            self.route_segmented_track(self.get_pad2_via(12, 23).GetCenter(), [down_and_left], self.back_copper_layer)
            for col in range(32, 33 + 1):
                self.route_segmented_track(self.get_pad2_via(11, col).GetCenter(), [down_and_right], self.back_copper_layer)
            self.route_segmented_track(self.get_pad2_via(11, 34).GetCenter(), around_to_the_right, self.back_copper_layer)
        elif self.network == 2:
            # since we are going in between, no need to route from net 4
            self.route_segmented_track(self.get_pad2_via(2, 34).GetCenter(), around_to_the_left, self.back_copper_layer)
            for col in range(25, 34 + 1):
                self.route_segmented_track(self.get_pad2_via(1, col).GetCenter(), [down_and_right], self.back_copper_layer)
            self.route_segmented_track(self.get_pad2_via(1, 24).GetCenter(), around_to_the_right, self.back_copper_layer)
            for col in range(14, 15 + 1):
                self.route_segmented_track(self.get_pad2_via(1, col).GetCenter(), [down_and_right], self.back_copper_layer)
            self.route_segmented_track(self.get_pad2_via(1, 13).GetCenter(), around_to_the_right, self.back_copper_layer)

        pcbnew.Refresh()

    def short_front_rows(self) -> None:
        """Short rows on the front layer as appropriate to join pin rows/cols."""
        start_padnum = 2 if self.network in (1, 3) else 1
        end_padnum = 1 if self.network in (1, 3) else 2
        for col in range(13, 23 + 1):
            row = 25 - col
            start_pad = self.led_footprint(row, col).FindPadByNumber(start_padnum)
            end_pad = self.led_footprint(row - 1, col).FindPadByNumber(end_padnum)
            self.add_track_between_items(start_pad, end_pad, layer=self.front_copper_layer)
        for col in range(25, 34 + 1):
            row = 36 - col
            start_pad = self.led_footprint(row, col).FindPadByNumber(start_padnum)
            end_pad = self.led_footprint(row - 1, col).FindPadByNumber(end_padnum)
            self.add_track_between_items(start_pad, end_pad, layer=self.front_copper_layer)

        pcbnew.Refresh()

    def place_connector_vias(self) -> None:
        """Route each pad on the connector to a nearby via.

        Since Networks need to be tiled tightly, it is easiest to put tracks
        to the connector on the two sparsely-populated inner layers.
        """
        j1_fp: pcbnew.FOOTPRINT = self.pcb.FindFootprintByReference(self.connector_ref)
        orientation_deg: float = j1_fp.GetOrientationDegrees()
        for padnum in range(1, 13):
            # pad 1-12, left side
            pad: pcbnew.PAD = j1_fp.FindPadByNumber(padnum)
            track_vec: pcbnew.VECTOR2I = self.vector2i_um(
                -self.connector_via_dist_um * cos(radians(orientation_deg)),
                self.connector_via_dist_um * sin(radians(orientation_deg))
            )
            via_pos: pcbnew.VECTOR2I = pad.GetCenter() + track_vec
            via: pcbnew.PCB_VIA = self.place_new_via(via_pos.x / 1000, via_pos.y / 1000, pad.GetNetCode())
            self.add_track_between_items(pad, via, layer=self.back_copper_layer)
        for padnum in range(13, 25):
            # pad 13-24, left side
            pad: pcbnew.PAD = j1_fp.FindPadByNumber(padnum)
            track_vec: pcbnew.VECTOR2I = self.vector2i_um(
                self.connector_via_dist_um * cos(radians(orientation_deg)),
                -self.connector_via_dist_um * sin(radians(orientation_deg))
            )
            via_pos: pcbnew.VECTOR2I = pad.GetCenter() + track_vec
            via: pcbnew.PCB_VIA = self.place_new_via(via_pos.x / 1000, via_pos.y / 1000, pad.GetNetCode())
            self.add_track_between_items(pad, via, layer=self.back_copper_layer)
        pcbnew.Refresh()

    def connect_sections_in1(self) -> None:
        if self.network in (1, 3):
            track_args = [
                (1,  1,  24, self.inner_layer_1, False),
                (2,  2,  25, self.inner_layer_1, False),
                (3,  3,  26, self.inner_layer_1, False),
                (4,  4,  27, self.inner_layer_1, False),
                (5,  5,  28, self.inner_layer_1, False),
                (6,  6,  29, self.inner_layer_1, False),
                (7,  7,  29, self.inner_layer_1, False),
                (8,  8,  30, self.inner_layer_1, False),
                (9,  9,  31, self.inner_layer_1, False),
                (10, 10, 32, self.inner_layer_1, False),
                (11, 11, 33, self.inner_layer_1, False),
                (11, 12, 34, self.inner_layer_1, True),
            ]
        else:
            track_args = [
                # (1,  13, 35, self.inner_layer_1, True), insufficient space
                (2,  14, 36, self.inner_layer_1, True),
                (3,  15, 37, self.inner_layer_1, True),
                (4,  16, 38, self.inner_layer_1, True),
                (5,  17, 39, self.inner_layer_1, True),
                (6,  18, 40, self.inner_layer_1, True),
                (7,  18, 41, self.inner_layer_1, True),
                (7,  19, 42, self.inner_layer_1, False),
                (8,  20, 43, self.inner_layer_1, False),
                (9,  21, 44, self.inner_layer_1, False),
                (10, 22, 45, self.inner_layer_1, False),
                (11, 23, 46, self.inner_layer_1, False),
            ]
        for args in track_args:
            self.add_track_around_vias(*args)
        pcbnew.Refresh()

    def connect_sections_in2(self) -> None:
        # dict indexed by row
        # values are in the form (row:int, col1:int, col2:int, layer:int,route_below:bool)
        if self.network in (1, 3):
            track_args = [
                (2,  14, 36, self.inner_layer_2, False),
                (3,  15, 37, self.inner_layer_2, False),
                (4,  16, 38, self.inner_layer_2, False),
                (5,  17, 39, self.inner_layer_2, False),
                (5,  19, 41, self.inner_layer_2, True),
                (6,  18, 40, self.inner_layer_2, True),
                (7,  19, 42, self.inner_layer_2, True),
                (8,  20, 43, self.inner_layer_2, True),
                (9,  21, 44, self.inner_layer_2, True),
                (10, 22, 45, self.inner_layer_2, True),
                (11, 23, 46, self.inner_layer_2, True),
            ]
        else:
            track_args = [
                (1,  1,  24, self.inner_layer_2, True),
                (2,  2,  25, self.inner_layer_2, True),
                (3,  3,  26, self.inner_layer_2, True),
                (4,  4,  27, self.inner_layer_2, True),
                (5,  5,  28, self.inner_layer_2, True),
                (6,  6,  29, self.inner_layer_2, True),
                (7,  7,  29, self.inner_layer_2, True),
                (8,  8,  30, self.inner_layer_2, True),
                (9,  9,  31, self.inner_layer_2, True),
                (10, 10, 32, self.inner_layer_2, True),
                (11, 11, 33, self.inner_layer_2, True),
                (11, 12, 34, self.inner_layer_2, False),
            ]
        for args in track_args:
            self.add_track_around_vias(*args)
        pcbnew.Refresh()

    # =====================================================
    # HELPER METHODS
    # =====================================================

    def add_track_around_vias(self, row: int, col1: int, col2: int, layer: int, route_below: bool=False) -> None:
        """Create a horizontal track that joins vias on the same row.

        Shape illustrated (roughly) for route_below. If route_below==False, it is mirrored vertically.
         \__________/
        """
        via_1 = self.get_pad2_via(row, col1)
        via_2 = self.get_pad2_via(row, col2)
        if via_1.GetCenter().x > via_2.GetCenter().x:
            right_via = via_1
            left_via = via_2
        else:
            right_via = via_2
            left_via = via_1

        direction: int = 1 if route_below else -1
        track_start = left_via.GetCenter()
        left_x_um = float(left_via.GetCenter().x / 1000)
        right_x_um = float(right_via.GetCenter().x / 1000)
        try:
            self.route_segmented_track(
                track_start,
                [
                    self.vector2i_um(self.col_width_um / 4, self.row_height_um / 2 * direction),
                    self.vector2i_um(right_x_um - left_x_um - self.col_width_um / 2, 0),
                    self.vector2i_um(self.col_width_um / 4, self.row_height_um / 2 * -direction)
                ],
                layer=layer
            )
        except OverflowError:
            print('something went wrong...')
            print(f'{right_x_um=}')
            print(f'{left_x_um=}')
            print(f'{right_x_um - left_x_um - self.col_width_um / 2=}')

    def route_segmented_track(self, start_loc: pcbnew.VECTOR2I, segments: list[pcbnew.VECTOR2I], layer=None) -> None:
        prev_loc: pcbnew.VECTOR2I = start_loc
        assert isinstance(segments, list), f"segments '{segments}' must be a list!"
        for vec in segments:
            assert isinstance(vec, pcbnew.VECTOR2I), f"Elements of segments must be VECTOR2Is! {vec=}"
            self.add_track_between_positions(prev_loc, prev_loc + vec, layer=layer)
            prev_loc += vec

    def add_track_between_items(self, start_item: pcbnew.BOARD_ITEM, end_item: pcbnew.BOARD_ITEM, layer=None) -> None:
        self.add_track_between_positions(start_item.GetCenter(), end_item.GetCenter(), layer=layer)

    def add_track_between_positions(self, start_pos: pcbnew.VECTOR2I, end_pos: pcbnew.VECTOR2I, layer=None) -> None:
        if layer is None: layer = self.front_copper_layer
        if start_pos == end_pos: return
        track: pcbnew.PCB_TRACK = pcbnew.PCB_TRACK(self.pcb)
        track.SetStart(start_pos)
        track.SetEnd(end_pos)
        track.SetWidth(self.track_width_nm)
        track.SetLayer(layer)
        self.pcb.Add(track)

    def place_new_via(self, x_um: float, y_um: float, net: int,
                      top_layer: int=None, bottom_layer: int=None) -> pcbnew.PCB_VIA:
        if top_layer is None: top_layer = self.front_copper_layer
        if bottom_layer is None: bottom_layer = self.back_copper_layer

        via = pcbnew.PCB_VIA(self.pcb)
        self.pcb.Add(via)
        self.set_microns(via, x_um, y_um)
        via.SetWidth(self.via_width_nm)
        via.SetDrill(self.via_drill_nm)
        via.SetViaType(self.via_type)
        via.SetLayerPair(top_layer, bottom_layer)
        via.SetNetCode(net)
        return via

    def get_pad2_via(self, row, col) -> pcbnew.PCB_VIA:
        assert len(self.pad2_vias) > 0, "this placer must run place_pad2_vias() before via refs can be obtained"
        return self.pad2_vias[self.led_footprint(row, col).GetReference()]

    def led_footprint(self, row: int, col: int) -> pcbnew.FOOTPRINT:
        return self.pcb.FindFootprintByReference(self.led_ref(row, col))

    def led_ref(self, row: int, col: int) -> str:
        """Get the refdes of an LED given its position in the grid.

        This method will break if the schematic is changed.

        :param int row: The row of the LED in the rectangular grid, from top (row 1) to bottom (row 12)
        :param int col: The column of the LED in the rectangular grid, from left (col 1) to right (col 46)
        :return int: LED refdes
        """
        network_offset = (self.network - 1) * 529
        return f'D{self.led_id(row, col) + network_offset}'

    def led_id(self, row: int, col: int) -> int:
        """Get the id of an LED given its position in the grid.

        This method will break if the schematic is changed.

        :param int row: The row of the LED in the rectangular grid, from top (row 1) to bottom (row 12)
        :param int col: The column of the LED in the rectangular grid, from left (col 1) to right (col 46)
        :return int: LED id
        """
        assert 1 <= row <= self.num_rows, f"row {row} is outside the grid!"
        assert 1 <= col <= self.num_cols, f"column {col} is outside the grid!"
        half_cols = self.num_cols // 2
        assert not (row == self.num_rows and col > half_cols), \
            f"final row (row {self.num_rows}) is only half-full, with LEDs from col 1 - {half_cols}!"

        row_idx = row - 1
        return row_idx * self.num_cols + col

    def set_microns(self, item: pcbnew.EDA_ITEM, x_um: float, y_um: float) -> None:
        item.SetPosition(self.vector2i_um(x_um, y_um))

    @staticmethod
    def vector2i_um(x_um: float, y_um: float) -> pcbnew.VECTOR2I:
        return pcbnew.VECTOR2I(int(x_um * 1000), int(y_um * 1000))

    def get_layertable(self) -> dict[str, int]:
        layertable: dict[str, int] = {}
        for i in range(1000):
            name = self.pcb.GetLayerName(i)
            if name != "BAD INDEX!":
                layertable[name] = i
        return layertable

    def get_leds(self) -> tuple[str, list[pcbnew.FOOTPRINT], float, float]:
        if self.network == 1:
            reference_led = 'D1'
            leds: list[pcbnew.FOOTPRINT] = [self.pcb.FindFootprintByReference(f'D{ref_id}') for ref_id in range(1, 530)]
            reference_x_um = 0.0
            reference_y_um = 0.0
        elif self.network == 2:
            reference_led = 'D530'
            leds: list[pcbnew.FOOTPRINT] = [self.pcb.FindFootprintByReference(f'D{ref_id}') for ref_id in range(530, 1059)]
            reference_x_um = 45 * self.col_width_um - 22 * self.row_shift_um
            reference_y_um = 22 * self.row_height_um
        elif self.network == 3:
            reference_led = 'D1059'
            leds: list[pcbnew.FOOTPRINT] = [self.pcb.FindFootprintByReference(f'D{ref_id}') for ref_id in range(1059, 1588)]
            reference_x_um = -23 * self.row_shift_um
            reference_y_um = 23 * self.row_height_um
        else:
            assert self.network == 4, "invalid network ID!"
            reference_led = 'D1588'
            leds: list[pcbnew.FOOTPRINT] = [self.pcb.FindFootprintByReference(f'D{ref_id}') for ref_id in range(1588, 2117)]
            reference_x_um = 45 * self.col_width_um - 45 * self.row_shift_um
            reference_y_um = 45 * self.row_height_um
        return reference_led, leds, reference_x_um, reference_y_um