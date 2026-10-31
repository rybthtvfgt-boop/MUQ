// Security helper: escape HTML to prevent XSS
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

// Student Dashboard System
let currentUser = null;

// Check authentication
async function checkAuth() {
    const user = await api.getCurrentUser();
    if (!user) {
        window.location.href = '../HTML/login.html';
        return null;
    }
    if ((user.user_type || user.type) !== 'student') {
        window.location.href = '../HTML/login.html';
        return null;
    }
    return user;
}

// Initialize
document.addEventListener('DOMContentLoaded', async function() {
    currentUser = await checkAuth();
    if (currentUser) {
        loadStudentInfo();
        loadOverview();
    }
});

function loadStudentInfo() {
    const student = db.getStudentById(currentUser.studentId);
    if (student) {
        const stageName = db.getStageNameById(student.stageId) || '-';
        document.getElementById('studentName').textContent = `${student.name} (${stageName} - ${student.branch || '-'})`;
    }
}

// Register face
function registerFace() {
    const student = db.getStudentById(currentUser.studentId);
    if (student) {
        window.location.href = `face-registration-new.html?type=student&id=${student.id}`;
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
        loadAttendance();
    } else if (sectionId === 'schedule') {
        loadSchedule();
    } else if (sectionId === 'profile') {
        loadProfile();
    }
}

// Load overview
function loadOverview() {
    const student = db.getStudentById(currentUser.studentId);
    const attendance = db.getAttendance().filter(a => a.studentId === student.id);
    const schedule = db.getSchedule();

    // Calculate total attendance
    const presentCount = attendance.filter(a => a.status === 'present').length;
    const totalAttendance = attendance.length > 0 ? Math.round((presentCount / attendance.length) * 100) : 0;
    document.getElementById('totalAttendance').textContent = totalAttendance + '%';

    // Present and absent days
    document.getElementById('presentDays').textContent = presentCount;
    document.getElementById('absentDays').textContent = attendance.length - presentCount;

    // Week lectures
    const today = new Date();
    const weekStart = new Date(today);
    weekStart.setDate(today.getDate() - today.getDay());
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekStart.getDate() + 6);

    const weekSchedule = schedule.filter(s => {
        const dayMap = {
            'الأحد': 0,
            'الإثنين': 1,
            'الثلاثاء': 2,
            'الأربعاء': 3,
            'الخميس': 4,
            'الجمعة': 5,
            'السبت': 6
        };
        const dayIndex = dayMap[s.day];
        return dayIndex >= weekStart.getDay() && dayIndex <= weekEnd.getDay() &&
               s.subject === student.subject && s.stage === student.stage;
    });
    document.getElementById('weekLectures').textContent = weekSchedule.length;

    // Monthly chart
    loadMonthlyChart(attendance);
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

// Load attendance
function loadAttendance() {
    const student = db.getStudentById(currentUser.studentId);
    const attendance = db.getAttendance().filter(a => a.studentId === student.id);
    const schedule = db.getSchedule();
    const teachers = db.getTeachers();
    const tbody = document.getElementById('attendanceTableBody');
    tbody.innerHTML = '';

    // Sort by date descending
    attendance.sort((a, b) => new Date(b.date) - new Date(a.date));

    attendance.forEach(record => {
        const scheduleItem = schedule.find(s => s.id === record.scheduleId);
        // Only show attendance for student's stage
        if (!scheduleItem || scheduleItem.stageId !== student.stageId) {
            return;
        }
        const teacher = teachers.find(t => t.id === (scheduleItem ? scheduleItem.teacherId : null));

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(record.date)}</td>
            <td>${escapeHtml(scheduleItem ? scheduleItem.subject : 'غير محدد')}</td>
            <td>${escapeHtml(teacher ? teacher.name : 'غير محدد')}</td>
            <td>${escapeHtml(scheduleItem ? scheduleItem.time : 'غير محدد')}</td>
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

// Load schedule
function loadSchedule() {
    const student = db.getStudentById(currentUser.studentId);
    let schedule = db.getSchedule().filter(s =>
        s.stageId === student.stageId
    );

    // Filter by branch if student has a branch
    if (student.branch && student.branch !== '') {
        schedule = schedule.filter(s => !s.branch || s.branch === student.branch || s.branch === '');
    }

    const teachers = db.getTeachers();
    const tbody = document.getElementById('scheduleTableBody');
    tbody.innerHTML = '';

    schedule.forEach(item => {
        const teacher = teachers.find(t => t.id === item.teacherId);
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.day}</td>
            <td>${item.time}</td>
            <td>${item.subject}</td>
            <td>${db.getStageNameById(item.stageId) || '-'}</td>
            <td>${item.branch || '-'}</td>
            <td>${teacher ? teacher.name : 'غير محدد'}</td>
            <td>${db.getDepartmentNameById(item.departmentId) || '-'}</td>
        `;
        tbody.appendChild(row);
    });
}

// Load profile
function loadProfile() {
    const student = db.getStudentById(currentUser.studentId);
    const profileContent = document.getElementById('profileContent');

    if (student) {
        profileContent.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h3>المعلومات الشخصية</h3>
                    <p><strong>الاسم:</strong> ${student.name}</p>
                    <p><strong>الرقم الجامعي:</strong> ${student.idNumber}</p>
                    <p><strong>القسم:</strong> ${db.getDepartmentNameById(student.departmentId) || '-'}</p>
                    <p><strong>المرحلة:</strong> ${db.getStageNameById(student.stageId) || '-'}</p>
                    <p><strong>الشعبة:</strong> ${student.branch || '-'}</p>
                    <p><strong>البريد الإلكتروني:</strong> ${student.email}</p>
                    <p><strong>رقم الهاتف:</strong> ${student.phone}</p>
                </div>
                <div>
                    <h3>معلومات الحساب</h3>
                    <p><strong>اسم المستخدم:</strong> ${student.username}</p>
                    <p><strong>حالة تسجيل الوجه:</strong> ${student.faceData && student.faceData.images && student.faceData.images.length > 0 ? 'مسجل' : 'غير مسجل'}</p>
                </div>
            </div>
        `;
    }
}