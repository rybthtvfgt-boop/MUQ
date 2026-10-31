// Security helper: escape HTML to prevent XSS
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

// Staff Dashboard System
let currentUser = null;
let staffVideoStream = null;
let currentStaff = null;

// Check authentication
async function checkAuth() {
    const user = await api.getCurrentUser();
    if (!user) {
        window.location.href = '../HTML/login.html';
        return null;
    }
    const userType = user.user_type || user.type;
    if (userType !== 'administrative' && userType !== 'security' && userType !== 'service') {
        window.location.href = '../HTML/login.html';
        return null;
    }
    return user;
}

// Initialize
document.addEventListener('DOMContentLoaded', async function() {
    currentUser = await checkAuth();
    if (currentUser) {
        loadStaffInfo();
        loadOverview();
    }
});

function loadStaffInfo() {
    let staff;
    switch(currentUser.type) {
        case 'administrative':
            staff = db.getAdministrativeStaff().find(s => s.id === currentUser.staffId);
            break;
        case 'security':
            staff = db.getSecurityStaff().find(s => s.id === currentUser.staffId);
            break;
        case 'service':
            staff = db.getServiceStaff().find(s => s.id === currentUser.staffId);
            break;
    }

    if (staff) {
        const typeNames = {
            'administrative': 'موظف إداري',
            'security': 'موظف أمني',
            'service': 'موظف خدمة'
        };
        document.getElementById('staffName').textContent = `${staff.name} (${typeNames[currentUser.type]})`;
        currentStaff = staff;
    }
}

async function logout() {
    await api.logout();
    window.location.href = '../HTML/login.html';
}

// Show section function
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });

    // Show selected section
    document.getElementById(sectionId).style.display = 'block';

    // Update active nav link
    document.querySelectorAll('.sidebar nav ul li a').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');

    // Load section data
    if (sectionId === 'overview') {
        loadOverview();
    } else if (sectionId === 'attendance') {
        loadAttendanceSection();
    } else if (sectionId === 'history') {
        loadHistory();
    } else if (sectionId === 'profile') {
        loadProfile();
    }
}

// Load overview
function loadOverview() {
    const staffAttendance = db.getStaffAttendanceByType(currentUser.type);
    const myAttendance = staffAttendance.filter(a => a.staffId === currentUser.staffId);

    // Calculate present and absent days this month
    const now = new Date();
    const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
    const monthAttendance = myAttendance.filter(a => new Date(a.date) >= firstDay);

    const presentCount = monthAttendance.filter(a => a.status === 'present').length;
    const absentCount = monthAttendance.filter(a => a.status === 'absent').length;
    const rate = monthAttendance.length > 0 ? Math.round((presentCount / monthAttendance.length) * 100) : 0;

    document.getElementById('presentDays').textContent = presentCount;
    document.getElementById('absentDays').textContent = absentCount;
    document.getElementById('attendanceRate').textContent = rate + '%';

    // Monthly chart
    loadMonthlyChart(myAttendance);
}

function loadMonthlyChart(attendance) {
    const chartContainer = document.getElementById('monthlyChart');
    chartContainer.innerHTML = '';

    // Get last 30 days
    const last30Days = [];
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        last30Days.push(date.toISOString().split('T')[0]);
    }

    // Group attendance by week
    const weeklyData = [];
    for (let i = 0; i < 4; i++) {
        const weekStart = i * 7;
        const weekEnd = weekStart + 6;
        const weekAttendance = attendance.filter(a => {
            const dateIndex = last30Days.indexOf(a.date);
            return dateIndex >= weekStart && dateIndex <= weekEnd;
        });
        const presentCount = weekAttendance.filter(a => a.status === 'present').length;
        const percentage = weekAttendance.length > 0 ? Math.round((presentCount / weekAttendance.length) * 100) : 0;
        weeklyData.push({
            week: `الأسبوع ${i + 1}`,
            percentage: percentage
        });
    }

    weeklyData.forEach(data => {
        const bar = document.createElement('div');
        bar.className = 'stat-bar';
        bar.style.height = data.percentage + '%';
        bar.title = `${data.week}: ${data.percentage}%`;

        const label = document.createElement('div');
        label.className = 'stat-label';
        label.textContent = data.week;

        const barContainer = document.createElement('div');
        barContainer.style.display = 'flex';
        barContainer.style.flexDirection = 'column';
        barContainer.style.alignItems = 'center';
        barContainer.appendChild(bar);
        barContainer.appendChild(label);

        chartContainer.appendChild(barContainer);
    });
}

// Load attendance section
function loadAttendanceSection() {
    // Reset attendance state
    document.getElementById('staffFaceStatus').textContent = 'يرجى الوقود أمام الكاميرا لتسجيل حضورك';
    document.getElementById('staffFaceStatus').className = 'face-status info';

    // Start camera
    startStaffCamera();
}

async function startStaffCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        staffVideoStream = stream;
        document.getElementById('staffVideo').srcObject = stream;
        updateStaffFaceStatus('الكاميرا تعمل. يرجى الوقود أمام الكاميرا لتسجيل حضورك', 'info');
    } catch (error) {
        console.error('Error accessing camera:', error);
        updateStaffFaceStatus('فشل في الوصول للكاميرا', 'error');
    }
}

async function captureStaffFace() {
    const video = document.getElementById('staffVideo');
    const canvas = document.getElementById('staffCanvas');
    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const capturedImage = canvas.toDataURL('image/jpeg');

    if (currentStaff && currentStaff.faceData && currentStaff.faceData.images && currentStaff.faceData.images.length > 0) {
        updateStaffFaceStatus('جاري التحقق من الهوية...', 'info');

        try {
            const result = await faceRecognition.verifyIdentity(capturedImage, currentStaff);

            if (result.verified) {
                // Check if already registered attendance today
                const today = new Date().toISOString().split('T')[0];
                const existingAttendance = db.getStaffAttendanceByDate(today).find(a =>
                    a.staffId === currentUser.staffId && a.staffType === currentUser.type
                );

                if (existingAttendance) {
                    updateStaffFaceStatus('تم تسجيل حضورك بالفعل اليوم!', 'info');
                } else {
                    // Record attendance
                    db.addStaffAttendance({
                        staffId: currentUser.staffId,
                        staffType: currentUser.type,
                        date: today,
                        status: 'present',
                        timestamp: new Date().toISOString()
                    });

                    updateStaffFaceStatus(`تم تسجيل حضورك بنجاح! (الثقة: ${result.confidence}%)`, 'success');

                    // Stop camera
                    stopStaffCamera();

                    // Redirect after 2 seconds
                    setTimeout(() => {
                        alert('تم تسجيل الحضور بنجاح');
                        showSection('overview');
                    }, 2000);
                }
            } else {
                updateStaffFaceStatus(`لم يتم التعرف على وجهك. الثقة: ${result.confidence}% - يرجى المحاولة مرة أخرى`, 'error');
            }
        } catch (error) {
            console.error('Face recognition error:', error);
            updateStaffFaceStatus('حدث خطأ في التحقق من الهوية. يرجى المحاولة مرة أخرى', 'error');
        }
    } else {
        updateStaffFaceStatus('لم يتم العثور على بيانات وجهك. يرجى التواصل مع الإدارة لتسجيل وجهك', 'error');
    }
}

function stopStaffCamera() {
    if (staffVideoStream) {
        staffVideoStream.getTracks().forEach(track => track.stop());
        staffVideoStream = null;
    }
}

function updateStaffFaceStatus(message, type) {
    const statusElement = document.getElementById('staffFaceStatus');
    statusElement.textContent = message;
    statusElement.className = `face-status ${type}`;
}

// Load history
function loadHistory() {
    const staffAttendance = db.getStaffAttendanceByType(currentUser.type);
    const myAttendance = staffAttendance.filter(a => a.staffId === currentUser.staffId);
    const tbody = document.getElementById('historyTableBody');
    tbody.innerHTML = '';

    // Sort by date descending
    myAttendance.sort((a, b) => new Date(b.date) - new Date(a.date));

    myAttendance.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(record.date)}</td>
            <td>${escapeHtml(new Date(record.timestamp).toLocaleTimeString('ar-SA'))}</td>
            <td><span class="status ${record.status}">${getStatusText(record.status)}</span></td>
        `;
        tbody.appendChild(row);
    });
}

function getStatusText(status) {
    switch(status) {
        case 'present': return 'حاضر';
        case 'absent': return 'غائب';
        case 'pending': return 'في الانتظار';
        default: return status;
    }
}

// Load profile
function loadProfile() {
    const profileContent = document.getElementById('profileContent');

    if (currentStaff) {
        const typeNames = {
            'administrative': 'موظف إداري',
            'security': 'موظف أمني',
            'service': 'موظف خدمة'
        };

        const faceStatus = currentStaff.faceData ?
            (currentStaff.faceData.version === 2 ? 'مسجل (جديد)' : 'مسجل (قديم)') :
            'غير مسجل';

        profileContent.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h3>المعلومات الشخصية</h3>
                    <p><strong>الاسم:</strong> ${currentStaff.name}</p>
                    <p><strong>النوع:</strong> ${typeNames[currentUser.type]}</p>
                    <p><strong>القسم:</strong> ${currentStaff.department}</p>
                    <p><strong>المسمى الوظيفي:</strong> ${currentStaff.position || '-'}</p>
                    <p><strong>البريد الإلكتروني:</strong> ${currentStaff.email}</p>
                    <p><strong>رقم الهاتف:</strong> ${currentStaff.phone}</p>
                </div>
                <div>
                    <h3>معلومات الحساب</h3>
                    <p><strong>اسم المستخدم:</strong> ${currentStaff.username}</p>
                    <p><strong>حالة تسجيل الوجه:</strong> ${faceStatus}</p>
                </div>
            </div>
        `;
    }
}

// Register face
function registerFace() {
    if (currentStaff) {
        window.location.href = `face-registration-new.html?type=${currentUser.type}&id=${currentStaff.id}`;
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    stopStaffCamera();
});