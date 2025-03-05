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

    def __init__(self, hi: int|list[int]=None, lo: int|list[int]=None, pin_count: int=24):

        self.pin_count = pin_count

        if hi is None: hi = []
        if lo is None: lo = []
        if isinstance(hi, int): hi = [hi]
        if isinstance(lo, int): lo = [lo]

        self._validate_input(hi, lo, pin_count)
        
        self.pin_states = [TriState.HI_Z for pin in range(pin_count)]
        for hi_pin in hi:
            self.set_pin(hi_pin, TriState.HIGH)
        for lo_pin in lo:
            self.set_pin(lo_pin, TriState.LOW)

    def _validate_input(self, hi: list[int], lo: list[int], pin_count: int) -> None:
        hi_and_lo: set = set(hi).intersection(lo)
        assert len(hi_and_lo) == 0, f"Pin(s) '{hi_and_lo}' cannot simultaneously be high and low."
        for idx in hi + lo:
            assert 0 <= idx < pin_count, f"Pin index '{idx}' must be between 0-{self.pin_count-1}, inclusive."
        
    def set_pin(self, index: int, value: TriState) -> bool:
        """Set the logic state of a pin. Returns true if the value was changed"""
        prev_val = self._pin_states[index]
        self._pin_states[index] = value
        return value != prev_val
    
    def set_all(self, value: TriState) -> None:
        """Set all pins' value to ``value``"""
        self._pin_states = [value for pin in range(self.pin_count)]

    def get_pin(self, index: int) -> TriState:
        """Get the value of pin at ``index``"""
        return self._pin_states[index]

    @property
    def pin_states(self) -> list[TriState]:
        """List representation of connector pin states"""
        return self._pin_states.copy()
    
    @pin_states.setter
    def pin_states(self, pin_states: list[TriState]) -> None:
        assert len(pin_states) == self.pin_count, "list ``pin_states`` must have length equal to ``self.pin_count``."
        self._pin_states = pin_states.copy()

    def __str__(self) -> str:
        pretty_dict = {idx:state.name for idx, state in enumerate(self._pin_states)}
        return str(pretty_dict)
