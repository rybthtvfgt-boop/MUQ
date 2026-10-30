// Face Registration System (New - Automatic Capture)
// تسجيل تلقائي لعدد كبير من العينات من زوايا مختلفة

let videoStream = null;
let targetPerson = null;
let isRegistering = false;
let registrationInterval = null;
let currentPoseIndex = 0;
let poses = [];
let acceptedCount = 0;
let rejectedCount = 0;
let blinkChallengePassed = false;

// Initialize
document.addEventListener('DOMContentLoaded', async function() {
    // Initialize poses from config
    poses = Object.keys(FACE_CONFIG.REGISTRATION.POSES).filter(pose => FACE_CONFIG.REGISTRATION.POSES[pose] > 0);
    
    // Check URL parameters first
    const urlParams = new URLSearchParams(window.location.search);
    const type = urlParams.get('type');
    const id = urlParams.get('id');

    if (type && id) {
        targetPerson = { type: type, id: parseInt(id) };
    } else {
        const targetData = localStorage.getItem('faceRegistrationTarget');
        if (!targetData) {
            showPersonPicker();
            return;
        }
        targetPerson = JSON.parse(targetData);
    }

    loadPersonInfo();
    startCamera();
});

// بوابة التسجيل تُفتح بلا شخص محدّد — نعرض شاشة اختيار بدل القفز إلى صفحة الدخول
const PICKER_TYPES = [
    { key: 'student', label: 'طالب' },
    { key: 'teacher', label: 'مدرس' },
    { key: 'administrative', label: 'موظف إداري' },
    { key: 'security', label: 'موظف أمني' },
    { key: 'service', label: 'موظف خدمة' }
];

// قائمة الأشخاص من خادم Django (المصدر الوحيد للهويات) — معرّف User.pk
// هو ما يُرسل للسيرفر عند الحفظ، لا معرّفات localStorage القديمة.
async function djangoPeople(userType) {
    const response = await fetch(
        `${FACE_CONFIG.STORAGE.API_URL}/api/users/?user_type=${userType}`,
        { headers: faceStorage.authHeaders() });
    if (!response.ok) {
        throw new Error(response.status === 401 || response.status === 403
            ? 'هذه البوابة تتطلب حساب مشرف أو قسم التسجيل'
            : 'تعذّر جلب قائمة الأشخاص من الخادم');
    }
    const data = await response.json();
    return (data.results || data).map(u => ({ id: u.id, name: u.name, idNumber: u.code }));
}

function showPersonPicker() {
    const container = document.querySelector('.face-registration-container');
    container.style.display = 'none';

    const picker = document.createElement('div');
    picker.className = 'person-picker';
    picker.innerHTML = `
        <h1>بوابة التسجيل</h1>
        <p class="person-picker-hint">اختر الشخص الذي تريد تسجيل وجهه للبدء.</p>
        <div class="form-group">
            <label for="pickerType">نوع الشخص</label>
            <select id="pickerType"></select>
        </div>
        <div class="form-group">
            <label for="pickerPerson">الاسم</label>
            <select id="pickerPerson"></select>
        </div>
        <p id="pickerError" style="color:#f87171; display:none;"></p>
        <button class="btn-primary" onclick="startPickerRegistration()">بدء تسجيل الوجه</button>
    `;
    container.parentNode.appendChild(picker);

    const typeSelect = picker.querySelector('#pickerType');
    typeSelect.innerHTML = PICKER_TYPES
        .map(t => `<option value="${t.key}">${t.label}</option>`).join('');
    typeSelect.addEventListener('change', fillPickerPeople);

    fillPickerPeople();
}

async function fillPickerPeople() {
    const group = document.getElementById('pickerType').value;
    const personSelect = document.getElementById('pickerPerson');
    const errorBox = document.getElementById('pickerError');
    try {
        const people = await djangoPeople(group);
        errorBox.style.display = 'none';
        personSelect.innerHTML = people.length
            ? people.map(p => `<option value="${p.id}">${p.name}${p.idNumber ? ' — ' + p.idNumber : ''}</option>`).join('')
            : '<option value="">لا يوجد مسجلون في هذه الفئة</option>';
    } catch (error) {
        errorBox.textContent = error.message;
        errorBox.style.display = 'block';
        personSelect.innerHTML = '<option value="">— تعذّر التحميل —</option>';
    }
}

function startPickerRegistration() {
    const type = document.getElementById('pickerType').value;
    const id = document.getElementById('pickerPerson').value;

    if (!id) {
        alert('اختر شخصًا أولًا.');
        return;
    }
    window.location.href = `face-registration-new.html?type=${type}&id=${id}`;
}

async function loadPersonInfo() {
    try {
        const response = await fetch(
            `${FACE_CONFIG.STORAGE.API_URL}/api/users/${targetPerson.id}/`,
            { headers: faceStorage.authHeaders() });
        if (!response.ok) throw new Error(String(response.status));
        const person = await response.json();
        document.getElementById('personName').textContent =
            `تسجيل وجه: ${person.name}${person.code ? ' — ' + person.code : ''}`;
    } catch (error) {
        document.getElementById('personName').textContent = 'تعذّر التحقق من بيانات الشخص من الخادم';
        updateMessage('لا يمكن بدء التسجيل قبل تحميل هوية الشخص من الخادم', 'error');
        document.getElementById('startBtn').disabled = true;
    }
}

async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 }
            } 
        });
        videoStream = stream;
        const video = document.getElementById('videoElement');
        video.srcObject = stream;
        await video.play();
        updateMessage('الكاميرا تعمل بنجاح', 'info');
    } catch (error) {
        updateMessage('فشل في الوصول للكاميرا', 'error');
    }
}

async function startRegistration() {
    // تحميل النماذج أولاً
    updateMessage('جاري تحميل نماذج التعرف على الوجه...', 'info');
    document.getElementById('startBtn').disabled = true;

    const modelsLoaded = await faceEngine.loadModels();
    if (!modelsLoaded) {
        updateMessage('فشل في تحميل النماذج', 'error');
        document.getElementById('startBtn').disabled = false;
        return;
    }

    // إعادة تعيين المحرك
    faceEngine.reset();
    acceptedCount = 0;
    rejectedCount = 0;
    currentPoseIndex = 0;
    blinkChallengePassed = false;

    // تحديث الواجهة
    isRegistering = true;
    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('stopBtn').style.display = 'inline-block';
    document.getElementById('saveBtn').style.display = 'none';

    // بدء التقاط تلقائي
    registrationInterval = setInterval(captureLoop, 200);
    updateMessage('بدء التسجيل التلقائي...', 'info');
}

async function captureLoop() {
    if (!isRegistering) return;

    const video = document.getElementById('videoElement');
    const currentPose = poses[currentPoseIndex];

    // تحديث التعليمات
    const instruction = faceEngine.getPoseInstruction(currentPose);
    document.getElementById('currentPose').textContent = instruction;

    // تحديث إطار الوجه وتوجيهات المستخدم
    await updateFaceGuidance(video, currentPose);

    // محاولة التقاط عينة
    const result = await faceEngine.captureSample(video, currentPose);

    if (result.success) {
        acceptedCount++;
        updateStats();
        updatePoseChecklist(currentPose);
        updateMessage(`تم التقاط عينة ${acceptedCount}/${FACE_CONFIG.REGISTRATION.TARGET_SAMPLES}`, 'success');

        // التحقق من اكتمال الوضع الحالي
        const targetCount = FACE_CONFIG.REGISTRATION.POSES[currentPose] || 0;
        const currentCount = faceEngine.getRegistrationStats().byPose[currentPose] || 0;

        if (currentCount >= targetCount) {
            currentPoseIndex++;
            if (currentPoseIndex >= poses.length) {
                // اكتمال جميع الوضعيات
                await completeRegistration();
            }
        }
    } else {
        rejectedCount++;
        updateStats();
        updateMessage(`رفض: ${result.reason}`, 'error');
    }

    // تحديث الجودة الحالية
    const detection = await faceEngine.detectFace(video);
    if (detection) {
        const quality = faceEngine.checkQuality(detection, video);
        updateQualityBar(quality.score);
    }
}

// تحديث توجيهات الوجه
async function updateFaceGuidance(video, targetPose) {
    const detection = await faceEngine.detectFace(video);
    const faceFrame = document.getElementById('faceFrame');
    const guidanceOverlay = document.getElementById('guidanceOverlay');
    const guidanceText = document.getElementById('guidanceText');

    // إعادة تعيين الأنماط
    faceFrame.className = 'face-frame';
    guidanceOverlay.style.display = 'none';

    if (!detection) {
        faceFrame.classList.add('invalid');
        updateGuidanceOverlay('لم يتم اكتشاف وجه - تأكد من وجودك أمام الكاميرا');
        return;
    }

    const faceBox = detection.detection.box;
    const faceSize = faceBox.width;
    const videoWidth = video.videoWidth || 640;
    const videoHeight = video.videoHeight || 480;

    // التحقق من حجم الوجه
    if (faceSize < FACE_CONFIG.QUALITY.MIN_FACE_SIZE) {
        faceFrame.classList.add('too-far');
        updateGuidanceOverlay('اقترب من الكاميرا - الوجه بعيد جداً');
        return;
    }

    if (faceSize > FACE_CONFIG.QUALITY.MAX_FACE_SIZE) {
        faceFrame.classList.add('too-close');
        updateGuidanceOverlay('ابتعد قليلاً - الوجه قريب جداً');
        return;
    }

    // التحقق من المركز
    const faceCenterX = faceBox.x + faceBox.width / 2;
    const faceCenterY = faceBox.y + faceBox.height / 2;
    const maxOffset = videoWidth * 0.15;

    if (Math.abs(faceCenterX - videoWidth / 2) > maxOffset) {
        if (faceCenterX < videoWidth / 2) {
            faceFrame.classList.add('move-right');
            updateGuidanceOverlay('حرّك وجهك قليلاً إلى اليمين لتكون في المنتصف');
        } else {
            faceFrame.classList.add('move-left');
            updateGuidanceOverlay('حرّك وجهك قليلاً إلى اليسار لتكون في المنتصف');
        }
        return;
    }

    // التحقق من الوضعية المطلوبة
    const detectedPose = faceEngine.detectPose(detection);
    const instruction = faceEngine.getPoseInstruction(targetPose);

    if (targetPose === 'front' && detectedPose !== 'front') {
        updateGuidanceOverlay('انظر مباشرة إلى الكاميرا');
        return;
    }

    if (targetPose === 'right_15' && (detectedPose === 'front' || detectedPose === 'left_15' || detectedPose === 'left_30')) {
        updateGuidanceOverlay('حرّك رأسك قليلاً إلى اليمين');
        return;
    }

    if (targetPose === 'right_30' && (detectedPose === 'front' || detectedPose === 'right_15' || detectedPose === 'left_15' || detectedPose === 'left_30')) {
        updateGuidanceOverlay('حرّك رأسك أكثر إلى اليمين');
        return;
    }

    if (targetPose === 'left_15' && (detectedPose === 'front' || detectedPose === 'right_15' || detectedPose === 'right_30')) {
        updateGuidanceOverlay('حرّك رأسك قليلاً إلى اليسار');
        return;
    }

    if (targetPose === 'left_30' && (detectedPose === 'front' || detectedPose === 'left_15' || detectedPose === 'right_15' || detectedPose === 'right_30')) {
        updateGuidanceOverlay('حرّك رأسك أكثر إلى اليسار');
        return;
    }

    if (targetPose === 'up' && detectedPose !== 'up') {
        updateGuidanceOverlay('انظر إلى الأعلى');
        return;
    }

    if (targetPose === 'down' && detectedPose !== 'down') {
        updateGuidanceOverlay('انظر إلى الأسفل');
        return;
    }

    // الوجه في الوضع الصحيح
    faceFrame.classList.add('valid');
    updateGuidanceOverlay(instruction, true);
}

// تحديث طبقة التوجيه
function updateGuidanceOverlay(text, isPositive = false) {
    const guidanceOverlay = document.getElementById('guidanceOverlay');
    const guidanceText = document.getElementById('guidanceText');

    guidanceOverlay.style.display = 'block';
    guidanceText.textContent = text;

    if (isPositive) {
        guidanceOverlay.style.background = 'rgba(0, 255, 0, 0.7)';
    } else {
        guidanceOverlay.style.background = 'rgba(255, 0, 0, 0.7)';
    }
}

async function completeRegistration() {
    // إيقاف التقاط
    stopRegistration();

    const stats = faceEngine.getRegistrationStats();
    const totalSamples = stats.total;

    if (totalSamples < FACE_CONFIG.REGISTRATION.TARGET_SAMPLES * 0.5) {
        updateMessage(`عدد العينات أقل من النصف المطلوب (${totalSamples}/${FACE_CONFIG.REGISTRATION.TARGET_SAMPLES})`, 'error');
        document.getElementById('startBtn').style.display = 'inline-block';
        document.getElementById('startBtn').disabled = false;
        return;
    }

    // تحدي الرمش
    if (FACE_CONFIG.LIVENESS.ENABLED && FACE_CONFIG.LIVENESS.BLINK_CHALLENGE) {
        await performBlinkChallenge();
    } else {
        showSaveButton();
    }
}

async function performBlinkChallenge() {
    document.getElementById('livenessChallenge').classList.add('active');
    updateMessage('تحدي التحقق الحيوي - رمش عينيك', 'info');

    faceEngine.resetBlinkDetection();
    let blinkDetected = false;
    let attempts = 0;
    const maxAttempts = 50; // 10 ثواني تقريباً

    const blinkInterval = setInterval(async () => {
        attempts++;
        const video = document.getElementById('videoElement');
        const detected = await faceEngine.checkBlink(video);

        if (detected) {
            blinkDetected = true;
            clearInterval(blinkInterval);
            document.getElementById('blinkStatus').textContent = '✓ تم اكتشاف الرمش';
            setTimeout(() => {
                document.getElementById('livenessChallenge').classList.remove('active');
                blinkChallengePassed = true;
                showSaveButton();
            }, 1000);
        } else if (attempts >= maxAttempts) {
            clearInterval(blinkInterval);
            document.getElementById('blinkStatus').textContent = '✗ لم يتم اكتشاف الرمش';
            setTimeout(() => {
                document.getElementById('livenessChallenge').classList.remove('active');
                // لا تسمح بالحفظ إذا فشل تحدي الرمش
                blinkChallengePassed = false;
                updateMessage('فشل تحدي الرمش - لا يمكن الحفظ. حاول مرة أخرى.', 'error');
                // لا تعرض زر الحفظ
            }, 1000);
        } else {
            document.getElementById('blinkStatus').textContent = `في انتظار الرمش... (${attempts}/${maxAttempts})`;
        }
    }, 200);
}

function showSaveButton() {
    // Only show save button if blink challenge passed (when enabled)
    if (FACE_CONFIG.LIVENESS.ENABLED && FACE_CONFIG.LIVENESS.BLINK_CHALLENGE && !blinkChallengePassed) {
        updateMessage('يجب اجتياز تحدي الرمش قبل الحفظ', 'error');
        return;
    }
    
    document.getElementById('saveBtn').style.display = 'inline-block';
    const stats = faceEngine.getRegistrationStats();
    updateMessage(`اكتمل التسجيل: ${stats.total} عينة - اضغط حفظ`, 'success');
}

function stopRegistration() {
    isRegistering = false;
    if (registrationInterval) {
        clearInterval(registrationInterval);
        registrationInterval = null;
    }
    document.getElementById('startBtn').style.display = 'inline-block';
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').style.display = 'none';
}

function saveFaceData() {
    const stats = faceEngine.getRegistrationStats();
    const totalSamples = stats.total;

    if (totalSamples < FACE_CONFIG.REGISTRATION.TARGET_SAMPLES * 0.5) {
        alert(`عدد العينات قليل جداً (${totalSamples}). يفضل إعادة التسجيل.`);
        return;
    }

    updateMessage('جاري حفظ البيانات...', 'info');
    document.getElementById('saveBtn').disabled = true;

    // حفظ البيانات الجديدة
    const newFaceData = faceEngine.saveFaceData();

    // حفظ في MySQL أو localStorage
    faceStorage.saveFaceData(targetPerson.type, targetPerson.id, newFaceData)
        .then(result => {
            if (result.success) {
                const storageType = result.storage || 'mysql';
                const samplesCount = result.samples_count || newFaceData.samples.length;

                updateMessage(`✅ تم حفظ ${samplesCount} عينة بنجاح في ${storageType}!`, 'success');

                // عرض تفاصيل الحفظ
                    samples: samplesCount,
                    version: newFaceData.version,
                    model: newFaceData.model,
                    storage: storageType,
                    byPose: stats.byPose
                });

                // القوالب البيومترية تُحفظ عند الخادم فقط — لا نسخ محلية
                // (معرّفات localStorage القديمة لا تطابق معرّفات Django،
                // ومزامنتها تنشر هويات خاطئة).

                // التوجيه للصفحة المناسبة
                setTimeout(() => {
                    stopCamera();
                    localStorage.removeItem('faceRegistrationTarget');

                    const operatorPage = portalOperatorRedirect();
                    if (operatorPage) {
                        window.location.href = operatorPage;
                    } else if (targetPerson.type === 'student') {
                        window.location.href = 'student-dashboard.html';
                    } else if (targetPerson.type === 'teacher') {
                        window.location.href = 'teacher-dashboard.html';
                    } else {
                        window.location.href = 'staff-dashboard.html';
                    }
                }, 2000);
            } else {
                updateMessage('❌ فشل في الحفظ: ' + (result.error || 'Unknown error'), 'error');
                document.getElementById('saveBtn').disabled = false;
            }
        })
        .catch(error => {
            updateMessage('❌ خطأ في حفظ البيانات: ' + error.message, 'error');
            document.getElementById('saveBtn').disabled = false;
        });
}

function updateStats() {
    const stats = faceEngine.getRegistrationStats();
    document.getElementById('totalSamples').textContent = stats.total;
    document.getElementById('acceptedSamples').textContent = acceptedCount;
    document.getElementById('rejectedSamples').textContent = rejectedCount;

    const progress = (stats.total / FACE_CONFIG.REGISTRATION.TARGET_SAMPLES) * 100;
    document.getElementById('progressFill').style.width = `${Math.min(progress, 100)}%`;
}

function updateQualityBar(score) {
    const percentage = Math.round(score * 100);
    document.getElementById('qualityFill').style.width = `${percentage}%`;
    document.getElementById('qualityValue').textContent = `${percentage}%`;

    if (score >= 0.8) {
        document.getElementById('qualityFill').style.background = '#00ff00';
    } else if (score >= 0.6) {
        document.getElementById('qualityFill').style.background = '#ffff00';
    } else {
        document.getElementById('qualityFill').style.background = '#ff0000';
    }
}

function updatePoseChecklist(currentPose) {
    const items = document.querySelectorAll('.pose-item');
    items.forEach(item => {
        const pose = item.getAttribute('data-pose');
        if (pose === currentPose) {
            item.classList.add('current');
            item.classList.remove('pending', 'completed');
        } else {
            const stats = faceEngine.getRegistrationStats();
            const count = stats.byPose[pose] || 0;
            const target = FACE_CONFIG.REGISTRATION.POSES[pose] || 10;

            if (count >= target) {
                item.classList.add('completed');
                item.classList.remove('pending', 'current');
            } else {
                item.classList.add('pending');
                item.classList.remove('completed', 'current');
            }
        }
    });
}

function updateMessage(message, type) {
    const messageBox = document.getElementById('messageBox');
    messageBox.textContent = message;
    messageBox.className = `message-box ${type}`;
}

function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
}

function portalOperatorRedirect() {
    let operator = null;
    try {
        operator = JSON.parse(localStorage.getItem('currentUser'));
    } catch (e) {
        return null;
    }
    if (!operator) return null;
    const operatorType = operator.user_type || operator.type;
    if (operatorType === 'registration') return 'face-registration-new.html';
    if (operatorType === 'admin' || operatorType === 'super_admin' || operator.is_superuser) return 'admin-dashboard.html';
    return null;
}

function goBack() {
    stopCamera();
    stopRegistration();
    localStorage.removeItem('faceRegistrationTarget');

    const operatorPage = portalOperatorRedirect();
    if (operatorPage) {
        window.location.href = operatorPage;
    } else if (targetPerson.type === 'student') {
        window.location.href = 'student-dashboard.html';
    } else if (targetPerson.type === 'teacher') {
        window.location.href = 'teacher-dashboard.html';
    } else {
        window.location.href = 'admin-dashboard.html';
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    stopCamera();
    stopRegistration();
});
