import os
import numpy as np
import tensorflow as tf
import pickle
import PyPDF2  # Library for extracting text from PDFs
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences


# ✅ Load the trained TensorFlow model (Ensure it's in .h5 format)
MODEL_PATH = os.path.join(settings.BASE_DIR, 'jobPredictionModel.h5')
model = tf.keras.models.load_model(MODEL_PATH)

# ✅ Load the tokenizer used during training (Ensure it's in .pkl format)
TOKENIZER_PATH = os.path.join(settings.BASE_DIR, 'resumescan', 'tokenizer.pkl')
with open(TOKENIZER_PATH, 'rb') as f:
    tokenizer = pickle.load(f)

# ✅ Maximum sequence length used in training
MAX_SEQUENCE_LENGTH = 500  

# ✅ List of job roles (Ensure these match the model's output labels)
JOB_CLASSES = ["Software Engineer", "Data Scientist", "Product Manager", "Cybersecurity Analyst", "ML Engineer",
    "Network Engineer", "Database Administrator", "Business Analyst", "AI Engineer", "Frontend Developer",
    "Backend Developer", "DevOps Engineer", "Cloud Architect", "Security Analyst", "Software Architect",
    "Mobile Developer", "Game Developer", "Blockchain Developer", "Technical Support", "Data Engineer",
    "UI/UX Designer", "Embedded Engineer", "IT Manager", "Full Stack Developer", "Systems Administrator"]

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
    extracted_text = extracted_text.lower()  # Convert to lowercase
    sequence = tokenizer.texts_to_sequences([extracted_text])  # Tokenize text

    if not sequence or len(sequence[0]) == 0:
        print("Error: Tokenized sequence is empty. Check the input text:", extracted_text)
        return None  # Return None instead of an empty sequence

    padded_sequence = pad_sequences(sequence, maxlen=MAX_SEQUENCE_LENGTH, padding='post')  # Pad sequence
    return padded_sequence

def decode_prediction(prediction):
    """
    Decodes model output into a job role and confidence score.
    """
    print("Prediction array:", prediction)  # Debugging print

    predicted_index = np.argmax(prediction)  # Get index of highest probability

    # ✅ Fix: Ensure the predicted index is within the valid range
    if predicted_index >= len(JOB_CLASSES):
        print(f"Error: Predicted index {predicted_index} is out of range for JOB_CLASSES.")
        return "Unknown", 0.0  # Return a default value instead of crashing

    predicted_job_role = JOB_CLASSES[predicted_index]  # Map index to job role
    confidence = np.max(prediction) * 100  # Convert confidence to percentage

    return predicted_job_role, confidence

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

        # ✅ Decode prediction
        predicted_job_role, confidence = decode_prediction(prediction)

        return JsonResponse({"result": {"job_role": predicted_job_role, "confidence": float(confidence)}}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)