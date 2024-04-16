from PIL import Image
import numpy as np
import os
from .pallete_aug import heatmapConverter
from glob import glob
import pandas as pd
import cv2
from tqdm import tqdm
from os import path as osp
import os
import shutil
from .flir_image_extractor import FlirImageExtractor
from .flir_image_extractor import is_flir_img
from .pallete_aug import heatmapConverter
import base64
from io import BytesIO

def pallete(img_idx, pallete_op, option):
    buffered_raw = BytesIO()
    buffered_IR = BytesIO()
    img_id = img_idx[8:-4]
    jpg_path = os.path.join("../imgs/thermal", img_idx)
    raw_path = os.path.join("../imgs/raw", "raw_" + img_id + ".png")
    IR_path = os.path.join("../imgs/IR", "IR_" + img_id + ".png")
    print(jpg_path)
    pal_path = os.path.join('./Flir/pallete', pallete_op + '.csv')
    
    pal = pd.read_csv(pal_path)

    fie = FlirImageExtractor()
    try:
        fie.process_image(jpg_path)
    except Exception as e:
        print(jpg_path, e)

    # print(fie.raw_image_np.shape)

    # img = fie.get_heatmap_image_np()
    # img = img[:,:,::-1]
    # # thermal = np.loadtxt(path, delimiter=',')
    raw_img = fie.get_rgb_np()
    # raw_img = cv2.cvtColor(raw_img, cv2.COLOR_BGR2RGB)
    raw_img = Image.fromarray(raw_img)
    raw_img.save(raw_path)
    raw_img.save(buffered_raw, format="JPEG")
    raw_img_str = str(base64.b64encode(buffered_raw.getvalue()))
    # print(type(img_str))
    
    # thermal = fie.get_thermal_np()
    # img = heatmapConverter(thermal, pal, is_colorbar=False, minmax = [thermal.min(), thermal.max()], option='o')
    IR_img = fie.thermal_palatte_conversion(is_colorbar=False, pal=pal, option=option, is_thermal=False)
    # img = fie.ir_real_fusion('fusion')
    IR_img = cv2.cvtColor(IR_img, cv2.COLOR_BGR2RGB)
    IR_img = Image.fromarray(IR_img)
    IR_img.save(IR_path)
    IR_img.save(buffered_IR, format="JPEG")
    IR_img_str = str(base64.b64encode(buffered_IR.getvalue()))
    # fie.export_thermal_to_csv()
    return {"raw" : raw_img_str, "IR" : IR_img_str}

if __name__ == '__main__':
    pallete('thermal_1703666379359.jpg', 'temp', "o")