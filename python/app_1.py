import numpy as np
import json
from flask import Flask, request, jsonify
from fourier import fourier
from rms import rms
import ssl
import torch
import model.decoder as decoder

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def perform_analyze():
    data = request.get_json()
    model = decoder()
    model = torch.load_state_dict('./model/decoder.pt')
    sensor_name = request.args.get('sensor')

    # sensor_data = [print(entry.keys()) for entry in data['data']]
    sensor_data = [entry[sensor_name] for entry in data['data']]
    label_data = model(torch.tensor(sensor_data).unsqueeze(0))
    
    print(sensor_data)
    
    if data['transform'] == 'Normal':
        result = {'vibe' : sensor_data, 'label' : label_data}
    elif data['transform'] == 'FFT':
        # print(sensor_data)  
        nfft = len(sensor_data)  # FFT 점수, 데이터 길이와 같음
        fs = 1000  # 샘플링 주파수, 예시 값
        result = fourier(nfft, fs, np.array(sensor_data))
        result['label'] = label_data
    else:
        result = rms(sensor_data)
        result['label'] = label_data

    return result

if __name__ == '__main__':
    
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    ssl_context.load_cert_chain(certfile='../cert/certificate.crt', keyfile='../cert/private.key')
    app.run(host='127.0.0.1', ssl_context=ssl_context)