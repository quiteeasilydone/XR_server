import numpy as np
import json
from flask import Flask, request, jsonify
import ssl
import random
import time
from Flir.temp import pallete

app = Flask(__name__)

@app.route('/flir', methods=['POST'])
def perform_analyze():
    data = request.get_json()
    id = data['id']
    palettemode = data['palettemode']
    option = data['option']
    
    result = pallete(id, palettemode, option)
    print(type(result['raw']))

    return result

if __name__ == '__main__':
    
    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    # ssl_context.load_cert_chain(certfile='../cert/certificate.crt', keyfile='../cert/private.key')
    app.run(host='127.0.0.1', port=5001)