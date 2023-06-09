import numpy as np 
from VISA_instrument import VISAInstrument, PrologixInstrument

class Agilent89410A(PrologixInstrument):
    def __init__(self):
        super().__init__()
        self.query_delay = 0.1
        self.instrument_type = "Agilent89410A Spectrum Analyser"
        self.initialise_device()

    def calibrate(self):
        lines = (
            "CALIBRATION:AUTO ONCE",
            "CALIBRATION:ZERO:AUTO ONCE",
            "CALIBRATION:AUTO ON",
            "CALIBRATION:ZERO:AUTO ON"
        )
        self.write_lines(lines)


