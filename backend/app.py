from flask import Flask, request, jsonify
import tensorflow as tf
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Load the model
MODEL_PATH = "jobPredictionModel.h5"
model = tf.keras.models.load_model(MODEL_PATH)

# Directory to store resumes temporarily
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Placeholder for actual model logic:
    # Use `filepath` to read the resume and predict.
    # For example, text extraction and prediction using `model`.
    result = {"job_role": "Software Engineer", "confidence": 95.0}

    return jsonify({"result": result}), 200

if __name__ == '__main__':
    app.run(debug=True)
