import position_mapping
import pcbnew

pcb: pcbnew.BOARD = pcbnew.GetBoard()
pos_mapper = position_mapping.LEDPositions850()


def get_anode_pin(row, col):
    diode_id: int = pos_mapper.led_id(row, col)
    diode_footprint: pcbnew.FOOTPRINT = pcb.FindFootprintByReference(f'D{diode_id}')
    anode_pad: pcbnew.PAD = diode_footprint.FindPadByNumber(1)
    net_name: str = anode_pad.GetDisplayNetname()
    print(f'LED at {row=}, {col=}, has anode (pad 1) in net: {net_name}')
    return int(net_name[1:]) # ('P1' --> 1)

def get_cathode_pin(row, col):
    diode_id: int = pos_mapper.led_id(row, col)
    diode_footprint: pcbnew.FOOTPRINT = pcb.FindFootprintByReference(f'D{diode_id}')
    cathode_pad: pcbnew.PAD = diode_footprint.FindPadByNumber(2)
    net_name: str = cathode_pad.GetDisplayNetname()
    print(f'LED at {row=}, {col=}, has cathode (pad 2) in net: {net_name}')
    return int(net_name[1:])  # ('P1' --> 1)

def get_anode_array() -> list[list[int]]:
    """Returns a 2D array indexed by [row][col] which returns the anode (pin to set LOW) for the LED at (row, col)"""
    anode_array = []
    for row_idx in range(12):
        row = row_idx + 1

        row_array = []
        for col_idx in range(46):
            col = col_idx + 1

            if row == 12 and col > 23:
                row_array.append(-1)  # no diode exists in last half-row
                continue

            row_array.append(get_anode_pin(row, col))
        anode_array.append(row_array)
    return anode_array

def get_cathode_array() -> list[list[int]]:
    """Returns a 2D array indexed by [row][col] which returns the cathode (pin to set HI) for the LED at (row, col)"""
    cathode_array = []
    for row_idx in range(12):
        row = row_idx + 1

        row_array = []
        for col_idx in range(46):
            col = col_idx + 1

            if row == 12 and col > 23:
                row_array.append(-1)  # no diode exists in last half-row
                continue

            row_array.append(get_cathode_pin(row, col))
        cathode_array.append(row_array)
    return cathode_array