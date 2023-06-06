import numpy as np 
import pyvisa
import time

class VISAInstrument():
    def __init__(self):
        self.rm = pyvisa.ResourceManager()

    def connect(self, address):
        self.instrument = self.rm.open_resource(address, open_timeout=2, read_termination='\n')
        self.instrument.query_delay = 1
        print(f"Successfully connected to signal generator with address {address}")

    def list_connections(self, verbose=False):
        if verbose:
            print(self.rm.list_resources_info())
        else:
            print(self.rm.list_resources())

    def write_SCPI(self, command: str):
        print(command)
        self.instrument.write(command)
        error = self.check_errors()

    def query_SCPI(self, query: str):
        query = self.instrument.query(query)
        error = self.check_errors()
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
        error = self.query_SCPI(":SYSTEM:ERROR?")
        if error != "0, No error":
            print(f"Error Returned: {error}")
        return error