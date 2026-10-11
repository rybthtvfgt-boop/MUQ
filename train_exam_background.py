import os
import sys
import numpy as np
import json
from datetime import datetime
import threading
import time

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from sklearn.model_selection import train_test_split

# إعداد إخراج UTF-8 لـ Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# الإعدادات
DATASET_PATH = r"C:\Users\moktata\Desktop\MUQ\archive\CCTV-Exam -Monitor -Dataset"
MODEL_DIR = r"C:\Users\moktata\Desktop\MUQ\models"
STATUS_FILE = os.path.join(MODEL_DIR, "training_status.json")
IMG_SIZE = (128, 128)
BATCH_SIZE = 32
EPOCHS = 30
LEARNING_RATE = 0.0001

# حالة التدريب العامة
training_state = {
    "status": "idle",  # خامل، قيد التشغيل، مكتمل، خطأ
    "progress": 0.0,
    "current_epoch": 0,
    "total_epochs": EPOCHS,
    "loss": 0.0,
    "val_loss": 0.0,
    "message": "",
    "start_time": None,
    "end_time": None
}

def save_status():
    """حفظ حالة التدريب في ملف"""
    with open(STATUS_FILE, 'w') as f:
        json.dump(training_state, f)

def load_status():
    """تحميل حالة التدريب من ملف"""
    global training_state
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            training_state = json.load(f)
    return training_state

def load_images(directory):
    """تحميل جميع الصور من المجلد"""
    images = []
    image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    print(f"Loading {len(image_files)} images from {directory}...")
    
    for i, img_file in enumerate(image_files):
        try:
            img_path = os.path.join(directory, img_file)
            img = load_img(img_path, target_size=IMG_SIZE)
            img_array = img_to_array(img) / 255.0
            images.append(img_array)
            
            if (i + 1) % 100 == 0:
                print(f"   Loaded {i+1}/{len(image_files)} images...")
        except Exception as e:
            print(f"   Error loading {img_file}: {e}")
    
    return np.array(images)

def build_strong_autoencoder(input_shape):
    """بناء مشفر تلقائي قوي باستخدام MobileNetV2"""
    base_model = keras.applications.MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=input_shape
    )
    base_model.trainable = False
    
    input_img = keras.Input(shape=input_shape)
    x = base_model(input_img, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(512, activation='relu')(x)
    encoded = layers.Dense(256, activation='relu')(x)
    
    x = layers.Dense(512, activation='relu')(encoded)
    x = layers.Dense(1024, activation='relu')(x)
    x = layers.Dense(8 * 8 * 128, activation='relu')(x)
    x = layers.Reshape((8, 8, 128))(x)
    x = layers.Conv2DTranspose(128, (3, 3), strides=2, padding='same', activation='relu')(x)
    x = layers.Conv2DTranspose(64, (3, 3), strides=2, padding='same', activation='relu')(x)
    x = layers.Conv2DTranspose(32, (3, 3), strides=2, padding='same', activation='relu')(x)
    x = layers.Conv2DTranspose(16, (3, 3), strides=2, padding='same', activation='relu')(x)
    decoded = layers.Conv2D(3, (3, 3), activation='sigmoid', padding='same')(x)
    
    autoencoder = keras.Model(input_img, decoded)
    autoencoder.compile(optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE), loss='mse')
    
    return autoencoder

class TrainingCallback(keras.callbacks.Callback):
    """استرجاع مخصص لتحديث حالة التدريب"""
    def __init__(self):
        super().__init__()
    
    def on_epoch_end(self, epoch, logs=None):
        global training_state
        training_state["current_epoch"] = epoch + 1
        training_state["progress"] = (epoch + 1) / training_state["total_epochs"] * 100
        training_state["loss"] = float(logs.get('loss', 0.0))
        training_state["val_loss"] = float(logs.get('val_loss', 0.0))
        training_state["message"] = f"Epoch {epoch + 1}/{training_state['total_epochs']} - Loss: {training_state['loss']:.4f}, Val Loss: {training_state['val_loss']:.4f}"
        save_status()

def train_model():
    """تدريب النموذج في الخلفية"""
    global training_state
    
    try:
        training_state["status"] = "running"
        training_state["start_time"] = datetime.now().isoformat()
        training_state["message"] = "Loading images..."
        save_status()
        
        # تحميل الصور
        train_dir = os.path.join(DATASET_PATH, "train")
        images = load_images(train_dir)
        
        training_state["message"] = f"Loaded {len(images)} images. Splitting dataset..."
        save_status()
        
        # التقسيم
        X_train, X_val = train_test_split(images, test_size=0.2, random_state=42)
        
        training_state["message"] = f"Training: {len(X_train)} images, Validation: {len(X_val)} images"
        save_status()
        
        # بناء النموذج
        training_state["message"] = "Building MobileNetV2 model..."
        save_status()
        autoencoder = build_strong_autoencoder(IMG_SIZE + (3,))
        
        # الاسترجاعات
        checkpoint_path = os.path.join(MODEL_DIR, "exam_anomaly_strong_best.h5")
        model_checkpoint = keras.callbacks.ModelCheckpoint(
            checkpoint_path,
            monitor='val_loss',
            save_best_only=True,
            verbose=1,
            save_weights_only=False
        )
        
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=8,
            restore_best_weights=True,
            verbose=1
        )
        
        reduce_lr = keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1
        )
        
        # التدريب
        training_state["message"] = "Starting training with MobileNetV2 Transfer Learning..."
        save_status()
        
        history = autoencoder.fit(
            X_train, X_train,
            batch_size=BATCH_SIZE,
            epochs=EPOCHS,
            validation_data=(X_val, X_val),
            callbacks=[model_checkpoint, early_stopping, reduce_lr, TrainingCallback()],
            verbose=1
        )
        
        # حفظ النموذج النهائي
        final_model_path = os.path.join(MODEL_DIR, "exam_anomaly_strong_final.h5")
        autoencoder.save(final_model_path, save_format='h5', include_optimizer=False)
        
        # حساب العتبة
        val_predictions = autoencoder.predict(X_val, verbose=0)
        val_mse = np.mean(np.square(X_val - val_predictions), axis=(1, 2, 3))
        threshold = np.mean(val_mse) + 2 * np.std(val_mse)
        
        # حفظ العتبة
        threshold_path = os.path.join(MODEL_DIR, "exam_anomaly_strong_threshold.json")
        with open(threshold_path, 'w') as f:
            json.dump({"threshold": float(threshold)}, f)
        
        # حفظ التاريخ
        history_path = os.path.join(MODEL_DIR, "exam_anomaly_strong_history.json")
        with open(history_path, 'w') as f:
            json.dump({
                "loss": [float(x) for x in history.history['loss']],
                "val_loss": [float(x) for x in history.history['val_loss']],
                "threshold": float(threshold),
                "epochs_trained": len(history.history['loss']),
                "training_date": datetime.now().isoformat(),
                "model_type": "MobileNetV2 Transfer Learning"
            }, f)
        
        # تحديث الحالة
        training_state["status"] = "completed"
        training_state["progress"] = 100.0
        training_state["message"] = f"Training completed! Best val_loss: {min(history.history['val_loss']):.4f}"
        training_state["end_time"] = datetime.now().isoformat()
        save_status()
        
        print("✅ Training completed successfully!")
        
    except Exception as e:
        training_state["status"] = "error"
        training_state["message"] = f"Error: {str(e)}"
        training_state["end_time"] = datetime.now().isoformat()
        save_status()
        print(f"❌ Error: {e}")

def start_training():
    """بدء التدريب في مؤشر ترابط الخلفية"""
    global training_state
    if training_state["status"] == "running":
        return {"error": "Training is already running"}
    
    thread = threading.Thread(target=train_model)
    thread.daemon = True
    thread.start()
    
    return {"status": "Training started"}

if __name__ == "__main__":
    train_model()
