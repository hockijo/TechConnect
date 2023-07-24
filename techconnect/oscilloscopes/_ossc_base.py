"""
The base class for oscilloscopes, containing methods for parsing and saving data. This is kept private

Pieces salvaged from InfiniiVision_SegmentedMemory_Waveform.py
"""
import numpy as np 
import pickle as pkl
import os
import time
from techconnect.base._instrument import VISAInstrument
import techconnect.tools.file_handling as file_handling

__all__ = []

class Oscilloscope(VISAInstrument):
    """
    Base Class representing an oscilloscope.
    """
    def __init__(self):
        super().__init__()
        self.query_delay = 0.1

    def segmented_initialization(self, channel):
        raise NotImplementedError()

    def calculate_segment_number(self, acquistion_time):
        raise NotImplementedError()
    
    def setup_time_window(self, time_window):
        raise NotImplementedError()

    def setup_triggering(self):
        raise NotImplementedError()

    def segmented_acquistion_setup(self):
        raise NotImplementedError()

    def manual_channel_setup(self):
        raise NotImplementedError()

    def auto_setup(self):
        raise NotImplementedError()

    def single_acquisition(self):
        raise NotImplementedError()

    def digitize_acquisition(self):
        raise NotImplementedError()

    def retrieve_channel_info(self):
        raise NotImplementedError()
    
    def data_export_setup(self):
        raise NotImplementedError()

    def get_number_of_points(self):
        raise NotImplementedError()

    def generate_x_data(self, channel_info):
        """
        Generate the x data based on the channel information.

        Parameters:
        -----------
        channel_info: dict
            A dictionary containing the channel information.
            It should have the following keys:
            - 'points': The number of points.
            - 'xreference': The x reference value.
            - 'xincrement': The x increment value.
            - 'xorigin': The x origin value.
            - 'type': The type of channel.

        Returns:
        --------
        ndarray
            The generated x data.

        """
        points = channel_info['points']
        x_data = ((np.linspace(0, points - 1, points) - channel_info['xreference'])*channel_info['xincrement']) + channel_info['xorigin']
        if channel_info['type'] == 1:
            x_data = np.repeat(x_data, 2)
        return x_data
    
    def stitch_multiseg_x_data(self, x_data, time_tags):
        """
        Concatenates the given `x_data` with each element in `time_tags`, constructing a stitched single array for the x data.

        Parameters:
        -----------
        x_data: numpy.ndarray
            The input data to be concatenated.
        time_tags: iterable
            A list of time tags to concatenate with `x_data`.

        Returns:
        --------
        numpy.ndarray
            The concatenated array.
        """
        return np.concatenate([x_data + time_tag for time_tag in time_tags])
    
    def scale_y_data(self, y_data, channel_info):
        """
        Scales the given y data based on the channel information.

        Parameters
        ----------
        y_data : array-like
            The y data to be scaled.
        channel_info : dict
            A dictionary containing channel information, including 'yreference', 'yincrement', and 'yorigin'.

        Returns
        -------
        array-like
            The scaled y data.
        """
        return ((y_data - channel_info['yreference'])*channel_info['yincrement']) + channel_info['yorigin']
    
    def collect_single_segment_data(self, segment_index, channel, channel_info):
        raise NotImplementedError()
    
    def collect_multi_segment_data(self, number_of_segments, channel, stitched: bool):
        """
        Collects multi-segment data for a given number of segments, channel, and stitched flag.

        Parameters
        ----------
        number_of_segments : int
            The number of segments to collect data from.
        channel : str
            The channel to collect data from.
        stitched : bool
            Flag indicating whether the data should be stitched.

        Returns
        -------
        tuple
            A tuple containing the following:
            x_data : ndarray
                The x-axis data.
            y_data : ndarray
                The y-axis data.
            time_tags : ndarray
                The time tags.
            channel_info : str
                The channel information.
        """
        self.data_export_setup(channel)
        channel_info = self.retrieve_channel_info(channel)

        segment_x_data = self.generate_x_data(channel_info)

        time_tags = []
        y_data = []
        for segment in range(1, number_of_segments+1):
            segment_time_tag, segment_y_data = self.collect_single_segment_data(segment, channel, channel_info)
            time_tags.append(segment_time_tag)
            y_data.append(segment_y_data)

        time_tags = np.asarray(time_tags)
        y_data = np.asarray(y_data)

        if stitched:
            x_data = self.stitch_multiseg_x_data(segment_x_data, time_tags)
            y_data = np.reshape(y_data, x_data.shape)
        else:
            x_data = segment_x_data

        return x_data, y_data, time_tags, channel_info
    
    def parse_and_save(self, save_directory, save_dict, acquisition_info):
        """
        Parses the data and saves it to a specified directory.

        Parameters
        ----------
        save_directory : str
            A string representing the directory where the data will be saved.
        save_dict : dict
            A dictionary containing the data to be saved.
        acquisition_info : dict, optional
            An optional dictionary containing additional acquisition information.

        Returns
        -------
        None
        """
        filename = f'{time.strftime(r"%d-%m-%Y-%H-%M-%S", time.localtime())}_data_collection'

        metadata = {
                'resource_info': self.instrument.resource_info._asdict().copy(),
                'collection_time_UTC': time.time()
            }
        metadata['resource_info'].update({'manufactuer_id': self.instrument.manufacturer_id,
                                            'manufactuer_name': self.instrument.manufacturer_name,
                                            'model_code': self.instrument.model_code,
                                            'model_name': self.instrument.model_name,
                                            'serial_number': self.instrument.serial_number,
                                            'idn': self.query_SCPI(u"*IDN?")})
        if acquisition_info is not None:
            metadata.update({'acquisition_info': acquisition_info})
        
        file_handling.save_to_pkl(save_dict, metadata=metadata, directory=save_directory, filename=filename)

    def stitched_data_acquisition(self, acquisition_time, channels, segment_number=1000, save_directory=None, acquisition_type='HRESOLUTION'):
        """
        Perform stitched data acquisition.

        Parameters
        ----------
        acquisition_time : float
            The total acquisition time in seconds.
        channels : list
            A list of channels to acquire.
        segment_number : int, optional
            The number of segments to divide the acquisition into. Defaults to 1000.
        save_directory : str, optional
            The directory to save the acquired data. `None` will not save, otherwise will create and save to given directory. Defaults to None.
        acquisition_type : str, optional
            The acquisition type. Defaults to 'HRESOLUTION'.

        Returns
        -------
        tuple
            A tuple containing the acquired x data, y data, time tags, and channel info.
        """
        self.auto_setup()
        time_window = acquisition_time/segment_number
        self.setup_time_window(time_window)
        self.setup_triggering()
        for channel in channels:
            self.segmented_initialization(channel)
        self.segmented_acquistion_setup(segment_number, acquistion_type=acquisition_type)

        self.digitize_acquisition(channels)
        time.sleep(1.5*acquisition_time+2)

        x_data = {}
        y_data = {}
        time_tags = {}
        channel_info = {}
        for channel in channels:
            channel_x_data, channel_y_data, channel_time_tags, channel_channel_info = self.collect_multi_segment_data(segment_number, channel, stitched=True)
            x_data.update({channel: channel_x_data})
            y_data.update({channel: channel_y_data})
            time_tags.update({channel: channel_time_tags})
            channel_info.update({channel: channel_channel_info})

        if save_directory is not None:
            save_dict = {
                            'x_data': x_data,
                            'y_data': y_data,
                            'time_tags': time_tags,
                            'channel_info': channel_info
                        }
            acquisition_info = {'type': acquisition_type, 'acq_time': acquisition_time, "segment_number": segment_number, 'time_window': time_window, 'stitched': True}
            self.parse_and_save(save_directory, save_dict, acquisition_info)

        return x_data, y_data, time_tags, channel_info
    
    def unstitched_data_acquisition(self, time_window, segment_number, channels, save_directory=None, acquisition_type='HRESOLUTION'):
        """
        Perform unstitched data acquisition for a given time window, segment number, and channels.

        Parameters
        ----------
        time_window : float
            The time window for each segment in seconds.
        segment_number : int
            The number of segments to acquire.
        channels : list
            A list of channels to acquire data from.
        save_directory : str, optional
            The directory to save the acquired data. Default is None.
        acquisition_type : str, optional
            The type of acquisition. Default is 'HRESOLUTION'.

        Returns
        -------
        tuple
            A tuple containing the acquired x_data, y_data, time_tags, and channel_info.
        """
        self.auto_setup()
        self.setup_time_window(time_window)
        self.setup_triggering()
        for channel in channels:
            self.segmented_initialization(channel)
        self.segmented_acquistion_setup(segment_number, acquistion_type=acquisition_type)

        self.digitize_acquisition(channels)
        time.sleep(3*(time_window*segment_number)+0.1*segment_number)

        x_data = {}
        y_data = {}
        time_tags = {}
        channel_info = {}
        for channel in channels:
            channel_x_data, channel_y_data, channel_time_tags, channel_channel_info = self.collect_multi_segment_data(segment_number, channel, stitched=False)
            x_data.update({channel: channel_x_data})
            y_data.update({channel: channel_y_data})
            time_tags.update({channel: channel_time_tags})
            channel_info.update({channel: channel_channel_info})

        if save_directory is not None:
            save_dict = {
                            'x_data': x_data,
                            'y_data': y_data,
                            'time_tags': time_tags,
                            'channel_info': channel_info
                        }
            acquisition_info = {'type': acquisition_type, 'acq_time': time_window*segment_number, "segment_number": segment_number, 'time_window': time_window, 'stitched': False}
            self.parse_and_save(save_directory, save_dict, acquisition_info)

        return x_data, y_data, time_tags, channel_info

