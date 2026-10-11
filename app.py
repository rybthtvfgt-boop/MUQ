"""
Flask WSGI wrapper for ML Backend
"""

from flask import Flask, request, jsonify
from ml_backend import get_ml_backend
import numpy as np
import cv2
import base64
import json

app = Flask(__name__)
ml = get_ml_backend()

# Initialize ML models on startup
ml.initialize()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'ML Backend is running'}), 200


@app.route('/api/process-image', methods=['POST'])
def process_image():
    """Process image with ML backend"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        task = data.get('task', 'face_recognition')
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        result = ml.process_image(image_data, task)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/detect-faces', methods=['POST'])
def detect_faces():
    """Detect faces in image"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        result = ml.process_image(image_data, 'face_recognition')
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/detect-smoking', methods=['POST'])
def detect_smoking():
    """Detect smoking in image"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        result = ml.process_image(image_data, 'smoking_detection')
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/detect-cheating', methods=['POST'])
def detect_cheating():
    """Detect cheating behavior in image"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        result = ml.process_image(image_data, 'cheating_detection')
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/detect-anomaly', methods=['POST'])
def detect_anomaly():
    """Detect exam anomalies in image"""
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        result = ml.process_image(image_data, 'exam_anomaly')
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        'name': 'MUQ ML Backend',
        'version': '1.0',
        'status': 'running',
        'endpoints': {
            '/health': 'Health check',
            '/api/detect-faces': 'Detect faces',
            '/api/detect-smoking': 'Detect smoking',
            '/api/detect-cheating': 'Detect cheating behavior',
            '/api/detect-anomaly': 'Detect exam anomalies'
        }
    }), 200


@app.errorhandler(404)
def not_found(error):
    """404 handler"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 handler"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
