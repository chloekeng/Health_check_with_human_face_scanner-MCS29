from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import glob, os

app = Flask(__name__)
CORS(app)

# Facial features to vote on
# face_features = ["mouth", "nose", "skin", "left_eye", "right_eye"]
face_features = ["mouth", "nose", "skin", "left_eye", "right_eye"]

# Load models for each region
models = {}
for feature in face_features:
    pattern = os.path.join("categorization", "model_saves", feature, "model_*.h5")
    # model_path = f'categorization/model_saves/{feature}/model_*.h5'
    candidates = glob.glob(pattern)
    if not candidates:
        raise FileNotFoundError(f"No models found for '{feature}', looked for {pattern}")

    # sort by the fold number and pick the highest
    candidates.sort(key=lambda p: int(os.path.basename(p).split("_")[1].split(".")[0]))
    best_checkpoint = candidates[-1]

    print(f"[INFO] Loading {feature} model from → {best_checkpoint}")
    models[feature] = tf.keras.models.load_model(best_checkpoint, compile=False)
    # try:
    #     models[feature] = tf.keras.models.load_model(model_path, compile=False)
    #     print(f"[INFO] Loaded model for {feature}")
    # except Exception as e:
    #     print(f"[ERROR] Could not load model for {feature}: {e}")

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
    final_result = "Sick" if sick_votes >= 2 else "Healthy"

    # DEBUG: show what each “doctor” said and the final tally
    print("=== VOTING DEBUG ===")
    for feature, score in confidence_scores.items():
        vote = "Sick" if score != "Error" and score > 0.5 else "Healthy"
        print(f" - {feature}: prob={score} → vote={vote}")
    print(f" Sick votes: {sick_votes}, Healthy votes: {healthy_votes}")
    print(f" FINAL result: {final_result}")
    print("====================")

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
