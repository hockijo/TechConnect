import numpy as np 
from base._instrument import VISAInstrument, PrologixInstrument


class DG1000(VISAInstrument):
    def __init__(self):
        super().__init__()
        self.query_delay = 1

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
        

class DG4000(VISAInstrument):
    def __init__(self):
        super().__init__()
        self.query_delay = 0.1

    def query_apply(self):
        query = self.query_SCPI(":APPLY?")
        print(f"Signal Generator setup {query}")
        return query
    
    def turnOn(self, channel):
        self.write_SCPI(f":OUTPUT{channel} ON")

    def turnOff(self, channel):
        self.write_SCPI(f":OUPUT{channel} OFF")

    def setupSine(self, frequency, amplitude_pp, offset=0, phase=0, channel=1):
        return self.setupFunc("SIN", frequency, amplitude_pp, offset, phase, channel)

    def setupFunc(self, func: str, frequency, amplitude_pp, offset, phase, channel):
        lines = (f":SOURCE{channel}:FUNC {func.upper()}",
                    f":SOURCE{channel}:FREQ:FIXED: {float(frequency)}",
                    f":SOURCE{channel}:VOLT {float(amplitude_pp)}",
                    f":SOURCE{channel}:VOLT:OFFSET {float(offset)}",
                    f":SOURCE{channel}:PHASE {float(phase)}",
                )

        self.write_lines(lines)
        return self.query_apply()
    
    def setupSweep(self, start_frequency, stop_frequency, amplitude_pp, sweep_time, 
                   return_time=0, spacing='LINEAR', trigger_source='INTERNAL', channel=1):
        lines = (f":SOURCE{channel}:FUNC SWEEP",
                    f":SOURCE{channel}:FREQ:START {float(start_frequency)}",
                    f":SOURCE{channel}:FREQ:STOP {float(stop_frequency)}",
                    f":SOURCE{channel}:VOLT {float(amplitude_pp)}",
                    f":SOURCE{channel}:SWEEP:TIME {float(sweep_time)}",
                    f":SOURCE{channel}:SWEEP:RTIME {float(return_time)}",
                    f":SOURCE{channel}:SWEEP:SPACING {float(spacing)}",
                    f":SOURCE{channel}:SWEEP:TRIGGER:SOURCE {float(trigger_source)}",
                    f":SOURCE{channel}:SWEEP:STATE ON",
                )

        self.write_lines(lines)
        return self.query_apply()
    
    def setupAM(self, frequency, function, depth=100, channel=1):
        lines = (f":SOURCE{channel}:MOD:TYPE AM",
                    f":SOURCE{channel}:MOD:AM:INTERNAL:FUNC {function.upper()}",
                    f":SOURCE{channel}:MOD:AM:INTERNAL:FREQ: {float(frequency)}",
                    f":SOURCE{channel}:MOD:AM:DEPTH {float(depth)}",
                    f":SOURCE{channel}:MOD:STATE ON",
                )

        self.write_lines(lines)
        return self.query_apply()
    
    def setupRamp(self, frequency, amplitude_pp, offset=0, phase=0, channel=1, symmetry=50):
        self.write_SCPI(f"SOURCE{channel}:FUNC:RAMP:SYMMETRY:{symmetry}")
        return self.setupFunc("RAMP", frequency, amplitude_pp, offset, phase, channel)