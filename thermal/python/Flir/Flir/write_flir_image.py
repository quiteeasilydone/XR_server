from FlirTool.utils import ord_
# from .flir_tags import *
import numpy as np
from PIL import Image
from pallete_aug import heatmapConverter
import pandas as pd
import os
import cv2

def increment_base(data, base):
    return ord_(data[base + 2]) * 256 + ord_(data[base + 3]) + 2

def dump_thumbnail(data, filename):
    """get rgb 3d array and dump thumbnail to file
    Args:
        data (numpy): rgb 3d array
        filename (str): filename to dump
    """
    img = Image.fromarray(data)
    img.save('./Cash.jpg')

    bf = open('./Cash.jpg', 'rb')
    byte_data = bytearray(bf.read())
    byte_data = byte_data[20:]
    bf.close()
    os.remove('./Cash.jpg')

    f = open(filename, 'rb')
    data = dump(byte_data, f)
    f.close()

    f = open(filename, 'wb')
    f.write(data)
    f.close()

def dump(dump_data, f):
    """
    data : data for dumping
    f : file to dump
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
                        # tmp = data[:base]
                        # tmp.extend(data[base + 12:])
                        # data = tmp
                        # base += increment - 12
                        base += increment
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
                thumbnail_base = base
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
    else:
        # file format not recognized
        return {}
    
    data = data[:thumbnail_base]
    data.extend(dump_data)
    

    # f.write(data)

    # # Extracting FLIR FFF Header information
    # if flirbase != 0:
    #     flirhdr = flirFFFHeader(data, flirbase) 
    #     tag_list = flirhdr.get_tags(tag_dict=FFF_TAGS)
    #     # dumping values of each tags in FFF Header
    #     for tag in tag_list.keys():
    #         flirhdr.dump_tags(tag, tag_list[tag], tag_dict=attr(tag))
        
    #     exifhdr = ExifHeader(data[:3000])
    #     zoom = exifhdr.get_ZoomRatio()
    #     flirhdr.tags['ZoomRatio'] = zoom
    # else:
    #     print('It is not Flir image file!')
    #     return -1
    # # flirhdr.round_floats()

    # return flirhdr.tags

    return data


if __name__ == '__main__':
    im = pd.read_csv('F:\짬통\FLIR Image 메타데이터 분석\작업용/FLIR0036.csv')
    imarr = im.to_numpy(dtype = float)
    print(imarr.shape)

    pal = pd.read_csv('F:\짬통\FLIR_Image_Extractor\pallete/IRON.csv')
    ht = heatmapConverter(imarr, pal, minmax = [imarr.min(), imarr.max()], is_colorbar = True, option='o')

    ht = cv2.cvtColor(ht, cv2.COLOR_BGR2RGB)
    dump_thumbnail(ht, 'F:\짬통\FLIR Image 메타데이터 분석\작업용/TEST_R.jpg')