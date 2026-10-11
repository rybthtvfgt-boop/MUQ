"""
سكريبت تدريب كاشف التدخين MUQ
تدريب كشف التدخين على بيانات حقيقية
"""

import tensorflow as tf
import sys
import io

# إصلاح الترميز لكونسول Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import json

# إعدادات التدريب
DATASET_PATH = r'C:\Users\moktata\Desktop\MUQ\smokingVSnotsmoking\dataset'
TRAIN_PATH = os.path.join(DATASET_PATH, 'training_data')
VAL_PATH = os.path.join(DATASET_PATH, 'validation_data')
TEST_PATH = os.path.join(DATASET_PATH, 'testing_data')

MODEL_SAVE_PATH = r'C:\Users\moktata\Desktop\MUQ\models'
HISTORY_PATH = r'C:\Users\moktata\Desktop\MUQ\training_history.json'

# إعدادات النموذج (مُعدلة للسرعة على CPU)
IMG_HEIGHT = 128
IMG_WIDTH = 128
BATCH_SIZE = 16
EPOCHS = 20
LEARNING_RATE = 0.001


def create_smoking_detection_model():
    """إنشاء نموذج CNN لكشف التدخين (نسخة مبسطة للسرعة)"""
    model = models.Sequential([
        # المجموعة 1
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=(IMG_HEIGHT, IMG_WIDTH, 3)),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),

        # المجموعة 2
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),

        # المجموعة 3
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),

        # تسطيح
        layers.Flatten(),

        # الطبقات الكثيفة (مُبسطة)
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),

        # طبقة الإخراج (فئتان: تدخين، غير مدخن)
        layers.Dense(2, activation='softmax')
    ])

    return model


def compile_model(model):
    """تجميع النموذج"""
    optimizer = tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE)
    model.compile(
        optimizer=optimizer,
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )
    return model


def create_data_generators():
    """إنشاء data generators للتدريب"""
    # زيادة البيانات للتدريب
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    # فقط rescale للتحقق والاختبار
    val_datagen = ImageDataGenerator(rescale=1./255)
    test_datagen = ImageDataGenerator(rescale=1./255)

    # تحميل البيانات
    train_generator = train_datagen.flow_from_directory(
        TRAIN_PATH,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    val_generator = val_datagen.flow_from_directory(
        VAL_PATH,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    test_generator = test_datagen.flow_from_directory(
        TEST_PATH,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )

    return train_generator, val_generator, test_generator


def plot_training_history(history):
    """رسم تاريخ التدريب"""
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs_range = range(1, len(acc) + 1)

    plt.figure(figsize=(15, 5))

    # رسم الدقة
    plt.subplot(1, 3, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.title('Training and Validation Accuracy')
    plt.legend()
    plt.grid(True)

    # رسم الخسارة
    plt.subplot(1, 3, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss')
    plt.legend()
    plt.grid(True)

    # رسم الدقة
    plt.subplot(1, 3, 3)
    plt.plot(epochs_range, history.history['precision'], label='Training Precision')
    plt.plot(epochs_range, history.history['val_precision'], label='Validation Precision')
    plt.xlabel('Epoch')
    plt.ylabel('Precision')
    plt.title('Training and Validation Precision')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    
    # حفظ الرسم
    plot_path = os.path.join(MODEL_SAVE_PATH, 'training_history.png')
    plt.savefig(plot_path)
    print(f"[INFO] Training plot saved to: {plot_path}")
    plt.close()


def train_model():
    """دالة التدريب الرئيسية"""
    print("=" * 60)
    print("تدريب نموذج كشف التدخين - MUQ System")
    print("=" * 60)

    # إنشاء مجلد الحفظ
    os.makedirs(MODEL_SAVE_PATH, exist_ok=True)

    # إنشاء النموذج
    print("\n[1/6] إنشاء النموذج...")
    model = create_smoking_detection_model()
    model.summary()

    # تجميع النموذج
    print("\n[2/6] تجميع النموذج...")
    model = compile_model(model)

    # إنشاء مولدات البيانات
    print("\n[3/6] تحميل البيانات...")
    train_generator, val_generator, test_generator = create_data_generators()

    # طباعة معلومات البيانات
    print(f"\n📊 معلومات البيانات:")
    print(f"   صور التدريب: {train_generator.samples}")
    print(f"   صور التحقق: {val_generator.samples}")
    print(f"   صور الاختبار: {test_generator.samples}")
    print(f"   عدد الفئات: {len(train_generator.class_indices)}")
    print(f"   الفئات: {train_generator.class_indices}")

    # الاسترجاعات
    print("\n[4/6] إعداد Callbacks...")
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            filepath=os.path.join(MODEL_SAVE_PATH, 'smoking_detector_best.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
    ]

    # التدريب
    print("\n[5/6] بدء التدريب...")
    print(f"   عدد الـepochs: {EPOCHS}")
    print(f"   حجم الـbatch: {BATCH_SIZE}")
    print(f"   معدل التعلم: {LEARNING_RATE}")
    print("\n" + "=" * 60)

    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=val_generator,
        callbacks=callbacks,
        verbose=1
    )

    # حفظ النموذج النهائي
    print("\n[6/6] حفظ النموذج...")
    final_model_path = os.path.join(MODEL_SAVE_PATH, 'smoking_detector_final.h5')
    model.save(final_model_path)
    print(f"✅ النموذج النهائي حفظ في: {final_model_path}")

    # حفظ تاريخ التدريب
    history_dict = {key: [float(x) for x in value] for key, value in history.history.items()}
    with open(HISTORY_PATH, 'w') as f:
        json.dump(history_dict, f, indent=2)
    print(f"✅ تاريخ التدريب حفظ في: {HISTORY_PATH}")

    # رسم التاريخ
    plot_training_history(history)

    # التقييم على بيانات الاختبار
    print("\n" + "=" * 60)
    print("تقييم النموذج على بيانات الاختبار")
    print("=" * 60)
    test_loss, test_acc, test_precision, test_recall = model.evaluate(test_generator, verbose=1)
    print(f"\n📊 نتائج الاختبار:")
    print(f"   Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")
    print(f"   Loss: {test_loss:.4f}")
    print(f"   Precision: {test_precision:.4f}")
    print(f"   Recall: {test_recall:.4f}")

    # حساب F1 Score
    f1_score = 2 * (test_precision * test_recall) / (test_precision + test_recall)
    print(f"   F1 Score: {f1_score:.4f}")

    print("\n" + "=" * 60)
    print("✅ التدريب اكتمل بنجاح!")
    print("=" * 60)

    return model, history


def export_model_for_production(model):
    """تصدير النموذج للإنتاج"""
    # تحويل إلى TFLite (اختياري - للاستخدام على الأجهزة المحمولة)
    try:
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        tflite_model = converter.convert()

        tflite_path = os.path.join(MODEL_SAVE_PATH, 'smoking_detector.tflite')
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        print(f"✅ نموذج TFLite حفظ في: {tflite_path}")
    except Exception as e:
        print(f"⚠️ خطأ في تحويل TFLite: {e}")


if __name__ == '__main__':
    # التدريب
    model, history = train_model()

    # التصدير للإنتاج
    export_model_for_production(model)

    print("\n🎉 كل شيء جاهز!")
    print(f"النموذج محفوظ في: {MODEL_SAVE_PATH}")
    print("يمكنك الآن استخدامه في ml_backend.py")
