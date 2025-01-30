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
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            # Save the uploaded file
            uploaded_file = request.FILES['file']
            file_name = default_storage.save(uploaded_file.name, uploaded_file)
            file_path = default_storage.path(file_name)

            # Process the file (replace this with your actual prediction logic)
            # For demonstration, we'll create a dummy prediction array
            prediction_array = np.array([[0.17109622, 0.00399314, 0.0006067, 0.00762716, 0.02798381, 
                                          0.00106717, 0.00128787, 0.01949132, 0.01516984, 0.09186373, 
                                          0.00677791, 0.0628721, 0.2990314, 0.00365305, 0.01498166, 
                                          0.01399446, 0.14559762, 0.01572833, 0.00590365, 0.03958469, 
                                          0.00239616, 0.02573004, 0.00087143, 0.00900396, 0.01368657]])

            # Convert the prediction array to a list (for JSON serialization)
            prediction_list = prediction_array.tolist()

            # Delete the uploaded file after processing (optional)
            os.remove(file_path)

            # Return the prediction array as JSON
            return JsonResponse({'result': prediction_list})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)