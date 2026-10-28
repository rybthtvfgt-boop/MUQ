# نظام كشف التدخين - Smoking Detection System

نظام للكشف عن التدخين باستخدام الذكاء الاصطناعي والرؤية الحاسوبية.

## 📊 Dataset

الموقع: `F:\MUQ\dataset`

- **Training**: 805 صورة تدخين + 805 صورة غير تدخين
- **Validation**: مجلد validation_data
- **Testing**: مجلد testing_data

## 🚀 التثبيت

```bash
cd F:\MUQ\smoking_detection
pip install -r requirements.txt
```

## 🎮 الاستخدام

### التدريب:
```bash
python train.py --config config.yaml
```

### المراقبة على صورة:
```bash
python predict.py --config config.yaml --image F:/MUQ/dataset/training_data/smoking/smoking_0001.jpg
```

### المراقبة على فيديو:
```bash
python predict.py --config config.yaml --video video.mp4 --output output.mp4
```

## 📋 الفئات
- 0: smoking (تدخين)
- 1: notsmoking (غير تدخين)
