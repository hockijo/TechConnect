"""
Agilent
========
This module contains the instrument classes for Agilent signal generators.
"""

import numpy as np 
from techconnect.base._instrument import VISAInstrument, PrologixInstrument


class Agilent33250A(PrologixInstrument):
    """
    Class representing the Agilent 33250A signal generator.

    Parameters
    ----------
    gpib_address : int
        The GPIB address of the signal generator.

    Attributes
    ----------
    query_delay : float
        The delay time (in seconds) for SCPI query commands.
    gpib_address : int
        The GPIB address of the signal generator.

    Methods
    -------
    query_apply()
        Query the applied settings on the signal generator.
    turnOn()
        Turn on the output of the signal generator.
    turnOff()
        Turn off the output of the signal generator.
    setupSine(frequency, amplitude_pp, offset=0, phase=0)
        Set up the signal generator to produce a sine wave.
    setupFunc(func, frequency, amplitude_pp, offset=0, phase=0)
        Set up the signal generator to produce a user-defined function waveform.
    """
    def __init__(self, gpib_address):
        super().__init__()
        self.query_delay = 0.1
        self.gpib_address = gpib_address

    def _check_channel(channel):
         if channel is not 1:
            raise ValueError("There is only one channel for this instrument")

    def query_apply(self):
        """
        Retrieves the current signal generator configuration by sending the SCPI command "APPLY?".

        Returns
        -------
        str
            The response from the signal generator containing the current configuration.
        """
        query = self.query_SCPI("APPLY?")
        print(f"Signal Generator setup {query}")
        return query
    
    def turnOn(self, channel=1):
        """
        Turns on the device.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self._check_channel(channel)
        self.write_SCPI("OUTPUT ON")

    def turnOff(self, channel=1):
        """
        Turns off the device.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self._check_channel(channel)
        self.write_SCPI("OUTPUT OFF")

    def setupSine(self, frequency, amplitude_pp, offset=0, phase=0, channel=1):
        """
        Set up a sine wave function with the given parameters.

        Parameters
        ----------
        frequency : float
            The frequency of the sine wave.
        amplitude_pp : float
            The peak-to-peak amplitude of the sine wave.
        offset : float, optional
            The DC offset of the sine wave. Defaults to 0.
        phase : float, optional
            The phase offset of the sine wave. Defaults to 0.

        Returns
        -------
        str
            The applied sine wave settings.
        """
        self._check_channel(channel)
        return self.setupFunc("SIN", frequency, amplitude_pp, offset, phase)

    def setupFunc(self, func: str, frequency, amplitude_pp, offset=0, phase=0, channel=1):
        """
        Sets up a function on the instrument.

        Parameters
        ----------
        func : str
            The function to be set up.
        frequency : 
            The frequency of the function in Hz.
        amplitude_pp : 
            The peak-to-peak amplitude of the function in volts.
        offset : float, optional
            The DC offset of the function in volts. Defaults to 0.
        phase : float, optional
            The phase offset of the function in degrees. Defaults to 0.

        Returns
        -------
        str
            The applied settings.
        """
        self._check_channel(channel)

        lines = (f"FUNC {func.upper()}",
                    f"FREQ {float(frequency)}",
                    f"VOLT {float(amplitude_pp)}",
                    f"VOLT:OFFSET {float(offset)}",
                    f"PHASE {float(phase)}",
                )

        self.write_lines(lines)
        return self.query_apply()