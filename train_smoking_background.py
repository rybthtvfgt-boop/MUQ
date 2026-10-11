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
DATASET_PATH = r"C:\Users\moktata\Desktop\MUQ\smokingVSnotsmoking\dataset\training_data"
MODEL_DIR = r"C:\Users\moktata\Desktop\MUQ\models"
STATUS_FILE = os.path.join(MODEL_DIR, "smoking_training_status.json")
IMG_SIZE = (224, 224)  # MobileNetV2 input size
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
    "accuracy": 0.0,
    "val_accuracy": 0.0,
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
    """تحميل جميع الصور من المجلد مع التسميات"""
    images = []
    labels = []
    
    print(f"Loading images from: {directory}")
    
    # فئة التدخين
    smoking_dir = os.path.join(directory, "smoking")
    if os.path.exists(smoking_dir):
        smoking_files = [f for f in os.listdir(smoking_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"Found {len(smoking_files)} smoking images...")
        for i, img_file in enumerate(smoking_files):
            try:
                img_path = os.path.join(smoking_dir, img_file)
                img = load_img(img_path, target_size=IMG_SIZE)
                img_array = img_to_array(img) / 255.0
                images.append(img_array)
                labels.append(1)  # تدخين = 1
                if (i + 1) % 100 == 0:
                    print(f"   Loaded {i+1}/{len(smoking_files)} smoking images...")
            except Exception as e:
                print(f"   Error loading {img_file}: {e}")
    else:
        print(f"Warning: Smoking directory not found: {smoking_dir}")
    
    # فئة غير المدخن
    not_smoking_dir = os.path.join(directory, "notsmoking")
    if os.path.exists(not_smoking_dir):
        not_smoking_files = [f for f in os.listdir(not_smoking_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"Found {len(not_smoking_files)} not smoking images...")
        for i, img_file in enumerate(not_smoking_files):
            try:
                img_path = os.path.join(not_smoking_dir, img_file)
                img = load_img(img_path, target_size=IMG_SIZE)
                img_array = img_to_array(img) / 255.0
                images.append(img_array)
                labels.append(0)  # غير مدخن = 0
                if (i + 1) % 100 == 0:
                    print(f"   Loaded {i+1}/{len(not_smoking_files)} not smoking images...")
            except Exception as e:
                print(f"   Error loading {img_file}: {e}")
    else:
        print(f"Warning: Not smoking directory not found: {not_smoking_dir}")
    
    print(f"Total loaded: {len(images)} images")
    return np.array(images), np.array(labels)

def build_smoking_classifier(input_shape):
    """بناء مصنف التدخين باستخدام MobileNetV2 Transfer Learning"""
    # تحميل MobileNetV2 المدرب مسبقاً على ImageNet
    base_model = keras.applications.MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=input_shape
    )
    
    # تجميد النموذج الأساسي في البداية
    base_model.trainable = False
    
    # بناء المصنف
    inputs = keras.Input(shape=input_shape)
    x = base_model(inputs, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    x = layers.Dense(512, activation='relu')(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(1, activation='sigmoid')(x)  # تصنيف ثنائي
    
    model = keras.Model(inputs, outputs)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model

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
        training_state["accuracy"] = float(logs.get('accuracy', 0.0))
        training_state["val_accuracy"] = float(logs.get('val_accuracy', 0.0))
        training_state["message"] = f"Epoch {epoch + 1}/{training_state['total_epochs']} - Acc: {training_state['accuracy']:.2%}, Val Acc: {training_state['val_accuracy']:.2%}"
        save_status()

def train_model():
    """تدريب نموذج كشف التدخين في الخلفية"""
    global training_state
    
    try:
        training_state["status"] = "running"
        training_state["start_time"] = datetime.now().isoformat()
        training_state["message"] = "Loading images..."
        save_status()
        
        # تحميل الصور
        images, labels = load_images(DATASET_PATH)
        
        training_state["message"] = f"Loaded {len(images)} images. Splitting dataset..."
        save_status()
        
        # التقسيم
        X_train, X_val, y_train, y_val = train_test_split(images, labels, test_size=0.2, random_state=42)
        
        training_state["message"] = f"Training: {len(X_train)} images, Validation: {len(X_val)} images"
        save_status()
        
        # بناء النموذج
        training_state["message"] = "Building MobileNetV2 model..."
        save_status()
        model = build_smoking_classifier(IMG_SIZE + (3,))
        
        # الاسترجاعات
        checkpoint_path = os.path.join(MODEL_DIR, "smoking_detector_best.h5")
        model_checkpoint = keras.callbacks.ModelCheckpoint(
            checkpoint_path,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1,
            save_weights_only=False
        )
        
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=8,
            restore_best_weights=True,
            verbose=1
        )
        
        reduce_lr = keras.callbacks.ReduceLROnPlateau(
            monitor='val_accuracy',
            factor=0.5,
            patience=3,
            min_lr=1e-7,
            verbose=1
        )
        
        # التدريب
        training_state["message"] = "Starting training with MobileNetV2 Transfer Learning..."
        save_status()
        
        history = model.fit(
            X_train, y_train,
            batch_size=BATCH_SIZE,
            epochs=EPOCHS,
            validation_data=(X_val, y_val),
            callbacks=[model_checkpoint, early_stopping, reduce_lr, TrainingCallback()],
            verbose=1
        )
        
        # حفظ النموذج النهائي
        final_model_path = os.path.join(MODEL_DIR, "smoking_detector_final.h5")
        model.save(final_model_path, save_format='h5', include_optimizer=False)
        
        # حفظ تاريخ التدريب
        history_path = os.path.join(MODEL_DIR, "smoking_training_history.json")
        with open(history_path, 'w') as f:
            json.dump({
                "loss": [float(x) for x in history.history['loss']],
                "val_loss": [float(x) for x in history.history['val_loss']],
                "accuracy": [float(x) for x in history.history['accuracy']],
                "val_accuracy": [float(x) for x in history.history['val_accuracy']],
                "best_val_accuracy": float(max(history.history['val_accuracy'])),
                "epochs_trained": len(history.history['loss']),
                "training_date": datetime.now().isoformat(),
                "model_type": "MobileNetV2 Transfer Learning",
                "total_images": len(images)
            }, f)
        
        # تحديث الحالة
        training_state["status"] = "completed"
        training_state["progress"] = 100.0
        training_state["message"] = f"Training completed! Best val_accuracy: {max(history.history['val_accuracy']):.2%}"
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
