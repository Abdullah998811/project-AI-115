from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import joblib
import os

app = Flask(__name__)

# Model load karo (pickle ya joblib dono support)
model_path = 'model.pkl'
scaler_path = 'scaler.pkl'

try:
    if os.path.exists(model_path):
        if model_path.endswith('.joblib'):
            model = joblib.load(model_path)
        else:
            model = pickle.load(open(model_path, 'rb'))
        print("Model loaded successfully!")
    else:
        model = None
        print("Warning: model.pkl not found!")

    # Scaler (optional)
    if os.path.exists(scaler_path):
        scaler = pickle.load(open(scaler_path, 'rb'))
        scaling_needed = True
    else:
        scaler = None
        scaling_needed = False
except Exception as e:
    print("Model loading error:", e)
    model = None

# IP types for one-hot encoding
IP_TYPES = ['datacenter', 'residential', 'mobile', 'vpn', 'public_proxy', 'tor']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        features = [
            float(data['inter_api_duration']),
            float(data['api_uniqueness']),
            int(data['sequence_length']),
            float(data['vsession_duration']),
            int(data['num_sessions']),
            int(data['num_users']),
            int(data['num_unique_apis'])
        ]

        # One-hot encode ip_type
        ip_type = data['ip_type']
        ip_onehot = [1 if ip_type == t else 0 for t in IP_TYPES]
        features.extend(ip_onehot)

        X = np.array([features])

        if scaling_needed and scaler:
            X = scaler.transform(X)

        if model is None:
            return jsonify({'status': 'error', 'message': 'Model not loaded!'})

        pred = model.predict(X)[0]
        prob = model.predict_proba(X)[0].max() * 100

        result = "Bot / Malicious" if pred == 1 else "Human / Benign"

        return jsonify({
            'status': 'success',
            'result': result,
            'confidence': f"{prob:.2f}%"
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    print("API Abuse Detector chal raha hai → http://127.0.0.1:5000")
    app.run(debug=True)