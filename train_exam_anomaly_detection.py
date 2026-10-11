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

# Configure UTF-8 output for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
DATASET_PATH = r"C:\Users\moktata\Desktop\MUQ\archive\CCTV-Exam -Monitor -Dataset"
MODEL_DIR = r"C:\Users\moktata\Desktop\MUQ\models"
IMG_SIZE = (64, 64)  # Reduced for faster training
BATCH_SIZE = 16  # Reduced for faster training
EPOCHS = 20  # Reduced for faster training
LEARNING_RATE = 0.001

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

print("="*60)
print("🎓 MUQ - Exam Anomaly Detection Training")
print("="*60)
print(f"📁 Dataset: {DATASET_PATH}")
print(f"📦 Model will be saved to: {MODEL_DIR}")
print(f"🖼️  Image size: {IMG_SIZE}")
print(f"📊 Batch size: {BATCH_SIZE}")
print(f"🔄 Epochs: {EPOCHS}")
print("="*60)

def load_images(directory, limit=None):
    """Load images from directory."""
    images = []
    image_files = [f for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if limit:
        image_files = image_files[:limit]
    
    print(f"\n📁 Loading {len(image_files)} images from {directory}...")
    
    for i, img_file in enumerate(image_files):
        try:
            img_path = os.path.join(directory, img_file)
            img = load_img(img_path, target_size=IMG_SIZE)
            img_array = img_to_array(img) / 255.0  # Normalize to [0, 1]
            images.append(img_array)
            
            if (i + 1) % 100 == 0:
                print(f"   Loaded {i+1}/{len(image_files)} images...")
        except Exception as e:
            print(f"   ⚠️  Error loading {img_file}: {e}")
    
    return np.array(images)

def build_autoencoder(input_shape):
    """Build Autoencoder model for anomaly detection."""
    input_img = keras.Input(shape=input_shape)
    
    # Encoder
    x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
    x = layers.MaxPooling2D((2, 2), padding='same')(x)
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = layers.MaxPooling2D((2, 2), padding='same')(x)
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    encoded = layers.MaxPooling2D((2, 2), padding='same')(x)
    
    # Decoder
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(encoded)
    x = layers.UpSampling2D((2, 2))(x)
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = layers.UpSampling2D((2, 2))(x)
    x = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    x = layers.UpSampling2D((2, 2))(x)
    decoded = layers.Conv2D(3, (3, 3), activation='sigmoid', padding='same')(x)
    
    autoencoder = keras.Model(input_img, decoded)
    autoencoder.compile(optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE), loss='mse')
    
    return autoencoder

def main():
    # Load training images
    train_dir = os.path.join(DATASET_PATH, "train")
    if not os.path.exists(train_dir):
        print(f"❌ Error: {train_dir} does not exist")
        return
    
    # Load images (limit to 500 for faster training on CPU)
    print("\n⚠️  Limiting to 500 images for faster training on CPU")
    print("   (You can remove the limit in the code if you want to use all images)")
    images = load_images(train_dir, limit=500)
    
    if len(images) == 0:
        print("❌ No images loaded!")
        return
    
    print(f"\n✅ Loaded {len(images)} images")
    print(f"   Image shape: {images[0].shape}")
    
    # Split into train and validation
    X_train, X_val = train_test_split(images, test_size=0.2, random_state=42)
    
    print(f"\n📊 Dataset split:")
    print(f"   Training: {len(X_train)} images")
    print(f"   Validation: {len(X_val)} images")
    
    # Build model
    print(f"\n🔨 Building Autoencoder model...")
    autoencoder = build_autoencoder(IMG_SIZE + (3,))
    autoencoder.summary()
    
    # Callbacks
    checkpoint_path = os.path.join(MODEL_DIR, "exam_anomaly_best.h5")
    model_checkpoint = keras.callbacks.ModelCheckpoint(
        checkpoint_path,
        monitor='val_loss',
        save_best_only=True,
        verbose=1
    )
    
    early_stopping = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    )
    
    # Train
    print(f"\n🚀 Starting training...")
    print(f"   This may take a while on CPU...")
    
    history = autoencoder.fit(
        X_train, X_train,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=(X_val, X_val),
        callbacks=[model_checkpoint, early_stopping],
        verbose=1
    )
    
    # Save final model
    final_model_path = os.path.join(MODEL_DIR, "exam_anomaly_final.h5")
    autoencoder.save(final_model_path)
    print(f"\n✅ Final model saved to: {final_model_path}")
    
    # Calculate threshold from validation loss
    print(f"\n📊 Calculating anomaly threshold...")
    val_predictions = autoencoder.predict(X_val)
    val_mse = np.mean(np.square(X_val - val_predictions), axis=(1, 2, 3))
    
    # Threshold = mean + 2 * std (95% confidence)
    threshold = np.mean(val_mse) + 2 * np.std(val_mse)
    print(f"   Anomaly threshold: {threshold:.6f}")
    
    # Save threshold
    threshold_path = os.path.join(MODEL_DIR, "exam_anomaly_threshold.json")
    with open(threshold_path, 'w') as f:
        json.dump({"threshold": float(threshold)}, f)
    print(f"   Threshold saved to: {threshold_path}")
    
    # Plot training history
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss')
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
    
    plot_path = os.path.join(MODEL_DIR, "exam_anomaly_training.png")
    plt.tight_layout()
    plt.savefig(plot_path)
    print(f"\n📊 Training plot saved to: {plot_path}")
    
    # Save training history
    history_path = os.path.join(MODEL_DIR, "exam_anomaly_history.json")
    with open(history_path, 'w') as f:
        json.dump({
            "loss": [float(x) for x in history.history['loss']],
            "val_loss": [float(x) for x in history.history['val_loss']],
            "threshold": float(threshold),
            "epochs_trained": len(history.history['loss']),
            "training_date": datetime.now().isoformat()
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

if __name__ == "__main__":
    main()
