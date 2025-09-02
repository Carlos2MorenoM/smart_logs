# services/anomaly_detector/src/app.py

import joblib
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

# --- Configuration ---
MODEL_PATH = "/model/anomaly_detector.joblib"

# Global variable to hold the loaded model
ml_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the model lifecycle. The model is loaded on startup and released on shutdown.
    """
    global ml_model
    print("🚀 Loading anomaly detection model...")
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(f"Model file not found at {MODEL_PATH}. Please train the model first.")

    ml_model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully.")

    yield

    # Clean up the model
    ml_model = None
    print("🛑 Model released.")


app = FastAPI(lifespan=lifespan)


# Pydantic model for input validation
class LogMessage(BaseModel):
    message: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict")
async def predict_anomaly(log: LogMessage):
    """
    Predicts if a single log message is an anomaly using the pre-loaded model.
    """

    try:
        # The model pipeline expects an iterable (list of strings)
        prediction = ml_model.predict([log.message])

        # IsolationForest returns -1 for anomalies (outliers) and 1 for normal (inliers)
        is_anomaly = bool(prediction[0] == -1)

        return {"message": log.message, "is_anomaly": is_anomaly}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during prediction: {str(e)}")