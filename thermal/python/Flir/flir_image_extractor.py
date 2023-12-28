#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import io
import json
import os
import os.path
import re
import csv
import subprocess
import struct
from PIL import Image
from math import sqrt, exp, log
from matplotlib import cm
from matplotlib import pyplot as plt
from .FlirTool.Flir_Extractor import process_file
from .FlirTool.Flir_Extractor import is_flir
from .pallete_aug import heatmapConverter
from .FlirTool.utils import palatte_converter
# from write_flir_image import Flir_Writer

import cv2
import numpy as np
import glob
from tqdm import tqdm

def is_flir_img(test_img_path):
    f = open(test_img_path, 'rb')
    flag = is_flir(f)
    f.close()
    return flag

class FlirImageExtractor:
    def __init__(self, is_debug=False):
        self.is_debug = is_debug
        self.flir_img_filename = ""
        self.rgb_image_filename = ""
        self.image_suffix = "_rgb_image.jpg"
        self.thumbnail_suffix = "_rgb_thumb.jpg"
        self.thermal_suffix = "_thermal.png"
        self.grayscale_suffix = "_grayscale.png"
        self.conv_fliename = ""
        self.default_distance = 1.0
        self.flir_tags = {}
        self._flip = False

        # valid for PNG thermal images
        self.use_thumbnail = False
        self.fix_endian = True

        self.rgb_image_np = None
        self.thermal_image_np = []
        self.raw_image_np = []
        self.heatmap_image = []
        self.crop_rgb = []
        self.normalized_image_np = None
    pass

    def process_image(self, flir_img_filename, save_dir=None):
        """
        Given a valid image path, process the file: extract real thermal values
        and a thumbnail for comparison (generally thumbnail is on the visible spectre)
        :param flir_img_filename:
        :return:
        """
        #if self.is_debug:
            # print("INFO Flir image filepath:{}".format(flir_img_filename))
        
        if not os.path.isfile(flir_img_filename):
            print(flir_img_filename)
            raise ValueError("Input file does not exist or this user don't have permission on this file")

        f = open(flir_img_filename, 'rb')
        self.flir_tags = process_file(f)
        f.close()

        self.flir_img_filename = flir_img_filename
        self.fn_prefix, _ = os.path.splitext(self.flir_img_filename)
        _, fn = os.path.split(self.flir_img_filename)
        fn, _ = os.path.splitext(fn)
        if save_dir:
            self.save_path = save_dir + fn
        else:
            self.save_path = self.fn_prefix
        self.rgb_image_filename = self.save_path + self.image_suffix
        self.pal = self.convert_pal()
        #
        # if self.get_image_type().upper().strip() == "TIFF":
        #     # valid for tiff images from Zenmuse XTR
        #     self.use_thumbnail = True
        #     self.fix_endian = False

        orit=np.array(self.export_flir_to_rawflr(self.flir_img_filename))
        if orit.shape[0] > orit.shape[1]:
            self._flip = True
        if 'EmbeddedImage' in self.flir_tags:
            self.rgb_image_np = self.extract_embedded_image()
        if self.flir_tags['RawThermalImageType'] == 'PNG':
            self.raw_image_np = np.vectorize(lambda x: (x >> 8) + ((x & 0x00ff) << 8))(self.extract_thermal_image())
        else:
            self.raw_image_np = self.extract_thermal_image()
        # self.raw_image_np = self.extract_thermal_image()
        # if self.flir_tags['ZoomRatio'] > 1:
        #     self.slice_by_zoom()

    def Write(self, filename = None):
        if not filename:
            filename = self.flir_img_filename
        f = open(self.flir_img_filename, 'rb')
        wr = Flir_Writer(filter, self.flir_tags, f)
        wr.write()

    def convert_temp(self):
        """
        convert raw data into thermal
        """
        self.thermal_image_np = self.convert_raw_to_temp()
        self.normalized_image_np = (self.thermal_image_np - np.amin(self.thermal_image_np)) / (np.amax(self.thermal_image_np) - np.amin(self.thermal_image_np))

    def convert_pal(self):
        return palatte_converter(self.flir_tags['Palette'])

    def set_csv_path(self):
        """
        set csv_path when already have thermal csv files(for fast performance)
        """
        csv_filename = self.save_path + '.csv'
        self.thermal_csv_filename = csv_filename

    def get_image_type(self):
        """
        Get the embedded thermal image type, generally can be TIFF or PNG
        :return:
        """
        return self.flir_tags['RawThermalImageType']

    def get_rgb_np(self):
        """
        Return the last extracted rgb image
        :return:
        """
        return self.rgb_image_np

    def get_thermal_np(self):
        """
        Return the last extracted thermal image
        :return:
        """
        if len(self.thermal_image_np) == 0:
            self.convert_temp()
        return self.thermal_image_np

    def get_heatmap_image_np(self):
        if len(self.heatmap_image) == 0:
            self.thermal_palatte_conversion(is_colorbar=False, is_thermal=False)
        
        return self.heatmap_image

    def thermal_palatte_conversion(self, is_colorbar = True, option = 'd', is_thermal = True, pal = None):
        if pal is None:
            pal = self.convert_pal()
        
        if is_thermal:
            self.heatmap_image = heatmapConverter(self.get_thermal_np(),
                                                pal,
                                                minmax=self.get_minmax(is_thermal=is_thermal),
                                                is_colorbar = is_colorbar, option = option)
        else:
            self.heatmap_image = heatmapConverter(self.raw_image_np,
                                                pal,
                                                minmax=self.get_minmax(is_thermal=is_thermal),
                                                is_colorbar = is_colorbar, option = option)
        return self.heatmap_image

    def extract_embedded_image(self):
        """
        extracts the visual image as 2D numpy array of RGB values
        """
        image_tag = "EmbeddedImage"
        if self.use_thumbnail:
            image_tag = "ThumbnailImage"

        visual_img_bytes = self.flir_tags[image_tag]
        # f = open('TEST.jpg', 'wb')
        # f.write(visual_img_bytes)
        # f.close()
        visual_img_stream = io.BytesIO(visual_img_bytes)

        visual_img = Image.open(visual_img_stream)
        visual_np = np.array(visual_img)

        if self._flip and visual_np.shape[0] < visual_np.shape[1]:
            visual_np = np.flip(visual_np, axis = 0)
            visual_np = np.swapaxes(visual_np, 0, 1)
        return visual_np

    def save_flir_tags(self):
        """
        Save flir metadata as .txt file
        """
        txt_filename = self.save_path + '_tags.txt'
        f = open(txt_filename, 'w')
        for key in self.flir_tags.keys():
            if key == 'EmbeddedImage': continue
            if key == 'Palette': continue
            if key == 'RawThermalImage': continue
            f.write(str(key) + ' ' + str(self.flir_tags[key]) + '\n')
        f.close()

    def save_heatmap_image(self):
        print('heat')
        if len(self.heatmap_image) == 0:
            img = heatmapConverter(self.raw_image_np,
                                    self.convert_pal(),
                                    minmax=self.get_minmax(is_thermal=False),
                                    is_colorbar = True)
        else:
            img = self.heatmap_image
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img.save(self.fn_prefix + '_conv.png')
        # cv2.imwrite(self.fn_prefix + '_conv.png', img)

    def extract_thermal_image(self):
        """
        extracts the thermal image as 2D numpy array with temperatures in oC
        """

        # read image metadata needed for conversion of the raw sensor values
        # E=1,SD=1,RTemp=20,ATemp=RTemp,IRWTemp=RTemp,IRT=1,RH=50,PR1=21106.77,PB=1501,PF=1,PO=-7340,PR2=0.012545258
        if 'Real2IR' in self.flir_tags:
            self.PiPTags = {'Real2IR' : self.flir_tags['Real2IR'],
                            'OffsetX' : self.flir_tags['OffsetX'],
                            'OffsetY' : self.flir_tags['OffsetY'],
                            'PiPX1' : self.flir_tags['PiPX1'],
                            'PiPX2' : self.flir_tags['PiPX2'],
                            'PiPY2' : self.flir_tags['PiPY2'],
                            'PiPY1' : self.flir_tags['PiPY1']}
        #print(self.PiPTags)
        # exifread can't extract the embedded thermal image, use exiftool instead
        thermal_img_bytes = self.flir_tags['RawThermalImage']
        thermal_img_stream = io.BytesIO(thermal_img_bytes)
        if self.flir_tags['RawThermalImageType'] == 'PNG':
            thermal_img = Image.open(thermal_img_stream)
            thermal_np = np.array(thermal_img)
        elif self.flir_tags['RawThermalImageType'] == 'RAW':
            thermal_np = np.frombuffer(thermal_img_bytes, dtype = np.uint16)
            thermal_np = np.reshape(thermal_np, (self.flir_tags['RawThermalImageHeight'], self.flir_tags['RawThermalImageWidth']))
            self.fix_endian = False
        else:
            raise Exception('Unknown Raw Data type')
        
        if self._flip:
            thermal_np = np.swapaxes(thermal_np, 0, 1)
            thermal_np = np.flip(thermal_np, axis = 0)
        
        return thermal_np
        # print(thermal_np.shape)  2
        # raw values -> temperature
    
    def raw2temp_np(self, raw_np):
        raw2tempfunc = np.vectorize(lambda x: FlirImageExtractor.raw2temp(x, E=self.flir_tags['Emissivity'], OD=1,
                                                                             RTemp=float(self.flir_tags['ReflectedApparentTemperature']),
                                                                             ATemp=float(self.flir_tags['AtmosphericTemperature']),
                                                                             IRWTemp=float(self.flir_tags['IRWindowTemperature']),
                                                                             IRT=self.flir_tags['IRWindowTransmission'],
                                                                             RH=self.flir_tags['RelativeHumidity'],
                                                                             PR1=self.flir_tags['PlanckR1'], PB=self.flir_tags['PlanckB'],
                                                                             PF=self.flir_tags['PlanckF'],
                                                                             PO=self.flir_tags['PlanckO'], PR2=self.flir_tags['PlanckR2'],
                                                                             ATA1 = self.flir_tags['AtmosphericTransAlpha1'],
                                                                             ATA2 = self.flir_tags['AtmosphericTransAlpha2'],
                                                                             ATB1 = self.flir_tags['AtmosphericTransBeta1'],
                                                                             ATB2 = self.flir_tags['AtmosphericTransBeta2'],
                                                                             ATX = self.flir_tags['AtmosphericTransX']))
        return raw2tempfunc(raw_np)

    def get_minmax(self, is_thermal):
        """[summary]
            retrurn Max and Min temperature value in image
        Args:
            is_thermal (bool): True if want thermal value, False if want Raw value
        Returns:
            [type]: list [min, max]
        """
        _min = self.flir_tags['RawValueMedian'] - int(self.flir_tags['RawValueRange'] / 2)
        _max = self.flir_tags['RawValueMedian'] + int(self.flir_tags['RawValueRange'] / 2)

        if _max > self.flir_tags['RawValueRangeMax']:
            _max = self.flir_tags['RawValueRangeMax']
        if _min < self.flir_tags['RawValueRangeMin']:
            _min = self.flir_tags['RawValueRangeMin']
        if is_thermal:
            return self.raw2temp_np([_min, _max])
        else:
            return [_min, _max]

    def convert_raw_to_temp(self):
        """[summary]
        convert raw data into thermal value
        Returns:
            [type]: converted thermal value in numpy
        """
        thermal_np = self.raw_image_np
        try:
            thermal_np = self.raw2temp_np(thermal_np)
        except:
            self.raw_image_np = np.vectorize(lambda x: (x >> 8) + ((x & 0x00ff) << 8))(self.raw_image_np)
            thermal_np = self.raw2temp_np(self.raw_image_np)
        return thermal_np

    @staticmethod
    def raw2temp(raw, E=1, OD=1, RTemp=20, ATemp=20, IRWTemp=20, IRT=1, RH=50, PR1=21106.77, PB=1501, PF=1, PO=-7340,
                PR2=0.012545258, ATA1 = 0.006569, ATA2 = 0.01262, ATB1 = -0.002276, ATB2 = -0.00667, ATX = 1.9):
        """
        convert raw values from the flir sensor to temperatures in C
        # this calculation has been ported to python from
        # https://github.com/gtatters/Thermimage/blob/master/R/raw2temp.R
        # a detailed explanation of what is going on here can be found there
        """
        # print(E, OD, RTemp, ATemp, IRWTemp, IRT, RH, PR1, PB, PF, PO, PR2)
        # constants

        # transmission through window (calibrated)
        emiss_wind = 1 - IRT
        refl_wind = 0

        # transmission through the air
        h2o = (RH / 100) * exp(1.5587 + 0.06939 * (ATemp) - 0.00027816 * (ATemp) ** 2 + 0.00000068455 * (ATemp) ** 3)
        tau1 = ATX * exp(-sqrt(OD / 2) * (ATA1 + ATB1 * sqrt(h2o))) + (1 - ATX) * exp(
            -sqrt(OD / 2) * (ATA2 + ATB2 * sqrt(h2o)))
        tau2 = ATX * exp(-sqrt(OD / 2) * (ATA1 + ATB1 * sqrt(h2o))) + (1 - ATX) * exp(
            -sqrt(OD / 2) * (ATA2 + ATB2 * sqrt(h2o)))

        # radiance from the environment
        raw_refl1 = PR1 / (PR2 * (exp(PB / (RTemp + 273.15)) - PF)) - PO
        raw_refl1_attn = (1 - E) / E * raw_refl1
        raw_atm1 = PR1 / (PR2 * (exp(PB / (ATemp + 273.15)) - PF)) - PO
        raw_atm1_attn = (1 - tau1) / E / tau1 * raw_atm1
        raw_wind = PR1 / (PR2 * (exp(PB / (IRWTemp + 273.15)) - PF)) - PO
        raw_wind_attn = emiss_wind / E / tau1 / IRT * raw_wind
        raw_refl2 = PR1 / (PR2 * (exp(PB / (RTemp + 273.15)) - PF)) - PO
        raw_refl2_attn = refl_wind / E / tau1 / IRT * raw_refl2
        raw_atm2 = PR1 / (PR2 * (exp(PB / (ATemp + 273.15)) - PF)) - PO
        raw_atm2_attn = (1 - tau2) / E / tau1 / IRT / tau2 * raw_atm2
        raw_obj = (raw / E / tau1 / IRT / tau2 - raw_atm1_attn -
                   raw_atm2_attn - raw_wind_attn - raw_refl1_attn - raw_refl2_attn)

        # temperature from radiance
        temp_celcius = PB / log(PR1 / (PR2 * (raw_obj + PO)) + PF) - 273.15
        return temp_celcius

    def save_images(self, options):  
        """
        Save the extracted images
        :return:
        """
        print(self.save_path)
        thermal_filename = self.save_path + self.thermal_suffix
        image_filename = self.save_path + self.image_suffix
 
        if 'thermal' in options:
            with open(thermal_filename, 'wb') as f:
                f.write(self.flir_tags['RawThermalImage'])
        if 'rgb' in options:
            with open(image_filename, 'wb') as f:
                f.write(self.flir_tags['EmbeddedImage'])
    
    def slice_by_zoom(self):
        zoom = self.flir_tags['ZoomRatio']
        thermal_img_bytes = self.flir_tags['RawThermalImage']
        thermal_img_stream = io.BytesIO(thermal_img_bytes)
        if self.flir_tags['RawThermalImageType'] == 'PNG':
            thermal_img = Image.open(thermal_img_stream)
            thermal_np = np.array(thermal_img)
        
        size_x = int(thermal_np.shape[0] / zoom)
        size_y = int(thermal_np.shape[1] / zoom)
        x1 = int((thermal_np.shape[0] - size_x) / 2)
        y1 = int((thermal_np.shape[1] - size_y) / 2)
        x2 = thermal_np.shape[0] - x1
        y2 = thermal_np.shape[1] - y1
        if x2 - x1 != size_x:
            x2 -= 1 
        if y2 - y1 != size_y:
            y2 -= 1
        sliced_ir_img = thermal_np[x1:x2, y1:y2]

        # rgb_np = self.get_rgb_np()
        # size_x = int(rgb_np.shape[0] / zoom)
        # size_y = int(rgb_np.shape[1] / zoom)
        # x1 = int((rgb_np.shape[0] - size_x) / 2)
        # y1 = int((rgb_np.shape[1] - size_y) / 2)
        # x2 = rgb_np.shape[0] - x1
        # y2 = rgb_np.shape[1] - y1
        # if x2 - x1 != size_x:
        #     x2 -= 1 
        # if y2 - y1 != size_y:
        #     y2 -= 1
        # sliced_real_img = rgb_np[x1:x2, y1:y2]

        # self.rgb_image_np = sliced_real_img
        self.raw_image_np = sliced_ir_img

    def export_thermal_to_csv(self, directory=False, spec_path=None):
        """
        Convert thermal data in numpy to json
        :return:
        """
        if len(self.thermal_image_np) == 0:
            self.convert_temp()
        
        if directory==True:
            print(self.flir_img_filename)
            dir_list = os.path.join(self.flir_img_filename, '*.jpg')
            for filename in glob.iglob(dir_list, recursive=True):
                 
                csv_filename = filename[:-4] + '.csv'
                
                thermal_data = np.copy(self.thermal_image_np)
                np.savetxt(csv_filename, thermal_data, fmt="%.2f", delimiter=",")
            
            pass
        csv_filename = self.save_path + '.csv'
        thermal_data = np.copy(self.thermal_image_np)
        if spec_path:
            save_path = os.path.join(spec_path, csv_filename.split(os.sep)[-1])
            np.savetxt(save_path, thermal_data, fmt="%.2f", delimiter=",")
        else:
            np.savetxt(csv_filename, thermal_data, fmt="%.2f", delimiter=",")
        # if args.normalize:
        #     np.savetxt('normalized_ '+csv_filename, thermal_data, fmt="%.2f", delimiter=",")
            # with open('normalized_'+csv_filename, 'w') as nfh:
            #     writer = csv.writer(nfh, delimiter=',')
            #     writer.writerows(self.normalized_image_np)

    def load_thermal_data(self):
        """
        return thermal data array
        """
        if self.thermal_image_np == None:
            self.convert_temp()
        pixel_values = []
        for e in np.ndenumerate(self.thermal_image_np):
            x, y = e[0]
            c = e[1]
            pixel_values.append([x,y,c])

        return pixel_values

    
    def export_thermal_to_np(self, flir_input, normalize=False):
        """
            Convert thermal path, open data convert temperature
        
            return Thermal Numpy
        """
        if self.thermal_image_np == None:
            self.convert_temp()
        if os.path.isdir(flir_input):

            dir_list = os.path.join(flir_input,'*.jpg')
            termal_list=[]
            for filename in glob.iglob(dir_list, recursive=True):
                print(filename)
                self.process_image(filename)
                if normalize:
                    resized_img = cv2.resize(self.normalized_image_np, (640, 480))
                    termal_list.append(resized_img)
                else:
                    resized_img = cv2.resize(self.thermal_image_np, (640, 480))
                    termal_list.append(resized_img)
            #Stack Thermal-Image List
            return np.stack(termal_list) 
        
        else:
            #self.process_image(flir_input)
            if normalize:
                return self.normalized_image_np
            else:
                return self.thermal_image_np
    
    def show_tags(self):
        print('FLIR_TAGS')
        for key in self.flir_tags.keys():
            if key == 'Palette': continue
            if key == 'RawThermalImage': continue
            if key == 'EmbeddedImage': continue
            print(key, self.flir_tags[key])

    def save_pal(self):
        """
        save palette file as csv
        """
        self.pal.to_csv(self.save_path + '_pal.csv')

    def imread(self, filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8): 
        try: 
            n = np.fromfile(filename, dtype) 
            img = cv2.imdecode(n, flags) 
            return img 
        except Exception as e: 
            print(e)
            return None

    def Boundary(self):
        self.ir_real_fusion()
        img_rgb = self.crop_rgb
        img_ir = self.heatmap_image
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

        thr = cv2.Laplacian(gray, cv2.CV_8U, ksize=5)
        thr = np.where(thr > 250, thr, 0)
        thr = cv2.cvtColor(thr, cv2.COLOR_GRAY2BGR)

        # thr = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, c, k)
        # thr = cv2.cvtColor(thr, cv2.COLOR_GRAY2BGR)
        # # boundx = cv2.Sobel(img_rgb, -1, 1, 0, ksize = 3)
        # # boundy = cv2.Sobel(img_rgb, -1, 0, 1, ksize = 3)
        bound = cv2.addWeighted(thr, 0.2, img_ir, 0.8, 0)
        # res = np.where(bound > 30, img_rgb, img_ir)

        return bound

    def export_flir_to_rawflr(self, filename):
        return self.imread(filename)

    def ir_real_fusion(self, option = ''):
        """[summary]
            fusion with ir image and real image
        Args:
            option (str): [description]
            two options can use : crop, fusion
            'crop' : real image that sliced to fit ir image
            'fusion' : fusion with ir and real image
        """
        rgb_np = self.rgb_image_np
        rgb_np = cv2.cvtColor(rgb_np, cv2.COLOR_BGR2RGB)
        real2ir = self.flir_tags['Real2IR']

        # fd = self.flir_tags['FocusDistance'] # FocusDistance 기준으로 Offset 조절 (미사용) -- offset / w 시 정확도 어느정도 증가, 근데 매우 드문 경우 곱해야 정확해지는 경우 있음
        # if fd != 0:
        #     w = - log(fd/(fd+0.3)) + 1
        # else:
        #     w = 1
        
        # test_orit = self.export_flir_to_rawflr(self.flir_img_filename)
        if len(self.heatmap_image) == 0:
            self.thermal_palatte_conversion(is_colorbar=False, is_thermal=False)
        test_orit=self.heatmap_image
        # print(np.shape(test_orit))
        ir_x = np.shape(test_orit)[1]
        ir_y = np.shape(test_orit)[0]
        fusion_x = int(ir_x * real2ir)
        fusion_y = int(ir_y * real2ir)

        rgb_img = cv2.resize(rgb_np, (fusion_x, fusion_y))
        _real2ir = real2ir / (real2ir - 1)
        #_real2ir = _real2ir / w

        zoom = self.flir_tags['ZoomRatio']
        center_x = int(fusion_x / 2) + int(self.flir_tags['OffsetX'] / _real2ir * (1 / zoom))
        center_y = int(fusion_y / 2) + int(self.flir_tags['OffsetY'] / _real2ir * (1 / zoom))

        x1 = center_x - int(ir_x / 2)
        x2 = center_x + int(ir_x / 2)
        y1 = center_y - int(ir_y / 2)
        y2 = center_y + int(ir_y / 2)

        if x2 - x1 < ir_x:
            x2 += 1
        if y2 - y1 < ir_y:
            y2 += 1

        rgb_res = np.copy(rgb_img)
        rgb_img = rgb_img[y1:y2 , x1:x2]
        try:
            rgb_res[y1:y2 , x1:x2] = test_orit
        except:
            print('img is to small')
            return
        
        # if 'crop' in option:
        #     cv2.imwrite(self.save_path + '_crop.png', rgb_img)
        # if 'fusion' in option:
        #     cv2.imwrite(self.save_path + '_fusion.png', rgb_res)

        # self.crop_rgb = rgb_img
        if option == 'crop':
            return rgb_img
        elif option == 'fusion':
            return rgb_res
    
    def ir_real_fusion_tmp(self, option = ''):
        """[summary]
            fusion with ir image and real image
        Args:
            option (str): [description]
            two options can use : crop, fusion
            'crop' : real image that sliced to fit ir image
            'fusion' : fusion with ir and real image
        """
        rgb_np = self.rgb_image_np
        rgb_np = cv2.cvtColor(rgb_np, cv2.COLOR_BGR2RGB)
        real2ir = self.flir_tags['Real2IR']

        rgb_y, rgb_x = rgb_np.shape[1], rgb_np.shape[0]
        center_x = int(rgb_x / 2) + self.flir_tags['OffsetY']
        center_y = int(rgb_y / 2) + self.flir_tags['OffsetX']
        
        _real2ir = real2ir / (real2ir - 1)
        ir_x = int(self.raw_image_np.shape[1] * _real2ir)
        ir_y = int(self.raw_image_np.shape[0] * _real2ir)

        x1 = center_x - int(ir_x / 2)
        x2 = center_x + int(ir_x / 2)
        y1 = center_y - int(ir_y / 2)
        y2 = center_y + int(ir_y / 2)

        if x2 - x1 < ir_x:
            x2 += 1
        if y2 - y1 < ir_y:
            y2 += 1

        rgb_img = rgb_np[y1:y2, x1:x2]
        rgb_img = cv2.resize(rgb_img, (self.raw_image_np.shape[1], self.raw_image_np.shape[0]))
        if option == 'crop':
            return rgb_img

    def pip_with_coords(self, x1, y1, x2, y2):
        if len(self.crop_rgb) == 0:
            self.crop_rgb = self.ir_real_fusion(option = 'crop')
        
        if len(self.heatmap_image) == 0:
            self.heatmap_image = self.thermal_palatte_conversion(is_colorbar=False, is_thermal=False)
        
        rgb_np = np.array(self.crop_rgb)
        rgb_np[x1:x2, y1:y2] = self.heatmap_image[x1:x2, y1:y2]
        return rgb_np

    def ir_real_fusion_flir_tool(self, options):
        rgb_np = self.rgb_image_np
        rgb_np = cv2.cvtColor(rgb_np, cv2.COLOR_BGR2RGB)
        real2ir = self.PiPTags['Real2IR']

        # test_orit = self.export_flir_to_rawflr(self.flir_img_filename)
        test_orit=self.export_flir_to_rawflr(self.flir_img_filename)
        ir_x = np.shape(test_orit)[1]
        ir_y = np.shape(test_orit)[0]
        fusion_x = int(ir_x * real2ir)
        fusion_y = int(ir_y * real2ir)

        rgb_img = cv2.resize(rgb_np, (fusion_x, fusion_y))
        _real2ir = real2ir / (real2ir - 1)
        # if self._flip:
        #     center_x = int(fusion_x / 2) + int(self.PiPTags['OffsetY'] / _real2ir)
        #     center_y = int(fusion_y / 2) + int(self.PiPTags['OffsetX'] / _real2ir)
        # else:
        center_x = int(fusion_x / 2) + int(self.PiPTags['OffsetX'] / _real2ir)
        center_y = int(fusion_y / 2) + int(self.PiPTags['OffsetY'] / _real2ir)

        x1 = center_x - int(ir_x / 2)
        x2 = center_x + int(ir_x / 2)
        y1 = center_y - int(ir_y / 2)
        y2 = center_y + int(ir_y / 2)

        if x2 - x1 < ir_x:
            x2 += 1
        if y2 - y1 < ir_y:
            y2 += 1

        rgb_img = rgb_img[y1:y2 , x1:x2]

        x1 = self.PiPTags['PiPX1']
        x2 = self.PiPTags['PiPX2']
        y1 = self.PiPTags['PiPY1']
        y2 = self.PiPTags['PiPY2']

        # rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2RGB)
        if 'real' in options:
            # cv2.imwrite(self.save_path + '_real.png', rgb_img)
            return rgb_img
        rgb_img[y1:y2, x1:x2] = test_orit[y1:y2, x1:x2]

        if 'fusion' in options:
            # cv2.imwrite(self.save_path + '_fusion.png', rgb_img)
            return rgb_img


if __name__ == '__main__':
    pass