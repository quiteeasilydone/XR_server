from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from flir_image_extractor import FlirImageExtractor
import numpy as np
import sys
from PIL import Image
import cv2
import pandas as pd

##정무함수랑 연동하는 부분 여기함수 리턴이랑 파리미터 형태만 지켜줘

class UI_Control:
# 지정한 좌표 영역만 옇화상인 pip 이미지
    def __init__(self, path):
        self.flir = FlirImageExtractor()
        self.flir.process_image(path)
        self.rgb_img = self.flir.ir_real_fusion(option = 'crop')
        self.ir_img = self.flir.get_heatmap_image_np()
        self.ir_img = cv2.cvtColor(self.ir_img, cv2.COLOR_BGR2RGB)
        self.thermal = self.flir.get_thermal_np()

    def getPipImage_area(self, left_x,left_y,right_x,right_y)->QPixmap:
        img_arr = self.flir.pip_with_coords(left_x, left_y, right_x, right_y)
        img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(img_arr)
        img = Qpixmap.fromImage(im)
        # print('pip')
        return img

    # # 좌표 지정 없음, 열화상영역 전체를 보여줌
    def getPipImage(self)->QPixmap:
        im = Image.fromarray(self.ir_arr)
        img = QPixmap.fromImage(im)
        # print('pip')
        return img

    #return MixImage 열혼합이미지  
    def getMixImage(self, alpha:float)->QPixmap:
        bld_img = cv2.addWeighted(self.rgb_img, alpha, self.ir_img, (1-alpha), 0)
        im = Image.fromarray(bld_img)
        img = QPixmap.fromImage(im)
        return img

    # return Thumal Image ( <640x480 )
    def getThermalImage(self)->QPixmap:
        im = Image.fromarray(self.ir_img)
        img = QPixmap.fromImage(im)
        # print('thumal')
        return img

    # return RealIMage
    def getRealImage(self)->QPixmap:
        im = Image.fromarray(self.rgb_img)
        img = QPixmap.fromImage(im)
        # print('real')
        return img

    # 사각형 좌측 상단, 우측 하단 좌표 입력시 박스영역에 rawdata 반환 (2차원)
    def getRawData_area(self, left_x,left_y,right_x,right_y)->np.array:
        raw_data = np.array(self.thermal[left_x:right_x, left_y:right_y])
        return raw_data

    #해당 파일에 전체 rawdata 값 반환
    def getRawData_path(self)->np.array:
        return self.thermal

    #해당좌표의 raw데이터 값
    def getRawData_point(self, x,y)->float:
        return self.thermal[x][y]

    #파일에 저장된 디바이스 정보 불러오기
    def getDeviceData(self)->dict:
        info_list = ['CameraModel', 'LensModel', 'PlanckO', 'PlanckR1', 'PlanckR1', 'PlanckB', 'PlanckF']
        data = {}
        for key in info_list:
            data[key] = self.flir.flir_tags[key]
        return data

    #받은 이미지에 pal_type에 해당하는 팔레트 적용 이미지 반환
    def getPalette_img(self, img:QPixmap, pal_type:str)->QPixmap:
        """
            img: 팔레트 적용 시킬 이미지
            pal_type: 적용시킬 팔레트 종류 (rainbow,red)
        """ 
        pal = pd.read_csv(pal_type)
        img_arr = self.flir.thermal_palatte_conversion(is_colorbar = False, pal = pal, is_thermal = False)
        im = Image.fromarray(img_arr)
        img = QPixmap.fromImage(im)
        return img
