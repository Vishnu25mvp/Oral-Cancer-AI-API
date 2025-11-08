import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image

# Load model once at startup
MODEL_PATH = "oral_cancer_detector_v2.h5"
model = tf.keras.models.load_model(MODEL_PATH)

# Labels (order from your training generator)
CLASS_NAMES = ['CANCER', 'NON CANCER']

def predict_image(img_path: str):
    """Predict single image using trained model."""
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    preds = model.predict(img_array)
    predicted_class = CLASS_NAMES[np.argmax(preds[0])]
    confidence = float(np.max(preds[0]))
    return predicted_class, confidence
