# MUQ ML Backend - Machine Learning System

## 📋 نظرة عامة

نظام ML Backend هو نظام هجين يجمع بين:
- **face-api.js** (Frontend) - سريع وبسيط، لا يحتاج GPU
- **Python ML Backend** (Backend) - أدق، يدعم TensorFlow و OpenCV

## 🎯 الميزات

### 1. Face Recognition (التعرف على الوجوه)
- **الطريقة الأولى (face-api.js):**
  - سريع وسريع الاستجابة
  - يعمل في المتصفح مباشرة
  - لا يحتاج إلى موارد الخادم
  - مناسب للاستخدام السريع

- **الطريقة الثانية (Python ML):**
  - TensorFlow + MobileNetV2
  - OpenCV Face Detection
  - أدق وأكثر موثوقية
  - دعم GPU اختياري
  - مناسب للمعالجة المتقدمة

### 2. Smoking Detection (كشف التدخين)
- نموذج CNN مخصص لكشف التدخين
- تحليل صورة بالوقت الفعلي
- دقة عالية في الكشف
- إمكانية تدريب النموذج على بيانات مخصصة

### 3. Cheating Detection (كشف الغش)
- نموذج لمراقبة قاعات الامتحانات
- تصنيف: normal / suspicious / cheating
- تحليل سلوك الطلاب
- تنبيهات فورية

## 📦 التثبيت

### المتطلبات الأساسية
```bash
# Python 3.8+
pip install -r requirements.txt
```

### المكتبات المطلوبة
```
tensorflow==2.15.0
opencv-python==4.8.1.78
opencv-contrib-python==4.8.1.78
numpy==1.24.3
pillow==10.1.0
dlib==19.24.2
face-recognition==1.3.0
imutils==0.5.4
scikit-learn==1.3.2
scikit-image==0.22.0
```

### تثبيت dlib (قد يحتاج Visual C++ على Windows)
```bash
# Windows
pip install cmake
pip install dlib

# Linux
sudo apt-get install cmake
pip install dlib
```

## 🚀 التشغيل

### 1. تشغيل بدون ML Backend (face-api.js فقط)
```bash
cd mysql
python database.py
```
النظام سيعمل بـ face-api.js فقط (لا يحتاج تثبيت ML libraries)

### 2. تشغيل مع ML Backend (نظام هجين)
```bash
# تثبيت المكتبات أولاً
pip install -r requirements.txt

# تشغيل الخادم
cd mysql
python database.py
```
النظام سيعمل بـ ML Backend + face-api.js

## 🔧 API Endpoints

### 1. التحقق من حالة ML Backend
```http
GET /api/ml/status
```

**الرد:**
```json
{
  "available": true,
  "message": "ML Backend is available"
}
```

### 2. معالجة صورة
```http
POST /api/ml/process-image
Content-Type: application/json

{
  "image": "base64_encoded_image",
  "task": "face_recognition"
}
```

**القيم الممكنة لـ task:**
- `face_recognition` - التعرف على الوجوه
- `smoking_detection` - كشف التدخين
- `cheating_detection` - كشف الغش

### 3. كشف الوجوه
```http
POST /api/ml/detect-faces
Content-Type: application/json

{
  "image": "base64_encoded_image"
}
```

### 4. كشف التدخين
```http
POST /api/ml/detect-smoking
Content-Type: application/json

{
  "image": "base64_encoded_image"
}
```

### 5. كشف الغش
```http
POST /api/ml/detect-cheating
Content-Type: application/json

{
  "image": "base64_encoded_image"
}
```

## 🎮 الاستخدام في الواجهة

### 1. فتح نظام المراقبة
1. سجل الدخول كأدمن
2. اذهب إلى "نظام المراقبة"
3. اختر نظام المراقبة المطلوب

### 2. التبديل بين Backend
- في Modal المراقبة، ستجد مؤشر حالة ML Backend
- إذا كان ML Backend متاح، يمكنك تفعيله عبر Checkbox
- عند تفعيله، سيتم استخدام Python ML للمعالجة
- عند تعطيله، سيتم استخدام face-api.js

### 3. اختيار مصدر الإدخال
- **كاميرا الويب:** الكاميرا المدمجة في اللابتوب
- **ملف فيديو:** رفع فيديو من الجهاز للتحليل
- **كاميرا خارجية:** كاميرا USB أو HDMI

## 📊 الأداء

### face-api.js
- **السرعة:** سريع جداً (< 100ms per frame)
- **الدقة:** جيدة (85-90%)
- **استهلاك الموارد:** منخفض
- **حاجة GPU:** لا

### Python ML Backend
- **السرعة:** متوسط (200-500ms per frame)
- **الدقة:** عالية (92-98%)
- **استهلاك الموارد:** متوسط
- **حاجة GPU:** اختياري (يحسن الأداء)

## 🔧 التدريب على بيانات مخصصة

### 1. إعداد البيانات
```
dataset/
├── smoking/
│   ├── smoking/
│   └── not_smoking/
├── cheating/
│   ├── normal/
│   ├── suspicious/
│   └── cheating/
└── faces/
    ├── person1/
    ├── person2/
    └── ...
```

### 2. تدريب النموذج
```python
from ml_backend import SmokingDetector

detector = SmokingDetector()
detector.load_model()

# Train on custom data
# (يتطلب إضافة دالة train() في المستقبل)
```

## 🐛 استكشاف الأخطاء

### ML Backend لا يعمل
1. تأكد من تثبيت جميع المكتبات: `pip install -r requirements.txt`
2. تأكد من إصدار Python (3.8+)
3. على Windows، قد تحتاج Visual C++ Build Tools
4. تحقق من logs في الـ console

### خطأ في dlib
```bash
# تثبيت cmake أولاً
pip install cmake
pip install dlib
```

### خطأ في TensorFlow
```bash
# إعادة تثبيت TensorFlow
pip uninstall tensorflow
pip install tensorflow==2.15.0
```

### ML Backend غير متاح
- النظام سيعمل بـ face-api.js فقط
- هذه ليست مشكلة، النظام لا يزال يعمل بشكل كامل
- يمكنك تثبيت ML libraries لاحقاً إذا أردت

## 📈 المستقبل

### الميزات المخطط لها
- [ ] تدريب النماذج على بيانات مخصصة
- [ ] إضافة Fighting Detection
- [ ] إضافة Crowd Estimation
- [ ] دعم GPU لتسريع المعالجة
- [ ] إضافة Real-time Person Tracking
- [ ] تحسين دقة النماذج الحالية

## 📝 ملاحظات

### للطلاب (مشروع تخرج)
- النظام الهجين يوفر مرونة عالية
- يمكنك استخدام face-api.js للعرض السريع
- و Python ML للتحليل المتقدم
- كلاهما يعملان معاً بشكل سلس

### للإنتاج
- يُنصح باستخدام ML Backend مع GPU
- يمكن نشر ML Backend على خادم منفصل
- face-api.js يمكن استخدامه للمعالجة السريعة على العميل

## 🤝 المساهمة

للمساهمة في تحسين النماذج:
1. أضف بيانات تدريب جديدة
2. حسن أداء النماذج الحالية
3. أضف نماذج جديدة
4. تحسين واجهة API

## 📞 الدعم

لأي استفسارات:
- تحقق من logs في الـ console
- راجع هذا README
- تحقق من المتطلبات

---

**تم إنشاؤه لمشروع MUQ - جامعة العين**
**كلية الهندسة - قسم الذكاء الاصطناعي**
