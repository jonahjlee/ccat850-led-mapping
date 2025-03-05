# ============================================================================ #
# position_mapping.py
#
# Jonah Lee
# CCAT Prime 2025
#
# Functions to map between LED 'refdes' references, pin logic states
# and LED positions (row/column, or positions in um).
# NOTE: Pin indices start at 0 -- i.e. a 24 pin connector has pins 0-23, inclusive.
#       This fact may conflict with KiCAD PCB/Schematic designs
# ============================================================================ #

from connector_state import ConnectorState, TriState

def get_() -> None:
    raise NotImplementedError  # TODO

if __name__ == "__main__":
    cs = ConnectorState(hi=[2, 3, -1], lo=4)
