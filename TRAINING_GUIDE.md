# تدريب نموذج Smoking Detection - دليل التدريب

## 📋 نظرة عامة

هذا الدليل يشرح كيفية تدريب نموذج كشف التدخين (Smoking Detection) على بيانات حقيقية لتحسين دقة نظام المراقبة.

## 🎯 الهدف

تدريب نموذج CNN لكي:
- يكتشف الأشخاص المدخنين بدقة عالية
- يقلل الأخطاء (false positives)
- يعمل بشكل أفضل في بيئة الجامعة

## 📂 هيكلية البيانات

المسار: `C:\Users\moktata\Desktop\MUQ\smokingVSnotsmoking\dataset`

```
dataset/
├── training_data/      # صور التدريب (70%)
│   ├── smoking/         # صور أشخاص يدخنون
│   └── not_smoking/    # صور أشخاص لا يدخنون
├── validation_data/    # صور التحقق (15%)
│   ├── smoking/
│   └── not_smoking/
└── testing_data/       # صور الاختبار (15%)
    ├── smoking/
    └── not_smoking/
```

## 🚀 خطوات التدريب

### 1. التحقق من البيانات

تأكد أن:
- كل صورة في المجلد الصحيح
- الصور بصيغة (JPG, PNG)
- الحجم مناسب (يفضل 2000x2000 pixels)
- التوزيع متوازن بين الفئتين

### 2. تشغيل التدريب

```bash
cd C:\Users\moktata\Desktop\MUQ
python train_smoking_detector.py
```

### 3. مراقبة التدريب

السكربت سيعرض:
- التقدم لكل epoch
- دقة التدريب (Training Accuracy)
- دقة التحقق (Validation Accuracy)
- الخسارة (Loss)
- Precision و Recall

### 4. النتائج

بعد انتهاء التدريب:
- النموذج يحفظ في: `models/smoking_detector_final.h5`
- أفضل نموذج يحفظ في: `models/smoking_detector_best.h5`
- رسم بياني للنتائج في: `models/training_history.png`
- تاريخ التدريب في: `training_history.json`

## ⚙️ إعدادات التدريب

يمكنك تعديل الإعدادات في `train_smoking_detector.py`:

```python
# حجم الصور
IMG_HEIGHT = 224
IMG_WIDTH = 224

# حجم الباتش
BATCH_SIZE = 32

# عدد الـepochs
EPOCHS = 50

# معدل التعلم
LEARNING_RATE = 0.001
```

### تعديلات مقترحة:

- **للبيانات قليلة:** `BATCH_SIZE = 16`, `EPOCHS = 30`
- **للبيانات كثيرة:** `BATCH_SIZE = 64`, `EPOCHS = 100`
- **للدقة أعلى:** `EPOCHS = 100`, `LEARNING_RATE = 0.0001`

## 📊 فهم النتائج

### Accuracy (الدقة)
- النسبة المئوية من التوقعات الصحيحة
- مثال: 0.95 = 95% دقة

### Precision (الدقة الإيجابية)
- من التوقعات الإيجابية الصحيحة
- مهم لتقليل الأخطاء (تحذير كاذب)

### Recall (الاستدعاء)
- من الحالات الإيجابية المكتشفة
- مهم لعدم تفويت حالة تدخين

### F1 Score
- المتوسط التوافقي بين Precision و Recall
- مقياس شامل للنموذج

## 🔧 تحسين النموذج

### إذا كانت الدقة منخفضة (< 80%):

1. **أكثر من البيانات:**
   - جمع المزيد من الصور
   - تأكد من توازن الفئات

2. **عدل Data Augmentation:**
   ```python
   train_datagen = ImageDataGenerator(
       rescale=1./255,
       rotation_range=30,  # زيادة الدوران
       width_shift_range=0.3,  # زيادة الإزاحة
       zoom_range=0.3,  # زيادة التكبير
       horizontal_flip=True
   )
   ```

3. **زيادة الـepochs:**
   ```python
   EPOCHS = 100
   ```

4. **استخدام نموذج أقوى:**
   - بدلاً من 4 طبقات CNN، استخدم 6 أو 8 طبقات
   - أو استخدم Transfer Learning (ResNet50, EfficientNet)

### إذا كان Overfitting (دقة تدريب عالية، دقة تحقق منخفضة):

1. **زيادة Dropout:**
   ```python
   layers.Dropout(0.5) → layers.Dropout(0.7)
   ```

2. **أكثر من Regularization:**
   ```python
   # إضافة L2 regularization
   tf.keras.regularizers.l2(0.01)
   ```

3. **أقل عدد الطبقات أو النيورنات**

## 🎓 استخدام النموذج المدرب

بعد التدريب، سيتم تحميل النموذج تلقائياً في `ml_backend.py`:

```python
# في ml_backend.py
self.model_path = 'models/smoking_detector_final.h5'
```

النظام سيستخدم النموذج المدرب بدلاً من النموذج الافتراضي.

## 📈 مقارنة: قبل وبعد التدريب

### قبل التدريب (نموذج افتراضي):
- دقة: ~70-75%
- كثير من الأخطاء
- لا يعرف بيئة الجامعة

### بعد التدريب (نموذج مدرب):
- دقة: 90-98% (حسب جودة البيانات)
- أخطاء أقل
- متخصص لبيئة الجامعة

## 🐛 استكشاف الأخطاء

### خطأ: لا يوجد البيانات
```
[Errno 2] No such file or directory
```
**الحل:** تأكد من المسار في `DATASET_PATH`

### خطأ: خطأ في شكل الصور
```
ValueError: Input arrays must have the same number of samples
```
**الحل:** تأكد أن كل المجلدات تحتوي نفس عدد الصور تقريباً

### خطأ: Out of Memory
```
ResourceExhaustedError
```
**الحل:**
- قلل `BATCH_SIZE` إلى 16 أو 8
- قلل حجم الصور إلى 128x128
- أو استخدم GPU

### خطأ: Overfitting
```
Training accuracy: 99%, Validation accuracy: 70%
```
**الحل:**
- زيادة Dropout
- أقل عدد الـepochs
- أكثر من البيانات

## 🎯 النصائح

1. **جمع بيانات متنوعة:**
   - إضاءة مختلفة
   - زوايا مختلفة
   - مسافات مختلفة
   - بيئات مختلفة (داخل، خارج)

2. **توازن البيانات:**
   - نفس العدد تقريباً لكل فئة
   - إذا كان التوزيع غير متوازن، استخدم class weights

3. **استخدم Early Stopping:**
   - يوقف التدريب تلقائياً
   - يمنع overfitting
   - يوفر الوقت

4. **احفظ عدة نسخ:**
   - `smoking_detector_best.h5` - أفضل نموذج
   - `smoking_detector_final.h5` - آخر epoch
   - قارن بينهم واختر الأفضل

## 📝 المخرجات

بعد التدريب ستحصل على:

1. **النموذج:**
   - `models/smoking_detector_final.h5` (~50 MB)
   - `models/smoking_detector_best.h5` (~50 MB)

2. **التاريخ:**
   - `training_history.json` - بيانات التدريب
   - `models/training_history.png` - رسم بياني

3. **التقييم:**
   - Accuracy على بيانات الاختبار
   - Precision, Recall, F1 Score

## 🚀 خطوات ما بعد التدريب

1. **اختبار النموذج:**
   ```bash
   python test_smoking_detector.py
   ```

2. **دمج في النظام:**
   - النموذج سيُحمل تلقائياً في `ml_backend.py`
   - أعد تشغيل السيرفر

3. **المراقبة الحية:**
   - افتح نظام المراقبة
   - اختبر كشف التدخين
   - راقب الدقة

## 💡 نصائح لجمع البيانات

### صور "smoking":
- صور أشخاص يضغون
- سيجارة في اليد
- دخان في الفم
- بيئات مختلفة

### صور "not_smoking":
- صور أشخاص عاديين
- لا سيجارة معهم
- نفس البيئات تقريباً

### تجنب:
- صور من الإنترنت (ما تناسب البيئة)
- صور واضحة جداً أو مظلمة جداً
- صور صغيرة جداً

## 🎯 مثال التدريب المثالي

### مع بيانات جيدة (500 صور لكل فئة):
- Epoch 1-10: دقة ترتفع من 70% إلى 85%
- Epoch 11-30: دقة ترتفع من 85% إلى 92%
- Epoch 31-50: دقة تستقر عند 93-95%
- Stop: تلقائيا بسبب Early Stopping

### النتيجة النهائية:
- Test Accuracy: 94.5%
- Test Precision: 93.2%
- Test Recall: 95.1%
- F1 Score: 94.1%

## 📞 الدعم

إذا واجهت مشاكل:
1. تحقق من مسار البيانات
2. تأكد من حجم الذاكرة
3. راجع رسائل الخطأ في الـconsole
4. راجع هذا الدليل

---

**تم إنشاؤه لنظام MUQ - جامعة العين**
**كلية الهندسة - قسم الذكاء الاصطناعي**
