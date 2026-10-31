// Face Registration System
let videoStream = null;
let capturedImages = [];
let targetPerson = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Check URL parameters first
    const urlParams = new URLSearchParams(window.location.search);
    const type = urlParams.get('type');
    const id = urlParams.get('id');

    if (type && id) {
        // Direct navigation from student/teacher dashboard
        targetPerson = { type: type, id: parseInt(id) };
    } else {
        // Navigation from admin dashboard
        const targetData = localStorage.getItem('faceRegistrationTarget');
        if (!targetData) {
            alert('لم يتم تحديد الشخص المراد تسجيل وجهه');
            window.location.href = '../HTML/login.html';
            return;
        }
        targetPerson = JSON.parse(targetData);
    }

    // Load person info
    loadPersonInfo();

    // Start camera
    startCamera();
});

function loadPersonInfo() {
    let person;
    if (targetPerson.type === 'student') {
        person = db.getStudentById(targetPerson.id);
    } else if (targetPerson.type === 'teacher') {
        person = db.getTeacherById(targetPerson.id);
    }

    if (person) {
        document.getElementById('personName').textContent = `تسجيل وجه: ${person.name}`;
    }
}

async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoStream = stream;
        document.getElementById('videoElement').srcObject = stream;
        updateFaceStatus('الكاميرا تعمل بنجاح', 'success');
    } catch (error) {
        console.error('Error accessing camera:', error);
        updateFaceStatus('فشل في الوصول للكاميرا. يرجى التأكد من السماح بالوصول للكاميرا', 'error');
    }
}

function captureFace() {
    const video = document.getElementById('videoElement');
    const canvas = document.getElementById('canvasElement');
    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to base64
    const imageData = canvas.toDataURL('image/jpeg');
    capturedImages.push(imageData);

    updateFaceStatus(`تم التقاط ${capturedImages.length} صورة. يوصى بالتقاط 3-5 صور من زوايا مختلفة`, 'info');

    // Show captured images
    displayCapturedImages();

    // Show save button if we have at least 3 images
    if (capturedImages.length >= 3) {
        document.getElementById('saveBtn').style.display = 'inline-block';
        document.getElementById('retakeBtn').style.display = 'inline-block';
    }
}

function displayCapturedImages() {
    const container = document.getElementById('capturedImages');
    const imagesContainer = document.getElementById('capturedImagesContainer');

    container.innerHTML = '';
    imagesContainer.style.display = 'block';

    capturedImages.forEach((imageData, index) => {
        const img = document.createElement('img');
        img.src = imageData;
        img.style.width = '100px';
        img.style.height = '100px';
        img.style.objectFit = 'cover';
        img.style.borderRadius = '5px';
        img.style.border = '2px solid #667eea';
        container.appendChild(img);
    });
}

function retakePhoto() {
    capturedImages = [];
    document.getElementById('capturedImages').innerHTML = '';
    document.getElementById('capturedImagesContainer').style.display = 'none';
    document.getElementById('saveBtn').style.display = 'none';
    document.getElementById('retakeBtn').style.display = 'none';
    updateFaceStatus('يرجى التأكد من أن وجهك واضح في الإطار', 'info');
}

function saveFaceData() {
    if (capturedImages.length < 3) {
        alert('يرجى التقاط على الأقل 3 صور');
        return;
    }

    // Save face data to database
    const faceData = {
        images: capturedImages,
        createdAt: new Date().toISOString()
    };

    if (targetPerson.type === 'student') {
        db.updateStudent(targetPerson.id, { faceData: faceData });
        // Also update user
        const student = db.getStudentById(targetPerson.id);
        const users = db.getUsers();
        const userIndex = users.findIndex(u => u.studentId === student.id);
        if (userIndex !== -1) {
            db.updateUser(users[userIndex].id, { faceData: faceData });
        }
    } else if (targetPerson.type === 'teacher') {
        db.updateTeacher(targetPerson.id, { faceData: faceData });
        // Also update user
        const teacher = db.getTeacherById(targetPerson.id);
        const users = db.getUsers();
        const userIndex = users.findIndex(u => u.teacherId === teacher.id);
        if (userIndex !== -1) {
            db.updateUser(users[userIndex].id, { faceData: faceData });
        }
    }

    updateFaceStatus('تم حفظ بيانات الوجه بنجاح!', 'success');

    // Stop camera
    stopCamera();

    // Clear target data
    localStorage.removeItem('faceRegistrationTarget');

    // Redirect back to appropriate dashboard after 2 seconds
    setTimeout(() => {
        if (targetPerson.type === 'student') {
            window.location.href = 'student-dashboard.html';
        } else if (targetPerson.type === 'teacher') {
            window.location.href = 'teacher-dashboard.html';
        } else {
            window.location.href = 'admin-dashboard.html';
        }
    }, 2000);
}

function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
}

function updateFaceStatus(message, type) {
    const statusElement = document.getElementById('faceStatus');
    statusElement.textContent = message;
    statusElement.className = `face-status ${type}`;
}

function goBack() {
    stopCamera();
    localStorage.removeItem('faceRegistrationTarget');
    window.location.href = 'admin-dashboard.html';
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    stopCamera();
});