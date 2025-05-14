from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image

app = Flask(__name__)
CORS(app)

# Facial features to vote on
face_features = ["mouth", "nose", "skin", "left_eye", "right_eye"]

# Load models for each region
models = {}
for feature in face_features:
    model_path = f'categorization/model_saves/{feature}/model.h5'
    try:
        models[feature] = tf.keras.models.load_model(model_path, compile=False)
        print(f"[INFO] Loaded model for {feature}")
    except Exception as e:
        print(f"[ERROR] Could not load model for {feature}: {e}")

def preprocess_image(file, size=128):
    img = Image.open(file).convert("RGB").resize((size, size))
    img_array = np.array(img) / 255.0
    return np.expand_dims(img_array, axis=0)

@app.route("/")
def index():
    return "Health Check API is running!"

@app.route("/predict", methods=["POST"])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file = request.files['file']
    try:
        img = preprocess_image(file)
    except Exception as e:
        return jsonify({'error': 'Image preprocessing failed', 'details': str(e)}), 500

    votes = []
    confidence_scores = {}

    for feature, model in models.items():
        try:
            prediction = model.predict(img)[0][0]
            label = 'Sick' if prediction > 0.5 else 'Healthy'
            votes.append(label)
            confidence_scores[feature] = float(prediction)
        except Exception as e:
            confidence_scores[feature] = f"Error: {str(e)}"
            votes.append("Error")

    sick_votes = votes.count("Sick")
    healthy_votes = votes.count("Healthy")
    final_result = "Sick" if sick_votes > healthy_votes else "Healthy"

    return jsonify({
        "result": final_result,
        "votes": {
            "Sick": sick_votes,
            "Healthy": healthy_votes
        },
        "confidences": confidence_scores
    })

if __name__ == "__main__":
    app.run(debug=True)
