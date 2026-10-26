// Face Recognition Configuration
// إعدادات مركزية لنظام التعرف على الوجه

const FACE_CONFIG = {
    // إعدادات التخزين
    STORAGE: {
        // نوع التخزين: 'mysql' = خادم Django (المصدر الوحيد للحقيقة)
        // 'local' متوافق قديم فقط ولا يُعتمد عليه للحضور الرسمي
        TYPE: 'mysql',
        // عنوان خادم Django: محلياً على المنفذ 8000 (نفس عقد api-client.js)،
        // وفي النشر نفس نطاق الموقع (whitenoise/railway).
        // IMPORTANT: If frontend and backend are on different domains in production,
        // configure BACKEND_URL environment variable or change this logic.
        API_URL: (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
            ? 'http://localhost:8000'
            : (window.BACKEND_URL || window.location.origin),
        // إعدادات localStorage (تخزين مؤقت للعرض فقط — ليس سجل حضور)
        LOCAL_KEY_PREFIX: 'muq_'
    },

    // إعدادات التسجيل
    REGISTRATION: {
        TARGET_SAMPLES: 3, // العدد المستهدف من العينات
        MIN_QUALITY: 0.7, // الحد الأدنى لجودة العينة (0-1)
        CAPTURE_INTERVAL: 500, // الحد الأدنى بين التقاط الصور (ms)
        POSES: {
            front: 1,
            right_15: 1,
            left_15: 1,
            // Additional poses with explicit counts (not used in current registration flow)
            right_30: 0,
            left_30: 0,
            up: 0,
            down: 0
        }
    },

    // إعدادات التعرف
    RECOGNITION: {
        // Threshold للتعرف (Euclidean Distance)
        // القيم الأقل تعني تطابق أفضل
        THRESHOLD: 0.6, // قيمة تجريبية، تحتاج للاختبار
        // منع العينات المكررة
        DUPLICATE_DISTANCE_THRESHOLD: 0.3 // قيمة تجريبية
    },

    // إعدادات النماذج
    MODELS: {
        // نماذج face-api.js محلية (frontend/vendor/face-api/models) —
        // لا تحميل خارجي: القوالب البيومترية لا تمر عبر خدمات第三方 والنظام يعمل دون إنترنت.
        MODELS_URL: '../vendor/face-api/models',
        // النماذج المطلوبة
        SSD_MOBILENET_V1: 'ssd_mobilenetv1_model-weights_manifest.json',
        FACE_LANDMARK_68: 'face_landmark_68_model-weights_manifest.json',
        FACE_RECOGNITION: 'face_recognition_model-weights_manifest.json'
    },

    // إعدادات Liveness (تحدي بسيط فقط)
    LIVENESS: {
        ENABLED: true,
        BLINK_CHALLENGE: true,
        // ملاحظة: هذا ليس حماية حيوية كاملة
        // This is not full liveness detection
        MESSAGE: "تحدي بسيط للتحقق من الحيوية - ليس حماية ضد جميع أنواع spoofing"
    },

    // إعدادات الجودة
    QUALITY: {
        MIN_FACE_SIZE: 100, // الحد الأدنى لحجم الوجه (بكسل)
        MAX_FACE_SIZE: 400, // الحد الأقصى لحجم الوجه (بكسل)
        MIN_BRIGHTNESS: 50, // الحد الأدنى للإضاءة (0-255)
        MAX_BRIGHTNESS: 200, // الحد الأقصى للإضاءة (0-255)
        BLUR_THRESHOLD: 100 // حد الضبابية
    },

    // إعدادات الإطار
    FRAME: {
        WIDTH: 640,
        HEIGHT: 480,
        FACE_BOX_PADDING: 20
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FACE_CONFIG;
}
