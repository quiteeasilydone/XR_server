import numpy as np 

def rms(vibe):
    
    s_value = np.power(vibe,2)
    m_value = np.mean(s_value)
    rms_value = np.power(m_value, 0.5)
    
    return {'rms':rms_value}

# if __name__ == '__main__':
#     print(rms([1,1,1,1]))