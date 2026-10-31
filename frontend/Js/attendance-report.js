// Attendance Report System
let filteredAttendance = [];
let currentReportType = 'students';
let MAX_ABSENCE_LIMIT = 5; // الحد المسموح من الغياب

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeFilters();
    loadInitialData();
});

function showSection(sectionId) {
    // Not used in this page, kept for compatibility
}

function initializeFilters() {
    // Populate subject filter
    const subjects = [...new Set([...db.getStudents(), ...db.getTeachers()].map(p => p.subject).filter(s => s))];
    const subjectFilter = document.getElementById('subjectFilter');
    subjects.forEach(subject => {
        const option = document.createElement('option');
        option.value = subject;
        option.textContent = subject;
        subjectFilter.appendChild(option);
    });

    // Set default date range (last 30 days)
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);

    document.getElementById('endDate').value = endDate.toISOString().split('T')[0];
    document.getElementById('startDate').value = startDate.toISOString().split('T')[0];
}

function loadInitialData() {
    loadStages();
    applyFilters();
}

function loadStages() {
    const stages = db.getStages();
    const stageFilter = document.getElementById('stageFilter');

    stageFilter.innerHTML = '<option value="">الكل</option>';
    stages.forEach(stage => {
        const option = document.createElement('option');
        option.value = stage.id;
        option.textContent = stage.name;
        stageFilter.appendChild(option);
    });
}

function toggleFilters() {
    // Could be used to show/hide specific filters based on report type
    currentReportType = document.getElementById('reportType').value;
    checkAbsenceAlerts();
}

function updateAbsenceLimit() {
    const limitInput = document.getElementById('absenceLimit');
    MAX_ABSENCE_LIMIT = parseInt(limitInput.value) || 5;
    checkAbsenceAlerts();
}

function applyFilters() {
    const reportType = document.getElementById('reportType').value;
    const subjectFilter = document.getElementById('subjectFilter').value;
    const stageFilter = document.getElementById('stageFilter').value;
    const branchFilter = document.getElementById('branchFilter').value.toLowerCase();
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const statusFilter = document.getElementById('statusFilter').value;
    const searchName = document.getElementById('searchName').value.toLowerCase();

    let attendance = db.getAttendance();
    const students = db.getStudents();
    const teachers = db.getTeachers();
    const administrativeStaff = db.getAdministrativeStaff();
    const securityStaff = db.getSecurityStaff();
    const serviceStaff = db.getServiceStaff();
    const schedule = db.getSchedule();

    // Filter by date range
    if (startDate) {
        attendance = attendance.filter(a => a.date >= startDate);
    }
    if (endDate) {
        attendance = attendance.filter(a => a.date <= endDate);
    }

    // Filter by status
    if (statusFilter) {
        attendance = attendance.filter(a => a.status === statusFilter);
    }

    // Build attendance records with details
    let detailedRecords = [];

    if (reportType === 'students') {
        // Student attendance records
        attendance.forEach(record => {
            const student = students.find(s => s.id === record.studentId);
            if (!student) return;

            const scheduleItem = schedule.find(s => s.id === record.scheduleId);
            const teacher = teachers.find(t => t.id === (scheduleItem ? scheduleItem.teacherId : null));

            detailedRecords.push({
                date: record.date,
                name: student.name,
                subject: scheduleItem ? scheduleItem.subject : '',
                stage: db.getStageNameById(student.stageId) || db.getStageNameById(scheduleItem?.stageId) || '',
                branch: student.branch || scheduleItem?.branch || '',
                person: teacher ? teacher.name : 'غير محدد',
                time: scheduleItem ? scheduleItem.time : '',
                status: record.status,
                idNumber: student.idNumber,
                studentId: student.id,
                scheduleId: record.scheduleId
            });
        });
    } else if (reportType === 'teachers') {
        // Teacher attendance records (based on their lectures)
        attendance.forEach(record => {
            const scheduleItem = schedule.find(s => s.id === record.scheduleId);
            if (!scheduleItem) return;

            const teacher = teachers.find(t => t.id === scheduleItem.teacherId);
            if (!teacher) return;

            const student = students.find(s => s.id === record.studentId);

            detailedRecords.push({
                date: record.date,
                name: teacher.name,
                subject: teacher.subject || scheduleItem.subject,
                stage: db.getStageNameById(teacher.stageId) || db.getStageNameById(scheduleItem?.stageId) || '',
                branch: teacher.branch || scheduleItem?.branch || '',
                person: student ? student.name : 'غير محدد',
                time: scheduleItem.time,
                status: record.status,
                idNumber: teacher.specialization || '',
                teacherId: teacher.id,
                scheduleId: record.scheduleId
            });
        });
    } else if (reportType === 'administrative') {
        // Administrative staff attendance
        attendance.forEach(record => {
            const staff = administrativeStaff.find(s => s.id === record.personId);
            if (!staff) return;

            detailedRecords.push({
                date: record.date,
                name: staff.name,
                subject: staff.department || '',
                stage: '-',
                branch: staff.position || '',
                person: staff.name,
                time: record.time || '',
                status: record.status,
                idNumber: staff.username || '',
                staffId: staff.id
            });
        });
    } else if (reportType === 'security') {
        // Security staff attendance
        attendance.forEach(record => {
            const staff = securityStaff.find(s => s.id === record.personId);
            if (!staff) return;

            detailedRecords.push({
                date: record.date,
                name: staff.name,
                subject: staff.department || '',
                stage: '-',
                branch: staff.position || '',
                person: staff.name,
                time: record.time || '',
                status: record.status,
                idNumber: staff.username || '',
                staffId: staff.id
            });
        });
    } else if (reportType === 'service') {
        // Service staff attendance
        attendance.forEach(record => {
            const staff = serviceStaff.find(s => s.id === record.personId);
            if (!staff) return;

            detailedRecords.push({
                date: record.date,
                name: staff.name,
                subject: staff.department || '',
                stage: '-',
                branch: staff.position || '',
                person: staff.name,
                time: record.time || '',
                status: record.status,
                idNumber: staff.username || '',
                staffId: staff.id
            });
        });
    }

    // Filter by subject
    if (subjectFilter) {
        detailedRecords = detailedRecords.filter(r => r.subject === subjectFilter);
    }

    // Filter by stage
    if (stageFilter) {
        detailedRecords = detailedRecords.filter(r => {
            if (reportType === 'students') {
                const student = students.find(s => s.id === r.studentId);
                return student && student.stageId === parseInt(stageFilter);
            } else {
                const teacher = teachers.find(t => t.id === r.teacherId);
                return teacher && teacher.stageId === parseInt(stageFilter);
            }
        });
    }

    // Filter by branch
    if (branchFilter) {
        detailedRecords = detailedRecords.filter(r =>
            r.branch && r.branch.toLowerCase().includes(branchFilter.toLowerCase())
        );
    }

    // Filter by name search
    if (searchName) {
        detailedRecords = detailedRecords.filter(r =>
            r.name.toLowerCase().includes(searchName) ||
            r.idNumber.toLowerCase().includes(searchName)
        );
    }

    // Sort by date descending
    detailedRecords.sort((a, b) => new Date(b.date) - new Date(a.date));

    filteredAttendance = detailedRecords;
    displayAttendance();
    updateStatistics();
    checkAbsenceAlerts();
}

function resetFilters() {
    document.getElementById('subjectFilter').value = '';
    document.getElementById('stageFilter').value = '';
    document.getElementById('branchFilter').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('searchName').value = '';

    // Reset date range to last 30 days
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 30);

    document.getElementById('endDate').value = endDate.toISOString().split('T')[0];
    document.getElementById('startDate').value = startDate.toISOString().split('T')[0];

    applyFilters();
}

function displayAttendance() {
    const tbody = document.getElementById('attendanceTableBody');
    const tableTitle = document.getElementById('tableTitle');
    tbody.innerHTML = '';

    const reportType = document.getElementById('reportType').value;

    const titles = {
        'students': 'سجل حضور الطلاب',
        'teachers': 'سجل حضور المدرسين',
        'administrative': 'سجل الموظفين الإداريين',
        'security': 'سجل الموظفين الأمنيين',
        'service': 'سجل موظفي الخدمة'
    };

    tableTitle.textContent = titles[reportType] || 'سجل الحضور';

    if (filteredAttendance.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">لا توجد سجلات</td></tr>';
        return;
    }

    filteredAttendance.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.date}</td>
            <td>${record.name}</td>
            <td>${record.subject || '-'}</td>
            <td>${record.stage || '-'}</td>
            <td>${record.branch || '-'}</td>
            <td>${record.person}</td>
            <td>${record.time || '-'}</td>
            <td><span class="badge badge-${record.status}">${getStatusText(record.status)}</span></td>
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

function updateStatistics() {
    const totalRecords = filteredAttendance.length;
    const totalPresent = filteredAttendance.filter(r => r.status === 'present').length;
    const totalAbsent = filteredAttendance.filter(r => r.status === 'absent').length;
    const attendanceRate = totalRecords > 0 ? Math.round((totalPresent / totalRecords) * 100) : 0;

    document.getElementById('totalRecords').textContent = totalRecords;
    document.getElementById('totalPresent').textContent = totalPresent;
    document.getElementById('totalAbsent').textContent = totalAbsent;
    document.getElementById('attendanceRate').textContent = attendanceRate + '%';
}

function checkAbsenceAlerts() {
    const reportType = document.getElementById('reportType').value;

    // فقط للطلاب
    if (reportType !== 'students') {
        document.getElementById('alertsSection').style.display = 'none';
        return;
    }

    const students = db.getStudents();
    const attendance = db.getAttendance();
    const alertsList = document.getElementById('alertsList');
    const alertsSection = document.getElementById('alertsSection');

    const alertedStudents = [];

    students.forEach(student => {
        const studentAttendance = attendance.filter(a => a.studentId === student.id && a.status === 'absent');
        const absentCount = studentAttendance.length;

        if (absentCount >= MAX_ABSENCE_LIMIT) {
            alertedStudents.push({
                student: student,
                absentCount: absentCount
            });
        }
    });

    if (alertedStudents.length === 0) {
        alertsSection.style.display = 'none';
        return;
    }

    alertsSection.style.display = 'block';
    alertsList.innerHTML = '';

    alertedStudents.forEach(alert => {
        const alertItem = document.createElement('div');
        alertItem.className = 'alert-item';
        alertItem.innerHTML = `
            <div class="student-info">
                <div class="student-name">${alert.student.name}</div>
                <div class="absent-count">عدد الغياب: ${alert.absentCount} من ${MAX_ABSENCE_LIMIT}</div>
            </div>
            <div class="alert-badge">⚠️ وصل للحد المسموح</div>
        `;
        alertsList.appendChild(alertItem);
    });
}

function exportToCSV() {
    if (filteredAttendance.length === 0) {
        alert('لا توجد بيانات للتصدير');
        return;
    }

    const headers = ['التاريخ', 'الاسم', 'المادة', 'المرحلة', 'الشعبة', 'المدرس/الطالب', 'الوقت', 'الحالة'];
    const csvContent = [
        headers.join(','),
        ...filteredAttendance.map(record => [
            record.date,
            record.name,
            record.subject || '',
            record.stage || '',
            record.branch || '',
            record.person,
            record.time || '',
            getStatusText(record.status)
        ].join(','))
    ].join('\n');

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `تقرير_الحضور_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
}

function printReport() {
    window.print();
}

function goBack() {
    // Check user type and redirect accordingly
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    if (currentUser) {
        switch(currentUser.type) {
            case 'admin':
                window.location.href = 'admin-dashboard.html';
                break;
            case 'teacher':
                window.location.href = 'teacher-dashboard.html';
                break;
            case 'student':
                window.location.href = 'student-dashboard.html';
                break;
            case 'administrative':
            case 'security':
            case 'service':
                window.location.href = 'staff-dashboard.html';
                break;
            default:
                window.location.href = '../HTML/login.html';
        }
    } else {
        window.location.href = '../HTML/login.html';
    }
}

// Auto-refresh on filter changes
document.getElementById('subjectFilter').addEventListener('change', applyFilters);
document.getElementById('stageFilter').addEventListener('change', applyFilters);
document.getElementById('branchFilter').addEventListener('change', applyFilters);
document.getElementById('statusFilter').addEventListener('change', applyFilters);
document.getElementById('startDate').addEventListener('change', applyFilters);
document.getElementById('endDate').addEventListener('change', applyFilters);

// Search on Enter key
document.getElementById('searchName').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        applyFilters();
    }
});