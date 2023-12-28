from flir_image_extractor import FlirImageExtractor
from glob import glob
import cv2
from tqdm import tqdm
import os
import os.path as osp
import argparse
from PIL import Image
import io
import numpy as np
from FlirTool.Flir_Extractor import is_flir

if __name__ == "__main__":
    paths = glob('thermal2/*.jpg')
    
    for path in paths:
        