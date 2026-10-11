# MUQ - نظام الحضور والمراقبة بالذكاء الاصطناعي

## 🎓 مشروع تخرج - كلية الهندسة - قسم الذكاء الاصطناعي
**جامعة العين**

---

## 📋 نظرة عامة

نظام متكامل لإدارة الحضور والمراقبة باستخدام تقنيات التعلم الآلي والتعرف على الوجوه. النظام يوفر:
- تسجيل الحضور التلقائي بالتعرف على الوجوه
- إدارة الطلاب والمدرسين والموظفين
- لوحات تحكم للإدارة
- مراقبة البوابات بالكاميرات
- تقارير وإحصائيات شاملة

---

## 🏗️ بنية المشروع

```
MUQ/
├── HTML/                    # صفحات الويب
│   ├── login.html          # صفحة تسجيل الدخول
│   ├── admin-dashboard.html # لوحة تحكم الأدمن
│   ├── student-dashboard.html
│   ├── teacher-dashboard.html
│   ├── staff-dashboard.html
│   ├── face-registration.html     # تسجيل الوجوه
│   ├── face-registration-new.html
│   ├── gate-entry.html             # نظام البوابات
│   ├── monitoring-system.html      # نظام المراقبة
│   └── attendance-report.html     # تقارير الحضور
│
├── Js/                      # ملفات JavaScript
│   ├── database.js         # إدارة قاعدة البيانات المحلية
│   ├── login.js            # تسجيل الدخول
│   ├── admin-dashboard.js  # لوحة الأدمن
│   ├── student-dashboard.js
│   ├── teacher-dashboard.js
│   ├── staff-dashboard.js
│   ├── face-recognition.js # التعرف على الوجوه
│   └── face-api.js         # مكتبة face-api.js
│
├── css/                     # ملفات التنسيق
│   └── style.css           # الأنماط الرئيسية
│
├── mysql/                   # Backend Python + MySQL
│   ├── database.py         # Flask API + SQLAlchemy
│   ├── database.sql        # schema قاعدة البيانات
│   ├── requirements.txt    # مكتبات Python
│   ├── check_database.py   # فحص قاعدة البيانات
│   └── health_check.py     # فحص صحة النظام
│
├── docs/                    # التوثيق
│   ├── DEPLOYMENT_GUIDE.txt
│   ├── DEPLOYMENT_PLATFORMS.txt
│   └── CHANGELOG.txt
│
├── scripts/                 # سكريبتات الإدارة
│   ├── backup.sh          # نسخ احتياطي (Linux)
│   ├── restore.sh         # استعادة (Linux)
│   ├── monitor.sh         # مراقبة (Linux)
│   ├── backup.ps1         # نسخ احتياطي (Windows)
│   ├── restore.ps1        # استعادة (Windows)
│   └── monitor.ps1        # مراقبة (Windows)
│
├── index.html              # الصفحة الرئيسية
├── .env.example            # نموذج متغيرات البيئة
├── Dockerfile              # إعدادات Docker
├── docker-compose.yml      # Docker Compose
├── requirements.txt        # مكتبات Python الرئيسية
└── README.md              # هذا الملف
```

---

## 🚀 التقنيات المستخدمة

### Frontend
- **HTML5** - بنية الصفحات
- **CSS3** - التصميم والألوان
- **JavaScript (ES6+)** - التفاعلية
- **face-api.js** - التعرف على الوجوه
- **Chart.js** - المخططات البيانية

### Backend
- **Python 3.14** - لغة البرمجة
- **Flask** - إطار العمل
- **Flask-SQLAlchemy** - ORM
- **PyMySQL** - MySQL Driver
- **Flask-CORS** - CORS Support

### Database
- **MySQL 8.0** - قاعدة البيانات

### DevOps
- **Docker** - حاوية التطبيق
- **Docker Compose** - إدارة الحاويات
- **GitHub Actions** - CI/CD
- **Railway/Render/Heroku** - منصات النشر

---

## 🔧 التثبيت والتشغيل

### المتطلبات
- Python 3.14+
- MySQL 8.0+
- npm (اختياري)
- Docker (اختياري)

### خطوات التثبيت

#### 1. استنساخ المشروع
```bash
git clone <repository-url>
cd MUQ
```

#### 2. تثبيت مكتبات Python
```bash
pip install -r requirements.txt
pip install -r mysql/requirements.txt
```

#### 3. إعداد قاعدة البيانات MySQL
```bash
# تسجيل الدخول إلى MySQL
mysql -u root -p

# إنشاء قاعدة البيانات
CREATE DATABASE muq_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# استيراد schema
USE muq_db;
SOURCE mysql/database.sql;
```

#### 4. إعداد متغيرات البيئة
```bash
cp .env.example .env
# عدل .env حسب إعداداتك
```

#### 5. تشغيل Backend
```bash
cd mysql
python database.py
```
الخادم سيعمل على: `http://localhost:5000`

#### 6. تشغيل Frontend
```bash
cd ..
python -m http.server 8000
```
الواجهة ستعمل على: `http://localhost:8000`

---

## 🔐 بيانات تسجيل الدخول الافتراضية

| النوع | اسم المستخدم | كلمة المرور |
|-------|--------------|-------------|
| أدمن | muq | 12345 |

⚠️ **مهم:** غيّر كلمة المرور الافتراضية في الإنتاج!

---

## 📊 الميزات الرئيسية

### 1. نظام تسجيل الدخول
- تسجيل دخول آمن بالكامل
- صلاحيات متعددة (أدمن، طالب، مدرس، موظف)
- إدارة الجلسات

### 2. لوحة تحكم الأدمن
- إدارة الطلاب
- إدارة المدرسين
- إدارة الموظفين
- إدارة الأقسام والمراحل
- إدارة البوابات
- إدارة الجدول الدراسي
- الملاحظات
- البحث المتقدم
- الإحصائيات والمخططات

### 3. التعرف على الوجوه
- تسجيل الوجوه للطلاب
- تسجيل الوجوه للمدرسين
- تسجيل الوجوه للموظفين
- التعرف التلقائي عند البوابات
- دعم متعدد الوجوه لكل شخص

### 4. نظام البوابات
- بوابة الدخول الرئيسية
- بوابات الفصول الدراسية
- بوابات الموظفين
- بوابات المدرسين
- مراقبة حية بالكاميرات

### 5. تقارير الحضور
- تقارير يومية
- تقارير شهرية
- تقارير حسب الفصل
- تصدير البيانات
- رسوم بيانية

### 6. المراقبة الحية
- عرض الكاميرات المباشرة
- التعرف على الوجوه بالوقت الفعلي
- تسجيل الفيديو
- التنبيهات التلقائية

---

## 🛠️ هيكل قاعدة البيانات

### الجداول الرئيسية:
- **users** - المستخدمين
- **students** - الطلاب
- **teachers** - المدرسين
- **administrative_staff** - الموظفين الإداريين
- **security_staff** - الموظفين الأمنيين
- **service_staff** - موظفي الخدمة
- **departments** - الأقسام
- **stages** - المراحل
- **branches** - الشعب
- **gateways** - البوابات
- **schedule** - الجدول الدراسي
- **attendance** - حضور الطلاب
- **staff_attendance** - حضور الموظفين

---

## 🤖 نظام Machine Learning الهجين

### النظام الهجين
المشروع يدعم نظام هجين يجمع بين:
- **face-api.js** (Frontend) - سريع وبسيط، لا يحتاج GPU
- **Python ML Backend** (Backend) - أدق، يدعم TensorFlow و OpenCV

### الميزات
- ✅ Face Recognition بالـ TensorFlow
- ✅ Smoking Detection (كشف التدخين)
- ✅ Cheating Detection (كشف الغش في الامتحانات)
- ✅ تبديل تلقائي بين face-api.js و ML Backend
- ✅ دعم كاميرات خارجية وملفات الفيديو

### التثبيت
```bash
# للعمل بـ face-api.js فقط (لا يحتاج ML libraries)
cd mysql
python database.py

# للعمل مع ML Backend (يحتاج تثبيت المكتبات)
pip install -r requirements.txt
cd mysql
python database.py
```

### التوثيق
راجع `ML_BACKEND_README.md` لمزيد من التفاصيل حول ML Backend

## 📦 النشر

### Railway (موصى به)
```bash
# تثبيت Railway CLI
npm install -g @railway/cli

# تسجيل الدخول
railway login

# نشر المشروع
railway up
```

### Docker
```bash
# بناء الصورة
docker build -t muq-system .

# تشغيل الحاوية
docker run -p 5000:5000 muq-system
```

### Docker Compose
```bash
docker-compose up -d
```

---

## 📚 التوثيق

للمزيد من المعلومات، راجع:
- `docs/DEPLOYMENT_GUIDE.txt` - دليل النشر الشامل
- `docs/DEPLOYMENT_PLATFORMS.txt` - مقارنة منصات النشر
- `docs/CHANGELOG.txt` - سجل التغييرات

---

## 🤝 المساهمة

هذا مشروع تخرج لطلاب مادة Machine Learning. للمساهمة:
1. Fork المشروع
2. أنشئ branch جديد
3. Commit التغييرات
4. Push إلى Branch
5. افتح Pull Request

---

## 👥 الفريق

- **الدكتور المشرف:** [الاسم]
- **الطلاب:**
  - [اسم الطالب 1]
  - [اسم الطالب 2]
  - [اسم الطالب 3]

---

## 📄 الترخيص

هذا المشروع مخصص لأغراض تعليمية لجامعة العين - كلية الهندسة - قسم الذكاء الاصطناعي.

---

## 📞 الدعم

لأي استفسارات، يرجى التواصل مع:
- البريد الإلكتروني: [email]
- الموقع: [website]

---

## 🎯 خارطة الطريق المستقبلية

- [ ] إضافة Mobile App
- [ ] تحسين دقة التعرف على الوجوه
- [ ] إضافة نظام الإشعارات
- [ ] دعم لغات متعددة
- [ ] تحسين الأمان
- [ ] إضافة نظام Backup السحابي

---

**صُنع بـ ❤️ لجامعة العين**
