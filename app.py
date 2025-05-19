from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import glob, os
import matplotlib
matplotlib.use("Agg")
from augment.face_org import extractFace, faceCascade, detector, predictor
from werkzeug.utils import secure_filename
from pathlib import Path


app = Flask(__name__, 
            static_folder='static',      # serves /static/*
            template_folder='templates') # renders templates/*.html
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
def home():
    return render_template("index.html")

@app.route("/scan")
def scan():
    return render_template("face-scanningpage.html")

@app.route("/analyse")
def analyse():
    return render_template("analysing-page.html")

@app.route("/result")
def result():
    return render_template("results-page.html")

def preprocess_array(arr, size=128):
    """Resize a NumPy array and scale to [0,1]."""
    img = Image.fromarray(arr).convert("RGB").resize((size, size))
    return np.expand_dims(np.array(img)/255.0, axis=0)

@app.route("/predict", methods=["POST"])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    upload = request.files['file']
    fname  = secure_filename(upload.filename)
    stem   = Path(fname).stem
    tmpdir = Path("data/parsed/tmp")
    tmpdir.mkdir(parents=True, exist_ok=True)
    on_disk = tmpdir / fname
    upload.save(on_disk)

    print("→ Saved upload to:", on_disk)
    print("→ tmpdir contents:", list(tmpdir.iterdir()))

    # 2) run your face-cropper
    cropped = extractFace(
        str(on_disk),
        status="tmp",
        file_name=stem,
        faceCascade=faceCascade,
        predictor=predictor,
        detector=detector
    )
    print("→ extractFace returned:", cropped)

    if cropped is None:
        return jsonify(error="No face detected"), 400

    # 3) make sure all five crops are there
    print("→ looking for crops:")
    for feat in face_features:
        p = tmpdir / f"{stem}_{feat}.png"
        print(f"    {feat:10s} -> exists={p.exists()} ({p.name})")
        if not p.exists():
            return jsonify(error=f"Missing crop for {feat}"), 500


    votes = []
    confidence_scores = {}

    for feat in face_features:
        p = tmpdir / f"{stem}_{feat}.png"
        print(f"    {feat:10s} -> {p.exists()}  ({p})")
        crop = tmpdir / f"{stem}_{feat}.png"
        if not crop.exists():
            return jsonify(error=f"Missing crop for {feat}"), 500

        arr = np.array(Image.open(str(crop)))
        x   = preprocess_array(arr)
        p   = float(models[feat].predict(x)[0][0])
        label = "Sick" if p > 0.5 else "Healthy"

        votes.append(label)
        confidence_scores[feat] = p


    sick_votes = votes.count("Sick")
    healthy_votes = votes.count("Healthy")
    final_result = "Sick" if sick_votes > healthy_votes else "Healthy"

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
