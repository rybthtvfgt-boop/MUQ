// Staff Face Registration System
let videoStream = null;
let capturedImages = [];
let targetStaff = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Get target staff info
    const targetData = localStorage.getItem('staffRegistrationTarget');
    if (!targetData) {
        alert('لم يتم تحديد الشخص المراد تسجيل وجهه');
        window.location.href = 'admin-dashboard.html';
        return;
    }

    targetStaff = JSON.parse(targetData);

    // Load staff info
    loadStaffInfo();

    // Start camera
    startCamera();
});

function loadStaffInfo() {
    let staff;
    switch(targetStaff.type) {
        case 'administrative':
            staff = db.getAdministrativeStaff().find(s => s.id === targetStaff.id);
            break;
        case 'security':
            staff = db.getSecurityStaff().find(s => s.id === targetStaff.id);
            break;
        case 'service':
            staff = db.getServiceStaff().find(s => s.id === targetStaff.id);
            break;
    }

    if (staff) {
        const typeNames = {
            'administrative': 'موظف إداري',
            'security': 'موظف أمني',
            'service': 'موظف خدمة'
        };
        document.getElementById('personName').textContent = `تسجيل وجه: ${staff.name} (${typeNames[targetStaff.type]})`;
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

    switch(targetStaff.type) {
        case 'administrative':
            db.updateAdministrativeStaff(targetStaff.id, { faceData: faceData });
            break;
        case 'security':
            db.updateSecurityStaff(targetStaff.id, { faceData: faceData });
            break;
        case 'service':
            db.updateServiceStaff(targetStaff.id, { faceData: faceData });
            break;
    }

    // Also update user account
    const users = db.getUsers();
    const userIndex = users.findIndex(u => u.staffId === targetStaff.id && u.staffType === targetStaff.type);
    if (userIndex !== -1) {
        db.updateUser(users[userIndex].id, { faceData: faceData });
    }

    updateFaceStatus('تم حفظ بيانات الوجه بنجاح!', 'success');

    // Stop camera
    stopCamera();

    // Clear target data
    localStorage.removeItem('staffRegistrationTarget');

    // Redirect back after 2 seconds
    setTimeout(() => {
        window.location.href = 'admin-dashboard.html';
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
    localStorage.removeItem('staffRegistrationTarget');
    window.location.href = 'admin-dashboard.html';
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    stopCamera();
});