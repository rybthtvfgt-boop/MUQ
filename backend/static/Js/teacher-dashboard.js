// Security helper: escape HTML to prevent XSS
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

// Teacher Dashboard System
let currentUser = null;
let currentLecture = null;
let teacherVideoStream = null;
let studentVideoStream = null;
let endLectureVideoStream = null;
let currentAttendance = [];
let teacherAttendanceRecorded = false;
let currentLectureStudents = [];

// Check authentication
async function checkAuth() {
    const user = await api.getCurrentUser();
    if (!user) {
        window.location.href = 'login.html';
        return null;
    }
    if ((user.user_type || user.type) !== 'teacher') {
        window.location.href = 'login.html';
        return null;
    }
    return user;
}

// Initialize
document.addEventListener('DOMContentLoaded', async function() {
    currentUser = await checkAuth();
    if (currentUser) {
        loadTeacherInfo();
        loadOverview();
    }
});

function loadTeacherInfo() {
    const teacher = db.getTeacherById(currentUser.teacherId);
    if (teacher) {
        const stageName = db.getStageNameById(teacher.stageId) || '-';
        document.getElementById('teacherName').textContent = `${teacher.name} (${teacher.subject || '-'} - ${stageName} - ${teacher.branch || '-'})`;
    }
}

// Register face
function registerFace() {
    const teacher = db.getTeacherById(currentUser.teacherId);
    if (teacher) {
        window.location.href = `face-registration-new.html?type=teacher&id=${teacher.id}`;
    }
}

async function logout() {
    await api.logout();
    window.location.href = 'login.html';
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
    } else if (sectionId === 'my-schedule') {
        loadMySchedule();
    } else if (sectionId === 'history') {
        loadHistory();
    } else if (sectionId === 'profile') {
        loadProfile();
    }
}

// Load overview
function loadOverview() {
    const teacher = db.getTeacherById(currentUser.teacherId);
    const schedule = db.getSchedule();
    const students = db.getStudents();
    const attendance = db.getAttendance();

    // Get today's lectures for this teacher's subject and stage
    const today = new Date().toLocaleDateString('ar-SA', { weekday: 'long' });
    const todayLectures = schedule.filter(s =>
        s.day === today &&
        s.teacherId === teacher.id &&
        s.stageId === teacher.stageId
    );
    document.getElementById('todayLectures').textContent = todayLectures.length;

    // Get total students in teacher's stage
    const totalStudents = db.getStudentsByStageId(teacher.stageId).length;
    document.getElementById('totalStudents').textContent = totalStudents;

    // Calculate week attendance for this teacher's lectures
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    const teacherScheduleIds = schedule
        .filter(s => s.teacherId === teacher.id && s.stageId === teacher.stageId)
        .map(s => s.id);
    const weekAttendance = attendance.filter(a =>
        new Date(a.date) >= weekAgo && teacherScheduleIds.includes(a.scheduleId)
    );
    const presentCount = weekAttendance.filter(a => a.status === 'present').length;
    const rate = weekAttendance.length > 0 ? Math.round((presentCount / weekAttendance.length) * 100) : 0;
    document.getElementById('weekAttendance').textContent = rate + '%';
}

// Load attendance section
function loadAttendanceSection() {
    const teacher = db.getTeacherById(currentUser.teacherId);
    const schedule = db.getSchedule();
    const today = new Date().toLocaleDateString('ar-SA', { weekday: 'long' });

    // Get today's lectures for this teacher based on stage and branch
    const todayLectures = schedule.filter(s =>
        s.day === today &&
        s.teacherId === teacher.id &&
        s.stageId === teacher.stageId &&
        (!teacher.branch || !s.branch || s.branch === teacher.branch || s.branch === '')
    );

    const lectureSelect = document.getElementById('lectureSelect');
    lectureSelect.innerHTML = '<option value="">-- اختر محاضرة --</option>';

    todayLectures.forEach(lecture => {
        const option = document.createElement('option');
        option.value = lecture.id;
        const stageName = db.getStageNameById(lecture.stageId) || '-';
        const branchName = lecture.branch || teacher.branch || '-';
        option.textContent = `${lecture.subject} - ${lecture.time} - ${stageName} - ${branchName}`;
        lectureSelect.appendChild(option);
    });

    // Reset attendance state
    currentLecture = null;
    currentAttendance = [];
    currentLectureStudents = [];
    teacherAttendanceRecorded = false;
    document.getElementById('attendanceContent').style.display = 'none';
    document.getElementById('studentAttendanceSection').style.display = 'none';
    document.getElementById('endLectureSection').style.display = 'none';
    document.getElementById('lectureInfo').style.display = 'none';
}

function loadLectureStudents() {
    const lectureId = parseInt(document.getElementById('lectureSelect').value);
    if (!lectureId) {
        document.getElementById('attendanceContent').style.display = 'none';
        document.getElementById('lectureInfo').style.display = 'none';
        return;
    }

    currentLecture = db.getSchedule().find(s => s.id === lectureId);
    if (!currentLecture) return;

    const teacher = db.getTeacherById(currentUser.teacherId);

    // Get students based on stage and branch from the schedule
    let students;
    if (currentLecture.branch && currentLecture.branch !== '') {
        students = db.getStudents().filter(s => s.stageId === currentLecture.stageId && s.branch === currentLecture.branch);
    } else {
        students = db.getStudents().filter(s => s.stageId === currentLecture.stageId);
    }

    currentLectureStudents = students;
    currentAttendance = students.map(student => ({
        studentId: student.id,
        name: student.name,
        idNumber: student.idNumber,
        status: 'pending'
    }));

    // Show lecture info
    document.getElementById('lectureInfo').style.display = 'block';
    document.getElementById('lectureSubject').textContent = currentLecture.subject;
    document.getElementById('lectureStage').textContent = db.getStageNameById(currentLecture.stageId) || '-';
    document.getElementById('lectureBranch').textContent = currentLecture.branch || '-';
    document.getElementById('lectureDepartment').textContent = db.getDepartmentNameById(currentLecture.departmentId) || '-';
    document.getElementById('lectureTime').textContent = currentLecture.time;
    document.getElementById('studentCount').textContent = students.length;

    // Show attendance content
    document.getElementById('attendanceContent').style.display = 'block';

    // Start teacher camera
    startTeacherCamera();

    // Display attendance list
    displayAttendanceList();
}

function displayAttendanceList() {
    const listContainer = document.getElementById('attendanceList');
    listContainer.innerHTML = '';

    currentAttendance.forEach(record => {
        const item = document.createElement('div');
        item.className = 'attendance-item';
        item.innerHTML = `
            <div class="student-info">
                <div class="student-name">${record.name}</div>
                <div class="student-id">${record.idNumber}</div>
            </div>
            <div class="status ${record.status}">${getStatusText(record.status)}</div>
        `;
        listContainer.appendChild(item);
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

// Teacher attendance
async function startTeacherCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        teacherVideoStream = stream;
        document.getElementById('teacherVideo').srcObject = stream;
        updateTeacherFaceStatus('الكاميرا تعمل. يرجى الوقود أمام الكاميرا لتسجيل حضورك', 'info');
    } catch (error) {
        console.error('Error accessing camera:', error);
        updateTeacherFaceStatus('فشل في الوصول للكاميرا', 'error');
    }
}

async function captureTeacherFace() {
    if (teacherAttendanceRecorded) {
        alert('تم تسجيل حضورك بالفعل');
        return;
    }

    const video = document.getElementById('teacherVideo');
    const canvas = document.getElementById('teacherCanvas');
    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const capturedImage = canvas.toDataURL('image/jpeg');
    const teacher = db.getTeacherById(currentUser.teacherId);

    if (teacher && teacher.faceData && teacher.faceData.images && teacher.faceData.images.length > 0) {
        updateTeacherFaceStatus('جاري التحقق من الهوية...', 'info');

        try {
            // Use face recognition to verify identity
            const result = await faceRecognition.verifyIdentity(capturedImage, teacher);

            if (result.verified) {
                teacherAttendanceRecorded = true;
                updateTeacherFaceStatus(`تم تسجيل حضورك بنجاح! (الثقة: ${result.confidence}%)`, 'success');

                // Stop teacher camera
                stopTeacherCamera();

                // Enable student attendance
                document.getElementById('studentAttendanceSection').style.display = 'block';
                startStudentCamera();
            } else {
                updateTeacherFaceStatus(`لم يتم التعرف على وجهك. الثقة: ${result.confidence}% - يرجى المحاولة مرة أخرى`, 'error');
            }
        } catch (error) {
            console.error('Face recognition error:', error);
            updateTeacherFaceStatus('حدث خطأ في التحقق من الهوية. يرجى المحاولة مرة أخرى', 'error');
        }
    } else {
        updateTeacherFaceStatus('لم يتم العثور على بيانات وجهك. يرجى التواصل مع الإدارة لتسجيل وجهك', 'error');
    }
}

function stopTeacherCamera() {
    if (teacherVideoStream) {
        teacherVideoStream.getTracks().forEach(track => track.stop());
        teacherVideoStream = null;
    }
}

function updateTeacherFaceStatus(message, type) {
    const statusElement = document.getElementById('teacherFaceStatus');
    statusElement.textContent = message;
    statusElement.className = `face-status ${type}`;
}

// Student attendance
async function startStudentCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        studentVideoStream = stream;
        document.getElementById('studentVideo').srcObject = stream;
        updateStudentFaceStatus('الكاميرا تعمل. يرجى إحضار الطالب أمام الكاميرا', 'info');
    } catch (error) {
        console.error('Error accessing camera:', error);
        updateStudentFaceStatus('فشل في الوصول للكاميرا', 'error');
    }
}

async function captureStudentFace() {
    const video = document.getElementById('studentVideo');
    const canvas = document.getElementById('studentCanvas');
    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const capturedImage = canvas.toDataURL('image/jpeg');

    // Find pending students
    const pendingStudents = currentAttendance.filter(a => a.status === 'pending');
    if (pendingStudents.length === 0) {
        updateStudentFaceStatus('تم تسجيل حضور جميع الطلاب', 'success');
        stopStudentCamera();
        document.getElementById('endLectureSection').style.display = 'block';
        startEndLectureCamera();
        return;
    }

    updateStudentFaceStatus('جاري البحث عن الطالب في قاعدة البيانات...', 'info');

    try {
        // Create face database from current lecture students
        const faceDatabase = currentLectureStudents.filter(student =>
            student.faceData && student.faceData.images && student.faceData.images.length > 0
        );

        if (faceDatabase.length === 0) {
            updateStudentFaceStatus('لا يوجد طلاب مسجلة وجوههم في هذه المحاضرة', 'error');
            return;
        }

        // Use face recognition to find match
        const match = await faceRecognition.findMatch(capturedImage, faceDatabase);

        if (match && match.match) {
            const student = match.match;
            const index = currentAttendance.findIndex(a => a.studentId === student.id);

            if (index !== -1 && currentAttendance[index].status === 'pending') {
                currentAttendance[index].status = 'present';
                updateStudentFaceStatus(`تم تسجيل حضور: ${student.name} (الثقة: ${match.confidence}%)`, 'success');
                displayAttendanceList();

                // Check if all students are processed
                const remaining = currentAttendance.filter(a => a.status === 'pending');
                if (remaining.length === 0) {
                    updateStudentFaceStatus('تم تسجيل حضور جميع الطلاب', 'success');
                    stopStudentCamera();
                    document.getElementById('endLectureSection').style.display = 'block';
                    startEndLectureCamera();
                }
            } else if (index !== -1 && currentAttendance[index].status === 'present') {
                updateStudentFaceStatus(`الطالب ${student.name} مسجل حضور بالفعل`, 'info');
            }
        } else {
            updateStudentFaceStatus('لم يتم التعرف على هذا الوجه. تأكد من أن الطالب مسجل وجهه', 'error');
        }
    } catch (error) {
        console.error('Face recognition error:', error);
        updateStudentFaceStatus('حدث خطأ في التعرف على الوجه. يرجى المحاولة مرة أخرى', 'error');
    }
}

function stopStudentCamera() {
    if (studentVideoStream) {
        studentVideoStream.getTracks().forEach(track => track.stop());
        studentVideoStream = null;
    }
}

function updateStudentFaceStatus(message, type) {
    const statusElement = document.getElementById('studentFaceStatus');
    statusElement.textContent = message;
    statusElement.className = `face-status ${type}`;
}

// End lecture confirmation
async function startEndLectureCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        endLectureVideoStream = stream;
        document.getElementById('endLectureVideo').srcObject = stream;
        updateEndLectureStatus('يرجى تصوير نفسك لتأكيد نهاية المحاضرة', 'info');
    } catch (error) {
        console.error('Error accessing camera:', error);
        updateEndLectureStatus('فشل في الوصول للكاميرا', 'error');
    }
}

function confirmEndLecture() {
    const video = document.getElementById('endLectureVideo');
    const canvas = document.getElementById('endLectureCanvas');
    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Save attendance records
    const today = new Date().toISOString().split('T')[0];
    currentAttendance.forEach(record => {
        db.addAttendance({
            studentId: record.studentId,
            scheduleId: currentLecture.id,
            date: today,
            status: record.status,
            teacherId: currentUser.teacherId,
            timestamp: new Date().toISOString()
        });
    });

    updateEndLectureStatus('تم تأكيد نهاية المحاضرة وحفظ سجل الحضور بنجاح!', 'success');

    // Stop camera
    stopEndLectureCamera();

    // Redirect after 2 seconds
    setTimeout(() => {
        alert('تم حفظ سجل الحضور بنجاح');
        loadAttendanceSection();
    }, 2000);
}

function stopEndLectureCamera() {
    if (endLectureVideoStream) {
        endLectureVideoStream.getTracks().forEach(track => track.stop());
        endLectureVideoStream = null;
    }
}

function updateEndLectureStatus(message, type) {
    const statusElement = document.getElementById('endLectureStatus');
    statusElement.textContent = message;
    statusElement.className = `face-status ${type}`;
}

// Load my schedule
function loadMySchedule() {
    const teacher = db.getTeacherById(currentUser.teacherId);
    const schedule = db.getSchedule().filter(s =>
        s.teacherId === teacher.id &&
        s.stageId === teacher.stageId &&
        (!teacher.branch || !s.branch || s.branch === teacher.branch)
    );
    const tbody = document.getElementById('scheduleTableBody');
    tbody.innerHTML = '';

    schedule.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(item.day)}</td>
            <td>${escapeHtml(item.time)}</td>
            <td>${escapeHtml(item.subject)}</td>
            <td>${escapeHtml(db.getDepartmentNameById(item.departmentId) || '-')}</td>
            <td>${escapeHtml(db.getStageNameById(item.stageId) || '-')}</td>
            <td>${item.branch || '-'}</td>
        `;
        tbody.appendChild(row);
    });
}

// Load profile
function loadProfile() {
    const teacher = db.getTeacherById(currentUser.teacherId);
    const profileContent = document.getElementById('profileContent');
    profileContent.innerHTML = '';

    if (teacher) {
        const stageName = db.getStageNameById(teacher.stageId) || '-';
        profileContent.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h3>المعلومات الشخصية</h3>
                    <p><strong>الاسم:</strong> ${teacher.name}</p>
                    <p><strong>التخصص:</strong> ${teacher.specialization}</p>
                    <p><strong>المادة:</strong> ${teacher.subject || '-'}</p>
                    <p><strong>القسم:</strong> ${db.getDepartmentNameById(teacher.departmentId) || '-'}</p>
                    <p><strong>المرحلة:</strong> ${stageName}</p>
                    <p><strong>الشعبة:</strong> ${teacher.branch || '-'}</p>
                    <p><strong>البريد الإلكتروني:</strong> ${teacher.email}</p>
                    <p><strong>رقم الهاتف:</strong> ${teacher.phone}</p>
                </div>
                <div>
                    <h3>معلومات الحساب</h3>
                    <p><strong>اسم المستخدم:</strong> ${teacher.username}</p>
                    <p><strong>حالة تسجيل الوجه:</strong> ${teacher.faceData && teacher.faceData.images && teacher.faceData.images.length > 0 ? 'مسجل' : 'غير مسجل'}</p>
                </div>
            </div>
        `;
    }
}

// Load history
function loadHistory() {
    const teacher = db.getTeacherById(currentUser.teacherId);
    const schedule = db.getSchedule().filter(s =>
        s.teacherId === teacher.id &&
        s.stageId === teacher.stageId
    );
    const attendance = db.getAttendance();
    const tbody = document.getElementById('historyTableBody');
    tbody.innerHTML = '';

    // Group attendance by date and schedule
    const scheduleIds = schedule.map(s => s.id);
    const teacherAttendance = attendance.filter(a => scheduleIds.includes(a.scheduleId));

    // Group by date
    const groupedByDate = {};
    teacherAttendance.forEach(record => {
        if (!groupedByDate[record.date]) {
            groupedByDate[record.date] = {
                date: record.date,
                scheduleId: record.scheduleId,
                present: 0,
                total: 0
            };
        }
        groupedByDate[record.date].total++;
        if (record.status === 'present') {
            groupedByDate[record.date].present++;
        }
    });

    Object.values(groupedByDate).forEach(group => {
        const scheduleItem = schedule.find(s => s.id === group.scheduleId);
        const rate = group.total > 0 ? Math.round((group.present / group.total) * 100) : 0;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${group.date}</td>
            <td>${scheduleItem ? scheduleItem.subject : 'غير محدد'}</td>
            <td>${group.present}</td>
            <td>${group.total}</td>
            <td>${rate}%</td>
        `;
        tbody.appendChild(row);
    });
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    stopTeacherCamera();
    stopStudentCamera();
    stopEndLectureCamera();
});