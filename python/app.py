import numpy as np
import json
from flask import Flask, request, jsonify
from fourier import fourier

app = Flask(__name__)

@app.route('/fourier', methods=['POST'])
def perform_fourier():
    data = request.get_json()
    
    sensor_name = request.args.get('sensor')
    
    sensor_data = [entry[sensor_name] for entry in data['data']]
    nfft = len(sensor_data)  # FFT 점수, 데이터 길이와 같음
    fs = 1000  # 샘플링 주파수, 예시 값
    result = fourier(nfft, fs, np.array(sensor_data))

    return result

if __name__ == '__main__':
    app.run(host='165.246.44.131')