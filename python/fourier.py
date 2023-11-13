import numpy as np 
import math


def fourier(nfft, fs, vibe):
    # nfft = 샘플 개수
    # df = 주파수 증가량
    df = fs/nfft 
    k = np.arange(nfft) 
    # f = 0부터~최대주파수까지의 범위
    f = k*df 

    # 스펙트럼은 중앙을 기준으로 대칭이 되기 때문에 절반만 구함
    nfft_half = math.trunc(nfft/2)
    f0 = f[range(nfft_half)] 
    # 증폭값을 두 배로 계산(위에서 1/2 계산으로 인해 에너지가 반으로 줄었기 때문)
    fft_y = np.fft.fft(vibe)/nfft * 2 
    fft_y0 = fft_y[range(nfft_half)]
    # 벡터(복소수)의 norm 측정(신호 강도)
    amp = abs(fft_y0)
    # 상위 3개의 주파수
    idxy = np.argsort(-amp)
    arfreq = []  
    aramp = []
    for i in range(3):  
        arfreq.append(f0[idxy[i]])
        aramp.append(fft_y[idxy[i]])
        # print('freq=', f0[idxy[i]], 'amp=', fft_y[idxy[i]])
    return {'freq' : arfreq, 'amp' : aramp}