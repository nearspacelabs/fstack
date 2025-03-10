from flask import Flask
from flask_cors import CORS
from telemetry import get_telemetry

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/api/test', methods=['GET'])
def test():
    return {'ok': True}

if __name__ == '__main__':
    app.run(debug=True, port=5000) 