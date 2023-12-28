import Flir_Extractor
import os
import glob
import string
import struct
import pandas as pd
import numpy as np

# filename = glob.glob('./img/*.jpg')
# filename = [fi.replace('\\', '/') for fi in filename]
# filename = [fi.replace('.jpg', '') for fi in filename]
filename = ['F:\짬통\FLIR Image 메타데이터 분석\작업용/FLIR0036']

for fi in filename:
    main_filename = fi + '.jpg'
    # # fi = fi.replace('./img', './extract')
    # png_filename = fi + '_raw.png'
    # # jpg_filename = fi + '_embedded.jpg'
    f = open(main_filename, 'rb')
    tags = Flir_Extractor.process_file(f)
    f.close()

    for key in tags.keys():
        # if key == 'JPEGThumbnail': continue
        # if key == 'Palette': continue
        # if key == 'EmbeddedImage': continue
        # if key == 'RawThermalImage': continue
        # print(key, tags[key])
        print(key)

    # png = open(png_filename, 'wb') 
    # png.write(tags['FLIR_RawThermalImage'])
    # png.close()
    # jpg = open(jpg_filename, 'wb')
    # jpg.write(tags['FLIR_EmbeddedImage'])
    # jpg.close()
