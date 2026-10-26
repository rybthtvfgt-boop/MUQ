# MUQ Project - جاهزية النشر على Railway

## التاريخ: 2026-10-23
## الحالة: ✅ جاهز للنشر

---

## الملفات المضافة/المحدثة للنشر:

### 1. إعدادات Railway:
- ✅ `railway.json` - إعدادات البناء الأساسية
- ✅ `railway.yaml` - إعدادات الخدمات وقاعدة البيانات
- ✅ `backend/Procfile` - أمر بدء التشغيل (موجود مسبقاً)

### 2. سكريبتات النشر:
- ✅ `backend/create_admin_production.py` - إنشاء حساب admin تلقائياً
- ✅ `deploy-railway.bat` - سكريبت لإعداد Git للنشر

### 3. ملفات إعداد البيئة:
- ✅ `backend/.env.example` - مثال محدث مع متغيرات الإنتاج
- ✅ `backend/requirements.txt` - محدث مع python-dotenv

### 4. دليل النشر:
- ✅ `RAILWAY_DEPLOYMENT_GUIDE.md` - دليل شامل خطوة بخطوة

### 5. Git:
- ✅ `.gitignore` - محدث لاستبعاد الملفات المؤقتة والتقارير

---

## متغيرات البيئة المطلوبة في Railway:

### الإلزامية:
```
DEBUG = False
SECRET_KEY = (قيمة مشفرة قوية - 32+ حرف)
ALLOWED_HOSTS = .railway.app,.vercel.app
DB_ENGINE = postgresql
DJANGO_SETTINGS_MODULE = muq_system.settings
```

### قاعدة البيانات (تلقائي من Railway):
```
DATABASE_URL = (يتم توليده تلقائياً)
```

### CORS:
```
CORS_ALLOWED_ORIGINS = https://*.railway.app,https://*.vercel.app
```

### اختيارية ولكن موصى بها:
```
ADMIN_PASSWORD = (كلمة مرور قوية للـ admin)
ADMIN_EMAIL = admin@muq.com
LANGUAGE_CODE = ar
TIME_ZONE = Asia/Baghdad
JWT_ACCESS_TOKEN_HOURS = 2
JWT_REFRESH_TOKEN_DAYS = 7
API_PAGE_SIZE = 100
```

---

## خطوات النشر السريعة:

### 1. إعداد Git المحلي:
```bash
cd F:\MUQ
deploy-railway.bat
```

### 2. دفع إلى GitHub:
```bash
git remote add origin https://github.com/YOUR_USERNAME/muq-system.git
git branch -M main
git push -u origin main
```

### 3. إنشاء مشروع Railway:
1. اذهب إلى https://railway.app/new
2. انقر "Deploy from GitHub repo"
3. اختر مستودع muq-system
4. Railway سيكتشف railway.yaml تلقائياً

### 4. إضافة متغيرات البيئة:
1. افتح خدمة muq-backend في Railway
2. انقر "Variables"
3. أضف المتغيرات المذكورة أعلاه

### 5. تشغيل الـ Migrations:
1. في Railway، أضف أمر "migrate"
2. الأمر: `python manage.py migrate --noinput`
3. شغّل الأمر

### 6. إنشاء حساب Admin:
1. أضف أمر "createadmin"
2. الأمر: `python manage.py shell < create_admin_production.py`
3. شغّل الأمر

### 7. نشر Frontend:
- الخيار الموصى به: Vercel (للملفات الثابتة)
- راجع RAILWAY_DEPLOYMENT_GUIDE.md للتفاصيل

---

## التحقق من النشر:

### اختبار صحة الـ API:
```bash
curl https://your-backend.railway.app/api/health/
```

### اختبار تسجيل الدخول:
```bash
curl -X POST https://your-backend.railway.app/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-admin-password"}'
```

---

## التكلفة التقديرية:

### Railway Free Tier:
- **الخدمات:** $5/month (500 ساعة)
- **قاعدة البيانات:** مجانية (PostgreSQL)
- **التخزين:** 1GB مجاني
- **مثالي للاختبار والتطوير**

### Railway Pro Plan ($20/month):
- **الخدمات:** $20/month (مضاعف الموارد)
- **قاعدة البيانات:** حتى 5GB
- **أداء أفضل وموثوقية أعلى**
- **موصى به للإنتاج**

---

## ملاحظات مهمة:

### 1. قاعدة البيانات:
- Railway سيوفر PostgreSQL تلقائياً
- Django سيقرأ DATABASE_URL تلقائياً
- لا حاجة لإعدادات يدوية

### 2. الملفات الثابتة:
- Whitenoise يخدم الملفات الثابتة
- Frontend يمكن نشره على Vercel
- أو دمجه داخل Django static

### 3. الأمان:
- SECRET_KEY يجب أن يكون قوياً
- ADMIN_PASSWORD يجب أن يكون قوياً
- SSL/HTTPS مفعل تلقائياً في Railway
- HSTS مفعل في الإنتاج

### 4. المراقبة:
- Railway يوفر Logs و Metrics مجاناً
- راقب الأخطاء والأداء بانتظام
- يمكن إعداد تنبيهات عبر Discord/Slack

---

## استكشاف الأخطاء الشائعة:

### ALLOWED_HOSTS Error:
**الحل:** تأكد من إضافة `.railway.app` إلى ALLOWED_HOSTS

### CORS Error:
**الحل:** تأكد من إضافة رابط Frontend إلى CORS_ALLOWED_ORIGINS

### Database Connection Error:
**الحل:** تأكد من أن قاعدة البيانات تعمل في Railway

### Migration Error:
**الحل:** شغّل `python manage.py migrate --noinput` يدوياً

---

## الموارد:

### Railway Docs:
- https://docs.railway.app

### Django Deployment:
- https://docs.djangoproject.com/en/5.1/howto/deployment/

### PostgreSQL on Railway:
- https://docs.railway.app/databases/postgresql

---

## الدعم:

للحصول على دعم أو مساعدة:
1. راجع `RAILWAY_DEPLOYMENT_GUIDE.md` للتفاصيل الكاملة
2. تحقق من Logs في Railway
3. راجع Django Debug Panel (عند DEBUG=True)

---

## الخلاصة:

المشروع جاهز بالكامل للنشر على Railway! 🚀

- ✅ جميع ملفات الإعداد موجودة
- ✅ متغيرات البيئة محددة
- ✅ سكريبتات النشر جاهزة
- ✅ دليل شامل متوفر
- ✅ Django مهيأ للإنتاج

ابدأ بتشغيل `deploy-railway.bat` ثم اتبع الخطوات!
