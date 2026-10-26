# دليل النشر - Django Backend

## 🚀 النشر على Railway

### المتطلبات
- حساب على [Railway](https://railway.app)
- حساب على GitHub
- Railway CLI (اختياري)

### الخطوات

#### 1. إعداد المشروع

```bash
# التأكد من أن جميع الملفات موجودة
cd backend
ls -la
```

يجب أن يتضمن:
- `Procfile`
- `railway.json`
- `nixpacks.toml`
- `requirements.txt`
- `.env.example`

#### 2. إعداد GitHub

```bash
# تهيئة git
git init
git add .
git commit -m "Initial commit"

# إضافة remote
git remote add origin https://github.com/your-username/muq-backend.git

# دفع الكود
git branch -M main
git push -u origin main
```

#### 3. إعداد Railway من CLI

```bash
# تثبيت Railway CLI
npm install -g @railway/cli

# تسجيل الدخول
railway login

# إنشاء مشروع جديد
railway init

# إضافة خدمات
railway add
# اختر: PostgreSQL Database
railway add
# اختر: Python (Django)

# إعداد المتغيرات البيئية
railway variables set DEBUG=False
railway variables set SECRET_KEY=your-secret-key-here
railway variables set DB_ENGINE=postgresql
railway variables set ALLOWED_HOSTS=your-app-url.railway.app
```

#### 4. تشغيل Migrations

```bash
# من Railway CLI
railway run python manage.py migrate

# إنشاء مستخدم الأدمن
railway run python create_admin.py
```

#### 5. النشر

```bash
# النشر
railway up

# فتح النظام في المتصفح
railway open
```

### المتغيرات البيئية المطلوبة

| المتغير | الوصف | القيمة الافتراضية |
|---------|-------|-------------------|
| DEBUG | وضع التطوير | False |
| SECRET_KEY | مفتاح Django السري | قيمة عشوائية |
| DB_ENGINE | نوع قاعدة البيانات | postgresql |
| DB_NAME | اسم قاعدة البيانات | يتم إنشاؤه تلقائياً |
| DB_USER | مستخدم قاعدة البيانات | يتم إنشاؤه تلقائياً |
| DB_PASSWORD | كلمة مرور قاعدة البيانات | يتم إنشاؤه تلقائياً |
| DB_HOST | مضيف قاعدة البيانات | localhost |
| DB_PORT | منفذ قاعدة البيانات | 5432 |
| ALLOWED_HOSTS | النطاقات المسموحة | *.railway.app |

## 🚀 النشر على Render

### الخطوات

1. سجل الدخول إلى [Render](https://render.com)
2. أنشئ حساب جديد
3. Connect your GitHub repository
4. أنشئ New Web Service
5. إعدادات البناء:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn muq_system.wsgi:application --bind 0.0.0.0:$PORT --workers 4`
6. إضافة Environment Variables من قسم البيئة
7. اضغط Deploy

## 🚀 النشر على Heroku

### المتطلبات
- حساب على [Heroku](https://heroku.com)
- Heroku CLI

### الخطوات

```bash
# تثبيت Heroku CLI
# من https://devcenter.heroku.com/articles/heroku-cli

# تسجيل الدخول
heroku login

# إنشاء تطبيق
heroku create muq-backend

# إضافة PostgreSQL
heroku addons:create heroku-postgresql:mini

# إعداد المتغيرات البيئية
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALLOWED_HOSTS=*.herokuapp.com

# تشغيل Migrations
heroku run python manage.py migrate

# إنشاء مستخدم الأدمن
heroku run python create_admin.py

# النشر
git push heroku main
```

## 🔒 الأمان في الإنتاج

### 1. تغيير كلمة المرور الافتراضية

بعد النشر، قم بتغيير كلمة مرور الأدمن فوراً:

```bash
heroku run python manage.py changepassword admin
# أو من Railway CLI
railway run python manage.py changepassword admin
```

### 2. إعداد HTTPS

Railway و Render و Heroku يوفرون HTTPS تلقائياً.

### 3. CORS Configuration

تأكد من أن `ALLOWED_HOSTS` يتضمن نطاق تطبيقك.

## 📊 المراقبة

### Railway

- Dashboard: https://railway.app
- Logs: من لوحة التحكم في Railway

### Render

- Dashboard: https://dashboard.render.com
- Logs: من لوحة التحكم في Render

### Heroku

- Dashboard: https://dashboard.heroku.com
- Logs: `heroku logs --tail`

## 🔄 CI/CD

### GitHub Actions

تم إعداد `.github/workflows/deploy.yml` للنشر التلقائي على Railway.

 عند كل push إلى الفرع `main`:
1. تشغيل الاختبارات
2. تشغيل Migrations
3. النشر التلقائي

## 🐛 استكشاف الأخطاء

### المشكلة: Migration فشل

```bash
# إعادة تعيين قاعدة البيانات
railway run python manage.py migrate --fake-initial
```

### المشكلة: Static files

```bash
# جمع static files
railway run python manage.py collectstatic --noinput
```

### المشكلة: Database connection

تأكد من أن:
- قاعدة البيانات تعمل
- المتغيرات البيئية صحيحة
- قاعدة البيانات PostgreSQL قيد التشغيل

## 📝 الملاحظات

- Railway يوفر $5/month للخدمات المجانية
- Render يوفر خدمة مجانية مع قيود
- Heroku يتطلب بطاقة ائتمانية (خدمة مجانية محدودة)
