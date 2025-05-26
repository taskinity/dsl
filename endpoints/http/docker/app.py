from flask import Flask, jsonify, request
import logging
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def hello():
    return jsonify({
        'service': 'http-mock',
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        'id': 1,
        'name': 'Test Data',
        'value': 42,
        'active': True
    })

@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.get_json()
    return jsonify({
        'status': 'success',
        'received': data
    })

@app.route('/api/status/<status_code>', methods=['GET'])
def status_code(status_code):
    try:
        code = int(status_code)
        return jsonify({
            'status': 'success',
            'code': code
        }), code
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid status code'
        }), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
