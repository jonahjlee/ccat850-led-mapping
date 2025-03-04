# ============================================================================ #
# position_mapping.py
#
# Jonah Lee
# CCAT Prime 2025
#
# Functions to map between LED 'refdes' references, pin logic states
# and LED positions (row/column, or positions in um.)
# ============================================================================ #

import enum

class TriState(enum.Enum):
    """Representation of a tri-state logic pin.
    
    See https://en.wikipedia.org/wiki/Three-state_logic for more
    """
    HIGH = 1
    LOW = 0
    HI_Z = -1


class ConnectorState:
    """Object representing a tri-state logic connector state."""
    def __init__(self, pin_state_list: list[TriState]=None, pin_count: int=24):

        if pin_state_list is None:
            pin_state_list = [TriState.HI_Z for pin in range(pin_count)]
        
        assert len(pin_state_list) == pin_count, "pin_state_list must have length equal to pin_count!"
        self.pin_state_list = pin_state_list

