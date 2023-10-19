"""
Rigol
--------
This module contains the instrument classes for Rigol oscilloscopes. It uses the methods created in the base class for the data parsing and saving,
but the communication is handled by the methods defined here.
"""
import os
import time

import numpy as np 
import pickle as pkl

from techconnect.base._instrument import VISAInstrument
import techconnect.tools.file_handling as file_handling
from techconnect.oscilloscopes._ossc_base import Oscilloscope 

class RigolDS4000(Oscilloscope):
    """
    Class representing the Rigol DS4000 oscilloscope.
    """

    def __init__(self):
        super().__init__()
        self.query_delay = 0.5

    def get_acq_type(self):
        acq_type = self.query_SCPI(f":ACQUIRE:TYPE?")
        if acq_type == 'NORM':
            return 0
        elif acq_type == 'AVER':
            return 1
        elif acq_type == 'PEAK':
            return 2
        elif acq_type == 'HRES':
            return 3
        else:
            raise ValueError(f"Oscilloscope returned unexpected :ACQUIRE:TYPE?: {acq_type}")

    def retrieve_channel_info(self, channel):
        channel_info = self.query_SCPI(f":WAVEFORM:SOURCE CHAN{channel};:WAVEFORM:PREAMBLE?").split(',')
        return {
            'format': int(channel_info[0]),
            'mode': int(channel_info[1]),
            'type': int(self.get_acq_type()),
            'points': int(float(channel_info[2])),
            'count': int(channel_info[3]),
            'xincrement': float(channel_info[4]),
            'xorigin': float(channel_info[5]),
            'xreference': float(channel_info[6]),
            'yincrement': float(channel_info[7]),
            'yorigin': float(channel_info[8]),
            'yreference': float(channel_info[9])
        }
    
    def auto_scale(self):
        """
        Automatically sets up the instrument by sending the SCPI command ":AUTOSCALE".
        """
        self.write_SCPI(f":AUTOSCALE")

    def single_acquisition(self):
        """
        Sends a command to the SCPI instrument to perform a single acquisition.
        """
        self.write_SCPI(f":SINGLE")

    def force_trigger(self):
        """
        Sends a command to the SCPI instrument to force a trigger.
        """
        self.write_SCPI(f":TFORCE")

    def data_export_setup(self, channel):
        """
        Set up the data export for a specific channel.

        Parameters
        ----------
        channel : int
            The channel number.

        Returns
        -------
        None
            This function does not return anything.
        """
        lines = (
            f":WAVEFORM:SOURCE {channel}",
            f":WAVEFORM:FORMAT BYTE",
            f":WAVEFORM:MODE NORM"
        )

        self.write_lines(lines)

    def read_data(self, delay:float, channel:int):
        return self.instrument.query_binary_values(f":WAVEFORM:SOURCE {channel};WAVEFORM:DATA?", delay=delay)
    
    def set_acq_type(self, acq_type:str):
        self.write_SCPI(f":ACQUIRE:TYPE {acq_type}")
