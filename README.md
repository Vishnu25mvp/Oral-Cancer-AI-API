* Deep Learning model (`ORAL CANCER.ipynb`)
* FastAPI backend for inference
* Integration of model with user result management.

Let’s create a **professional, developer-ready project documentation** that you can use in GitHub, college submission, or for presentation.

---

# 🧠 Oral Cancer Detection AI System

### 🔍 Deep Learning + FastAPI Based Oral Cancer Prediction Platform

---

## 📘 Overview

**Oral Cancer Detection AI** is an end-to-end intelligent platform designed to assist in early diagnosis of oral cancer using deep learning.
It combines a **Convolutional Neural Network (CNN)**–based image classifier with a **FastAPI backend** for real-time prediction, user management, and result tracking.

The system allows users or clinicians to upload **intra-oral images**, and the AI model classifies them as either **“CANCER”** or **“NON-CANCER”** with confidence scores.

---

## ⚙️ System Architecture

```
┌──────────────────────────┐
│  Oral Cancer Dataset     │
│  (CANCER / NON-CANCER)   │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Deep Learning Model     │
│  (MobileNetV2 Transfer)  │
│  Trained in Google Colab │
│  Output: .h5 Model       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  FastAPI Backend Server  │
│  - Model Integration     │
│  - Result Aggregation    │
│  - Role-based Access     │
│  - DB via SQLModel       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Web / Mobile Interface  │
│  - Image Uploads         │
│  - Result View           │
│  - Admin Dashboard       │
└──────────────────────────┘
```

---

## 🧩 Components

### 1️⃣ Deep Learning Model (`ORAL CANCER.ipynb`)

* Framework: **TensorFlow + Keras**
* Architecture: **MobileNetV2 (transfer learning)**
* Dataset: [Kaggle Oral Cancer Dataset (ZaidPy)](https://www.kaggle.com/datasets/zaidpy/oral-cancer-dataset)
* Data size: ~750 images (600 training / 150 validation)
* Accuracy: ~96% training / ~86% validation
* Model Output: `oral_cancer_detector_v2.h5`

#### Training Steps:

* Image preprocessing (224×224, normalization)
* Data augmentation (rotation, zoom, flips)
* Transfer learning with frozen base model
* Fine-tuning with low learning rate
* Evaluation with precision/recall and Grad-CAM visualization

#### Output:

The trained model predicts:

```python
{
  "prediction": "CANCER",
  "confidence": 92.35
}
```

---

### 2️⃣ Backend API (FastAPI)

Located in `server/` directory.

#### **Key Files:**

| File                         | Description                                  |
| ---------------------------- | -------------------------------------------- |
| `main.py`                    | FastAPI app entrypoint                       |
| `lib/routes/result.py`       | Handles result creation, prediction, listing |
| `lib/utils/model_predict.py` | TensorFlow model loader & predictor          |
| `lib/models/sql.py`          | Database models (User, Result)               |
| `lib/config/database.py`     | SQLModel database configuration              |

---

### 3️⃣ Model Integration

#### 🔮 `model_predict.py`

```python
import tensorflow as tf, numpy as np
from tensorflow.keras.preprocessing import image

MODEL_PATH = "oral_cancer_detector_v2.h5"
model = tf.keras.models.load_model(MODEL_PATH)
CLASS_NAMES = ["CANCER", "NON CANCER"]

def predict_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    preds = model.predict(img_array)
    label = CLASS_NAMES[np.argmax(preds[0])]
    confidence = round(float(np.max(preds[0])) * 100, 2)
    return label, confidence
```

---

### 4️⃣ `/results` Endpoint (with ML Integration)

#### **POST /api/v1/result/results/**

Uploads one or multiple images, runs AI predictions, and stores results.

```python
@router.post("/", response_model=ResultRead)
async def create_result_entry(...):
    # Save uploaded images
    # Predict each with model
    # Compute average confidence & final label
    # Store in database
```

**Aggregated Logic:**

```python
avg_conf = round(float(np.mean(confidences)) * 100, 2)
final_result = "CANCER" if predictions.count("CANCER") > predictions.count("NON CANCER") else "NON CANCER"
```

**Sample Response:**

```json
{
  "user_id": 7,
  "result": "CANCER",
  "confidence": 91.33,
  "images": [
    "uploads/results/7/7_img1.jpg",
    "uploads/results/7/7_img2.jpg"
  ]
}
```

---

### 5️⃣ Database Models

#### User Model

```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    role: str = "user"
    otp_verified: bool = True
```

#### Result Model

```python
class Result(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    result: Optional[str]
    confidence: Optional[float]
    images: List[str]
    created_by: Optional[int]
    date: datetime = Field(default_factory=datetime.utcnow)
```

---

## 📡 API Endpoints Summary

| Method   | Endpoint                      | Description                                 |
| -------- | ----------------------------- | ------------------------------------------- |
| `POST`   | `/api/v1/result/results/`     | Upload oral images and generate predictions |
| `GET`    | `/api/v1/result/results/`     | Paginated list of all results               |
| `GET`    | `/api/v1/result/results/{id}` | Fetch a specific result by ID               |
| `PUT`    | `/api/v1/result/results/{id}` | Update result info                          |
| `DELETE` | `/api/v1/result/results/{id}` | Delete result entry                         |

---

## 🧮 Example Usage

### Upload Multiple Oral Images:

```bash
curl -X POST "http://localhost:8000/api/v1/result/results/" \
  -F "email=user@example.com" \
  -F "name=John Doe" \
  -F "age=45" \
  -F "gender=Male" \
  -F "files=@img1.jpg" \
  -F "files=@img2.jpg"
```

Response:

```json
{
  "result": "CANCER",
  "confidence": 93.22
}
```

---

## 🧠 AI Model Performance

| Metric             | Train | Validation |
| ------------------ | ----- | ---------- |
| Accuracy           | 97.7% | 86.7%      |
| Loss               | 0.07  | 0.44       |
| Precision (CANCER) | 0.93  | 0.88       |
| Recall (CANCER)    | 0.94  | 0.84       |

Visualization (Grad-CAM heatmaps) highlights the lesion areas influencing predictions.

---

## 🧰 Tech Stack

| Layer        | Technology                       |
| ------------ | -------------------------------- |
| AI Model     | TensorFlow, Keras, NumPy, OpenCV |
| Backend      | FastAPI, SQLModel, AsyncSession  |
| DB           | SQLite / PostgreSQL              |
| Auth & Roles | JWT + Custom Role Middleware     |
| Email        | FastMail (async)                 |
| Deployment   | Uvicorn / Docker-ready           |

---

## 🚀 Deployment Guide

1️⃣ **Clone the Repo**

```bash
git clone https://github.com/yourusername/oral-cancer-ai.git
cd server
```

2️⃣ **Create Virtual Environment**

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

3️⃣ **Install Dependencies**

```bash
pip install -r requirements.txt
```

4️⃣ **Run Server**

```bash
uvicorn main:app --reload
```

5️⃣ **Open Docs**
→ [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧑‍⚕️ Future Enhancements

* Integrate **Grad-CAM visualization** in dashboard
* Add **multi-class detection** (leukoplakia, carcinoma, etc.)
* Implement **TensorFlow Lite** version for mobile deployment
* Connect to **medical report generator (PDF)**

---

