import numpy as np
import json
from flask import Flask, request, jsonify
from fourier import fourier

app = Flask(__name__)

@app.route('/fourier', methods=['POST'])
def test():
    lists = request.args['file_name']
    lists = lists.split(',')
    data = []
    for list in lists:
        data.append(list)

    return jsonify({
        'result': data
    })

if __name__ == '__main__':
    app.run()