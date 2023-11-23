import numpy as np
import json
from flask import Flask, request, jsonify
from fourier import fourier
from rms import rms
import ssl

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def perform_analyze():
    data = request.get_json()
    
    print(data)
    sensor_name = request.args.get('sensor')

    # sensor_data = [print(entry.keys()) for entry in data['data']]
    sensor_data = [entry[sensor_name] for entry in data['data']]
    label_data = max([entry['label'] for entry in data['data']])
    
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
    ssl_context.load_cert_chain(certfile='./mkcert+7.pem', keyfile='./mkcert+7-key.pem')
    app.run(host='127.0.0.1', ssl_context=ssl_context)