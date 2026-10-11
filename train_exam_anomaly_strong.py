import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
from datetime import datetime

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
IMG_SIZE = (128, 128)  # أكبر لدقة أفضل
BATCH_SIZE = 32
EPOCHS = 30
LEARNING_RATE = 0.0001  # أقل لتدريب أفضل

# التأكد من وجود مجلد النموذج
os.makedirs(MODEL_DIR, exist_ok=True)

print("="*60)
print("🎓 MUQ - Exam Anomaly Detection (STRONG - MobileNetV2)")
print("="*60)
print(f"📁 Dataset: {DATASET_PATH}")
print(f"📦 Model will be saved to: {MODEL_DIR}")
print(f"🖼️  Image size: {IMG_SIZE}")
print(f"📊 Batch size: {BATCH_SIZE}")
print(f"🔄 Epochs: {EPOCHS}")
print("="*60)

def load_images(directory, limit=None):
    """تحميل الصور من المجلد."""
    images = []
    image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if limit:
        image_files = image_files[:limit]
    
    print(f"\n📁 Loading {len(image_files)} images from {directory}...")
    
    for i, img_file in enumerate(image_files):
        try:
            img_path = os.path.join(directory, img_file)
            img = load_img(img_path, target_size=IMG_SIZE)
            img_array = img_to_array(img) / 255.0  # تطبيع إلى [0، 1]
            images.append(img_array)
            
            if (i + 1) % 100 == 0:
                print(f"   Loaded {i+1}/{len(image_files)} images...")
        except Exception as e:
            print(f"   ⚠️  Error loading {img_file}: {e}")
    
    return np.array(images)

def build_strong_autoencoder(input_shape):
    """بناء مشفر تلقائي قوي باستخدام MobileNetV2 كمشفر"""
    # تحميل MobileNetV2 المدرب مسبقاً على ImageNet (بدون الطبقات العليا)
    base_model = keras.applications.MobileNetV2(
        weights='imagenet',
        include_top=False,
        input_shape=input_shape
    )
    
    # تجميد النموذج الأساسي
    base_model.trainable = False
    
    # المشفر
    input_img = keras.Input(shape=input_shape)
    x = base_model(input_img, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(512, activation='relu')(x)  # عنق الزجاجة
    encoded = layers.Dense(256, activation='relu')(x)  # ضغط إضافي
    
    # فك التشفير
    x = layers.Dense(512, activation='relu')(encoded)
    x = layers.Dense(1024, activation='relu')(x)
    x = layers.Dense(8 * 8 * 128, activation='relu')(x)  # تسطيح لإعادة التشكيل
    x = layers.Reshape((8, 8, 128))(x)
    x = layers.Conv2DTranspose(128, (3, 3), strides=2, padding='same', activation='relu')(x)  # 16x16
    x = layers.Conv2DTranspose(64, (3, 3), strides=2, padding='same', activation='relu')(x)   # 32x32
    x = layers.Conv2DTranspose(32, (3, 3), strides=2, padding='same', activation='relu')(x)   # 64x64
    x = layers.Conv2DTranspose(16, (3, 3), strides=2, padding='same', activation='relu')(x)   # 128x128
    decoded = layers.Conv2D(3, (3, 3), activation='sigmoid', padding='same')(x)
    
    autoencoder = keras.Model(input_img, decoded)
    autoencoder.compile(optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE), loss='mse')
    
    return autoencoder

def main():
    # تحميل صور التدريب
    train_dir = os.path.join(DATASET_PATH, "train")
    if not os.path.exists(train_dir):
        print(f"❌ Error: {train_dir} does not exist")
        return
    
    # تحميل الصور (استخدام جميع الصور لتحقيق أقصى دقة)
    print("\n⚠️  Using ALL available images for maximum accuracy")
    print("   (MobileNetV2 is pre-trained, so it learns faster)")
    images = load_images(train_dir, limit=None)  # بدون حد - استخدام جميع الصور
    
    if len(images) == 0:
        print("❌ No images loaded!")
        return
    
    print(f"\n✅ Loaded {len(images)} images")
    print(f"   Image shape: {images[0].shape}")
    
    # تقسيم إلى تدريب وتحقق
    X_train, X_val = train_test_split(images, test_size=0.2, random_state=42)
    
    print(f"\n📊 Dataset split:")
    print(f"   Training: {len(X_train)} images")
    print(f"   Validation: {len(X_val)} images")
    
    # بناء النموذج
    print(f"\n🔨 Building Strong Autoencoder with MobileNetV2...")
    autoencoder = build_strong_autoencoder(IMG_SIZE + (3,))
    autoencoder.summary()
    
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
    print(f"\n🚀 Starting training with MobileNetV2 Transfer Learning...")
    print(f"   This will be STRONGER than previous model!")
    
    history = autoencoder.fit(
        X_train, X_train,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=(X_val, X_val),
        callbacks=[model_checkpoint, early_stopping, reduce_lr],
        verbose=1
    )
    
    # حفظ النموذج النهائي
    final_model_path = os.path.join(MODEL_DIR, "exam_anomaly_strong_final.h5")
    autoencoder.save(final_model_path, save_format='h5', include_optimizer=False)
    print(f"\n✅ Final model saved to: {final_model_path}")
    
    # حساب العتبة من خسارة التحقق
    print(f"\n📊 Calculating anomaly threshold...")
    val_predictions = autoencoder.predict(X_val, verbose=0)
    val_mse = np.mean(np.square(X_val - val_predictions), axis=(1, 2, 3))
    
    # العتبة = المتوسط + 2 * الانحراف المعياري (ثقة 95%)
    threshold = np.mean(val_mse) + 2 * np.std(val_mse)
    print(f"   Anomaly threshold: {threshold:.6f}")
    
    # حفظ العتبة
    threshold_path = os.path.join(MODEL_DIR, "exam_anomaly_strong_threshold.json")
    with open(threshold_path, 'w') as f:
        json.dump({"threshold": float(threshold)}, f)
    print(f"   Threshold saved to: {threshold_path}")
    
    # رسم تاريخ التدريب
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss (MobileNetV2)')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.hist(val_mse, bins=50)
    plt.axvline(threshold, color='r', linestyle='--', label=f'Threshold: {threshold:.3f}')
    plt.title('Validation MSE Distribution')
    plt.xlabel('MSE')
    plt.ylabel('Count')
    plt.legend()
    
    plot_path = os.path.join(MODEL_DIR, "exam_anomaly_strong_training.png")
    plt.tight_layout()
    plt.savefig(plot_path)
    print(f"\n📊 Training plot saved to: {plot_path}")
    
    # حفظ تاريخ التدريب
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
    print(f"📊 Training history saved to: {history_path}")
    
    print(f"\n{'='*60}")
    print(f"✅ Training completed successfully!")
    print(f"{'='*60}")
    print(f"\n📁 Model files:")
    print(f"   1. {checkpoint_path} (best model)")
    print(f"   2. {final_model_path} (final model)")
    print(f"   3. {threshold_path} (anomaly threshold)")
    print(f"   4. {plot_path} (training plot)")
    print(f"   5. {history_path} (training history)")
    print(f"\n🎯 How to use:")
    print(f"   Load the model and predict on new images")
    print(f"   If MSE > threshold, it's an anomaly!")
    print(f"   If MSE <= threshold, it's normal (similar to training data)")
    print(f"\n💡 This model uses MobileNetV2 pre-trained on ImageNet")
    print(f"   making it STRONGER and more accurate!")

if __name__ == "__main__":
    main()
