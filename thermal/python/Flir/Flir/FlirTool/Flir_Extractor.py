from .classes import flirFFFHeader
from .classes import ExifHeader
from .utils import ord_
from .flir_tags import *

def increment_base(data, base):
    return ord_(data[base + 2]) * 256 + ord_(data[base + 3]) + 2

def process_file(f):
    """
    
    """
    # by default do not fake an EXIF beginning
    flirbase = 0
    jpg_base = []
    # determine whether it's a JPEG or TIFF
    data = bytearray(f.read(12))
    if data[0:4] in [b'II*\x00', b'MM\x00*']:
        # it's a TIFF file
        f.seek(0)
        endian = f.read(1)
        f.read(1)
    elif data[0:2] == b'\xFF\xD8':
        # it's a JPEG file
        base = 2
        while ord_(data[2]) == 0xFF and data[6:10] in (b'JFIF', b'JFXX', b'OLYM', b'Phot'):
            length = ord_(data[4]) * 256 + ord_(data[5])
            f.read(length - 8)
            # fake an EXIF beginning of file
            # I don't think this is used. --gd
            data = b'\xFF\x00' + f.read(10)
            if base <= 2:
                base = length + 4

        f.seek(0)
        data = bytearray(f.read())
        # base = 2
        
        while 1:
            if data[base:base + 2] == b'\xFF\xE1':
                # APP1
                if data[base + 4:base + 8] == b"Exif":
                    #base -= 2
                    exifbase = base-2
                    #break
                if data[base + 4:base + 8] == b"FLIR":
                    # this should actually be FLIRFFF. The other tables will be pointed by it.
                    flir_header_name="".join(map(chr,data[base + 4:base + 8]+data[base + 12:base + 15]))
                    if(flir_header_name  == 'FLIRFFF'):
                        flirbase = base + 12
                        increment = increment_base(data, base)
                        base += increment
                    else:
                        increment = increment_base(data, base)
                        tmp = data[:base]
                        tmp.extend(data[base + 12:])
                        data = tmp
                        base += increment - 12
                else:
                    increment = increment_base(data, base)
                    base += increment
            elif data[base:base + 2] == b'\xFF\xE0':
                # APP0
                jpg_base.append(base)
                increment = increment_base(data, base)
                base += increment
            elif data[base:base + 2] == b'\xFF\xE2':
                # APP2
                increment = increment_base(data, base)
                base += increment
            elif data[base:base + 2] == b'\xFF\xEE':
                # APP14
                increment = increment_base(data, base)
                base += increment
            elif data[base:base + 2] == b'\xFF\xDB':
                break
            elif data[base:base + 2] == b'\xFF\xD8':
                # APP12
                increment = increment_base(data, base)
                base += increment
            elif data[base:base + 2] == b'\xFF\xEC':
                # APP12
                increment = increment_base(data, base)
                base += increment
            else:
                try:
                    increment = increment_base(data, base)
                except IndexError:
                    return {}
                else:
                    base += increment
    elif data[0:3] == b'FFF':
        # it's a csq or raw file
        f.seek(0)
        data = bytearray(f.read())
        flirbase = 0
        flirhdr = flirFFFHeader(data, flirbase)
        tag_list = flirhdr.get_tags(tag_dict=FFF_TAGS)
        # dumping values of each tags in FFF Header
        for tag in tag_list.keys():
            flirhdr.dump_tags(tag, tag_list[tag], tag_dict=attr(tag))
    else:
        # file format not recognized
        return {}

    # Extracting FLIR FFF Header information
    if flirbase != 0:
        flirhdr = flirFFFHeader(data, flirbase) 
        tag_list = flirhdr.get_tags(tag_dict=FFF_TAGS)
        # dumping values of each tags in FFF Header
        for tag in tag_list.keys():
            flirhdr.dump_tags(tag, tag_list[tag], tag_dict=attr(tag))
        
        exifhdr = ExifHeader(data[:3000])
        zoom = exifhdr.get_ZoomRatio()
        flirhdr.tags['ZoomRatio'] = zoom
    else:
        raise ValueError("Input file is not flir image")
    # flirhdr.round_floats()

    return flirhdr.tags

def is_flir(f):
    # by default do not fake an EXIF beginning
    flirbase = 0
    jpg_base = []
    # determine whether it's a JPEG or TIFF
    data = bytearray(f.read(12))
    if data[0:4] in [b'II*\x00', b'MM\x00*']:
        # it's a TIFF file
        f.seek(0)
        endian = f.read(1)
        f.read(1)
    elif data[0:2] == b'\xFF\xD8':
        # it's a JPEG file
        base = 2
        while ord_(data[2]) == 0xFF and data[6:10] in (b'JFIF', b'JFXX', b'OLYM', b'Phot'):
            length = ord_(data[4]) * 256 + ord_(data[5])
            f.read(length - 8)
            # fake an EXIF beginning of file
            # I don't think this is used. --gd
            data = b'\xFF\x00' + f.read(10)
            if base <= 2:
                base = length + 4

        f.seek(0)
        data = bytearray(f.read())
        # base = 2
        
        flir_flag = False
        while 1:
            if data[base:base + 2] == b'\xFF\xE1':
                # APP1
                if data[base + 4:base + 8] == b"Exif":
                    #base -= 2
                    exifbase = base-2
                    #break
                if data[base + 4:base + 8] == b"FLIR":
                    # this should actually be FLIRFFF. The other tables will be pointed by it.
                    flir_header_name="".join(map(chr,data[base + 4:base + 8]+data[base + 12:base + 15]))
                    if(flir_header_name  == 'FLIRFFF'):
                        flirbase = base + 12
                        increment = increment_base(data, base)
                        base += increment
                        flir_flag = True
                        break
                    else:
                        increment = increment_base(data, base)
                        tmp = data[:base]
                        tmp.extend(data[base + 12:])
                        data = tmp
                        base += increment - 12
                else:
                    increment = increment_base(data, base)
                    base += increment
            elif data[base:base + 2] == b'\xFF\xE0':
                # APP0
                jpg_base.append(base)
                increment = increment_base(data, base)
                base += increment
            elif data[base:base + 2] == b'\xFF\xE2':
                # APP2
                increment = increment_base(data, base)
                base += increment
            elif data[base:base + 2] == b'\xFF\xEE':
                # APP14
                increment = increment_base(data, base)
                base += increment
            elif data[base:base + 2] == b'\xFF\xDB':
                break
            elif data[base:base + 2] == b'\xFF\xD8':
                # APP12
                increment = increment_base(data, base)
                base += increment
            elif data[base:base + 2] == b'\xFF\xEC':
                # APP12
                increment = increment_base(data, base)
                base += increment
            else:
                try:
                    increment = increment_base(data, base)
                except IndexError:
                    return {}
                else:
                    base += increment

    return flir_flag