"""
Module for the base classes of the instruments. Contain methods for communicating with instruments, and
the specific instrument classes inherit these methods
"""

import time
import numpy as np 
import pyvisa
from adapters.prologix import PrologixAdapter

__all__ = ['VISAInstrument', 'PrologixInstrument']

class VISAInstrument():
    """
    For instruments communicating via VISA (ie USB, ethernet, etc)

    Attributes:
    -----------
    instrument: pyvisa Resource
        the instrument connected
    query_delay: float
        delay in seconds
    
    Methods:
    --------
    connect(address)
        connects to an instrument
    list_connections(verbose=True)
        list connections available
    initialise_device()
        initialises the device by clearing any existing data
    write_SCPI(command)
        writes a command to the instrument
    query_SCPI(query)
        queries the instrument and returns query
    write_lines(lines)
        writes lines to the instrument
    close_device()
        clears and closes the instrument
    check_error()
        checks for and returns errors
    """
    def __init__(self):
        self.query_delay = 0.1
        self.rm = pyvisa.ResourceManager()

    def connect(self, address):
        """
        Connects to an instrument at the specified address.

        Parameters:
        -----------
        address: str
            The address of the instrument.

        Returns:
        --------
            None
        """
        self.instrument = self.rm.open_resource(address, open_timeout=2, read_termination='\n')
        self.instrument.query_delay = self.query_delay
        print(f"Successfully connected to instrument with address {address}")

    def initialise_device(self):
        """
        Initializes the device.

        This function is responsible for initializing the device. It clears any existing data on the instrument.

        Returns:
        --------
            None
        """
        self.instrument.clear()

    def list_connections(self, verbose=True):
        """
        List connections and print the resource information if verbose is True. Otherwise, print only the resource names.

        Parameters:
        -----------
        verbose: bool, optional
            Whether to print resource information. Defaults to True.

        Returns:
        --------
        list
            A list of resource names.
        """
        if verbose:
            print(self.rm.list_resources_info())
        else:
            print(self.rm.list_resources())
        return self.rm.list_resources()

    def write_SCPI(self, command: str):
        """
        Writes an SCPI command to the instrument.

        Parameters:
        -----------
        command: str
            The SCPI command to be written.

        Returns:
        --------
            None
        """
        print(command)
        self.instrument.write(command)
        #error = self.check_errors()

    def query_SCPI(self, query: str):
        """
        Execute a SCPI query command and return the response.

        Parameters:
        -----------
        query: str
            The SCPI query command to send to the instrument.

        Returns:
        --------
        str
            The response received from the instrument.

        """
        query = self.instrument.query(query)
        #error = self.check_errors()
        return query

    def write_lines(self, lines):
        """
        Writes a list of lines to the device.

        Parameters:
        -----------
        lines: list or tuple
            The list of lines to write.

        Returns:
        --------
            None
        """
        for line in lines:
            self.write_SCPI(line)
            time.sleep(0.1)

    def close_device(self):
        """
        Closes the device.

        This function clears the instrument and then closes the connection to the device.

        Returns:
        --------
            None
        """
        self.instrument.clear()
        self.instrument.close()

    def check_errors(self):
        """
        Check for errors by querying the SCPI and handling the returned error.

        Returns:
        --------
        str
            The error message returned by the SCPI query.
        """
        #TODO: implement return error handling
        error = self.query_SCPI("SYSTEM:ERROR?")
        if error != "+0, No error":
            print(f"Error Returned: {error}")
        return error
    

class PrologixInstrument(VISAInstrument):
    """
    For instruments communicating via Prologix GPIB adapter

    Attributes:
    -----------
    instrument: pyvisa Resource
        the instrument connected
    query_delay: float
        delay in seconds
    
    Methods:
    --------
    connect(address)
        connects to an instrument
    list_connections(verbose=True)
        list connections available
    initialise_device()
        initialises the device by clearing any existing data
    write_SCPI(command)
        writes a command to the instrument
    query_SCPI(query)
        queries the instrument and returns query
    write_lines(lines)
        writes lines to the instrument
    close_device()
        clears and closes the instrument
    check_error()
        checks for and returns errors
    """
    def connect(self, address):
        """
        Connects to an instrument at the specified address.

        Parameters:
        -----------
        address: str
            The address of the instrument to connect to.

        Returns:
        --------
            None
        """
        
        self.instrument = PrologixAdapter(address, self.gpib_address, timeout=1000) # open_timeout=2, read_termination='\n', resource_pyclass=Prologix
        self.instrument.query_delay = self.query_delay
        #self.instrument.configure(vna_gpib_address=self.gpib_address)
        print(f"Successfully connected to instrument with address {address}")

    def query_SCPI(self, query: str):
        """
        Send a query to the SCPI instrument and return the response.

        Parameters:
        -----------
        query: str
            The query to send to the instrument.

        Returns:
        --------
        str
            The response from the instrument.

        """
        self.instrument.write(query)
        time.sleep(self.query_delay)
        query = self.instrument.read().strip('\n')
        #error = self.check_errors()
        return query