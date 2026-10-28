# نظام كشف الأنشطة الخطرة - Dangerous Activity Detection System

نظام متكامل للكشف عن الأنشطة الخطرة والأشياء الممنوعة باستخدام الذكاء الاصطناعي والرؤية الحاسوبية، مبني على dataset UCF-Crimes.

## 🎯 الأنشطة الخطرة المكتشفة

### 1. **الأنشطة العنيفة (خطر عالي)**
- ✅ إساءة المعاملة (Abuse)
- ✅ الاعتداء (Assault)
- ✅ القتال (Fighting)
- ✅ إطلاق النار (Shooting)
- ✅ السرقة بالقوة (Robbery)

### 2. **جرائم الممتلكات (خطر متوسط)**
- ✅ السطو (Burglary)
- ✅ السرقة من المتاجر (Shoplifting)
- ✅ السرقة (Stealing)

### 3. **حالات الطوارئ (خطر عالي)**
- ✅ الحريق العمد (Arson)
- ✅ الانفجارات (Explosion)
- ✅ حوادث الطرق (RoadAccidents)

### 4. **إنفاذ القانون (خطر متوسط)**
- ✅ القبض (Arrest)

## 📁 هيكل المشروع

```
danger_detection/
├── config.yaml          # ملف التكوين
├── train.py            # سكريبت التدريب
├── predict.py          # سكريبت التنبؤ والمراقبة
├── requirements.txt     # المكتبات المطلوبة
└── README.md          # هذا الملف
```

## 📊 Dataset UCF-Crimes

الموقع: `F:\MUQ\UCF_Crimes\UCF_Crimes\Videos`

### الفئات:
- **الفيديوات الطبيعية**: Training_Normal_Videos_Anomaly, Testing_Normal_Videos_Anomaly
- **الفيديوات الخطرة**: 13 فئة مختلفة

## 🚀 التثبيت

### 1. تثبيت المكتبات المطلوبة

```bash
cd F:\MUQ\danger_detection
pip install -r requirements.txt
```

### 2. التأكد من تثبيت PyTorch مع CUDA (اختياري)

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 🔧 التكوين

ملف `config.yaml` يحتوي على جميع إعدادات النظام:

```yaml
# اختيار نموذج YOLO
model:
  variant: yolov8n  # n=nano, s=small, m=medium, l=large, x=xlarge
  confidence: 0.5
  iou: 0.45

# إعدادات التدريب
training:
  epochs: 50
  batch_size: 8
  img_size: 640
  device: cuda

# قواعد كشف الخطر
danger_detection:
  person_count_threshold: 3      # تنبيه إذا أكثر من 3 أشخاص
  weapon_detection: true          # كشف الأسلحة
  violence_detection: true        # كشف العنف
```

## 🎮 الاستخدام

### 1. **استخراج الإطارات من الفيديوات (اختياري)**

```bash
python train.py --config config.yaml --extract-frames
```

سيقوم هذا باستخراج إطارات من فيديوهات UCF-Crimes للتحليل.

### 2. **تدريب النموذج**

```bash
python train.py --config config.yaml
```

### 3. **المراقبة على صورة**

```bash
python predict.py --config config.yaml --image path/to/image.jpg
```

### 4. **المراقبة على فيديو**

```bash
python predict.py --config config.yaml --video path/to/video.avi --output output.mp4
```

## 📈 الكشف عن الأشياء الخطرة

يستخدم النظام **YOLOv8** المدرب على dataset COCO مع فئات ذات صلة:

### الفئات المكتشفة:
- 👤 Person (أشخاص)
- 🔪 Knife (سكين)
- ✂️ Scissors (مقص)
- 📱 Cell Phone (هاتف)
- 🍶 Bottle (زجاجة)
- 🪑 Chair (كرسي)
- 🚒 Fire Hydrant (رشاش حريق)
- 🚦 Traffic Light (إشارة مرور)

## ⚠️ مستويات الخطر

### 🟢 منخفض (Low)
- نشاط طبيعي
- مواصلة المراقبة

### 🟠 متوسط (Medium)
- تجمع أشخاص (>3)
- أشياء مشبوهة
- زيادة المراقبة

### 🔴 عالي (High)
- أسلحة مكتشفة
- عنف أو سلوك خطير
- استجابة طارئة

## 📝 أمثلة الاستخدام

### مثال 1: مراقبة صورة فردية

```python
from predict import DangerDetector

detector = DangerDetector('config.yaml')
result = detector.process_image('scene.jpg')

# النتيجة
# {
#     'analysis': {
#         'persons': 5,
#         'weapons': 1,
#         'dangerous_objects': [...]
#     },
#     'assessment': {
#         'level': 'high',
#         'recommendation': 'emergency_response'
#     }
# }
```

### مثال 2: مراقبة فيديو مباشر

```python
from predict import DangerDetector

detector = DangerDetector('config.yaml')
detector.process_video('surveillance.avi', 'output.mp4')
```

## 🛠️ التخصيص

### إضافة فئات جديدة

عدّل `config.yaml`:

```yaml
activities:
  custom:
    - new_activity_1
    - new_activity_2
```

### تعديل عتبات الخطر

```yaml
danger_detection:
  person_count_threshold: 5  # تغيير العتبة
  custom_rules:
    - head_down: true
    - suspicious_movement: true
```

## 📊 إحصائيات Dataset

- **إجمالي الفئات**: 13 فئة خطرة + 2 فئة طبيعية
- **الفيديوات الخطرة**: Abuse, Arrest, Arson, Assault, Burglary, Explosion, Fighting, RoadAccidents, Robbery, Shooting, Shoplifting, Stealing
- **الفيديوات الطبيعية**: Training_Normal_Videos_Anomaly, Testing_Normal_Videos_Anomaly

## 🔔 نظام التنبيهات

### أنواع التنبيهات:
- 🖥️ عرض في Console
- 📝 تسجيل في Log
- 📧 إيميل (قيد التطوير)
- 📱 SMS (قيد التطوير)

### معلومات التنبيه:
- مستوى الخطر
- نوع التهديد
- التوصية
- الطابع الزمني

## 🔗 التكامل مع نظام MUQ

يمكن ربط نظام كشف الخطر مع:
- Backend API
- قاعدة البيانات
- نظام الإشعارات
- نظام المراقبة CCTV

## 📚 المراجع

- [UCF-Crimes Dataset](https://www.crcv.ucf.edu/projects/real-world/)
- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [COCO Dataset](https://cocodataset.org/)

## 💡 نصائح

1. استخدم `yolov8n` للسرعة، و `yolov8x` للدقة العالية
2. إذا لم يكن لديك GPU، استخدم CPU لكن سيكون أبطأ
3. قلل `frame_sample_rate` لزيادة السرعة
4. يمكنك إيقاف المراقبة في أي وقت بـ `q`

## 🤝 المساهمة

للمساهمة في المشروع:
1. Fork المشروع
2. إنشاء branch جديد
3. Commit التغييرات
4. Push إلى Branch
5. فتح Pull Request

## 📄 الترخيص

هذا المشروع جزء من نظام MUQ.

## 📞 الدعم

للدعم الفني:
- البريد الإلكتروني: support@muq.ai
- التوثيق: docs.muq.ai

---

**صُنع بـ ❤️ لنظام MUQ**
