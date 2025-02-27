from led_placer import LedPlacer

# FIXME - make placers 'smart' so that they behave differently & place in correct locations
p1 = LedPlacer(1)
p2 = LedPlacer(2)
p3 = LedPlacer(3)
p4 = LedPlacer(4)

placers = [p1, p2, p3, p4]

def wait_for_input(msg="Press enter to continue..."):
    user_input = input(msg)

if __name__ == "__main__":

    # =====================================================
    # FRONT LAYER
    # =====================================================

    # Place LEDs
    for p in placers:
        p.place_leds()

    # Place & route pad 2 vias
    # for p in placers:
    #     p.place_pad2_vias()

    # Route front rows
    # for p in placers:
    #     wait_for_input(f"Route rows for network {p.network}, then press enter...")

    # Short front pins
    # for p in placers:
    #     wait_for_input(f"Short front pins for network {p.network}, then press enter...")

    # =====================================================
    # BACK LAYER
    # =====================================================

    # Route back columns
    # for p in placers:
        # p.route_columns()
        # wait_for_input(f"Route back columns for network {p.network}, then press enter...")

    # Stitch diagonals
    # for p in placers:
    #     wait_for_input(f"Stitch back diagonals for network {p.network}, then press enter...")

    # =====================================================
    # INNER LAYERS
    # =====================================================

    # Inner layer 1 - stitch rectangles
    # Inner layer 2 - stitch rectangles

    # =====================================================
    # CONNECTOR
    # =====================================================

    # Add & route connector vias
    # Route pins on front layer
    # Route pins on inner layer 1

    # =====================================================
    # MISC
    # =====================================================

    # Route bottom row
    # Left side - route to existing connector via
    # Right side - add new via and route on inner layer 2
