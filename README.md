# ccat850-led-mapping
CAD files for CCAT 850GHz LED mapping array PCB &amp; peripherals

This project contains various cad files relating to hardware required to perform LED mapping for CCAT's 850GHz module.
This project includes the following directories:
- ``led_mapper_850``
  - The defining the PCB for one rhombus of the LED mapper array. Contains the KiCAD project and some Python programs used to automate the LED/via/track layout.
- ``multiplexer`` - NO LONGER USED
  - The cable splitter used between the Arduino shield and the mapper array. Splits the inputs into 13 parallel 24-pin connectors. Since the PCB has been updated to use a single connector, this is no longer relevant to the project.
- ``collimator``
  - SOLIDWORKS CAD files for the collimator, which mounts to the array and nests each LED such that light is funneled one-to-one with the feedhorns.


In addition, there is the collimator which is placed between the detectors and the LED array to funnel light & prevent cross-talk.
Its CAD model can be found in [this onshape project](https://cad.onshape.com/documents/4a9874995d3b4039a34f4491/w/a61d1c1f9ee3ea8193c6d7eb/e/afbea4677e4648f6492246a2).
