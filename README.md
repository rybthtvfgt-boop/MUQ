# نظام MUQ - نظام تسجيل الحضور بالتعرف على الوجوه

نظام متطور لتسجيل حضور الطلاب باستخدام تقنية التعرف على الوجوه، مع لوحات تحكم شاملة للأدمن والمدرسين والطلاب.

## 📁 هيكل المشروع

```
MUQ/
├── backend/              # Django REST Framework Backend
│   ├── attendance/       # Attendance & Schedule models
│   ├── departments/      # Department, Stage, Branch models
│   ├── users/           # User & FaceProfile models
│   ├── muq_system/      # Django project settings
│   ├── manage.py        # Django management script
│   ├── requirements.txt # Python dependencies
│   ├── Procfile         # Railway deployment config
│   ├── railway.json     # Railway project config
│   ├── .env.example     # Environment variables template
│   ├── DEPLOYMENT.md    # Deployment guide
│   └── README.md        # Backend documentation
│
├── frontend/            # Vanilla JavaScript Frontend
│   ├── HTML/           # HTML pages
│   ├── Js/             # JavaScript modules
│   ├── css/            # Stylesheets
│   ├── index.html      # Entry point
│   └── README.md       # Frontend documentation
│
├── _backups/           # Archived Flask & Node.js backups
│   ├── flask/          # Old Flask backend
│   └── nodejs/         # Old Node.js backend
│
├── AUDIT_PHASE1.md     # Initial audit report
└── README.md           # This file
```

## 🚀 البدء السريع

### الطريقة السهلة (Windows)

1. **إعداد البيئة (مرة واحدة فقط):**
```bash
setup-env.bat
```

2. **إنشاء مستخدم المشرف (مرة واحدة فقط):**
```bash
cd backend
venv\Scripts\activate
python manage.py create_superuser
```

3. **تشغيل النظام:**
- Terminal 1: `start.bat` (تشغيل Backend)
- Terminal 2: `start-frontend.bat` (تشغيل Frontend)

4. **فتح المتصفح:**
- افتح `http://localhost:8010` في المتصفح
- سجل الدخول بالمستخدم الذي أنشأته

### الطريقة اليدوية

#### Backend (Django)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
python manage.py migrate
python manage.py create_superuser
python manage.py runserver
```

Backend سيكون متاح على `http://localhost:8000/api/`

#### Frontend

```bash
cd frontend
python -m http.server 8010
```

Frontend سيكون متاح على `http://localhost:8010`

## 📖 دليل الاستخدام الشامل

راجع ملف [SETUP.md](SETUP.md) للحصول على دليل مفصل لجميع ميزات النظام.

## 🌐 النشر

### النشر على Railway

#### الخطوة 1: إعداد Railway

1. سجل الدخول إلى [Railway](https://railway.app)
2. أنشئ مشروع جديد
3. قم بربط مستودع GitHub الخاص بك

#### الخطوة 2: إعداد المتغيرات البيئية

في Railway، أضف المتغيرات التالية:

```
DEBUG=False
SECRET_KEY=<your-secret-key>
DB_ENGINE=postgresql
DB_NAME=<database-name>
DB_USER=<database-user>
DB_PASSWORD=<database-password>
DB_HOST=<database-host>
DB_PORT=5432
ALLOWED_HOSTS=<your-railway-app-url>
```

#### الخطوة 3: النشر التلقائي

- Railway سيقوم بالنشر تلقائياً عند كل push إلى الفرع `main`
- GitHub Actions ستعمل CI/CD تلقائياً

### النشر على GitHub

#### الخطوة 1: إنشاء مستودع GitHub

```bash
cd F:\MUQ
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/muq-system.git
git push -u origin main
```

#### الخطوة 2: إعداد GitHub Secrets

في GitHub repository settings، أضف:
- `RAILWAY_TOKEN`: Railway API token
- `SECRET_KEY`: Django secret key
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`: بيانات قاعدة البيانات

### النشر على Render

بديل لـ Railway:

1. سجل الدخول إلى [Render](https://render.com)
2. أنشئ New Web Service
3. Connect your GitHub repository
3. استخدم `backend/render.yaml` للإعدادات

### النشر المحلي

#### Backend (Django)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
python manage.py migrate
python create_admin.py
python manage.py runserver
```

Backend سيكون متاح على `http://localhost:8000`

#### بيانات تسجيل الدخول الافتراضية:
- **اسم المستخدم**: admin
- **كلمة المرور**: admin123

## المميزات

### للأدمن
- تسجيل الدخول (المشرف الأعلى)
- إدارة الطلاب (إضافة، تعديل، حذف) مع تحديد المادة والمرحلة والشعبة
- إدارة المدرسين (إضافة، تعديل، حذف) مع تحديد المادة والمرحلة والشعبة
- إدارة الموظفين (إداريين، أمنيين، خدمة)
- تسجيل بيانات الوجه للطلاب والمدرسين والموظفين
- إنشاء الجداول الدراسية حسب المادة والمرحلة والشعبة
- عرض الإحصائيات والتقارير

## كيفية الاستخدام

### 1. إعداد المشرف الأعلى (مرة واحدة فقط)
```bash
cd backend
python manage.py create_superuser
```
أدخل اسم المستخدم وكلمة المرور الجديدة
هذا الحساب سيكون له صلاحيات المشرف الأعلى

### 2. تشغيل النظام محلياً

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python -m http.server 8010
```

### 3. تسجيل الدخول
- افتح المتصفح على `http://localhost:8010`
- استخدم اسم المستخدم وكلمة المرور التي أنشأتها
- سيتم تحديد نوع المستخدم تلقائياً بناءً على الصلاحيات

### للمدرسين
- عرض الجدول الدراسي حسب المادة والمرحلة الخاصة بهم
- تسجيل الحضور باستخدام التعرف على الوجه الحقيقي
- تسجيل حضور الطلاب عبر الكاميرا مع مقارنة الوجوه
- تأكيد نهاية المحاضرة بالتصوير
- عرض سجل الحضور التفصيلي

### للطلاب
- عرض سجل الحضور الشخصي
- عرض الجدول الدراسي حسب المادتهم ومرحلتهم
- عرض الإحصائيات الشاملة
- عرض الملف الشخصي
- الوصول لتقرير الحضور والغياب الشامل

### للموظفين (إداريين، أمنيين، خدمة)
- تسجيل الحضور اليومي باستخدام التعرف على الوجه
- عرض سجل الحضور الشخصي
- عرض الإحصائيات الشاملة
- عرض الملف الشخصي

## التقنيات المستخدمة

### Backend
- Django 5.1.1
- Django REST Framework 3.15.2
- Django REST Framework SimpleJWT 5.3.1
- PostgreSQL
- Gunicorn
- Whitenoise

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla)
- WebRTC (Camera access)
- face-api.js (Face recognition)
- JWT Authentication

## المميزات الأمنية

- JWT authentication مع token refresh
- Token blacklisting عند تسجيل الخروج
- تشفير كلمات المرور
- CORS configuration
- Session security
- HSTS و SSL redirect في الإنتاج

## الدعم

- [Backend Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)
- [Deployment Guide](backend/DEPLOYMENT.md)
- [Initial Audit Report](AUDIT_PHASE1.md)

لأي استفسارات أو مشاكل، يرجى التواصل مع فريق الدعم الفني.

## License

Proprietary - MUQ System