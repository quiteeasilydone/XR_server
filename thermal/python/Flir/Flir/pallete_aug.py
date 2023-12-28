import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
import cv2
import os
from collections import OrderedDict
import matplotlib.image as mpimg
import copy
import time
import random
from matplotlib.colors import ListedColormap
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from math import tan, sqrt, log
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

plt.rcParams.update({'figure.max_open_warning': 0})

def get_cmap(_cmap, cnt, reg_rate = False, rate = None):
    
    cmap = _cmap.to_numpy()/255
    
    length, h = cmap.shape
    
    # mid_idx = int(length*0.5)
    if reg_rate:
        size = int(length / cnt)
        rate = np.array(rate)

        X = []
        for idx in range(cnt):
            X.append(cv2.resize(cmap[size * idx:size * (idx + 1), :], (h, int(size *rate[idx]) + 1)))

        cmap = np.vstack(X)
        cmap = cv2.resize(cmap, (h, length))

    return ListedColormap(cmap)

def normalize_thermal(data):
    # normalizedImg = np.zeros((480, 640))
    normalizedImg = cv2.normalize(data, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    return normalizedImg

def figure_to_array(fig):
    """
    plt.figure를 RGBA로 변환(layer가 4개)
    shape: height, width, layer
    """
    fig.canvas.draw()
    data = np.array(fig.canvas.renderer._renderer)
    data = cv2.cvtColor(data, cv2.COLOR_BGRA2RGB)
    return data

def removeOutliers(x, outlierConstant=10):
    
    a = copy.deepcopy(x)
    #a = np.abs(stats.zscore(a))
    upper_quartile = np.percentile(a, 75)
    lower_quartile = np.percentile(a, 25)
    IQR = (upper_quartile - lower_quartile) * outlierConstant
    quartileSet = (lower_quartile - IQR, upper_quartile + IQR)
    #print(quartileSet)
    
    t = np.where((a >= quartileSet[0]), a, quartileSet[0])
    result = np.where((t <= quartileSet[1]), t, quartileSet[1])
    
    return result

def open_path_array(csv_path, csv=True):
    # Checking if the file exist
    if not os.path.isfile(csv_path):
        print("File {} does not exist!".format(csv_path))
        raise EOFError
        # Reading image as numpy matrix in gray scale (image, color_param)
    if csv_path.lower().endswith(('.csv')):
        data = np.loadtxt(csv_path, delimiter=',')
    elif csv_path.lower().endswith(('.json')):
        import json
        with open(csv_path, 'r') as f:
            json_data = json.load(f)
        data = json_data['tempData']
    return data

def heatMapConvert(data, palette, minmax, is_colorbar, reg_rate):
    #Deep Copy Original Thermal Data
    ori_data = copy.deepcopy(data)

    _min = minmax[0]
    _max = minmax[1]

    # number to divide palette
    field_num  = 6
    w = (_max - _min) / field_num
    cnt = np.zeros(field_num)
    mid = np.zeros(field_num + 1)
    mid[0] = _min
    mid[field_num] = _max
    _rate = np.zeros(field_num)
    rate = []

    for idx in range(field_num):
        cnt[idx] = np.logical_and(data >= _min + w * idx, data < _min + w * (idx + 1)).sum()
    
    for idx in range(field_num):
        rate.append(cnt[idx] / cnt.sum())

    tmp = []
    for idx in range(field_num):
        tmp.append('%.5f' % rate[idx])
    # print(tmp)

    weight = np.array(rate)
    # rate = np.where(rate < 0.01, rate - 0.1, rate)
    rate = np.full(field_num, 1) - rate

    for _idx in range(30):
        # get rate of how many pixels each palette field
        _sum = 0.0
        for idx in range(field_num):
            _sum += rate[idx]
        for idx in range(field_num):
            _rate[idx] = rate[idx] / _sum
        for idx in range(1, field_num):
            mid[idx] = mid[idx - 1] + (_max - _min) * _rate[idx - 1]
        for idx in range(field_num):
            cnt[idx] = np.logical_and(data >= mid[idx], data < mid[idx + 1]).sum()
        for idx in range(field_num):
            _rate[idx] = cnt[idx] / cnt.sum()

        if np.where(_rate < 0.1, 1, 0).sum() == 0:
            break

        for idx in range(field_num):
            rate[idx] += 10/(30.5 * _rate[idx] + 1)
            
        if np.min(rate) > 100:
            rate /= np.full(field_num, 100)
        
    tmp = []
    for idx in range(field_num):
        tmp.append('%.5f' % _rate[idx])
    # print(tmp, _idx)

    img, ax1 = plt.subplots(1, figsize=(data.shape[1] / 100, data.shape[0] / 100))
    plt.axis("off")
    plt.tight_layout()
    plt.xticks([]), plt.yticks([])
    plt.subplots_adjust(left = 0, bottom = 0, right = 1, top = 1, hspace = 0, wspace = 0)

    cmap = get_cmap(palette, field_num, rate = rate, reg_rate=reg_rate)

    
    """
    ---------- insert logo in Image -----------
    if data.shape[0] == 480 and data.shape[1] == 640:
        logo = mpimg.imread('./img/logo.png')
        img.figimage(logo, 2, 0)
    """

    psm = plt.pcolormesh(data, cmap=cmap,  vmin=_min, vmax=_max)
    ax1.pcolormesh(data, cmap=cmap, vmin=_min, vmax=_max)
    ax1.invert_yaxis()
    if is_colorbar:
        axins1 = inset_axes(ax1,
                width="3%", 
                height="85%",  
                loc='center right')
        plt.colorbar(psm, cax=axins1, ticks = [])

    tmp = np.array(figure_to_array(img))
    if is_colorbar:
        fontsize = int(sqrt(tmp.shape[0] * tmp.shape[1]) / 28.7)
        ax1.text(0.94, 0.955, str('%.1f' % _max), fontsize = fontsize, color = 'white', horizontalalignment='center', verticalalignment='center', transform=ax1.transAxes)
        ax1.text(0.94, 0.03, str('%.1f' % _min), fontsize = fontsize, color = 'white', horizontalalignment='center', verticalalignment='center', transform=ax1.transAxes)
    _data = figure_to_array(img)
    plt.clf()

    return _data

def heatmapConverter(data, palette, is_colorbar, minmax, option = 'd'):
    if option == 'd':
        img = heatMapConvert(data, palette, minmax = minmax, is_colorbar = is_colorbar, reg_rate = True)
    if option == 'o':
        img = heatMapConvert(data, palette, minmax = minmax, is_colorbar = is_colorbar, reg_rate = False)
    return img

if __name__ == "__main__":
    pass