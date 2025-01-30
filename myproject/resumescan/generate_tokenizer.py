import pickle
from tensorflow.keras.preprocessing.text import Tokenizer

# Sample data to fit tokenizer (Replace this with your training data)
texts = ["Software Engineer", "Data Scientist", "Product Manager", "Cybersecurity Analyst", "ML Engineer"]

# Create and fit tokenizer
tokenizer = Tokenizer(num_words=5000)
tokenizer.fit_on_texts(texts)

# Save tokenizer
TOKENIZER_PATH = "C:/Users/KIIT/Desktop/flutter_projects/resumescan/myproject/resumescan/tokenizer.pkl"
with open(TOKENIZER_PATH, "wb") as f:
    pickle.dump(tokenizer, f)

print("Tokenizer saved successfully!")