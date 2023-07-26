"""
Setup and run a sine wave on a GPIB instrument
==============================================
This example script sets up a sine wave on an Agilent 33250A signal generator connected over a Prologix GPIB adaptor

Usage:
    - Import the necessary modules: Agilent33250A
    - Create an instance of the Agilent33250A class and connect to the signal generator using the `connect` method.
    - Define the `channel` variable as the channel number.
    - Call the `setup_sine` method of the Agilent33250A class setup the waveform.

Note:
    - This module assumes that the necessary dependencies are installed and the signal generator is properly connected.
"""

from techconnect.signal_generators.agilent import Agilent33250A

def main():
    """
    Connects to an Agilent33250A signal generator and sets up a sine wave signal on a specified channel.
    """
    # Set the channel number
    channel = 1

    # Create an instance of Agilent33250A and connect to it
    signal_gen = Agilent33250A(gpib_address=10)
    signal_gen.connect(signal_gen.list_connections(verbose=True)[0])

    # Turn off the specified channel
    signal_gen.turnOff(channel)

    # Set up a sine wave with frequency 100 and amplitude 1
    signal_gen.setupSine(100, 1)

    # Turn on the specified channel
    signal_gen.turnOn(channel)

if __name__== "__main__":
    main()	

