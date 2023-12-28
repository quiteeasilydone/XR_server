#Based on the work of Phil Harvey
#http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/FLIR.html
#Information extracted from the maker notes of JPEG images from thermal imaging cameras by FLIR Systems Inc.
#Tag ID

def attr(tag_name):
    return globals()[tag_name]


TAGS = {
0x0001: ('ImageTemperatureMax',),
0x0002: ('ImageTemperatureMin',),
0x0003: ('Emissivity',),
0x0004: ('UnknownTemperature',),
0x0005: ('CameraTemperatureRangeMax?',),
0x0006: ('CameraTemperatureRangeMin?',)
}

#Information extracted from FLIR FFF images and the FLIR APP1 segment of JPEG images.
#Tag ID    Tag Name       Values 
#'_header' FFFHeader ---> FLIR Header Tags
FFF_TAGS = {
    0x0001: ('RawData', 4, '>I'),
    0x0005: ('GainDeadData', 4, '>I'),
    0x0006: ('CoarseData', 4, '>I'),
    0x000E: ('EmbeddedImage', 4, '>I'),
    0x0020: ('CameraInfo', 4, '>I'),
    0x0021: ('MeasurementInfo', 4, '>I'),
    0x0022: ('PaletteInfo', 4, '>I'),
    0x0023: ('TextInfo', 4, '>I'),
    0x0024: ('EmbeddedAudioFile', 4, '>I'),
    0x0028: ('PaintData', 4, '>I'),
    0x002A: ('PiP', 4, '>I'),
    0x002B: ('GPSInfo', 4, '>I'),
    0x002C: ('MeterLink', 4, '>I'),
    0x002E: ('ParameterInfo', 4, '>I')
}

#Index2 = multiplier for calculating a byte offset is 2
RawData = {
    2: ('RawThermalImageWidth', 2, '<H'),
    4: ('RawThermalImageHeight', 2, '<H'),
    32: ('RawThermalImageType', 4, 'type'),
    32.1: ('RawThermalImage', -1, 'file')
}

#Index2 = multiplier for calculating a byte offset is 2
GainDeadData = {
    2: ('GainDeadMapImageWidth', 2, '<H'),
    4: ('GainDeadMapImageHeight', 2, '<H'),
#16: ('GainDeadMapImageType',)
    16.1: ('GainDeadMapImage', -1, 'file')
}

#Information found in FFF-format .CRS correction image files.
#Index2 = multiplier for calculating a byte offset is 2
CoarseData = {
    2: ('CoarseMapImageWidth', 2, '<H'),
    4: ('CoarseMapImageHeight', 2, '<H'),
#16: ('CoarseMapImageType')
    16.1: ('CoarseMapImage', -1, 'file')
}

#Index2 = multiplier for calculating a byte offset is 2
EmbeddedImage = {
    2: ('EmbeddedImageWidth', 2, '<H'),
    4: ('EmbeddedImageHeight', 2, '<H'),
    32: ('EmbeddedImageType', 4, 'type'),
    32.1: ('EmbeddedImage', -1, 'file')
}

#FLIR camera information. The Planck tags are variables used in the temperature calculation
#Index1 = multiplier for calculating a byte offset is 1
CameraInfo = {
    32: ('Emissivity', 4, '<f'),
    36: ('ObjectDistance', 4, '<f'),
    40: ('ReflectedApparentTemperature', 4, 'temp'),
    44: ('AtmosphericTemperature', 4, 'temp'),
    48: ('IRWindowTemperature', 4, 'temp'),
    52: ('IRWindowTransmission', 4, '<f'),
    60: ('RelativeHumidity', 4, '<f'),
    88: ('PlanckR1', 4, '<f'),
    92: ('PlanckB', 4, '<f'),
    96: ('PlanckF', 4, '<f'),
    112: ('AtmosphericTransAlpha1', 4, '<f'),
    116: ('AtmosphericTransAlpha2', 4, '<f'),
    120: ('AtmosphericTransBeta1', 4, '<f'),
    124: ('AtmosphericTransBeta2', 4, '<f'),
    128: ('AtmosphericTransX', 4, '<f'),
    144: ('CameraTemperatureRangeMax', 4, 'temp'),
    148: ('CameraTemperatureRangeMin', 4, 'temp'),
    152: ('CameraTemperatureMaxClip', 4, 'temp'),
    156: ('CameraTemperatureMinClip', 4, 'temp'),
    160: ('CameraTemperatureMaxWarn', 4, 'temp'),
    164: ('CameraTemperatureMinWarn', 4, 'temp'),
    168: ('CameraTemperatureMaxSaturated', 4, 'temp'),
    172: ('CameraTemperatureMinSaturated', 4, 'temp'),
    212: ('CameraModel', 32, '>s'),
    244: ('CameraPartNumber', 16, '>s'),
    260: ('CameraSerialNumber', 16, '>s'),
    276: ('CameraSoftware', 16, '>s'),
    368: ('LensModel', 32, '>s'),
    400: ('LensPartNumber', 16, '>s'),
    416: ('LensSerialNumber', 16, '>s'),
    436: ('FieldOfView', 8, '<d'),
    492: ('FilterModel', 16, '>s'),
    508: ('FilterPartNumber', 32, '>s'),
    540: ('FilterSerialNumber', 16, '>s'),
    776: ('PlanckO', 4, '<i'),
    780: ('PlanckR2',4, '<f'),
    784: ('RawValueRangeMin', 2, '<H'),
    786: ('RawValueRangeMax', 2, '<H'),
    824: ('RawValueMedian', 4, '<i'),
    828: ('RawValueRange', 2, '<H'),
    #900: ('DateTimeOriginal', 0, ''),
    912: ('FocusStepCount', 4, '<i'),
    1116: ('FocusDistance', 4, '<f')
}

#Index1 = multiplier for calculating a byte offset is 1
PaletteInfo = {
    0: ('PaletteColors', 4, '<I'),
    6: ('AboveColor', 1, '<B', 1, '<B', 1, '<B'),
    9: ('BelowColor', 1, '<B', 1, '<B', 1, '<B'),
    12: ('OverflowColor', 1, '<B', 1, '<B', 1, '<B'),
    15: ('UnderflowColor', 1, '<B', 1, '<B', 1, '<B'),
    18: ('Isotherm1Color', 1, '<B', 1, '<B', 1, '<B'),
    21: ('Isotherm2Color', 1, '<B', 1, '<B', 1, '<B'),
    26: ('PaletteMethod', 1, '<B'),
    27: ('PaletteStretch', 1, '<B'),
    48: ('PaletteFileName', 32, '>s'),
    80: ('PaletteName', 16, '>s'),
    112: ('Palette', -1, 'file')
}

#Index1 = multiplier for calculating a byte offset is 1
GPSInfo = {
    88: ('GPSMapDatum', 16, '>s')
}

#FLIR Picture in Picture tags.
#Index2 = multiplier for calculating a byte offset is 2
PiP = {
    0: ('Real2IR', 4, '<f'),
    4: ('OffsetX', 2, '<h'),
    6: ('OffsetY', 2, '<h'),
    8: ('PiPX1', 2, '<H'),
    10: ('PiPX2', 2, '<H'),
    12: ('PiPY1', 2, '<H'),
    14: ('PiPY2', 2, '<H')
}

MeasurementInfo = {}

TextInfo = {}

MeterLink = {}

ParameterInfo = {}

PaintData = {}