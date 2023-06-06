import numpy as np 
import pyvisa
import os
import time
from VISA_instrument import VISAInstrument


class DG1000(VISAInstrument):
    def query_apply(self, channel):
        if channel == 1:
            query = self.query_SCPI(f"APPLY?")
        elif channel == 2:
            query = self.query_SCPI(f"APPLY:CH{channel}?")
        print(f"Signal Generator setup {query}")
        return query
    
    def turnOn(self, channel):
        if channel == 1:
            lines = ("OUTPUT ON",)
        if channel == 2:
            lines = ("OUTPUT:CH2 ON",)

        self.write_lines(lines)

    def turnOff(self, channel):
        if channel == 1:
            lines = ("OUTPUT OFF",)
        if channel == 2:
            lines = ("OUTPUT:CH2 OFF",)

        self.write_lines(lines)

    def setupSine(self, frequency, amplitude_pp, offset=0, phase=0, channel=1):
        self.setupFunc("SIN", frequency, amplitude_pp, offset, phase, channel=channel)

    def setupFunc(self, func: str, frequency, amplitude_pp, offset=0, phase=0, channel=1):
        if channel == 1:
            lines = (f"FUNC {func.upper()}",
                    f"FREQ {float(frequency)}",
                    f"VOLT {float(amplitude_pp)}",
                    f"VOLT:OFFSET {float(offset)}",
                    f"PHASE {float(phase)}",
                )
            
        elif channel == 2:
            lines = (f"FUNC:CH{channel} {func.upper()}",
                    f"FREQ:CH{channel} {float(frequency)}",
                    f"VOLT:CH{channel} {float(amplitude_pp)}",
                    f"VOLT:CH{channel}:OFFSET {float(offset)}",
                    f"PHASE:CH{channel} {float(phase)}",
                )

        self.write_lines(lines)
        _ = self.query_apply(channel)
    


""" class Agilent33250A(VISASignalGenerator):
    


class DG4000(VISASignalGenerator):
    def query_apply(self):
        return self.query_SCPI("APPLY?")
 """

dg1022u_address = r"USB0::0x0400::0x09C4::DG1G170900658::INSTR"
dg1022u = DG1000()
dg1022u.connect(dg1022u_address)

rm = pyvisa.ResourceManager()
my_instr = rm.open_resource(dg1022u_address)

print()