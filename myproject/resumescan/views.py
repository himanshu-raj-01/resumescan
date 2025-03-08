import os
import numpy as np
import tensorflow as tf
import pickle
import PyPDF2  # Library for extracting text from PDFs
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# ✅ Load the trained TensorFlow model (Ensure it's in .h5 format)
MODEL_PATH = os.path.join(settings.BASE_DIR, 'resume_predict_model.h5')
model = tf.keras.models.load_model(MODEL_PATH)

# ✅ Load the tokenizer used during training (Ensure it's in .pkl format)
TOKENIZER_PATH = os.path.join(settings.BASE_DIR, 'resumescan', 'tokenizer.pkl')
with open(TOKENIZER_PATH, 'rb') as f:
    tokenizer = pickle.load(f)

# ✅ Maximum sequence length used in training
MAX_SEQUENCE_LENGTH = 200  

# ✅ Load job roles from the CSV file
CSV_PATH = os.path.join(settings.BASE_DIR, 'UpdatedResumeDataSet.csv')

# ✅ Read CSV and print column names for debugging
df = pd.read_csv(CSV_PATH)
df.columns = df.columns.str.strip()  # ✅ Remove extra spaces in column names

print("CSV Column Names:", df.columns)  # Debugging print

# ✅ Ensure correct column exists
EXPECTED_COLUMN = "Category"  # Change this if needed
if EXPECTED_COLUMN not in df.columns:
    raise KeyError(f"Error: Column '{EXPECTED_COLUMN}' not found in CSV. Available columns: {df.columns}")

# ✅ Load job titles
JOB_CLASSES = df[EXPECTED_COLUMN].unique().tolist()

def extract_text_from_pdf(filepath):
    """
    Extracts text from a PDF file.
    """
    text = ""
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in range(len(reader.pages)):
            extracted_text = reader.pages[page].extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text.strip()

def preprocess_text(extracted_text):
    """
    Converts raw text into a numerical sequence suitable for model prediction.
    """
    extracted_text = extracted_text.lower()
    sequence = tokenizer.texts_to_sequences([extracted_text])

    if not sequence or len(sequence[0]) == 0:
        print("Error: Tokenization resulted in an empty sequence.")
        return None

    padded_sequence = pad_sequences(sequence, maxlen=MAX_SEQUENCE_LENGTH, padding='post')
    return padded_sequence

def decode_predictions(prediction):
    """
    Returns the top 5 predicted job roles, ensuring index safety.
    """
    num_classes = len(JOB_CLASSES)  # Get the actual number of job classes
    top_indices = np.argsort(prediction[0])[-5:][::-1]  # Get top 5 indices

    # ✅ Ensure predicted indices do not exceed available job classes
    valid_indices = [i for i in top_indices if i < num_classes]

    if not valid_indices:
        print(f"Warning: No valid predictions found. Model output shape: {prediction.shape}")
        return ["Unknown"]  # Default if no valid indices

    predicted_roles = [JOB_CLASSES[i] for i in valid_indices]
    return predicted_roles

@csrf_exempt
def predict(request):
    if request.method == 'POST':
        if 'file' not in request.FILES:
            return JsonResponse({"error": "No file part"}, status=400)

        file = request.FILES['file']
        if file.name == '':
            return JsonResponse({"error": "No selected file"}, status=400)

        # ✅ Save file temporarily
        filepath = os.path.join('uploads', file.name)
        path = default_storage.save(filepath, ContentFile(file.read()))
        full_path = os.path.join(settings.MEDIA_ROOT, path)

        # ✅ Extract text from the uploaded PDF resume
        extracted_text = extract_text_from_pdf(full_path)
        if not extracted_text:
            return JsonResponse({"error": "Could not extract text from the resume"}, status=400)

        # ✅ Preprocess text
        processed_text = preprocess_text(extracted_text)
        if processed_text is None:
            return JsonResponse({"error": "Tokenization failed: No valid words found in resume."}, status=400)

        # ✅ Make prediction
        prediction = model.predict(processed_text)

        # ✅ Debugging: Print model output
        print("Prediction shape:", prediction.shape)
        print("Raw prediction array:", prediction)

        # ✅ Decode prediction
        predicted_job_roles = decode_predictions(prediction)

        return JsonResponse({"result": {"job_roles": predicted_job_roles}}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)