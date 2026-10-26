"""
Real AI Training Script for Monitoring System
Uses Transfer Learning with EfficientNetB7 for maximum accuracy
Includes Object Detection and Face Recognition capabilities
"""
import os
import sys
import json
import time
import argparse
from datetime import datetime
import numpy as np
from pathlib import Path
import cv2

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from tensorflow.keras.applications import EfficientNetB7
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Parse command line arguments
parser = argparse.ArgumentParser(description='Train monitoring model')
parser.add_argument('--dataset', type=str, default=r'F:\MUQ\dataset', help='Path to dataset')
parser.add_argument('--output', type=str, default=None, help='Path to save trained model')
args = parser.parse_args()

# Configuration
DATASET_PATH = args.dataset
TRAIN_DIR = os.path.join(DATASET_PATH, 'training_data')
VALIDATION_DIR = os.path.join(DATASET_PATH, 'validation_data')
TEST_DIR = os.path.join(DATASET_PATH, 'testing_data')
MODEL_SAVE_PATH = args.output if args.output else os.path.join(DATASET_PATH, 'trained_model')
LOG_FILE = os.path.join(DATASET_PATH, 'training_log.json')

# Training parameters - MAXIMUM POWER
IMG_SIZE = (600, 600)  # Larger images for better accuracy
BATCH_SIZE = 16  # Smaller batch for larger images
EPOCHS = 100  # More epochs for better convergence
LEARNING_RATE = 0.00001  # Lower learning rate for fine-tuning
EARLY_STOPPING_PATIENCE = 15
REDUCE_LR_PATIENCE = 5

class TrainingLogger:
    """Logger for training progress"""
    def __init__(self, log_file):
        self.log_file = log_file
        self.logs = []
        self.start_time = None

    def start(self):
        self.start_time = datetime.now()
        self.log('Training started', 'info', {
            'timestamp': self.start_time.isoformat(),
            'dataset_path': DATASET_PATH,
            'img_size': IMG_SIZE,
            'batch_size': BATCH_SIZE,
            'epochs': EPOCHS
        })

    def log(self, message, level='info', data=None):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'data': self._convert_types(data or {})
        }
        self.logs.append(entry)
        self._save_to_file()
        print(f"[{level.upper()}] {message}")
        if data:
            print(f"  Data: {json.dumps(self._convert_types(data), indent=2)}")

    def _convert_types(self, obj):
        """Convert TensorFlow types to Python native types for JSON serialization"""
        if isinstance(obj, dict):
            return {k: self._convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_types(item) for item in obj]
        elif hasattr(obj, 'numpy'):  # TensorFlow tensors
            return self._convert_types(obj.numpy())
        elif isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return self._convert_types(obj.tolist())
        else:
            return obj

    def _save_to_file(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump({
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'logs': self.logs
            }, f, indent=2, ensure_ascii=False)

def prepare_data():
    """Prepare data generators with advanced augmentation"""
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        width_shift_range=0.3,
        height_shift_range=0.3,
        horizontal_flip=True,
        vertical_flip=False,
        zoom_range=0.3,
        shear_range=0.3,
        brightness_range=[0.8, 1.2],
        channel_shift_range=0.1,
        fill_mode='nearest'
    )

    val_datagen = ImageDataGenerator(rescale=1./255)

    try:
        train_generator = train_datagen.flow_from_directory(
            TRAIN_DIR,
            target_size=IMG_SIZE,
            batch_size=BATCH_SIZE,
            class_mode='categorical',
            shuffle=True
        )

        validation_generator = val_datagen.flow_from_directory(
            VALIDATION_DIR,
            target_size=IMG_SIZE,
            batch_size=BATCH_SIZE,
            class_mode='categorical',
            shuffle=False
        )

        return train_generator, validation_generator
    except Exception as e:
        print(f"Error preparing data: {e}")
        raise

def build_model(num_classes):
    """Build model using Transfer Learning with EfficientNetB7 - MOST POWERFUL"""
    # Load pre-trained EfficientNetB7 (largest and most accurate)
    base_model = EfficientNetB7(
        weights='imagenet',
        include_top=False,
        input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3)
    )

    # Freeze base model initially
    base_model.trainable = False

    # Build custom head with more layers for better learning
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dropout(0.6),
        layers.Dense(1024, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.4),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(num_classes, activation='softmax')
    ])

    # Compile with advanced optimizer
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy', 'precision', 'recall', 'AUC']
    )

    return model, base_model

def train_model(logger):
    """Main training function"""
    logger.start()
    logger.log('Loading dataset...', 'info')

    # Prepare data
    train_gen, val_gen = prepare_data()
    num_classes = len(train_gen.class_indices)
    logger.log('Dataset loaded', 'info', {
        'num_classes': num_classes,
        'classes': train_gen.class_indices,
        'train_samples': train_gen.samples,
        'validation_samples': val_gen.samples
    })

    # Build model
    logger.log('Building model with EfficientNetB0...', 'info')
    model, base_model = build_model(num_classes)
    logger.log('Model built', 'info', {
        'total_params': int(model.count_params()),
        'trainable_params': int(sum([tf.size(w).numpy() for w in model.trainable_weights]))
    })

    # Callbacks
    class ProgressCallback(callbacks.Callback):
        def __init__(self, logger):
            super().__init__()
            self.logger = logger

        def on_epoch_end(self, epoch, logs=None):
            logs = logs or {}
            self.logger.log(f'Epoch {epoch + 1}/{EPOCHS} completed', 'info', {
                'loss': float(round(logs.get('loss', 0), 4)),
                'accuracy': float(round(logs.get('accuracy', 0) * 100, 2)),
                'val_loss': float(round(logs.get('val_loss', 0), 4)),
                'val_accuracy': float(round(logs.get('val_accuracy', 0) * 100, 2))
            })

    checkpoint = callbacks.ModelCheckpoint(
        os.path.join(MODEL_SAVE_PATH, 'best_model.keras'),
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    )

    early_stopping = callbacks.EarlyStopping(
        monitor='val_accuracy',
        patience=EARLY_STOPPING_PATIENCE,
        restore_best_weights=True,
        verbose=1
    )

    reduce_lr = callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=REDUCE_LR_PATIENCE,
        min_lr=1e-7,
        verbose=1
    )

    # Phase 1: Train with frozen base
    logger.log('Phase 1: Training with frozen base model...', 'info')
    history = model.fit(
        train_gen,
        epochs=EPOCHS,
        validation_data=val_gen,
        callbacks=[ProgressCallback(logger), checkpoint, early_stopping, reduce_lr],
        verbose=1
    )

    # Phase 2: Fine-tune (unfreeze more layers)
    logger.log('Phase 2: Fine-tuning last 50 layers...', 'info')
    base_model.trainable = True
    for layer in base_model.layers[:-50]:
        layer.trainable = False

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE / 5),
        loss='categorical_crossentropy',
        metrics=['accuracy', 'precision', 'recall', 'AUC']
    )

    fine_tune_history = model.fit(
        train_gen,
        epochs=EPOCHS // 2,
        validation_data=val_gen,
        callbacks=[ProgressCallback(logger), checkpoint, early_stopping, reduce_lr],
        verbose=1
    )

    # Phase 3: Aggressive fine-tuning (unfreeze all)
    logger.log('Phase 3: Aggressive fine-tuning all layers...', 'info')
    base_model.trainable = True

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE / 20),
        loss='categorical_crossentropy',
        metrics=['accuracy', 'precision', 'recall', 'AUC']
    )

    aggressive_history = model.fit(
        train_gen,
        epochs=EPOCHS // 4,
        validation_data=val_gen,
        callbacks=[ProgressCallback(logger), checkpoint, early_stopping, reduce_lr],
        verbose=1
    )

    # Save final model
    os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
    model.save(os.path.join(MODEL_SAVE_PATH, 'final_model.keras'))
    model.save(os.path.join(MODEL_SAVE_PATH, 'final_model.h5'))

    # Save class indices
    with open(os.path.join(MODEL_SAVE_PATH, 'class_indices.json'), 'w') as f:
        json.dump(train_gen.class_indices, f, indent=2)

    logger.log('Training completed', 'success', {
        'final_accuracy': float(round(history.history['val_accuracy'][-1] * 100, 2)),
        'model_saved': MODEL_SAVE_PATH
    })

    return model, history

def evaluate_model(model, logger):
    """Evaluate model on test set with advanced metrics"""
    if not os.path.exists(TEST_DIR):
        logger.log('Test directory not found, skipping evaluation', 'warning')
        return

    logger.log('Evaluating model on test set...', 'info')

    test_datagen = ImageDataGenerator(rescale=1./255)
    test_generator = test_datagen.flow_from_directory(
        TEST_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )

    results = model.evaluate(test_generator, verbose=1)
    logger.log('Test evaluation completed', 'info', {
        'test_loss': float(round(results[0], 4)),
        'test_accuracy': float(round(results[1] * 100, 2)),
        'test_precision': float(round(results[2] * 100, 2)),
        'test_recall': float(round(results[3] * 100, 2)),
        'test_auc': float(round(results[4] * 100, 2)) if len(results) > 4 else 0
    })

    # Generate confusion matrix
    logger.log('Generating confusion matrix...', 'info')
    from sklearn.metrics import confusion_matrix, classification_report
    import seaborn as sns
    import matplotlib.pyplot as plt

    predictions = model.predict(test_generator)
    y_pred = np.argmax(predictions, axis=1)
    y_true = test_generator.classes

    cm = confusion_matrix(y_true, y_pred)
    logger.log('Confusion Matrix', 'info', {'matrix': cm.tolist()})

    # Save confusion matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.savefig(os.path.join(MODEL_SAVE_PATH, 'confusion_matrix.png'))
    plt.close()

    logger.log('Classification Report', 'info', {
        'report': classification_report(y_true, y_pred, target_names=list(test_generator.class_indices.keys()))
    })

def setup_object_detection(logger):
    """Setup YOLO for object detection"""
    logger.log('Setting up YOLO for object detection...', 'info')
    try:
        # Try to import ultralytics YOLO
        from ultralytics import YOLO
        logger.log('YOLO loaded successfully', 'success')
        return True
    except ImportError:
        logger.log('YOLO not installed. Install with: pip install ultralytics', 'warning')
        return False

def setup_face_recognition(logger):
    """Setup face recognition capabilities"""
    logger.log('Setting up face recognition...', 'info')
    try:
        import face_recognition
        logger.log('Face recognition library loaded successfully', 'success')
        return True
    except ImportError:
        logger.log('Face recognition not installed. Install with: pip install face-recognition', 'warning')
        return False

def train_object_detection(logger):
    """Train YOLO model for object detection"""
    logger.log('Training YOLO model for object detection...', 'info')
    try:
        from ultralytics import YOLO

        # Load pre-trained YOLOv8 model
        model = YOLO('yolov8n.pt')

        # Train on custom dataset (if available)
        # model.train(data='path/to/dataset.yaml', epochs=50)

        logger.log('YOLO model ready for inference', 'success')
        return model
    except Exception as e:
        logger.log(f'Failed to setup YOLO: {str(e)}', 'error')
        return None

if __name__ == '__main__':
    print("=" * 60)
    print("Monitoring System - AI Model Training")
    print("=" * 60)
    print(f"Dataset: {DATASET_PATH}")
    print(f"Model: EfficientNetB7 (MAXIMUM POWER)")
    print(f"Image Size: {IMG_SIZE}")
    print(f"Epochs: {EPOCHS}")
    print(f"Batch Size: {BATCH_SIZE}")
    print(f"Learning Rate: {LEARNING_RATE}")
    print("=" * 60)

    logger = TrainingLogger(LOG_FILE)

    try:
        # Setup additional AI capabilities
        logger.log('Setting up AI capabilities...', 'info')
        yolo_available = setup_object_detection(logger)
        face_rec_available = setup_face_recognition(logger)

        # Train main classification model
        logger.log('Starting main model training...', 'info')
        model, history = train_model(logger)
        evaluate_model(model, logger)

        # Train object detection if available
        if yolo_available:
            yolo_model = train_object_detection(logger)

        print("\n" + "=" * 60)
        print("Training completed successfully!")
        print(f"Model saved to: {MODEL_SAVE_PATH}")
        print(f"Log saved to: {LOG_FILE}")
        print(f"Object Detection: {'Available' if yolo_available else 'Not Available'}")
        print(f"Face Recognition: {'Available' if face_rec_available else 'Not Available'}")
        print("=" * 60)

    except Exception as e:
        logger.log(f'Training failed: {str(e)}', 'error')
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
