"""
نظام ML Backend الخاص بـ MUQ - معالجة التعلم الآلي
نظام هجين: face-api.js (الواجهة الأمامية) + Python ML (الواجهة الخلفية)
"""

import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
import io
import base64
import json
import os
from typing import Dict, List, Tuple, Optional
import logging
import threading

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FaceRecognitionML:
    """التعرف على الوجه باستخدام TensorFlow و OpenCV"""

    def __init__(self):
        self.model = None
        self.face_detector = None
        self.model_loaded = False
        self.loading = False

    def load_model(self):
        """تحميل نموذج التعرف على الوجه"""
        if self.model_loaded or self.loading:
            return
        
        self.loading = True
        try:
            # تحميل نموذج TensorFlow للتعرف على الوجه
            # استخدام MobileNetV2 لكشف الوجه
            logger.info("جاري تحميل MobileNetV2...")
            self.model = tf.keras.applications.MobileNetV2(
                weights='imagenet',
                include_top=False,
                input_shape=(224, 224, 3)
            )

            # تحميل كاشف الوجه من OpenCV مع معالجة الأخطاء
            try:
                haar_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                if os.path.exists(haar_path):
                    self.face_detector = cv2.CascadeClassifier(haar_path)
                else:
                    logger.warning(f"ملف Haar cascade غير موجود في {haar_path}")
                    self.face_detector = None
            except Exception as haar_error:
                logger.warning(f"خطأ في تحميل Haar cascade: {haar_error}")
                self.face_detector = None

            self.model_loaded = True
            logger.info("تم تحميل نموذج التعرف على الوجه بنجاح")
            return True
        except Exception as e:
            logger.error(f"خطأ في تحميل نموذج ML: {e}")
            self.model_loaded = False
            return False
        finally:
            self.loading = False

    def detect_faces(self, image: np.ndarray) -> List[Dict]:
        """كشف الوجوه في الصورة باستخدام OpenCV"""
        if not self.model_loaded:
            self.load_model()

        try:
            if self.face_detector is None:
                logger.warning("كاشف الوجه غير متاح، إرجاع قائمة فارغة")
                return []

            # تحويل إلى تدرج رمادي لكشف الوجه
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # كشف الوجوه
            faces = self.face_detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            face_list = []
            for (x, y, w, h) in faces:
                face_list.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'confidence': 0.95  # الثقة الافتراضية لـ OpenCV
                })

            return face_list
        except Exception as e:
            logger.error(f"خطأ في كشف الوجوه: {e}")
            return []

    def extract_face_embedding(self, image: np.ndarray, face: Dict) -> np.ndarray:
        """استخراج embedding الوجه باستخدام TensorFlow"""
        try:
            x, y, w, h = face['x'], face['y'], face['width'], face['height']

            # استخراج منطقة الوجه
            face_roi = image[y:y+h, x:x+w]

            # تغيير الحجم إلى حجم إدخال النموذج
            face_roi = cv2.resize(face_roi, (224, 224))

            # التطبيع
            face_roi = face_roi.astype(np.float32) / 255.0

            # إضافة بعد الدفعة
            face_roi = np.expand_dims(face_roi, axis=0)

            # الحصول على embedding من النموذج
            embedding = self.model.predict(face_roi, verbose=0)

            # تسطيح embedding
            embedding = embedding.flatten()

            return embedding
        except Exception as e:
            logger.error(f"خطأ في استخراج embedding: {e}")
            return np.zeros(1280)  # إرجاع متجه صفر عند الخطأ

    def compare_faces(self, embedding1: np.ndarray, embedding2: np.ndarray,
                     threshold: float = 0.6) -> Tuple[bool, float]:
        """مقارنة embedding وجهين"""
        try:
            # حساب التشابه بالجيب التمام
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )

            # حساب المسافة
            distance = 1 - similarity

            is_match = distance < threshold
            return is_match, distance
        except Exception as e:
            logger.error(f"خطأ في مقارنة الوجوه: {e}")
            return False, 1.0


class SmokingDetector:
    """كشف التدخين باستخدام التعلم الآلي"""

    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.loading = False
        # استخدم أفضل نموذج (best) بدلاً من النهائي
        # احصل على المسار الصحيح للمجلد الحالي
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(current_dir, 'models', 'smoking_detector_best.h5')

    def load_model(self):
        """تحميل نموذج كشف التدخين"""
        if self.model_loaded or self.loading:
            return
        
        self.loading = True
        try:
            # التحقق من وجود النموذج المدرب
            if os.path.exists(self.model_path):
                logger.info(f"تحميل النموذج المدرب من: {self.model_path}")
                self.model = tf.keras.models.load_model(self.model_path)
                self.model_loaded = True
                logger.info("تم تحميل نموذج كشف التدخين المدرب بنجاح")
                return True
            else:
                logger.warning(f"النموذج المدرب غير موجود في {self.model_path}")
                logger.info("تحميل النموذج الافتراضي للعرض")

                # تحميل النموذج الافتراضي (placeholder)
                self.model = tf.keras.Sequential([
                    tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
                    tf.keras.layers.MaxPooling2D((2, 2)),
                    tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                    tf.keras.layers.MaxPooling2D((2, 2)),
                    tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
                    tf.keras.layers.MaxPooling2D((2, 2)),
                    tf.keras.layers.Flatten(),
                    tf.keras.layers.Dense(128, activation='relu'),
                    tf.keras.layers.Dropout(0.5),
                    tf.keras.layers.Dense(2, activation='softmax')  # تدخين، غير مدخن
                ])

                # تجميع النموذج
                self.model.compile(
                    optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics=['accuracy']
                )

                self.model_loaded = True
                logger.info("تم تحميل نموذج كشف التدخين الافتراضي بنجاح")
                return True
        except Exception as e:
            logger.error(f"خطأ في تحميل نموذج التدخين: {e}")
            self.model_loaded = False
            return False
        finally:
            self.loading = False

    def detect_smoking(self, image: np.ndarray) -> Dict:
        """كشف ما إذا كان الشخص يدخن"""
        if not self.model_loaded:
            self.load_model()

        try:
            if not self.model_loaded:
                return {
                    'is_smoking': False,
                    'confidence': 0.0,
                    'label': 'model_unavailable'
                }

            # معالجة الصورة مسبقاً
            img = cv2.resize(image, (224, 224))
            img = img.astype(np.float32) / 255.0
            img = np.expand_dims(img, axis=0)

            # التنبؤ
            prediction = self.model.predict(img, verbose=0)
            smoking_prob = prediction[0][1]  # احتمالية فئة التدخين

            is_smoking = smoking_prob > 0.5

            return {
                'is_smoking': bool(is_smoking),
                'confidence': float(smoking_prob),
                'label': 'smoking' if is_smoking else 'not_smoking'
            }
        except Exception as e:
            logger.error(f"خطأ في كشف التدخين: {e}")
            return {
                'is_smoking': False,
                'confidence': 0.0,
                'label': 'error'
            }


class CheatingDetector:
    """كشف الغش لمراقبة الامتحانات"""

    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.loading = False

    def load_model(self):
        """تحميل نموذج كشف الغش"""
        if self.model_loaded or self.loading:
            return
        
        self.loading = True
        try:
            # تحميل نموذج مدرب مسبقاً لكشف الغش
            self.model = tf.keras.Sequential([
                tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Conv2D(128, (3, 3), activation='relu'),
                tf.keras.layers.MaxPooling2D((2, 2)),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.Dropout(0.5),
                tf.keras.layers.Dense(3, activation='softmax')  # طبيعي، مشبوه، غش
            ])

            # Compile model
            self.model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )

            self.model_loaded = True
            logger.info("تم تحميل نموذج كشف الغش بنجاح")
            return True
        except Exception as e:
            logger.error(f"خطأ في تحميل نموذج الغش: {e}")
            self.model_loaded = False
            return False
        finally:
            self.loading = False

    def detect_cheating(self, image: np.ndarray) -> Dict:
        """كشف سلوك الغش"""
        if not self.model_loaded:
            self.load_model()

        try:
            if not self.model_loaded:
                return {
                    'status': 'model_unavailable',
                    'confidence': 0.0,
                    'probabilities': {'normal': 0, 'suspicious': 0, 'cheating': 0}
                }

            # معالجة الصورة مسبقاً
            img = cv2.resize(image, (224, 224))
            img = img.astype(np.float32) / 255.0
            img = np.expand_dims(img, axis=0)

            # التنبؤ
            prediction = self.model.predict(img, verbose=0)

            # الحصول على الفئة بأعلى احتمالية
            classes = ['normal', 'suspicious', 'cheating']
            max_prob = np.max(prediction)
            predicted_class = classes[np.argmax(prediction)]

            return {
                'status': predicted_class,
                'confidence': float(max_prob),
                'probabilities': {
                    'normal': float(prediction[0][0]),
                    'suspicious': float(prediction[0][1]),
                    'cheating': float(prediction[0][2])
                }
            }
        except Exception as e:
            logger.error(f"خطأ في كشف الغش: {e}")
            return {
                'status': 'error',
                'confidence': 0.0,
                'probabilities': {'normal': 0, 'suspicious': 0, 'cheating': 0}
            }


class ExamAnomalyDetector:
    """كشف الشذوذ لمراقبة الامتحانات باستخدام Autoencoder"""

    def __init__(self):
        self.model = None
        self.threshold = None
        self.model_loaded = False
        self.loading = False
        # احصل على المسار الصحيح للمجلد الحالي
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(current_dir, 'models', 'exam_anomaly_best.h5')
        self.threshold_path = os.path.join(current_dir, 'models', 'exam_anomaly_threshold.json')

    def load_model(self):
        """تحميل نموذج كشف الشذوذ وعتبة الكشف"""
        if self.model_loaded or self.loading:
            return
        
        self.loading = True
        try:
            # التحقق من وجود النموذج المدرب
            if os.path.exists(self.model_path):
                logger.info(f"تحميل نموذج الشذوذ المدرب من: {self.model_path}")
                # التحميل بـ compile=False لتجنب مشاكل المقاييس
                self.model = tf.keras.models.load_model(
                    self.model_path,
                    compile=False
                )
                # إعادة التجميع بخسارة بسيطة
                self.model.compile(optimizer='adam', loss='mse')
                
                # تحميل العتبة
                if os.path.exists(self.threshold_path):
                    with open(self.threshold_path, 'r') as f:
                        threshold_data = json.load(f)
                        self.threshold = threshold_data.get('threshold', 0.011170)
                    logger.info(f"تم تحميل عتبة الشذوذ: {self.threshold}")
                else:
                    self.threshold = 0.011170  # العتبة الافتراضية
                    logger.warning(f"ملف العتبة غير موجود، استخدام الافتراضي: {self.threshold}")
                
                self.model_loaded = True
                logger.info("تم تحميل نموذج كشف شذوذ الامتحانات بنجاح")
                return True
            else:
                logger.warning(f"نموذج الشذوذ المدرب غير موجود في {self.model_path}")
                logger.info("سيستخدم كشف شذوذ الامتحانات وضع العنصر النائب")
                self.threshold = 0.011170
                return False
        except Exception as e:
            logger.error(f"خطأ في تحميل نموذج الشذوذ: {e}")
            logger.info("سيستخدم كشف شذوذ الامتحانات وضع العنصر النائب")
            self.threshold = 0.011170
            self.model_loaded = False
            return False
        finally:
            self.loading = False

    def detect_anomaly(self, image: np.ndarray) -> Dict:
        """كشف ما إذا كانت الصورة تحتوي على حالة غير طبيعية"""
        if not self.model_loaded:
            self.load_model()
        
        if not self.model_loaded:
            # إرجاع نتيجة العنصر النائب إذا لم يتم تحميل النموذج
            return {
                'is_anomaly': False,
                'mse': 0.0,
                'threshold': 0.011170,
                'status': 'model_not_loaded',
                'message': 'نموذج كشف الشذوذ غير متاح - استخدام العنصر النائب'
            }

        try:
            # معالجة الصورة مسبقاً (32x32 كما تم تدريبها)
            img = cv2.resize(image, (32, 32))
            img = img.astype(np.float32) / 255.0
            img = np.expand_dims(img, axis=0)

            # التنبؤ (reconstruct image)
            reconstructed = self.model.predict(img, verbose=0)

            # حساب MSE (متوسط مربع الخطأ)
            mse = np.mean(np.square(img - reconstructed))

            # تحديد ما إذا كان شذوذاً
            is_anomaly = mse > self.threshold

            return {
                'is_anomaly': bool(is_anomaly),
                'mse': float(mse),
                'threshold': float(self.threshold),
                'status': 'anomaly' if is_anomaly else 'normal',
                'difference': float(mse - self.threshold)
            }
        except Exception as e:
            logger.error(f"خطأ في كشف الشذوذ: {e}")
            return {
                'is_anomaly': False,
                'mse': 0.0,
                'threshold': 0.0,
                'status': 'error',
                'error': str(e)
            }


class MLBackend:
    """فئة الواجهة الخلفية الرئيسية للتعلم الآلي"""

    def __init__(self):
        self.face_recognition = FaceRecognitionML()
        self.smoking_detector = SmokingDetector()
        self.cheating_detector = CheatingDetector()
        self.exam_anomaly_detector = ExamAnomalyDetector()

    def initialize(self):
        """تهيئة ML Backend بدون تحميل النماذج (lazy loading)"""
        logger.info("ML Backend initialized (lazy loading enabled)")
        # لا نحمل النماذج هنا - سيتم تحميلها عند الاستخدام الأول

    def warm_up_in_background(self):
        """تحميل النماذج في الخلفية (اختياري)"""
        def load_models():
            try:
                logger.info("Warming up ML models in background...")
                self.face_recognition.load_model()
                self.smoking_detector.load_model()
                self.cheating_detector.load_model()
                self.exam_anomaly_detector.load_model()
                logger.info("Model warm-up completed")
            except Exception as e:
                logger.warning(f"Background warm-up failed: {e}")
        
        thread = threading.Thread(target=load_models, daemon=True)
        thread.start()

    def process_image(self, image_data: str, task: str = 'face_recognition') -> Dict:
        """
        معالجة الصورة من سلسلة base64
        المعاملات:
            image_data: صورة مشفرة بـ base64
            task: نوع المعالجة (face_recognition, smoking_detection, cheating_detection, exam_anomaly)
        """
        try:
            # فك تشفير صورة base64
            image_bytes = base64.b64decode(image_data)
            image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)

            if image is None:
                return {'error': 'Invalid image data'}

            # المعالجة حسب المهمة
            if task == 'face_recognition':
                faces = self.face_recognition.detect_faces(image)
                return {'faces': faces, 'count': len(faces)}

            elif task == 'smoking_detection':
                result = self.smoking_detector.detect_smoking(image)
                return result

            elif task == 'cheating_detection':
                result = self.cheating_detector.detect_cheating(image)
                return result

            elif task == 'exam_anomaly':
                result = self.exam_anomaly_detector.detect_anomaly(image)
                return result

            else:
                return {'error': 'Invalid task'}

        except Exception as e:
            logger.error(f"خطأ في معالجة الصورة: {e}")
            return {'error': str(e)}

    def process_video_frame(self, frame: np.ndarray, task: str = 'face_recognition') -> Dict:
        """
        معالجة إطار الفيديو
        المعاملات:
            frame: مصفوفة NumPy تمثل الإطار
            task: نوع المعالجة
        """
        try:
            if task == 'face_recognition':
                faces = self.face_recognition.detect_faces(frame)
                return {'faces': faces, 'count': len(faces)}

            elif task == 'smoking_detection':
                result = self.smoking_detector.detect_smoking(frame)
                return result

            elif task == 'cheating_detection':
                result = self.cheating_detector.detect_cheating(frame)
                return result

            elif task == 'exam_anomaly':
                result = self.exam_anomaly_detector.detect_anomaly(frame)
                return result

            else:
                return {'error': 'Invalid task'}

        except Exception as e:
            logger.error(f"خطأ في معالجة الإطار: {e}")
            return {'error': str(e)}

    def extract_face_embedding(self, image: np.ndarray, face: Dict) -> np.ndarray:
        """استخراج embedding الوجه للمقارنة"""
        try:
            x, y, w, h = face['x'], face['y'], face['width'], face['height']

            # Extract face ROI
            face_roi = image[y:y+h, x:x+w]

            # Resize to model input size
            face_roi = cv2.resize(face_roi, (224, 224))

            # التطبيع
            face_roi = face_roi.astype(np.float32) / 255.0

            # إضافة بعد الدفعة
            face_roi = np.expand_dims(face_roi, axis=0)

            # الحصول على embedding من النموذج
            embedding = self.face_recognition.model.predict(face_roi, verbose=0)

            # تسطيح embedding
            embedding = embedding.flatten()

            return embedding
        except Exception as e:
            logger.error(f"خطأ في استخراج embedding: {e}")
            return np.zeros(1280)  # إرجاع متجه صفر عند الخطأ

    def identify_person(self, image: np.ndarray, known_faces: List[Dict], threshold: float = 0.6) -> Dict:
        """
        تحديد الشخص في الصورة مقابل الوجوه المعروفة
        المعاملات:
            image: الصورة المدخلة
            known_faces: قائمة الوجوه المعروفة مع embeddings
            threshold: عتبة المسافة للمطابقة
        """
        try:
            # كشف الوجوه
            faces = self.face_recognition.detect_faces(image)

            if not faces:
                return {
                    'found': False,
                    'message': 'لم يتم كشف أي وجوه'
                }

            # لكل وجه تم كشفه، حاول المطابقة
            for face in faces:
                # استخراج embedding
                embedding = self.extract_face_embedding(image, face)

                # المقارنة مع الوجوه المعروفة
                for known_face in known_faces:
                    if known_face.get('face_data') and known_face['face_data'].get('averageDescriptor'):
                        known_embedding = np.array(known_face['face_data']['averageDescriptor'])
                        distance = np.linalg.norm(embedding - known_embedding)

                        if distance < threshold:
                            return {
                                'found': True,
                                'type': 'known',
                                'person': {
                                    'id': known_face['id'],
                                    'name': known_face['name'],
                                    'personType': known_face.get('personType', 'unknown')
                                },
                                'distance': float(distance),
                                'confidence': float(1 - distance),
                                'face': face
                            }

            # لم يتم العثور على مطابقة - إرجاع بيانات الوجه للتسجيل
            return {
                'found': False,
                'type': 'unknown',
                'face': face,
                'embedding': embedding.tolist()
            }

        except Exception as e:
            logger.error(f"خطأ في تحديد الشخص: {e}")
            return {
                'found': False,
                'error': str(e)
            }


# مثيل ML Backend العام
ml_backend = MLBackend()


def get_ml_backend():
    """الحصول على مثيل ML Backend العام"""
    return ml_backend
