# services/anomaly_detector/src/train.py

import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline

# --- Configuration ---
# This path assumes the training data is mounted into the container.
# In a real MLOps pipeline, this would be pulled from a versioned source like DVC.
TRAINING_DATA_PATH = "/data/raw/Linux_2k.log"
MODEL_DIR = "/model"
MODEL_PATH = os.path.join(MODEL_DIR, "anomaly_detector.joblib")

def train_model():
    """
    Trains the TF-IDF + Isolation Forest model and saves it to a file.
    This function represents a single step in a Continuous Training (CT) pipeline.
    """
    print("🚀 Starting model training...")

    # 1. Load and prepare data
    print(f"Loading training data from {TRAINING_DATA_PATH}...")
    try:
        with open(TRAINING_DATA_PATH, 'r') as f:
            # We assume the entire file represents "normal" log messages for the baseline.
            normal_log_samples = f.readlines()
    except FileNotFoundError:
        print(f"🚨 Error: Training data not found at {TRAINING_DATA_PATH}. Aborting.")
        return

    if not normal_log_samples:
        print("🚨 Error: Training data is empty. Aborting.")
        return

    print(f"Loaded {len(normal_log_samples)} log samples for training.")

    # 2. Define the model pipeline (as per strategic plan)
    pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(max_features=5000, stop_words='english')),
        ('model', IsolationForest(contamination='auto', random_state=42, n_jobs=-1))
    ])

    # 3. Train the model
    print("Fitting the pipeline (TF-IDF + Isolation Forest)...")
    pipeline.fit(normal_log_samples)
    print("✅ Model training complete.")

    # 4. Save the trained model artifact
    print(f"Saving model to {MODEL_PATH}...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print("💾 Model saved successfully.")

if __name__ == "__main__":
    train_model()
