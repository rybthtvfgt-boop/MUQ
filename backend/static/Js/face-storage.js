// Face Storage Manager
// إدارة تخزين بيانات الوجه — الخادم (Django) هو مصدر الحقيقة الوحيد للتسجيل والتعرّف.
// localStorage هنا عرض مؤقت فقط؛ لا يُستخدم بديلاً عند فشل الخادم في عمليات التسجيل.

class FaceStorageManager {
    constructor() {
        this.storageType = FACE_CONFIG.STORAGE.TYPE;
        this.apiUrl = FACE_CONFIG.STORAGE.API_URL;
    }

    authHeaders() {
        const headers = { 'Content-Type': 'application/json' };
        const token = localStorage.getItem('accessToken');
        if (token) headers['Authorization'] = `Bearer ${token}`;
        return headers;
    }

    // حفظ بيانات الوجه — يتطلب حساب مشغّل مخوّل (مشرف/قسم التسجيل) مصادَقاً عليه من الخادم
    async saveFaceData(personType, personId, faceData) {
        if (this.storageType === 'mysql') {
            return await this.saveToMySQL(personType, personId, faceData);
        }
        return this.saveToLocal(personType, personId, faceData);
    }

    // حفظ في خادم Django — لا رجوع صامت للتخزين المحلي عند الفشل
    async saveToMySQL(personType, personId, faceData) {
        try {
            const response = await fetch(`${this.apiUrl}/api/face-profiles/`, {
                method: 'POST',
                headers: this.authHeaders(),
                body: JSON.stringify({
                    person: personId,
                    model_name: faceData.model || 'face-api.js',
                    model_version: '1',
                    samples: (faceData.samples || []).map(s => ({
                        embedding: s.embedding,
                        pose: s.pose,
                        quality_score: s.quality,
                        source: 'registration'
                    }))
                })
            });

            const result = await response.json().catch(() => ({}));

            if (response.ok) {
                return { success: true, id: result.id, samples_count: result.sample_count };
            }
            if (response.status === 401 || response.status === 403) {
                return { success: false, error: 'صلاحية غير كافية أو انتهت الجلسة — سجّل الدخول من حساب مخوّل.' };
            }
            const detail = result.error || result.detail ||
                (result.samples && JSON.stringify(result.samples)) ||
                (result.person && JSON.stringify(result.person)) || 'خطأ غير معروف';
            return { success: false, error: detail };
        } catch (error) {
            return { success: false, error: 'تعذّر الاتصال بالخادم — لم يُحفظ شيء.', networkError: true };
        }
    }

    // حفظ في localStorage (وضع التوافق المحلي فقط)
    saveToLocal(personType, personId, faceData) {
        try {
            const key = this.getLocalKey(personType, personId);
            localStorage.setItem(key, JSON.stringify(faceData));
            return { success: true, storage: 'local' };
        } catch (error) {
            console.error('❌ Error saving to localStorage:', error);
            return { success: false, error: error.message };
        }
    }

    // قراءة بيانات الوجه (وصف الملف بدون عينات بيومترية — القوالب لا تغادر الخادم)
    async getFaceData(personType, personId) {
        if (this.storageType === 'mysql') {
            return await this.getFromMySQL(personType, personId);
        }
        return this.getFromLocal(personType, personId);
    }

    async getFromMySQL(personType, personId) {
        try {
            const status = await this.profileStatus(personId);
            if (!status || !status.exists) return null;
            return {
                version: 2,
                model: status.model_name,
                sampleCount: status.sample_count,
                isVerified: status.is_verified,
                createdAt: status.created_at
            };
        } catch (error) {
            console.error('❌ Error loading profile from server:', error);
            return null;
        }
    }

    getFromLocal(personType, personId) {
        try {
            const data = localStorage.getItem(this.getLocalKey(personType, personId));
            return data ? JSON.parse(data) : null;
        } catch (error) {
            return null;
        }
    }

    // التعرف على الوجه — القرار للمطابقة على الخادم دائماً
    async recognizeFace(embedding) {
        if (this.storageType === 'mysql') {
            return await this.recognizeFromMySQL(embedding);
        }
        return this.recognizeFromLocal(embedding);
    }

    async recognizeFromMySQL(embedding) {
        try {
            const response = await fetch(`${this.apiUrl}/api/face-recognition/recognize`, {
                method: 'POST',
                headers: this.authHeaders(),
                body: JSON.stringify({ embedding: embedding })
            });
            const result = await response.json().catch(() => ({}));

            if (response.status === 401 || response.status === 403) {
                return { matched: false, denied: true, reason: 'غير مخوّل — تحقق من جلسة الدخول.' };
            }
            if (!response.ok && result.matched === undefined) {
                return { matched: false, reason: result.error || 'تعذّر تنفيذ المطابقة.' };
            }
            // تحويل صيغة الخادم إلى صيغة الصفحات: person.id/user_type بدل type/id
            if (result.matched && result.person) {
                result.person = {
                    type: result.person.user_type,
                    id: result.person.id,
                    name: result.person.name,
                    code: result.person.code
                };
            }
            return result;
        } catch (error) {
            console.error('❌ Error recognizing from server:', error);
            return { matched: false, networkError: true, reason: 'انقطاع الاتصال بالخادم' };
        }
    }

    // التعرف من localStorage — وضع التوافق المحلي فقط (غير موثوق للسجل الرسمي)
    recognizeFromLocal(embedding) {
        try {
            const faceDatabase = [];
            const groups = {
                student: 'muq_students', teacher: 'muq_teachers',
                administrative: 'muq_administrative_staff', security: 'muq_security_staff',
                service: 'muq_service_staff'
            };
            for (const [type, key] of Object.entries(groups)) {
                (JSON.parse(localStorage.getItem(key) || '[]')).forEach(person => {
                    if (person.faceData && person.faceData.version === 2) {
                        faceDatabase.push({ type, id: person.id, name: person.name, faceData: person.faceData });
                    }
                });
            }

            let bestMatch = null;
            let bestDistance = Infinity;
            for (const person of faceDatabase) {
                for (const sample of person.faceData.samples) {
                    const distance = faceEngine.euclideanDistance(embedding, sample.embedding);
                    if (distance < bestDistance) {
                        bestDistance = distance;
                        bestMatch = person;
                    }
                }
            }

            const threshold = FACE_CONFIG.RECOGNITION.THRESHOLD;
            if (bestMatch && bestDistance < threshold) {
                return { matched: true, person: bestMatch, distance: bestDistance,
                         confidence: Math.max(0, 1 - (bestDistance / threshold)), storage: 'local' };
            }
            return { matched: false, reason: 'No match found', distance: bestDistance === Infinity ? null : bestDistance };
        } catch (error) {
            return { matched: false, reason: error.message };
        }
    }

    getLocalKey(personType, personId) {
        return `${FACE_CONFIG.STORAGE.LOCAL_KEY_PREFIX}face_${personType}_${personId}`;
    }

    // التحقق 1:1 من هوية محددة — على الخادم، لا على المتصفح
    async verifyIdentity(personType, personId, embedding) {
        if (this.storageType === 'mysql') {
            try {
                const response = await fetch(`${this.apiUrl}/api/face-recognition/verify`, {
                    method: 'POST',
                    headers: this.authHeaders(),
                    body: JSON.stringify({ person: personId, embedding: embedding })
                });
                const result = await response.json().catch(() => ({}));
                if (!response.ok) {
                    return { verified: false, reason: result.error || result.detail || 'فشل التحقق.' };
                }
                return result;
            } catch (error) {
                return { verified: false, networkError: true, reason: 'انقطاع الاتصال بالخادم' };
            }
        }
        const faceData = this.getFromLocal(personType, personId);
        if (!faceData || faceData.version !== 2) {
            return { verified: false, reason: 'لا توجد بيانات وجه محلية لهذا الشخص' };
        }
        let bestDistance = Infinity;
        for (const sample of faceData.samples) {
            const distance = faceEngine.euclideanDistance(embedding, sample.embedding);
            if (distance < bestDistance) bestDistance = distance;
        }
        const threshold = FACE_CONFIG.RECOGNITION.THRESHOLD;
        return { verified: bestDistance < threshold, distance: bestDistance };
    }
}

// إنشاء نسخة واحدة من مدير التخزين
const faceStorage = new FaceStorageManager();
