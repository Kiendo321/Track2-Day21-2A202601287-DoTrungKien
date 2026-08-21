from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import storage
import joblib
import os

app = FastAPI()

GCS_BUCKET = os.environ.get("GCS_BUCKET", "mlops-wine-bucket-gragas-2026")
GCS_MODEL_KEY = "models/latest/model.pkl"
MODEL_PATH = os.path.expanduser("~/models/model.pkl")


def download_model():
    """Tải file model.pkl từ GCS về máy khi server khởi động."""
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(GCS_MODEL_KEY)
    blob.download_to_filename(MODEL_PATH)
    print(f"Downloaded model from gs://{GCS_BUCKET}/{GCS_MODEL_KEY} to {MODEL_PATH}")


# Gọi hàm này khi module được import (chạy khi server khởi động)
try:
    download_model()
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Warning/Error loading model at startup: {e}")
    model = None


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():
    """Endpoint kiểm tra sức khỏe server. GitHub Actions dùng endpoint này để xác nhận deploy thành công."""
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    """
    Endpoint suy luận.

    Đầu vào: JSON {"features": [f1, f2, ..., f12]}
    Đầu ra:  JSON {"prediction": <0|1|2>, "label": <"thap"|"trung_binh"|"cao">}
    """
    if len(req.features) != 12:
        raise HTTPException(
            status_code=400,
            detail="Expected 12 features (wine quality)"
        )

    if model is None:
        raise HTTPException(status_code=500, detail="Model is not loaded")

    preds = model.predict([req.features])
    pred_int = int(preds[0])

    label_map = {0: "thap", 1: "trung_binh", 2: "cao"}
    label_str = label_map.get(pred_int, "khong_xac_dinh")

    return {"prediction": pred_int, "label": label_str}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
