from PIL import Image
import numpy as np
import os
from pallete_aug import heatmapConverter
from glob import glob
import pandas as pd
import cv2
from tqdm import tqdm
from os import path as osp
import os
import shutil
from flir_image_extractor import FlirImageExtractor
from flir_image_extractor import is_flir_img
from pallete_aug import heatmapConverter

jpg_paths = glob('XR_test/*.jpg')
# jpg_paths = ['img/test1.jpg']
pal = pd.read_csv('pallete/RAINBOW1.csv')

for path in jpg_paths:
    fie = FlirImageExtractor()
    try:
        fie.process_image(path)
    except Exception as e:
        print(path, e)
        continue

    print(fie.raw_image_np.shape)

    # img = fie.get_heatmap_image_np()
    # img = img[:,:,::-1]
    # # thermal = np.loadtxt(path, delimiter=',')

    # thermal = fie.get_thermal_np()
    # img = heatmapConverter(thermal, pal, is_colorbar=False, minmax = [thermal.min(), thermal.max()], option='o')
    img = fie.thermal_palatte_conversion(is_colorbar=False, pal=pal, option='o', is_thermal=False)
    # img = fie.ir_real_fusion('fusion')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img.save(path.replace('.jpg', '_heat.png'))
    # fie.export_thermal_to_csv()