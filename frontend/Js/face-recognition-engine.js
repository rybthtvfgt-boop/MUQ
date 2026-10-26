// Face Recognition Engine
// محرك مشترك للتعرف على الوجه باستخدام face-api.js
// This is not full liveness detection - it's a simple challenge-based approach

class FaceRecognitionEngine {
    constructor() {
        this.modelsLoaded = false;
        this.currentSamples = [];
        this.lastCaptureTime = 0;
        this.blinkDetected = false;
        this.blinkFrames = 0;
    }

    // تحميل نماذج face-api.js
    async loadModels() {
        if (this.modelsLoaded) return true;

        try {
            const modelsUrl = FACE_CONFIG.MODELS.MODELS_URL;

            // تحميل النماذج المطلوبة
            await faceapi.nets.ssdMobilenetv1.loadFromUri(modelsUrl);
            await faceapi.nets.faceLandmark68Net.loadFromUri(modelsUrl);
            await faceapi.nets.faceRecognitionNet.loadFromUri(modelsUrl);

            this.modelsLoaded = true;
            console.log('✅ Face-API models loaded successfully');
            return true;
        } catch (error) {
            console.error('❌ Error loading face-api models:', error);
            return false;
        }
    }

    // اكتشاف الوجه في الصورة
    async detectFace(imageElement) {
        if (!this.modelsLoaded) {
            await this.loadModels();
        }

        try {
            const detections = await faceapi.detectSingleFace(imageElement)
                .withFaceLandmarks()
                .withFaceDescriptor();

            return detections;
        } catch (error) {
            console.error('Error detecting face:', error);
            return null;
        }
    }

    // اكتشاف جميع الوجوه
    async detectAllFaces(imageElement) {
        if (!this.modelsLoaded) {
            await this.loadModels();
        }

        try {
            const detections = await faceapi.detectAllFaces(imageElement)
                .withFaceLandmarks()
                .withFaceDescriptors();

            return detections;
        } catch (error) {
            console.error('Error detecting all faces:', error);
            return [];
        }
    }

    // فحص جودة الصورة
    checkQuality(detection, imageElement) {
        if (!detection) {
            return {
                valid: false,
                reason: 'لم يتم اكتشاف وجه'
            };
        }

        const quality = {
            valid: true,
            reason: '',
            score: 0
        };

        // حجم الوجه
        const faceSize = detection.detection.box.width;
        if (faceSize < FACE_CONFIG.QUALITY.MIN_FACE_SIZE) {
            quality.valid = false;
            quality.reason = 'الوجه صغير جداً';
            return quality;
        }
        if (faceSize > FACE_CONFIG.QUALITY.MAX_FACE_SIZE) {
            quality.valid = false;
            quality.reason = 'الوجه قريب جداً';
            return quality;
        }

        // حساب درجة الجودة
        quality.score = this.calculateQualityScore(detection, imageElement);

        if (quality.score < FACE_CONFIG.REGISTRATION.MIN_QUALITY) {
            quality.valid = false;
            quality.reason = 'جودة الصورة منخفضة';
        }

        return quality;
    }

    // حساب درجة الجودة
    calculateQualityScore(detection, imageElement) {
        let score = 1.0;

        // تقليل النقاط للوجه الصغير
        const faceSize = detection.detection.box.width;
        if (faceSize < FACE_CONFIG.QUALITY.MIN_FACE_SIZE * 1.5) {
            score -= 0.2;
        }

        // تقليل النقاط للوجه غير المتمركز
        const imageWidth = imageElement.width || 640;
        const imageHeight = imageElement.height || 480;
        const faceCenter = detection.detection.box;
        const centerX = faceCenter.x + faceCenter.width / 2;
        const centerY = faceCenter.y + faceCenter.height / 2;

        const distanceFromCenter = Math.sqrt(
            Math.pow(centerX - imageWidth / 2, 2) +
            Math.pow(centerY - imageHeight / 2, 2)
        );

        const maxDistance = Math.sqrt(
            Math.pow(imageWidth / 2, 2) +
            Math.pow(imageHeight / 2, 2)
        );

        if (distanceFromCenter > maxDistance * 0.3) {
            score -= 0.2;
        }

        return Math.max(0, score);
    }

    // تحديد زاوية الرأس
    detectPose(detection) {
        if (!detection || !detection.landmarks) {
            return 'unknown';
        }

        const landmarks = detection.landmarks;
        const leftEye = landmarks.getLeftEye();
        const rightEye = landmarks.getRightEye();
        const nose = landmarks.getNose();

        // حساب زاوية الرأس الأفقية
        const eyeXDiff = rightEye[3].x - leftEye[0].x;
        const eyeYDiff = rightEye[3].y - leftEye[0].y;
        const yawAngle = Math.atan2(eyeYDiff, eyeXDiff) * (180 / Math.PI);

        // حساب زاوية الرأس العمودية
        const noseTip = nose[3];
        const faceCenter = detection.detection.box;
        const pitchAngle = Math.atan2(
            noseTip.y - (faceCenter.y + faceCenter.height / 2),
            faceCenter.height / 2
        ) * (180 / Math.PI);

        // تحديد الوضعية
        if (Math.abs(yawAngle) < 10 && Math.abs(pitchAngle) < 10) {
            return 'front';
        } else if (yawAngle > 10 && yawAngle < 25) {
            return 'right_15';
        } else if (yawAngle >= 25) {
            return 'right_30';
        } else if (yawAngle < -10 && yawAngle > -25) {
            return 'left_15';
        } else if (yawAngle <= -25) {
            return 'left_30';
        } else if (pitchAngle > 10) {
            return 'up';
        } else if (pitchAngle < -10) {
            return 'down';
        }

        return 'unknown';
    }

    // التحقق من التكرار
    isDuplicate(newEmbedding, existingSamples) {
        for (const sample of existingSamples) {
            const distance = this.euclideanDistance(newEmbedding, sample.embedding);
            if (distance < FACE_CONFIG.RECOGNITION.DUPLICATE_DISTANCE_THRESHOLD) {
                return true;
            }
        }
        return false;
    }

    // حساب Euclidean Distance
    euclideanDistance(embedding1, embedding2) {
        if (!embedding1 || !embedding2 || embedding1.length !== embedding2.length) {
            return Infinity;
        }

        let sum = 0;
        for (let i = 0; i < embedding1.length; i++) {
            sum += Math.pow(embedding1[i] - embedding2[i], 2);
        }

        return Math.sqrt(sum);
    }

    // التقاط عينة مع فحص الجودة
    async captureSample(imageElement, currentPose) {
        const now = Date.now();

        // فحص الفاصل الزمني
        if (now - this.lastCaptureTime < FACE_CONFIG.REGISTRATION.CAPTURE_INTERVAL) {
            return {
                success: false,
                reason: 'انتظر قليلاً...'
            };
        }

        // اكتشاف الوجه
        const detection = await this.detectFace(imageElement);
        if (!detection) {
            return {
                success: false,
                reason: 'لم يتم اكتشاف وجه'
            };
        }

        // فحص وجود أكثر من وجه
        const allDetections = await this.detectAllFaces(imageElement);
        if (allDetections.length > 1) {
            return {
                success: false,
                reason: 'يوجد أكثر من وجه أمام الكاميرا'
            };
        }

        // فحص الجودة
        const quality = this.checkQuality(detection, imageElement);
        if (!quality.valid) {
            return {
                success: false,
                reason: quality.reason
            };
        }

        // التحقق من الزاوية المطلوبة
        const detectedPose = this.detectPose(detection);
        
        // Reject unknown poses during registration
        if (detectedPose === 'unknown') {
            return {
                success: false,
                reason: 'لم يتم تحديد زاوية الرأس - انظر مباشرة للكاميرا'
            };
        }
        
        if (currentPose && detectedPose !== currentPose) {
            return {
                success: false,
                reason: `حرّك رأسك نحو ${this.getPoseInstruction(currentPose)}`
            };
        }

        // التحقق من التكرار
        const embedding = detection.descriptor;
        if (this.isDuplicate(embedding, this.currentSamples)) {
            return {
                success: false,
                reason: 'هذه الصورة مشابهة جداً لصورة سابقة'
            };
        }

        // حفظ العينة
        const sample = {
            embedding: Array.from(embedding), // تح Float32Array إلى Array
            pose: detectedPose,
            quality: quality.score,
            capturedAt: new Date().toISOString()
        };

        this.currentSamples.push(sample);
        this.lastCaptureTime = now;

        return {
            success: true,
            sample: sample,
            totalSamples: this.currentSamples.length
        };
    }

    // الحصول على تعليمات الوضعية
    getPoseInstruction(pose) {
        const instructions = {
            'front': 'انظر مباشرة إلى الكاميرا',
            'right_15': 'حرّك رأسك قليلاً إلى اليمين',
            'right_30': 'حرّك رأسك أكثر إلى اليمين',
            'left_15': 'حرّك رأسك قليلاً إلى اليسار',
            'left_30': 'حرّك رأسك أكثر إلى اليسار',
            'up': 'انظر إلى الأعلى',
            'down': 'انظر إلى الأسفل'
        };
        return instructions[pose] || 'انظر مباشرة إلى الكاميرا';
    }

    // التحقق من الرمش (للـ Liveness البسيط)
    async checkBlink(imageElement) {
        if (!FACE_CONFIG.LIVENESS.BLINK_CHALLENGE) {
            return true;
        }

        const detection = await this.detectFace(imageElement);
        if (!detection || !detection.landmarks) {
            return false;
        }

        const landmarks = detection.landmarks;
        const leftEye = landmarks.getLeftEye();
        const rightEye = landmarks.getRightEye();

        // حساب ارتفاع العين
        const leftEyeHeight = this.calculateEyeHeight(leftEye);
        const rightEyeHeight = this.calculateEyeHeight(rightEye);

        // إذا كانت العين مفتوحة
        if (leftEyeHeight > 10 && rightEyeHeight > 10) {
            this.blinkFrames++;
        } else {
            // إذا كانت العين مغلقة لعدة إطارات
            if (this.blinkFrames > 5) {
                this.blinkDetected = true;
            }
            this.blinkFrames = 0;
        }

        return this.blinkDetected;
    }

    // حساب ارتفاع العين
    calculateEyeHeight(eyePoints) {
        const top = eyePoints[1].y;
        const bottom = eyePoints[5].y;
        return Math.abs(bottom - top);
    }

    // إعادة تعيين حالة الرمش
    resetBlinkDetection() {
        this.blinkDetected = false;
        this.blinkFrames = 0;
    }

    // حفظ بيانات الوجه
    saveFaceData() {
        if (this.currentSamples.length === 0) {
            return null;
        }

        return {
            version: 2,
            model: 'face-api.js',
            samples: this.currentSamples,
            createdAt: new Date().toISOString()
        };
    }

    // تحميل بيانات الوجه
    loadFaceData(faceData) {
        if (!faceData) {
            return null;
        }

        // التحقق من الإصدار
        if (faceData.version === 2) {
            this.currentSamples = faceData.samples || [];
            return faceData;
        }

        // إذا كان إصدار قديم، تحويله
        if (faceData.version === 1 || faceData.images) {
            // نحتاج لتحويل الصور القديمة إلى embeddings
            // هذا يتطلب معالجة خاصة
            console.log('Legacy face data detected - migration needed');
            return {
                version: 1,
                legacyImages: faceData.images || [],
                samples: [],
                createdAt: faceData.createdAt
            };
        }

        return null;
    }

    // البحث عن تطابق
    async findMatch(imageElement, faceDatabase) {
        if (!this.modelsLoaded) {
            await this.loadModels();
        }

        const detection = await this.detectFace(imageElement);
        if (!detection) {
            return {
                matched: false,
                reason: 'لم يتم اكتشاف وجه'
            };
        }

        const embedding = detection.descriptor;
        let bestMatch = null;
        let bestDistance = Infinity;
        let matchedSample = null;

        for (const person of faceDatabase) {
            if (!person.faceData || person.faceData.version !== 2) {
                continue;
            }

            for (const sample of person.faceData.samples) {
                const distance = this.euclideanDistance(embedding, sample.embedding);

                if (distance < bestDistance) {
                    bestDistance = distance;
                    bestMatch = person;
                    matchedSample = sample;
                }
            }
        }

        const threshold = FACE_CONFIG.RECOGNITION.THRESHOLD;

        if (bestDistance < threshold) {
            return {
                matched: true,
                person: bestMatch,
                distance: bestDistance,
                matchedSample: matchedSample,
                // قيمة تقديرية ليست احتمالاً إحصائياً
                confidence: Math.max(0, 1 - (bestDistance / threshold))
            };
        }

        return {
            matched: false,
            reason: 'لم يتم العثور على تطابق',
            distance: bestDistance
        };
    }

    // التحقق من هوية محددة
    async verifyIdentity(imageElement, targetPerson) {
        if (!targetPerson || !targetPerson.faceData) {
            return {
                verified: false,
                reason: 'لا توجد بيانات وجه لهذا الشخص'
            };
        }

        const detection = await this.detectFace(imageElement);
        if (!detection) {
            return {
                verified: false,
                reason: 'لم يتم اكتشاف وجه'
            };
        }

        const embedding = detection.descriptor;
        let bestDistance = Infinity;
        let matchedSample = null;

        if (targetPerson.faceData.version === 2) {
            for (const sample of targetPerson.faceData.samples) {
                const distance = this.euclideanDistance(embedding, sample.embedding);
                if (distance < bestDistance) {
                    bestDistance = distance;
                    matchedSample = sample;
                }
            }
        }

        const threshold = FACE_CONFIG.RECOGNITION.THRESHOLD;

        return {
            verified: bestDistance < threshold,
            distance: bestDistance,
            matchedSample: matchedSample,
            confidence: bestDistance < threshold ? Math.max(0, 1 - (bestDistance / threshold)) : 0
        };
    }

    // إعادة تعيين المحرك
    reset() {
        this.currentSamples = [];
        this.lastCaptureTime = 0;
        this.resetBlinkDetection();
    }

    // الحصول على إحصائيات التسجيل
    getRegistrationStats() {
        const stats = {
            total: this.currentSamples.length,
            byPose: {}
        };

        for (const sample of this.currentSamples) {
            if (!stats.byPose[sample.pose]) {
                stats.byPose[sample.pose] = 0;
            }
            stats.byPose[sample.pose]++;
        }

        return stats;
    }
}

// إنشاء نسخة واحدة من المحرك
const faceEngine = new FaceRecognitionEngine();
