import numpy as np 
import pyvisa
import time

class VISAInstrument():
    def __init__(self):
        self.rm = pyvisa.ResourceManager()

    def connect(self, address):
        self.sig_gen = self.rm.open_resource(address, open_timeout=2, read_termination='\n')
        self.sig_gen.query_delay = 1
        print(f"Successfully connected to signal generator with address {address}")

    def list_connections(self, verbose=False):
        if verbose:
            print(self.rm.list_resources_info())
        else:
            print(self.rm.list_resources())

    def write_SCPI(self, command: str):
        print(command)
        self.sig_gen.write(command)

    def query_SCPI(self, query: str):
        return self.sig_gen.query(query)
    
    def write_lines(self, lines):
        for line in lines:
            self.write_SCPI(line)
            time.sleep(0.1)

    def close_device(self):
        self.sig_gen.close()
        self.sig_gen.clear()

    def check_errors():
        #TODO: implement return error handling
        pass