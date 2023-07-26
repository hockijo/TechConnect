"""
Rigol
-----
This module contains the instrument classes for rigol signal generators.
"""

import numpy as np 
from techconnect.base._instrument import VISAInstrument, PrologixInstrument


class DG1000(VISAInstrument):
    """
    Class representing the DG1000 signal generator.

    Parameters
    ----------
    None

    Attributes
    ----------
    query_delay : int
        The delay time (in seconds) for SCPI query commands.

    Methods
    -------
    query_apply(channel)
        Queries the signal generator for the current applied settings on the specified channel.
    turnOn(channel)
        Turns on the output for the specified channel.
    turnOff(channel)
        Turns off the output for the specified channel.
    setupSine(frequency, amplitude_pp, offset=0, phase=0, channel=1)
        Sets up the signal generator to produce a sine wave on the specified channel.
    setupFunc(func, frequency, amplitude_pp, offset=0, phase=0, channel=1)
        Sets up the signal generator to produce a user-defined function waveform on the specified channel.
    """

    def __init__(self):
        super().__init__()
        self.query_delay = 1

    def query_apply(self, channel):
        """
        Query applied settings to a specific channel.

        Parameters
        ----------
        channel : int
            The channel number.

        Returns
        -------
        str
            The query response.
        """

        if channel == 1:
            query = self.query_SCPI(f"APPLY?")
        elif channel == 2:
            query = self.query_SCPI(f"APPLY:CH{channel}?")
        print(f"Signal Generator setup {query}")
        return query
    
    def turnOn(self, channel):
        """
        Turn on the specified channel.

        Parameters
        ----------
        channel : int
            The channel to turn on. Must be either 1 or 2.

        Returns
        -------
        None
        """

        if channel == 1:
            lines = ("OUTPUT ON",)
        if channel == 2:
            lines = ("OUTPUT:CH2 ON",)

        self.write_lines(lines)

    def turnOff(self, channel):
        """
        Turns off the specified channel.

        Parameters
        ----------
        channel : int
            The channel number to turn off. Valid values are 1 and 2.

        Returns
        -------
        None
            This function does not return anything.
        """
        if channel == 1:
            lines = ("OUTPUT OFF",)
        if channel == 2:
            lines = ("OUTPUT:CH2 OFF",)

        self.write_lines(lines)

    def setupSine(self, frequency, amplitude_pp, offset=0, phase=0, channel=1):
        """
        Set up the sine wave generator with the specified parameters.

        Parameters
        ----------
        frequency : float
            The frequency of the sine wave in Hz.
        amplitude_pp : float
            The peak-to-peak amplitude of the sine wave in volts.
        offset : float, optional
            The DC offset of the sine wave in volts. Defaults to 0.
        phase : float, optional
            The phase of the sine wave in degrees. Defaults to 0.
        channel : int, optional
            The channel number. Defaults to 1.

        Returns
        -------
        None
        """

        self.setupFunc("SIN", frequency, amplitude_pp, offset, phase, channel=channel)

    def setupFunc(self, func: str, frequency, amplitude_pp, offset=0, phase=0, channel=1):
        """
        Set up the function parameters for generating a waveform on a specific channel of the instrument.

        Parameters
        ----------
        func : str
            The type of waveform to generate.
        frequency : float
            The frequency of the waveform in Hz.
        amplitude_pp : float
            The peak-to-peak amplitude of the waveform in volts.
        offset : float, optional
            The DC offset of the waveform in volts. Defaults to 0.
        phase : float, optional
            The phase shift of the waveform in degrees. Defaults to 0.
        channel : int, optional
            The channel number to generate the waveform on. Defaults to 1.

        Returns
        -------
        None
        """
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
    """
    Class representing the DG4000 signal generator.

    Parameters
    ----------
    None

    Attributes
    ----------
    query_delay : float
        The delay time (in seconds) for SCPI query commands.

    Methods
    -------
    query_apply()
        Query the applied settings on the signal generator.
    turnOn(channel)
        Turn on the output for the specified channel.
    turnOff(channel)
        Turn off the output for the specified channel.
    setupSine(frequency, amplitude_pp, offset=0, phase=0, channel=1)
        Set up the signal generator to produce a sine wave on the specified channel.
    setupFunc(func, frequency, amplitude_pp, offset=0, phase=0, channel=1)
        Set up the signal generator to produce a user-defined function waveform on the specified channel.
    setupSweep(start_frequency, stop_frequency, amplitude_pp, sweep_time, return_time=0, spacing='LINEAR', trigger_source='INTERNAL', channel=1)
        Set up the signal generator to produce a sweep waveform on the specified channel.
    setupAM(frequency, function, depth=100, channel=1)
        Set up the signal generator to produce an amplitude-modulated waveform on the specified channel.
    setupRamp(frequency, amplitude_pp, offset=0, phase=0, channel=1, symmetry=50)
        Set up the signal generator to produce a ramp waveform on the specified channel.
    """

    def __init__(self):
        super().__init__()
        self.query_delay = 0.1

    def query_apply(self):
        """
        Query applied settings to a specific channel.

        Parameters
        ----------
        channel : int
            The channel number.

        Returns
        -------
        str
            The query response.
        """
        query = self.query_SCPI(":APPLY?")
        print(f"Signal Generator setup {query}")
        return query
    
    def turnOn(self, channel):
        """
        Turn on the specified channel.

        Parameters
        ----------
        channel : int
            The channel to turn on. Must be either 1 or 2.

        Returns
        -------
        None
        """
        self.write_SCPI(f":OUTPUT{channel} ON")

    def turnOff(self, channel):
        """
        Turns off the specified channel.

        Parameters
        ----------
        channel : int
            The channel number to turn off. Valid values are 1 and 2.

        Returns
        -------
        None
            This function does not return anything.
        """
        self.write_SCPI(f":OUPUT{channel} OFF")

    def setupSine(self, frequency, amplitude_pp, offset=0, phase=0, channel=1):
        """
        Set up the sine wave generator with the specified parameters.

        Parameters
        ----------
        frequency : float
            The frequency of the sine wave in Hz.
        amplitude_pp : float
            The peak-to-peak amplitude of the sine wave in volts.
        offset : float, optional
            The DC offset of the sine wave in volts. Defaults to 0.
        phase : float, optional
            The phase of the sine wave in degrees. Defaults to 0.
        channel : int, optional
            The channel number. Defaults to 1.

        Returns
        -------
        str
            The applied sine wave settings.
        """
        return self.setupFunc("SIN", frequency, amplitude_pp, offset, phase, channel)

    def setupFunc(self, func: str, frequency, amplitude_pp, offset, phase, channel):
        """
        Set up the function parameters for generating a waveform on a specific channel of the instrument.

        Parameters
        ----------
        func : str
            The type of waveform to generate.
        frequency : float
            The frequency of the waveform in Hz.
        amplitude_pp : float
            The peak-to-peak amplitude of the waveform in volts.
        offset : float, optional
            The DC offset of the waveform in volts. Defaults to 0.
        phase : float, optional
            The phase shift of the waveform in degrees. Defaults to 0.
        channel : int, optional
            The channel number to generate the waveform on. Defaults to 1.

        Returns
        -------
        str
            The applied settings.
        """
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
        """
        Sets up a sweep on a specified channel of the instrument.

        Parameters
        ----------
        start_frequency : float
            The start frequency of the sweep.
        stop_frequency : float
            The stop frequency of the sweep.
        amplitude_pp : float
            The peak-to-peak amplitude of the sweep.
        sweep_time : float
            The duration of the sweep.
        return_time : float, optional
            The return time of the sweep. Defaults to 0.
        spacing : str, optional
            The spacing of the sweep. Defaults to 'LINEAR'.
        trigger_source : str, optional
            The trigger source of the sweep. Defaults to 'INTERNAL'.
        channel : int, optional
            The channel to set up the sweep on. Defaults to 1.

        Returns
        -------
        str
            The applied sweep settings.
        """

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
        """
        Sets up the amplitude modulation (AM) for a specific frequency, function, depth, and channel.

        Parameters
        ----------
        frequency : float
            The frequency of the AM signal.
        function : str
            The function used for the AM modulation.
        depth : float, optional
            The depth of the AM modulation. Defaults to 100%.
        channel : int, optional
            The channel number. Defaults to 1.

        Returns
        -------
        str
        The applied AM settings.
        """

        lines = (f":SOURCE{channel}:MOD:TYPE AM",
                    f":SOURCE{channel}:MOD:AM:INTERNAL:FUNC {function.upper()}",
                    f":SOURCE{channel}:MOD:AM:INTERNAL:FREQ: {float(frequency)}",
                    f":SOURCE{channel}:MOD:AM:DEPTH {float(depth)}",
                    f":SOURCE{channel}:MOD:STATE ON",
                )

        self.write_lines(lines)
        return self.query_apply()
    
    def setupRamp(self, frequency, amplitude_pp, offset=0, phase=0, channel=1, symmetry=50):
        """
        Set up a ramp waveform on the specified channel.

        Parameters
        ----------
        frequency : float
            The frequency of the ramp waveform in Hz.
        amplitude_pp : float
            The peak-to-peak amplitude of the ramp waveform in volts.
        offset : float, optional
            The DC offset of the ramp waveform in volts. Defaults to 0.
        phase : float, optional
            The phase offset of the ramp waveform in degrees. Defaults to 0.
        channel : int, optional
            The channel number to set up the ramp waveform on. Defaults to 1.
        symmetry : int, optional
            The symmetry percentage of the ramp waveform. Defaults to 50.

        Returns
        -------
        str
            The applied ramp settings.
        """
        self.write_SCPI(f"SOURCE{channel}:FUNC:RAMP:SYMMETRY:{symmetry}")
        return self.setupFunc("RAMP", frequency, amplitude_pp, offset, phase, channel)