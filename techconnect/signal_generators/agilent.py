import numpy as np 
from base._instrument import VISAInstrument, PrologixInstrument


class Agilent33250A(PrologixInstrument):
    def __init__(self, gpib_address):
        super().__init__()
        self.query_delay = 0.1
        self.gpib_address = gpib_address

    def query_apply(self):
        query = self.query_SCPI("APPLY?")
        print(f"Signal Generator setup {query}")
        return query
    
    def turnOn(self):
        self.write_SCPI("OUTPUT ON")

    def turnOff(self):
        self.write_SCPI("OUTPUT OFF")

    def setupSine(self, frequency, amplitude_pp, offset=0, phase=0):
        return self.setupFunc("SIN", frequency, amplitude_pp, offset, phase)

    def setupFunc(self, func: str, frequency, amplitude_pp, offset=0, phase=0):
        lines = (f"FUNC {func.upper()}",
                    f"FREQ {float(frequency)}",
                    f"VOLT {float(amplitude_pp)}",
                    f"VOLT:OFFSET {float(offset)}",
                    f"PHASE {float(phase)}",
                )

        self.write_lines(lines)
        return self.query_apply()