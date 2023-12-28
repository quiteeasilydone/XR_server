import struct
import re
from math import sqrt, exp, log
import io
from PIL import Image

try:
    basestring
except NameError:
    basestring = str

class ExifHeader:
    """ 
    just for Tag 'DigitalZoomRatio'
    """
    def __init__(self, data):
        self.header = bytes(data)
        self.offset = 30
    
    def s2n(self, offset, length):
        offset += self.offset
        if length == 2:
            _type = '<H'
        else:
            _type = '<I'
        return struct.unpack(_type, self.header[offset: offset + length])[0]

    def get_first_ifd(self):
        return self.s2n(4, 4)

    def get_tag_from_ifd(self, ifd, target_tag):
        entries = self.s2n(ifd, 2)
        for idx in range(entries):
            entry = ifd + 2 + 12 * idx
            tag = self.s2n(entry, 2)
            if tag == target_tag:
                value = self.s2n(entry + 8, 4)
                break
        return value
    
    def get_ZoomRatio(self):
        ifd0 = self.get_first_ifd()
        exif_ifd = self.get_tag_from_ifd(ifd0, 34665)
        
        zoom_offset = self.get_tag_from_ifd(exif_ifd, 41988)
        val1 = self.s2n(zoom_offset, 4)
        val2 = self.s2n(zoom_offset + 4, 4)
        return val1 / val2

class flirFFFHeader:
    """
    Handle a FLIR FFF Header.
    """
    def __init__(self, data, offset):
        self.file = bytes(data)
        self.offset = offset
        self.tags = {}
        self.tag_offset = {}
        
        # It's end offset of Embedded Image
        self.app1_size = struct.unpack('>I', data[offset + 52: offset+56])[0]
        self.file_end = {}

        # Some tags have multiple values
        self.multivalue_list = ['OverflowColor', 'AboveColor', 'BelowColor', 'UnderflowColor', 'Isotherm1Color', 'Isotherm2Color']
        self.file_list = ['RawData', 'GainDeadData', 'CoarseData', 'EmbeddedImage', 'PaletteInfo']

    def s2n(self, offset, length, _type):
        """
        Convert slice to each format
        It use struct module
        """
        offset += self.offset
        if _type == 'file':
            end = length + self.offset
            return self.file[offset: end]
        sliced = self.file[offset: offset + length]
        if _type == '>s':
            val = sliced.decode('ascii')
        elif _type == 'temp':
            val = round(struct.unpack('<f', sliced)[0], 2)
            val = '%0.2f' % (val - 273.15)
            # val = struct.unpack('<f', sliced)[0] - 273.15
        elif _type == 'type':
            if sliced == b'\x89PNG': val = 'PNG'
            elif sliced == b'\xff\xd8\xff\xe0': val = 'JPG'
            elif sliced == b'\xff\xd8\xff\xf7' : val = 'TIFF'
            else: val = 'RAW'
        else: 
            val = struct.unpack(_type, sliced)[0]
        return val

    def get_tags(self, tag_dict):
        """
        Extract Tag names from FFF Header
        """
        offset = 64
        tag_list = {}
        end_flag = False
        end_tag = ''
        
        while(1):
            tag_id = self.s2n(offset, 2, '>H')
            if tag_id == 0: break
            tag = tag_dict.get(tag_id)
            if not(tag):
                offset += 32
                continue
            tag_list[tag[0]] = self.s2n(offset + 12, tag[1], tag[2])
            if end_flag:
                self.file_end[end_tag] = tag_list[tag[0]]
                end_flag = False
            if tag[0] in self.file_list:
                end_flag = True
                end_tag = tag[0]
            offset += 32
        if end_flag:
            self.file_end[end_tag] = self.app1_size
        return tag_list

    def dump_tags(self, tag_name, offset, tag_dict):
        """
        dumping tag values with offset

        Args:
            tag_name (str): FFF header tag names
            offset (int): 
            tag_dict (dict):
        """
        for key in tag_dict.keys():
            tag = tag_dict[key]
            dump_name = tag[0]
            if tag[2] == 'file':
                self.tags[dump_name] = self.get_file(tag[0], offset + int(key))
            elif tag[0] in self.multivalue_list:
                self.tags[dump_name] = []
                jump = 0
                for idx in range(1,len(tag),2):
                    self.tags[dump_name].append(self.s2n(offset + key + jump, tag[idx], tag[idx + 1]))
                    jump += tag[idx]     
            else:
                try:
                    self.tags[dump_name] = self.s2n(offset + key, tag[1], tag[2])
                except:
                    # print(dump_name)
                    pass

    def get_file(self, tag, offset):
        match = {'RawThermalImage' : 'RawData', 'GainDeadMapImage' : 'GainDeadData', 'CoarseMapImage' : 'CoarseData', 'EmbeddedImage' : 'EmbeddedImage'}
        if tag == 'Palette':
            end = offset + (self.tags['PaletteColors'] * 3)
        else:
            end = self.file_end[match[tag]]
        return self.s2n(offset, end, 'file')
    
    def round_floats(self):
        float_list = {'PlanckR1' : 3, 'PlanckB' : 1, 'PlanckR2' : 3}
        for key in float_list.keys():
            self.tags[key] = round(self.tags[key], float_list[key])