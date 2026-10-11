"""
Flask WSGI wrapper for ML Backend
"""

import os
from flask import Flask, request, jsonify, Response
from ml_backend import get_ml_backend

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
    html = """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>MUQ ML Backend</title>
      <style>
        :root {
          --bg: #0f172a;
          --panel: #111827;
          --panel-2: #1f2937;
          --text: #e5e7eb;
          --muted: #9ca3af;
          --accent: #38bdf8;
          --accent-2: #22c55e;
        }
        * { box-sizing: border-box; }
        body {
          margin: 0;
          background: linear-gradient(135deg, #020817, var(--bg));
          color: var(--text);
          font-family: Arial, sans-serif;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .container {
          width: min(960px, 90vw);
          background: rgba(17, 24, 39, 0.9);
          border: 1px solid rgba(148, 163, 184, 0.2);
          border-radius: 18px;
          padding: 32px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
        }
        h1 {
          margin: 0 0 12px;
          font-size: 2rem;
        }
        .tag {
          display: inline-block;
          background: rgba(56, 189, 248, 0.15);
          color: var(--accent);
          border: 1px solid rgba(56, 189, 248, 0.45);
          border-radius: 999px;
          padding: 6px 12px;
          font-size: 0.8rem;
          margin-bottom: 16px;
        }
        p {
          color: var(--muted);
          line-height: 1.6;
        }
        .cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 16px;
          margin-top: 24px;
        }
        .card {
          background: var(--panel-2);
          border: 1px solid rgba(148, 163, 184, 0.18);
          border-radius: 12px;
          padding: 18px;
        }
        .card h3 {
          margin: 0 0 10px;
          font-size: 1rem;
          color: var(--text);
        }
        code {
          display: block;
          background: rgba(15, 23, 42, 0.9);
          border-radius: 8px;
          padding: 10px 12px;
          color: #bfdbfe;
          margin-top: 8px;
          white-space: pre-wrap;
          word-wrap: break-word;
        }
        .status {
          color: var(--accent-2);
          font-weight: 700;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="tag">MUQ Backend</div>
        <h1>MUQ ML Backend</h1>
        <p class="status">Status: running</p>
        <p>This service exposes the ML and detection API endpoints used by the MUQ system. The root URL is not the application UI; the API is available through the routes below.</p>

        <div class="cards">
          <div class="card">
            <h3>Health</h3>
            <code>GET /health</code>
          </div>
          <div class="card">
            <h3>Face detection</h3>
            <code>POST /api/detect-faces</code>
          </div>
          <div class="card">
            <h3>Smoking detection</h3>
            <code>POST /api/detect-smoking</code>
          </div>
          <div class="card">
            <h3>Cheating detection</h3>
            <code>POST /api/detect-cheating</code>
          </div>
          <div class="card">
            <h3>Exam anomaly detection</h3>
            <code>POST /api/detect-anomaly</code>
          </div>
          <div class="card">
            <h3>Generic processing</h3>
            <code>POST /api/process-image</code>
          </div>
        </div>
      </div>
    </body>
    </html>
    """
    return Response(html, mimetype='text/html')


@app.route('/login', methods=['GET'])
def login_page():
    return index()


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)
