import pickle
import joblib
import os

# Set paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Project root directory
PKL_MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")  # Old .pkl model
JOBLIB_MODEL_PATH = os.path.join(BASE_DIR, "model.joblib")  # New .joblib model

# ✅ Load the model from .pkl
print("🔄 Loading model from .pkl file...")
with open(PKL_MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# ✅ Save the model in .joblib format
print("💾 Saving model as .joblib format...")
joblib.dump(model, JOBLIB_MODEL_PATH)

print(f"✅ Model successfully converted to .joblib format! Saved at: {JOBLIB_MODEL_PATH}")