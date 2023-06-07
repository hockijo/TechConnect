import numpy as np 
import pickle as pkl
import pyvisa
import os
import time
from VISA_instrument import VISAInstrument

################################################################
#Peices salvaged from InfiniiVision_SegmentedMemory_Waveform.py#
################################################################

class Keysight3000T(VISAInstrument):
    def segmented_initialization(self, channel):
        lines = (
            f":CHAN{channel}:DISPLAY ON",
            f":ACQUIRE:CHAN {channel}:SRATE:AUTO ON",
            f":ACQUIRE:CHAN {channel}:POINTS:AUTO ON"
        )

        self.write_lines(lines)

    def calculate_segment_number(self, acquistion_time):
        sample_rate = int(float(self.query_SCPI(f":ACQUIRE:SRATE?")))
        points_per_segment = int(float(self.query_SCPI(f":ACQUIRE:POINTS?")))
        
        segment_number = int(np.ceil((acquistion_time*sample_rate)/points_per_segment))
        return segment_number
    
    def setup_time_window(self, acquistion_time, segment_number):
        time_window = acquistion_time/segment_number
        self.write_SCPI(f":TIMEBASE:SCALE {time_window/10}")

    def setup_triggering(self):
        lines = (":TRIGGER:MODE EDGE",
                 ":TRIGGER:EDGE:SOURCE EXT",
                 ":TRIGGER:EDGE:SLOPE EITHER")
        self.write_lines(lines)

    def segmented_acquistion_setup(self, segment_count:int,  
                                    acquistion_type='NORMAL',
                                    sample_rate='AUTO'
                                    ):

        lines = (
            f":ACQUIRE:MODE SEGMENTED",
            f":ACQUIRE:SEGMENTED:COUNT {segment_count}",
            f":ACQUIRE:TYPE {acquistion_type}"
        )

        self.write_lines(lines)

    def manual_channel_setup(self, channel: int,
                      vertical_scale,
                      vertical_range,
                      vertical_offset,
                      bw_limit,
                      coupling,
                      ):
        
        lines = (
            f":CHAN{channel}:DISPLAY ON",
            f":CHAN{channel}:BWLIMIT{bw_limit}",
            f":CHAN{channel}:COUPLING{coupling}",
            f":CHAN{channel}:OFFSET{vertical_offset}",
            f":CHAN{channel}:RANGE{vertical_range}",
            f":CHAN{channel}:SCALE{vertical_scale}",
        )

        self.write_lines(lines)

    def auto_setup(self):
        self.write_SCPI(f":AUTOSCALE")

    def single_acquisition(self):
        self.write_SCPI(f":SINGLE")

    def digitize_acquisition(self, channels):
        line = ":DIGITIZE"
        if len(channels)>1:
            for channel in channels:
                line += f" CHANNEL{channel}"

        self.write_SCPI(line)

    def retrieve_channel_info(self, channel):
        channel_info = self.query_SCPI(f":WAVEFORM:SOURCE CHAN{channel};:WAVEFORM:PREAMBLE?").split(',')
        return {
            'format': int(channel_info[0]),
            'type': int(channel_info[1]),
            'points': int(float(channel_info[2])),
            'count': int(channel_info[3]),
            'xincrement': float(channel_info[4]),
            'xorigin': float(channel_info[5]),
            'xreference': float(channel_info[6]),
            'yincrement': float(channel_info[7]),
            'yorigin': float(channel_info[8]),
            'yreference': float(channel_info[9])
        }
    
    def data_export_setup(self, channel):
        lines = (
            f":WAVEFORM:SOURCE CHAN{channel}",
            f":WAVEFORM:FORMAT WORD",
            f":WAVEFORM:BYTEORDER LSBFIRST",
            f":WAVEFORM:UNSIGNED 0",
            f":WAVEFORM:POINTS MAX",
            f":WAVEFORM:POINTS:MODE RAW"
        )

        self.write_lines(lines)

    def get_number_of_points(self, channel):
        return int(self.write_SCPI(f"WAVEFORM:SOURCE CHAN{channel};:WAVEFORM:POINTS?"))

    def generate_x_data(self, channel_info):
        points = channel_info['points']
        x_data = ((np.linspace(0, points - 1, points) - channel_info['xreference'])*channel_info['xincrement']) + channel_info['xorigin']
        if channel_info['type'] == 1:
            x_data = np.repeat(x_data, 2)
        return x_data
    
    def stitch_multiseg_x_data(self, x_data, time_tags):
        return np.concatenate([x_data + time_tag for time_tag in time_tags])
    
    def scale_y_data(self, y_data, channel_info):
        return ((y_data - channel_info['yreference'])*channel_info['yincrement']) + channel_info['yorigin']
    
    def collect_single_segment_data(self, segment_index, channel, channel_info):
        self.write_SCPI(f":ACQUIRE:SEGMENTED:INDEX {segment_index}")
        segment_time_tag = float(self.query_SCPI(f":WAVEFORM:SEGMENTED:TTAG?"))

        y_data = np.asarray(self.instrument.query_binary_values(f":WAVEFORM:SOURCE CHAN{channel};DATA?", 'h', False))
        y_data = self.scale_y_data(y_data, channel_info)

        return segment_time_tag, y_data
    
    def collect_multi_segment_data(self, number_of_segments, channel):
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

        x_data = self.stitch_multiseg_x_data(segment_x_data, time_tags)
        y_data = np.reshape(y_data, x_data.shape)

        return x_data, y_data, time_tags, channel_info
    
    def data_acquistion(self, acquistion_time, channels, segment_number=1000, save_directory=None):
        self.auto_setup()
        time.sleep(2)
        # segment_number = self.calculate_segment_number(acquistion_time)
        self.setup_time_window(acquistion_time, segment_number)
        self.setup_triggering()
        time.sleep(2)
        for channel in channels:
            self.segmented_initialization(channel)
        time.sleep(2)
        self.segmented_acquistion_setup(segment_number, acquistion_type='HRESOLUTION')
        time.sleep(2)

        self.digitize_acquisition(channels)
        time.sleep(2+acquistion_time)

        x_data = {}
        y_data = {}
        time_tags = {}
        channel_info = {}
        for channel in channels:
            channel_x_data, channel_y_data, channel_time_tags, channel_channel_info = self.collect_multi_segment_data(segment_number, channel)
            x_data.update({channel: channel_x_data})
            y_data.update({channel: channel_y_data})
            time_tags.update({channel: channel_time_tags})
            channel_info.update({channel: channel_channel_info})

        if save_directory is not None:
            time_string = time.strftime(r"%d-%m-%Y-%H-%M-%S", time.localtime())
            save_dict = {
                            'x_data': x_data,
                            'y_data': y_data,
                            'time_tags': time_tags,
                            'channel_info': channel_info
                        }
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)
            with open(f"{save_directory}//{time_string}_data_collection.pkl", 'wb') as f:
                pkl.dump(save_dict, f)

        return x_data, y_data, time_tags, channel_info


