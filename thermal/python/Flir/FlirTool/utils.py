import struct
import pandas as pd
import cv2

def ord_(dta):
    if isinstance(dta, str):
        return ord(dta)
    return dta

def palatte_converter(pal):
    """
    return pandas palette
    """
    r = list()
    g = list()
    b = list()
    y = list()
    cb = list()
    cr = list()
    for i in range(0, len(pal), 3):
        y.append(struct.unpack('>B', pal[i:i+1])[0])
    for i in range(1, len(pal), 3):
        cr.append(struct.unpack('>B', pal[i:i+1])[0])
    for i in range(2, len(pal), 3):
        cb.append(struct.unpack('>B', pal[i:i+1])[0])
    for i in range(len(y)):
        r.append(int(y[i] + 1.402 * (cr[i] - 128)))
        g.append(int(y[i] - 0.344136 * (cb[i] - 128) - 0.714136 * (cr[i] - 128)))
        b.append(int(y[i] + 1.772 * (cb[i] - 128)))
    p = pd.DataFrame()
    p['red'] = pd.Series(r)
    p['green'] = pd.Series(g)
    p['blue'] = pd.Series(b)
    p['red'] = cv2.normalize(p['red'].to_numpy(), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    p['green'] = cv2.normalize(p['green'].to_numpy(), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
    p['blue'] = cv2.normalize(p['blue'].to_numpy(), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

    return p


def raw2temp(raw, E=1, OD=1, RTemp=20, ATemp=20, IRWTemp=20, IRT=1, RH=50, PR1=21106.77, PB=1501, PF=1, PO=-7340,
                PR2=0.012545258):
    """
    convert raw values from the flir sensor to temperatures in C
    # this calculation has been ported to python from
    # https://github.com/gtatters/Thermimage/blob/master/R/raw2temp.R
    # a detailed explanation of what is going on here can be found there
    """
    # print(E, OD, RTemp, ATemp, IRWTemp, IRT, RH, PR1, PB, PF, PO, PR2)
    # constants

    ATA1 = 0.006569
    ATA2 = 0.01262
    ATB1 = -0.002276
    ATB2 = -0.00667
    ATX = 1.9

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