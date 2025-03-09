import os
import joblib
import pickle
import numpy as np
import PyPDF2  # Library for extracting text from PDFs
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer

# ✅ Load scikit-learn model properly (OneVsRestClassifier)
MODEL_PATH = os.path.join(settings.BASE_DIR, 'model.joblib')

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found: {MODEL_PATH}. Please convert model.pkl to model.joblib.")

print("🔄 Loading job classification model...")
model = joblib.load(MODEL_PATH)  # Load OneVsRestClassifier model
print("✅ Model loaded successfully!")

# ✅ Load the tokenizer (TF-IDF Vectorizer used in training)
TOKENIZER_PATH = os.path.join(settings.BASE_DIR, 'resumescan', 'tfidf.pkl')

if not os.path.exists(TOKENIZER_PATH):
    raise FileNotFoundError(f"Tokenizer file not found: {TOKENIZER_PATH}")

with open(TOKENIZER_PATH, 'rb') as f:
    vectorizer = pickle.load(f)

# ✅ Load job roles from the CSV file
CSV_PATH = os.path.join(settings.BASE_DIR, 'UpdatedResumeDataSet.csv')

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

# ✅ Read CSV and ensure correct column exists
df = pd.read_csv(CSV_PATH)
df.columns = df.columns.str.strip()  # Removing extra spaces in column names

EXPECTED_COLUMN = "Category"  # Change this if needed
if EXPECTED_COLUMN not in df.columns:
    raise KeyError(f"Error: Column '{EXPECTED_COLUMN}' not found in CSV. Available columns: {df.columns}")

# ✅ Load job titles (categories)
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
    Converts raw text into TF-IDF features suitable for model prediction.
    """
    extracted_text = extracted_text.lower()
    transformed_text = vectorizer.transform([extracted_text])  # Use TF-IDF vectorizer
    return transformed_text

def decode_predictions(prediction_proba):
    """
    Returns the best predicted job role.
    """
    # ✅ Ensure we are working with probabilities
    if len(prediction_proba.shape) == 1:
        prediction_proba = prediction_proba.reshape(1, -1)

    # ✅ Get the index of the best job role
    best_index = np.argmax(prediction_proba[0])  # Get the highest probability index

    # ✅ Ensure the index is within range
    if best_index >= len(JOB_CLASSES):
        print("⚠ Warning: No valid predictions found.")
        return "Unknown"

    return JOB_CLASSES[best_index]  # ✅ Return only the best job role

@csrf_exempt
def predict(request):
    """
    API endpoint to predict job roles from uploaded resumes.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        # ✅ Ensure 'file' exists in request
        if 'file' not in request.FILES:
            return JsonResponse({"error": "No file part in the request"}, status=400)

        file = request.FILES['file']
        if file.name == '':
            return JsonResponse({"error": "No file selected"}, status=400)

        # ✅ Save file temporarily
        filepath = os.path.join('uploads', file.name)
        path = default_storage.save(filepath, ContentFile(file.read()))
        full_path = os.path.join(settings.MEDIA_ROOT, path)

        # ✅ Extract text from the uploaded PDF resume
        extracted_text = extract_text_from_pdf(full_path)
        if not extracted_text:
            return JsonResponse({"error": "Could not extract text from the resume"}, status=400)

        # ✅ Preprocess text (Convert to TF-IDF features)
        processed_text = preprocess_text(extracted_text)
        if processed_text is None or processed_text.shape[1] == 0:
            return JsonResponse({"error": "Preprocessing failed: No valid words found in resume."}, status=400)

        # ✅ Make prediction using scikit-learn model (Get probabilities)
        prediction_proba = model.predict_proba(processed_text)

        # ✅ Decode prediction
        predicted_job_roles = decode_predictions(prediction_proba)

        return JsonResponse({"result": {"job_roles": predicted_job_roles}}, status=200)

    except Exception as e:
        print(f"❌ Error in predict(): {str(e)}")
        return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)