# نظام مراقبة الامتحانات - Exam Monitoring System

نظام متكامل لمراقبة الامتحانات باستخدام الذكاء الاصطناعي والرؤية الحاسوبية للكشف عن الغش والسلوك المشبوه.

## 🎯 الميزات

### 1. **كشف الغش والسلوك المشبوه**
- ✅ اكتشاف استخدام الهواتف المحمولة
- ✅ اكتشاف استخدام اللابتوب والأجهزة الإلكترونية
- ✅ كشف التعاون بين الطلاب (أكثر من شخص في الإطار)
- ✅ اكتشاف الأجهزة غير المصرح بها

### 2. **التعرف على الوجوه والهوية**
- ✅ التعرف على هوية الطلاب
- ✅ التحقق من الحضور والغياب
- ✅ ربط ببيانات نظام MUQ

### 3. **تتبع الحركة**
- ✅ تتبع حركة الطلاب في القاعة
- ✅ حساب عدد الطلاب الحاضرين
- ✅ مراقبة الخروج والدخول

### 4. **كشف الكائنات**
- ✅ اكتشاف الكتب والأوراق
- ✅ اكتشاف المشروبات والأشياء الممنوعة
- ✅ رصد الأشياء غير المصرح بها

## 📁 هيكل المشروع

```
exam_monitoring/
├── config.yaml          # ملف التكوين
├── train.py            # سكريبت التدريب
├── evaluate.py         # سكريبت التقييم
├── predict.py          # سكريبت التنبؤ والمراقبة
├── requirements.txt     # المكتبات المطلوبة
└── README.md          # هذا الملف
```

## 🚀 التثبيت

### 1. تثبيت المكتبات المطلوبة

```bash
pip install -r requirements.txt
```

### 2. التأكد من تثبيت PyTorch مع CUDA (اختياري)

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 📊 بيانات التدريب

يستخدم النظام dataset **CCTV-Exam-Monitor-Dataset**:

- **Train**: 7,734 صورة
- **Test**: 220 صورة
- **Valid**: 202 صورة

الموقع: `F:\MUQ\CCTV-Exam -Monitor -Dataset`

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
  epochs: 100
  batch_size: 16
  img_size: 640
  device: cuda

# قواعد كشف الغش
cheating_detection:
  phone_threshold: 0.6
  unauthorized_objects: ['cell_phone', 'laptop', 'keyboard', 'mouse']
```

## 🎮 الاستخدام

### 1. **تدريب النموذج**

```bash
python train.py --config config.yaml
```

### 2. **تقييم النموذج**

```bash
python evaluate.py --config config.yaml --model exam_monitor_yolov8n.pt
```

### 3. **المراقبة على صورة**

```bash
python predict.py --config config.yaml --image path/to/image.jpg
```

### 4. **المراقبة على فيديو**

```bash
python predict.py --config config.yaml --video path/to/video.mp4 --output output.mp4
```

## 📈 الأداء

يستخدم النظام **YOLOv8** المدرب على dataset COCO مع تحسينات خاصة بمراقبة الامتحانات:

### الفئات المكتشفة:
- 👤 Person (طالب/مدرس)
- 📱 Cell Phone (هاتف محمول)
- 💻 Laptop (لابتوب)
- ⌨️ Keyboard (لوحة مفاتيح)
- 🖱️ Mouse (فأرة)
- 📚 Book (كتاب/ورقة)
- 🍶 Cup/Bottle (مشروبات)

### القواعد:
- ⚠️ **خطر عالي**: استخدام الهاتف أو اللابتوب
- ⚠️ **خطر متوسط**: أكثر من شخص في الإطار، أجهزة إلكترونية كثيرة
- ✅ **طبيعي**: لا يوجد نشاط مشبوه

## 🔗 التكامل مع نظام MUQ

لربط نظام المراقبة مع نظام MUQ:

1. **API Endpoint**: إنشاء endpoint في backend لاستقبال نتائج المراقبة
2. **Real-time Streaming**: إرسال الصور من الكاميرات إلى النظام
3. **Database**: تخزين أحداث الغش في قاعدة البيانات
4. **Alerts**: إرسال تنبيهات فورية للمشرفين

## 📝 أمثلة الاستخدام

### مثال 1: مراقبة صورة فردية

```python
from predict import ExamMonitor

monitor = ExamMonitor('config.yaml')
result = monitor.process_image('exam_room_1.jpg')

# النتيجة
# {
#     'analysis': {
#         'persons': 2,
#         'phones': 1,
#         'laptops': 0,
#         'books': 3
#     },
#     'cheating': [
#         {'type': 'phone_usage', 'severity': 'high', 'count': 1},
#         {'type': 'multiple_persons', 'severity': 'medium', 'count': 2}
#     ]
# }
```

### مثال 2: مراقبة فيديو مباشر

```python
from predict import ExamMonitor

monitor = ExamMonitor('config.yaml')
monitor.process_video('exam_stream.mp4', 'output.mp4')
```

## 🛠️ التخصيص

### إضافة فئات جديدة

عدّل `config.yaml`:

```yaml
detection:
  custom_classes:
    - smartwatch: 85
    - tablet: 69
```

### تعديل قواعد الغش

```yaml
cheating_detection:
  custom_rules:
    - head_down: true
    - looking_around: true
    - whispering: true
```

## 📚 المراجع

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [COCO Dataset](https://cocodataset.org/)
- [OpenCV Documentation](https://docs.opencv.org/)

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
