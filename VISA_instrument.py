import numpy as np 
import pyvisa
import time
import decorator
from adapters import PrologixAdapter


class VISAInstrument():
    def __init__(self):
        self.query_delay = 0.1
        self.rm = pyvisa.ResourceManager()

    def connect(self, address):
        self.instrument = self.rm.open_resource(address, open_timeout=2, read_termination='\n')
        self.instrument.query_delay = self.query_delay
        print(f"Successfully connected to signal generator with address {address}")

    def list_connections(self, verbose=False):
        if verbose:
            print(self.rm.list_resources_info())
        else:
            print(self.rm.list_resources())
        return self.rm.list_resources()

    def write_SCPI(self, command: str):
        print(command)
        self.instrument.write(command)
        #error = self.check_errors()

    def query_SCPI(self, query: str):
        query = self.instrument.ask(query)
        #error = self.check_errors()
        return query

    def write_lines(self, lines):
        for line in lines:
            self.write_SCPI(line)
            time.sleep(0.1)

    def close_device(self):
        self.instrument.clear()
        self.instrument.close()

    def check_errors(self):
        #TODO: implement return error handling
        error = self.query_SCPI("SYSTEM:ERROR?")
        if error != "+0, No error":
            print(f"Error Returned: {error}")
        return error
    

class PrologixInstrument(VISAInstrument):
    def connect(self, address):
        self.instrument = PrologixAdapter(address, self.gpib_address, serial_timeout=1000) # open_timeout=2, read_termination='\n', resource_pyclass=Prologix
        self.instrument.query_delay = self.query_delay
        #self.instrument.configure(vna_gpib_address=self.gpib_address)
        print(f"Successfully connected to signal generator with address {address}")

    def query_SCPI(self, query: str):
        self.instrument.write(query)
        time.sleep(self.query_delay)
        query = self.instrument.read()
        #error = self.check_errors()
        return query