// Security helper: escape HTML to prevent XSS
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
}

// Check authentication
async function checkAuth() {
    const user = await api.getCurrentUser();
    if (!user) {
        window.location.href = 'login.html';
        return null;
    }
    const userType = user.user_type || user.type;
    if (userType !== 'admin' && userType !== 'super_admin' && !user.is_superuser) {
        window.location.href = 'login.html';
        return null;
    }
    return user;
}

let currentUser = null;
checkAuth().then(async user => {
    currentUser = user;
    if (currentUser) {
        await loadOverview();
    }
});

// Logout function
async function logout() {
    await api.logout();
    window.location.href = 'login.html';
}

// Show section function
async function showSection(sectionId, event) {
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
    if (event && event.target) {
        event.target.classList.add('active');
    }

    // Load section data
    if (sectionId === 'overview') {
        await loadOverview();
    } else if (sectionId === 'users') {
        loadUsers();
    } else if (sectionId === 'students') {
        loadStudents();
    } else if (sectionId === 'teachers') {
        loadTeachers();
    } else if (sectionId === 'classifications') {
        loadClassifications();
    } else if (sectionId === 'staff') {
        loadStaff();
    } else if (sectionId === 'schedule') {
        loadSchedule();
    } else if (sectionId === 'statistics') {
        loadStatistics();
    } else if (sectionId === 'portals') {
        loadPortalAccounts();
    }
}

// Load overview data
async function loadOverview() {
    const students = await db.getStudents();
    const teachers = await db.getTeachers();
    const administrativeStaff = await db.getAdministrativeStaff();
    const securityStaff = await db.getSecurityStaff();
    const serviceStaff = await db.getServiceStaff();
    const schedule = await db.getSchedule();
    const attendance = await db.getAttendance();

    document.getElementById('totalStudents').textContent = students.length;
    document.getElementById('totalTeachers').textContent = teachers.length;

    // Get today's lectures
    const today = new Date().toLocaleDateString('ar-SA', { weekday: 'long' });
    const todayLectures = schedule.filter(s => s.day === today);
    document.getElementById('todayLectures').textContent = todayLectures.length;

    // Calculate attendance rate
    if (attendance.length > 0) {
        const presentCount = attendance.filter(a => a.status === 'present').length;
        const rate = Math.round((presentCount / attendance.length) * 100);
        document.getElementById('attendanceRate').textContent = rate + '%';
    }
}

// Load students
function loadStudents() {
    const students = db.getStudents();
    const tbody = document.getElementById('studentsTableBody');
    tbody.innerHTML = '';

    students.forEach(student => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${escapeHtml(student.name)}</td>
            <td>${escapeHtml(student.idNumber)}</td>
            <td>${escapeHtml(db.getDepartmentNameById(student.departmentId) || '-')}</td>
            <td>${escapeHtml(db.getStageNameById(student.stageId) || '-')}</td>
            <td>${escapeHtml(student.branch || '-')}</td>
            <td>${student.faceData && student.faceData.images && student.faceData.images.length > 0 ? 'مسجل' : 'غير مسجل'}</td>
            <td>
                <button class="btn btn-edit" onclick="editStudent(${student.id})">تعديل</button>
                <button class="btn btn-delete" onclick="deleteStudent(${student.id})">حذف</button>
                <button class="btn btn-add" onclick="registerFace(${student.id}, 'student')">تسجيل الوجه</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Load teachers
function loadTeachers() {
    const teachers = db.getTeachers();
    const tbody = document.getElementById('teachersTableBody');
    tbody.innerHTML = '';

    teachers.forEach(teacher => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${teacher.name}</td>
            <td>${teacher.specialization}</td>
            <td>${teacher.subject || '-'}</td>
            <td>${db.getDepartmentNameById(teacher.departmentId) || '-'}</td>
            <td>${db.getStageNameById(teacher.stageId) || '-'}</td>
            <td>${teacher.branch || '-'}</td>
            <td>${teacher.email}</td>
            <td>${teacher.faceData && teacher.faceData.images && teacher.faceData.images.length > 0 ? 'مسجل' : 'غير مسجل'}</td>
            <td>
                <button class="btn btn-edit" onclick="editTeacher(${teacher.id})">تعديل</button>
                <button class="btn btn-delete" onclick="deleteTeacher(${teacher.id})">حذف</button>
                <button class="btn btn-add" onclick="registerFace(${teacher.id}, 'teacher')">تسجيل الوجه</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Load schedule
function loadSchedule() {
    const schedule = db.getSchedule();
    const teachers = db.getTeachers();
    const tbody = document.getElementById('scheduleTableBody');
    tbody.innerHTML = '';

    // Populate filter dropdowns
    populateScheduleFilters();

    // Populate teacher select in modal (all teachers initially)
    updateTeacherSelect();

    // Get filter values
    const stageFilter = document.getElementById('scheduleStageFilter').value;
    const departmentFilter = document.getElementById('scheduleDepartmentFilter').value;

    // Filter schedule
    let filteredSchedule = schedule;
    if (stageFilter) {
        filteredSchedule = filteredSchedule.filter(s => s.stageId === parseInt(stageFilter));
    }
    if (departmentFilter) {
        filteredSchedule = filteredSchedule.filter(s => s.departmentId === parseInt(departmentFilter));
    }

    // Group by stage for better organization
    const stages = db.getStages();
    const groups = {};

    stages.forEach(stage => {
        groups[stage.id] = {
            stageName: stage.name,
            items: []
        };
    });

    filteredSchedule.forEach(item => {
        if (groups[item.stageId]) {
            groups[item.stageId].items.push(item);
        }
    });

    // Display grouped schedule
    stages.forEach(stage => {
        if (groups[stage.id] && groups[stage.id].items.length > 0) {
            // Add stage header row
            const headerRow = document.createElement('tr');
            headerRow.className = 'stage-header';
            headerRow.innerHTML = `
                <td colspan="8" style="background: var(--accent-color); color: white; font-weight: bold; padding: 12px;">
                    ${stage.name}
                </td>
            `;
            tbody.appendChild(headerRow);

            // Add items for this stage
            groups[stage.id].items.forEach(item => {
                const teacher = teachers.find(t => t.id === item.teacherId);
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${item.day}</td>
                    <td>${item.time}</td>
                    <td>${item.subject}</td>
                    <td>${db.getDepartmentNameById(item.departmentId) || '-'}</td>
                    <td>${db.getStageNameById(item.stageId) || '-'}</td>
                    <td>${item.branch || '-'}</td>
                    <td>${teacher ? teacher.name : 'غير محدد'}</td>
                    <td>
                        <button class="btn btn-edit" onclick="editSchedule(${item.id})">تعديل</button>
                        <button class="btn btn-delete" onclick="deleteSchedule(${item.id})">حذف</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
    });

    // If no items, show message
    if (filteredSchedule.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td colspan="8" style="text-align: center; padding: 20px; color: #999;">
                لا توجد محاضرات
            </td>
        `;
        tbody.appendChild(row);
    }
}

function populateScheduleFilters() {
    // Populate stage filter
    const stageFilter = document.getElementById('scheduleStageFilter');
    const currentStageValue = stageFilter.value;
    stageFilter.innerHTML = '<option value="">-- جميع المراحل --</option>';
    const stages = db.getStages();
    stages.forEach(stage => {
        const option = document.createElement('option');
        option.value = stage.id;
        option.textContent = stage.name;
        stageFilter.appendChild(option);
    });
    stageFilter.value = currentStageValue;

    // Populate department filter
    const departmentFilter = document.getElementById('scheduleDepartmentFilter');
    const currentDepartmentValue = departmentFilter.value;
    departmentFilter.innerHTML = '<option value="">-- جميع الأقسام --</option>';
    const departments = db.getDepartments();
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept.id;
        option.textContent = dept.name;
        departmentFilter.appendChild(option);
    });
    departmentFilter.value = currentDepartmentValue;
}

function filterScheduleByStage() {
    loadSchedule();
}

// Update teacher select based on subject, stage, and branch
function updateTeacherSelect() {
    const subject = document.getElementById('scheduleSubject').value;
    const departmentId = document.getElementById('scheduleDepartment').value ? parseInt(document.getElementById('scheduleDepartment').value) : null;
    const stageId = document.getElementById('scheduleStage').value ? parseInt(document.getElementById('scheduleStage').value) : null;
    const branch = document.getElementById('scheduleBranch').value;
    const teacherSelect = document.getElementById('scheduleTeacher');

    teacherSelect.innerHTML = '<option value="">-- اختر المدرس --</option>';

    const teachers = db.getTeachers();
    let filteredTeachers = teachers;

    if (subject) {
        filteredTeachers = filteredTeachers.filter(t => t.subject === subject);
    }
    if (departmentId) {
        filteredTeachers = filteredTeachers.filter(t => t.departmentId === departmentId);
    }
    if (stageId) {
        filteredTeachers = filteredTeachers.filter(t => t.stageId === stageId);
    }
    if (branch) {
        filteredTeachers = filteredTeachers.filter(t => !t.branch || t.branch === branch);
    }

    filteredTeachers.forEach(teacher => {
        const option = document.createElement('option');
        option.value = teacher.id;
        const stageName = db.getStageNameById(teacher.stageId) || '-';
        option.textContent = `${teacher.name} (${teacher.subject || '-'} - ${stageName} - ${teacher.branch || 'للكل'})`;
        teacherSelect.appendChild(option);
    });
}

// Load statistics
function loadStatistics() {
    const students = db.getStudents();
    const attendance = db.getAttendance();

    // Create attendance chart
    const chartContainer = document.getElementById('attendanceChart');
    chartContainer.innerHTML = '';

    const last7Days = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        last7Days.push(date.toISOString().split('T')[0]);
    }

    last7Days.forEach(date => {
        const dayAttendance = attendance.filter(a => a.date === date);
        const presentCount = dayAttendance.filter(a => a.status === 'present').length;
        const totalCount = dayAttendance.length;
        const percentage = totalCount > 0 ? Math.round((presentCount / totalCount) * 100) : 0;

        const bar = document.createElement('div');
        bar.className = 'stat-bar';
        bar.style.height = percentage + '%';
        bar.title = `${date}: ${percentage}%`;

        const label = document.createElement('div');
        label.className = 'stat-label';
        label.textContent = date.slice(5);

        const barContainer = document.createElement('div');
        barContainer.style.display = 'flex';
        barContainer.style.flexDirection = 'column';
        barContainer.style.alignItems = 'center';
        barContainer.appendChild(bar);
        barContainer.appendChild(label);

        chartContainer.appendChild(barContainer);
    });

    // Load top students
    const studentAttendance = students.map(student => {
        const studentRecords = attendance.filter(a => a.studentId === student.id);
        const presentCount = studentRecords.filter(a => a.status === 'present').length;
        const percentage = studentRecords.length > 0 ? Math.round((presentCount / studentRecords.length) * 100) : 0;
        return {
            ...student,
            attendancePercentage: percentage
        };
    }).sort((a, b) => b.attendancePercentage - a.attendancePercentage).slice(0, 5);

    const topStudentsBody = document.getElementById('topStudentsBody');
    topStudentsBody.innerHTML = '';

    studentAttendance.forEach(student => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${student.name} (${db.getStageNameById(student.stageId) || '-'} - ${db.getBranchNameById(student.branchId) || '-'})</td>
            <td>${student.attendancePercentage}%</td>
        `;
        topStudentsBody.appendChild(row);
    });
}

// Load staff
function loadStaff() {
    const administrativeStaff = db.getAdministrativeStaff();
    const securityStaff = db.getSecurityStaff();
    const serviceStaff = db.getServiceStaff();
    const tbody = document.getElementById('staffTableBody');
    tbody.innerHTML = '';

    // Combine all staff
    const allStaff = [
        ...administrativeStaff.map(s => ({ ...s, type: 'موظف إداري', typeCode: 'administrative' })),
        ...securityStaff.map(s => ({ ...s, type: 'موظف أمني', typeCode: 'security' })),
        ...serviceStaff.map(s => ({ ...s, type: 'موظف خدمة', typeCode: 'service' }))
    ];

    allStaff.forEach(staff => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${staff.name}</td>
            <td>${staff.type}</td>
            <td>${staff.department}</td>
            <td>${staff.email}</td>
            <td>${staff.phone}</td>
            <td>${staff.faceData && staff.faceData.images && staff.faceData.images.length > 0 ? 'مسجل' : 'غير مسجل'}</td>
            <td>
                <button class="btn btn-edit" onclick="editStaff(${staff.id}, '${staff.typeCode}')">تعديل</button>
                <button class="btn btn-delete" onclick="deleteStaff(${staff.id}, '${staff.typeCode}')">حذف</button>
                <button class="btn btn-add" onclick="registerStaffFace(${staff.id}, '${staff.typeCode}')">تسجيل الوجه</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Load classifications
function loadClassifications() {
    loadDepartments();
    loadStages();
    loadBranches();
}

function showClassificationTab(tabName) {
    document.querySelectorAll('.classification-tab').forEach(tab => {
        tab.style.display = 'none';
    });
    document.getElementById(tabName + 'Tab').style.display = 'block';

    // Update active button
    document.querySelectorAll('#classifications .filter-row button').forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-add');
    });
    event.target.classList.remove('btn-add');
    event.target.classList.add('btn-primary');

    // Load data
    if (tabName === 'departments') {
        loadDepartments();
    } else if (tabName === 'stages') {
        loadStages();
    } else if (tabName === 'branches') {
        loadBranches();
    }
}

function loadDepartments() {
    const departments = db.getDepartments();
    const students = db.getStudents();
    const tbody = document.getElementById('departmentsTableBody');
    tbody.innerHTML = '';

    departments.forEach(dept => {
        const studentCount = students.filter(s => s.departmentId === dept.id).length;

        // Get stage names
        let stageNames = '-';
        if (dept.stageIds && dept.stageIds.length > 0) {
            stageNames = dept.stageIds.map(stageId => db.getStageNameById(stageId)).filter(name => name).join('، ');
        }

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${dept.name}</td>
            <td>${dept.description || '-'}</td>
            <td>${stageNames}</td>
            <td>${studentCount}</td>
            <td>
                <button class="btn btn-edit" onclick="editDepartment(${dept.id})">تعديل</button>
                <button class="btn btn-delete" onclick="deleteDepartment(${dept.id})">حذف</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function loadStages() {
    const departmentFilter = document.getElementById('stageDepartmentFilter').value;
    let stages = db.getStages();
    const students = db.getStudents();
    const tbody = document.getElementById('stagesTableBody');
    tbody.innerHTML = '';

    // Populate department filter
    const departmentSelect = document.getElementById('stageDepartmentFilter');
    const currentDeptValue = departmentSelect.value;
    departmentSelect.innerHTML = '<option value="">-- جميع الأقسام --</option>';
    const departments = db.getDepartments();
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept.id;
        option.textContent = dept.name;
        departmentSelect.appendChild(option);
    });
    departmentSelect.value = currentDeptValue;

    // Filter by department
    if (departmentFilter) {
        stages = stages.filter(s => s.departmentId === parseInt(departmentFilter));
    }

    stages.forEach(stage => {
        const studentCount = students.filter(s => s.stageId === stage.id).length;
        const branches = db.getBranchesByStageId(stage.id);
        const branchCount = branches.length;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${stage.name}</td>
            <td>${db.getDepartmentNameById(stage.departmentId) || '-'}</td>
            <td>${stage.description || '-'}</td>
            <td>${branchCount} شعبة</td>
            <td>${studentCount}</td>
            <td>
                <button class="btn btn-edit" onclick="editStage(${stage.id})">تعديل</button>
                <button class="btn btn-delete" onclick="deleteStage(${stage.id})">حذف</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function loadBranches() {
    const departmentFilter = document.getElementById('branchDepartmentFilter').value;
    const stageFilter = document.getElementById('branchStageFilter').value;
    let branches = db.getBranches();
    const students = db.getStudents();
    const tbody = document.getElementById('branchesTableBody');
    tbody.innerHTML = '';

    // Populate department filter
    const departmentSelect = document.getElementById('branchDepartmentFilter');
    const currentDeptValue = departmentSelect.value;
    departmentSelect.innerHTML = '<option value="">-- جميع الأقسام --</option>';
    const departments = db.getDepartments();
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept.id;
        option.textContent = dept.name;
        departmentSelect.appendChild(option);
    });
    departmentSelect.value = currentDeptValue;

    // Populate stage filter based on selected department
    const stageSelect = document.getElementById('branchStageFilter');
    const currentStageValue = stageSelect.value;
    stageSelect.innerHTML = '<option value="">-- جميع المراحل --</option>';
    let stages = db.getStages();
    if (departmentFilter) {
        stages = stages.filter(s => s.departmentId === parseInt(departmentFilter));
    }
    stages.forEach(stage => {
        const option = document.createElement('option');
        option.value = stage.id;
        option.textContent = stage.name;
        stageSelect.appendChild(option);
    });
    stageSelect.value = currentStageValue;

    // Filter by department and stage
    if (departmentFilter) {
        branches = branches.filter(b => {
            const stage = db.getStageById(b.stageId);
            return stage && stage.departmentId === parseInt(departmentFilter);
        });
    }
    if (stageFilter) {
        branches = branches.filter(b => b.stageId === parseInt(stageFilter));
    }

    branches.forEach(branch => {
        const studentCount = students.filter(s => s.branchId === branch.id).length;
        const stage = db.getStageById(branch.stageId);
        const department = stage ? db.getDepartmentById(stage.departmentId) : null;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${branch.name}</td>
            <td>${department ? department.name : '-'}</td>
            <td>${stage ? stage.name : '-'}</td>
            <td>${branch.description || '-'}</td>
            <td>${studentCount}</td>
            <td>
                <button class="btn btn-edit" onclick="editBranch(${branch.id})">تعديل</button>
                <button class="btn btn-delete" onclick="deleteBranch(${branch.id})">حذف</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Department modal functions
function openDepartmentModal() {
    document.getElementById('departmentModal').classList.add('active');
    document.getElementById('departmentModalTitle').textContent = 'إضافة قسم جديد';
    document.getElementById('departmentForm').reset();
    document.getElementById('departmentId').value = '';

    // Load all stages for selection
    loadStagesForDepartmentSelection();
}

function loadStagesForDepartmentSelection() {
    const allStages = db.getStages();
    const selectionContainer = document.getElementById('departmentStagesSelection');
    selectionContainer.innerHTML = '';

    allStages.forEach(stage => {
        const checkbox = document.createElement('div');
        checkbox.style.display = 'flex';
        checkbox.style.alignItems = 'center';
        checkbox.style.gap = '8px';
        checkbox.innerHTML = `
            <input type="checkbox" id="stage_${stage.id}" value="${stage.id}" class="stage-checkbox">
            <label for="stage_${stage.id}">${stage.name}</label>
        `;
        selectionContainer.appendChild(checkbox);
    });

    // Add change listener to limit to 4 stages
    const checkboxes = document.querySelectorAll('.stage-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const checked = document.querySelectorAll('.stage-checkbox:checked');
            if (checked.length > 4) {
                this.checked = false;
                alert('يمكن اختيار 4 مراحل فقط');
            }
        });
    });
}

function closeDepartmentModal() {
    document.getElementById('departmentModal').classList.remove('active');
}

function editDepartment(id) {
    const department = db.getDepartmentById(id);
    if (department) {
        document.getElementById('departmentModal').classList.add('active');
        document.getElementById('departmentModalTitle').textContent = 'تعديل القسم';
        document.getElementById('departmentId').value = department.id;
        document.getElementById('departmentName').value = department.name;
        document.getElementById('departmentDescription').value = department.description || '';

        // Load stages for selection
        loadStagesForDepartmentSelection();

        // Check the previously selected stages
        if (department.stageIds && department.stageIds.length > 0) {
            department.stageIds.forEach(stageId => {
                const checkbox = document.getElementById(`stage_${stageId}`);
                if (checkbox) {
                    checkbox.checked = true;
                }
            });
        }
    }
}

function deleteDepartment(id) {
    if (confirm('هل أنت متأكد من حذف هذا القسم؟ سيتم فصل جميع الطلاب المرتبطين به')) {
        db.deleteDepartment(id);
        // Update students to remove department reference
        const students = db.getStudents().filter(s => s.departmentId === id);
        students.forEach(student => {
            db.updateStudent(student.id, { departmentId: null });
        });
        loadDepartments();
    }
}

// Stage modal functions
function openStageModal() {
    document.getElementById('stageModal').classList.add('active');
    document.getElementById('stageModalTitle').textContent = 'إضافة مرحلة جديدة';
    document.getElementById('stageForm').reset();
    document.getElementById('stageId').value = '';

    // Populate department dropdown
    const departmentSelect = document.getElementById('stageDepartment');
    departmentSelect.innerHTML = '<option value="">-- اختر القسم --</option>';
    const departments = db.getDepartments();
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept.id;
        option.textContent = dept.name;
        departmentSelect.appendChild(option);
    });
}

function closeStageModal() {
    document.getElementById('stageModal').classList.remove('active');
}

function editStage(id) {
    const stage = db.getStageById(id);
    if (stage) {
        document.getElementById('stageModal').classList.add('active');
        document.getElementById('stageModalTitle').textContent = 'تعديل المرحلة';
        document.getElementById('stageId').value = stage.id;
        document.getElementById('stageName').value = stage.name;
        document.getElementById('stageDescription').value = stage.description || '';

        // Populate department dropdown
        const departmentSelect = document.getElementById('stageDepartment');
        departmentSelect.innerHTML = '<option value="">-- اختر القسم --</option>';
        const departments = db.getDepartments();
        departments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept.id;
            option.textContent = dept.name;
            departmentSelect.appendChild(option);
        });
        departmentSelect.value = stage.departmentId || '';
    }
}

function deleteStage(id) {
    if (confirm('هل أنت متأكد من حذف هذه المرحلة؟ سيتم فصل جميع الطلاب المرتبطين بها')) {
        db.deleteStage(id);
        // Update students to remove stage reference
        const students = db.getStudents().filter(s => s.stageId === id);
        students.forEach(student => {
            db.updateStudent(student.id, { stageId: null });
        });
        loadStages();
    }
}

// Branch modal functions
function openBranchModal() {
    document.getElementById('branchModal').classList.add('active');
    document.getElementById('branchModalTitle').textContent = 'إضافة شعبة جديدة';
    document.getElementById('branchForm').reset();
    document.getElementById('branchId').value = '';

    // Populate department dropdown
    const departmentSelect = document.getElementById('branchDepartment');
    departmentSelect.innerHTML = '<option value="">-- اختر القسم --</option>';
    const departments = db.getDepartments();
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept.id;
        option.textContent = dept.name;
        departmentSelect.appendChild(option);
    });

    // Reset stage dropdown
    const stageSelect = document.getElementById('branchStage');
    stageSelect.innerHTML = '<option value="">-- اختر المرحلة --</option>';
}

function updateBranchStageOptions() {
    const departmentId = document.getElementById('branchDepartment').value;
    const stageSelect = document.getElementById('branchStage');
    stageSelect.innerHTML = '<option value="">-- اختر المرحلة --</option>';

    if (departmentId) {
        const stages = db.getStagesByDepartmentId(parseInt(departmentId));
        stages.forEach(stage => {
            const option = document.createElement('option');
            option.value = stage.id;
            option.textContent = stage.name;
            stageSelect.appendChild(option);
        });
    }
}

function closeBranchModal() {
    document.getElementById('branchModal').classList.remove('active');
}

function editBranch(id) {
    const branch = db.getBranchById(id);
    if (branch) {
        document.getElementById('branchModal').classList.add('active');
        document.getElementById('branchModalTitle').textContent = 'تعديل الشعبة';
        document.getElementById('branchId').value = branch.id;
        document.getElementById('branchName').value = branch.name;
        document.getElementById('branchDescription').value = branch.description || '';

        // Populate department dropdown
        const departmentSelect = document.getElementById('branchDepartment');
        departmentSelect.innerHTML = '<option value="">-- اختر القسم --</option>';
        const departments = db.getDepartments();
        departments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept.id;
            option.textContent = dept.name;
            departmentSelect.appendChild(option);
        });

        // Set department and update stages
        const stage = db.getStageById(branch.stageId);
        if (stage) {
            departmentSelect.value = stage.departmentId || '';
            updateBranchStageOptions();
            document.getElementById('branchStage').value = branch.stageId || '';
        }
    }
}

function deleteBranch(id) {
    if (confirm('هل أنت متأكد من حذف هذه الشعبة؟ سيتم فصل جميع الطلاب المرتبطين بها')) {
        db.deleteBranch(id);
        // Update students to remove branch reference
        const students = db.getStudents().filter(s => s.branchId === id);
        students.forEach(student => {
            db.updateStudent(student.id, { branchId: null });
        });
        loadBranches();
    }
}

// Staff modal functions
function openStaffModal(staffType) {
    document.getElementById('staffModal').classList.add('active');
    const typeNames = {
        'administrative': 'موظف إداري',
        'security': 'موظف أمني',
        'service': 'موظف خدمة'
    };
    document.getElementById('staffModalTitle').textContent = `إضافة ${typeNames[staffType]}`;
    document.getElementById('staffForm').reset();
    document.getElementById('staffId').value = '';
    document.getElementById('staffType').value = staffType;
}

function closeStaffModal() {
    document.getElementById('staffModal').classList.remove('active');
}

function editStaff(id, staffType) {
    let staff;
    switch(staffType) {
        case 'administrative':
            staff = db.getAdministrativeStaff().find(s => s.id === id);
            break;
        case 'security':
            staff = db.getSecurityStaff().find(s => s.id === id);
            break;
        case 'service':
            staff = db.getServiceStaff().find(s => s.id === id);
            break;
    }

    if (staff) {
        document.getElementById('staffModal').classList.add('active');
        const typeNames = {
            'administrative': 'موظف إداري',
            'security': 'موظف أمني',
            'service': 'موظف خدمة'
        };
        document.getElementById('staffModalTitle').textContent = `تعديل ${typeNames[staffType]}`;
        document.getElementById('staffId').value = staff.id;
        document.getElementById('staffType').value = staffType;
        document.getElementById('staffName').value = staff.name;
        document.getElementById('staffDepartment').value = staff.department;
        document.getElementById('staffPosition').value = staff.position || '';
        document.getElementById('staffEmail').value = staff.email;
        document.getElementById('staffPhone').value = staff.phone;
        document.getElementById('staffUsername').value = staff.username;
        document.getElementById('staffPassword').value = staff.password;
    }
}

function deleteStaff(id, staffType) {
    if (confirm('هل أنت متأكد من حذف هذا الموظف؟')) {
        switch(staffType) {
            case 'administrative':
                db.deleteAdministrativeStaff(id);
                break;
            case 'security':
                db.deleteSecurityStaff(id);
                break;
            case 'service':
                db.deleteServiceStaff(id);
                break;
        }
        loadStaff();
    }
}

function registerStaffFace(id, staffType) {
    localStorage.setItem('staffRegistrationTarget', JSON.stringify({ id, type: staffType }));
    window.location.href = 'staff-face-registration.html';
}

// Portal accounts (بوابة الدخول / بوابة التسجيل)
const portalTypeNames = {
    'gate': 'بوابة الدخول',
    'registration': 'بوابة التسجيل'
};

function loadPortalAccounts() {
    const tbody = document.getElementById('portalAccountsTableBody');
    tbody.innerHTML = '';

    const accounts = db.getUsers().filter(u => u.type === 'gate' || u.type === 'registration');

    accounts.forEach(account => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${account.name}</td>
            <td>${account.username}</td>
            <td>${account.password}</td>
            <td>${portalTypeNames[account.type]}</td>
            <td>
                <button class="btn btn-edit" onclick="editPortalAccount(${account.id})">تعديل</button>
                <button class="btn btn-delete" onclick="deletePortalAccount(${account.id})">حذف</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function openPortalAccountModal(portalType) {
    document.getElementById('portalAccountModal').classList.add('active');
    document.getElementById('portalAccountForm').reset();
    document.getElementById('portalAccountId').value = '';
    document.getElementById('portalAccountType').value = portalType;
    document.getElementById('portalAccountModalTitle').textContent = `إضافة حساب ${portalTypeNames[portalType]}`;
}

function closePortalAccountModal() {
    document.getElementById('portalAccountModal').classList.remove('active');
}

function editPortalAccount(id) {
    const account = db.getUsers().find(u => u.id === id);
    if (!account) return;

    document.getElementById('portalAccountModal').classList.add('active');
    document.getElementById('portalAccountModalTitle').textContent = `تعديل حساب ${portalTypeNames[account.type]}`;
    document.getElementById('portalAccountId').value = account.id;
    document.getElementById('portalAccountType').value = account.type;
    document.getElementById('portalAccountName').value = account.name;
    document.getElementById('portalAccountUsername').value = account.username;
    document.getElementById('portalAccountPassword').value = account.password;
}

function deletePortalAccount(id) {
    if (confirm('هل أنت متأكد من حذف هذا الحساب؟ لن يستطيع صاحبه دخول البوابة بعده.')) {
        db.deleteUser(id);
        loadPortalAccounts();
    }
}

document.getElementById('portalAccountForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const id = document.getElementById('portalAccountId').value;
    const accountData = {
        name: document.getElementById('portalAccountName').value.trim(),
        username: document.getElementById('portalAccountUsername').value.trim(),
        password: document.getElementById('portalAccountPassword').value.trim(),
        type: document.getElementById('portalAccountType').value,
        faceData: null
    };

    const taken = db.getUsers().some(u =>
        u.username.toLowerCase() === accountData.username.toLowerCase() && String(u.id) !== id
    );
    if (taken) {
        alert('اسم المستخدم مستخدم بالفعل، اختر اسمًا آخر.');
        return;
    }

    if (id) {
        db.updateUser(parseInt(id, 10), accountData);
    } else {
        db.addUser(accountData);
    }

    closePortalAccountModal();
    loadPortalAccounts();
});

// Student modal functions
function openStudentModal() {
    document.getElementById('studentModal').classList.add('active');
    document.getElementById('studentModalTitle').textContent = 'إضافة طالب جديد';
    document.getElementById('studentForm').reset();
    document.getElementById('studentId').value = '';

    // Populate classification dropdowns
    populateClassificationDropdowns();
}

function populateClassificationDropdowns() {
    // Populate department dropdown
    const departmentSelect = document.getElementById('studentDepartment');
    departmentSelect.innerHTML = '<option value="">-- اختر القسم --</option>';
    const departments = db.getDepartments();
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept.id;
        option.textContent = dept.name;
        departmentSelect.appendChild(option);
    });

    // Add onchange handler to update stages (only if not already set)
    if (!departmentSelect.onchange) {
        departmentSelect.onchange = function() {
            updateStudentStageOptions();
        };
    }

    // Populate stage dropdown
    updateStudentStageOptions();
}

function updateStudentStageOptions() {
    const departmentId = document.getElementById('studentDepartment').value;
    const stageSelect = document.getElementById('studentStage');
    stageSelect.innerHTML = '<option value="">-- اختر المرحلة --</option>';

    if (departmentId) {
        const stages = db.getStagesByDepartmentId(parseInt(departmentId));
        stages.forEach(stage => {
            const option = document.createElement('option');
            option.value = stage.id;
            option.textContent = stage.name;
            stageSelect.appendChild(option);
        });
    }
}

function closeStudentModal() {
    document.getElementById('studentModal').classList.remove('active');
}

function editStudent(id) {
    const student = db.getStudentById(id);
    if (student) {
        document.getElementById('studentModal').classList.add('active');
        document.getElementById('studentModalTitle').textContent = 'تعديل بيانات الطالب';
        document.getElementById('studentId').value = student.id;
        document.getElementById('studentName').value = student.name;
        document.getElementById('studentIdNumber').value = student.idNumber;
        document.getElementById('studentEmail').value = student.email;
        document.getElementById('studentPhone').value = student.phone;
        document.getElementById('studentUsername').value = student.username;
        document.getElementById('studentPassword').value = student.password;

        // Populate classification dropdowns first
        populateClassificationDropdowns();

        // Then set the selected values
        document.getElementById('studentDepartment').value = student.departmentId || '';
        updateStudentStageOptions();
        document.getElementById('studentStage').value = student.stageId || '';
        document.getElementById('studentBranch').value = student.branch || '';
    }
}

function deleteStudent(id) {
    if (confirm('هل أنت متأكد من حذف هذا الطالب؟')) {
        db.deleteStudent(id);
        loadStudents();
    }
}

// Teacher modal functions
function openTeacherModal() {
    document.getElementById('teacherModal').classList.add('active');
    document.getElementById('teacherModalTitle').textContent = 'إضافة مدرس جديد';
    document.getElementById('teacherForm').reset();
    document.getElementById('teacherId').value = '';

    // Populate classification dropdowns
    populateTeacherClassificationDropdowns();
}

function populateTeacherClassificationDropdowns() {
    // Populate department dropdown
    const departmentSelect = document.getElementById('teacherDepartment');
    departmentSelect.innerHTML = '<option value="">-- اختر القسم --</option>';
    const departments = db.getDepartments();
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept.id;
        option.textContent = dept.name;
        departmentSelect.appendChild(option);
    });

    // Add onchange handler to update stages (only if not already set)
    if (!departmentSelect.onchange) {
        departmentSelect.onchange = function() {
            updateTeacherStageOptions();
        };
    }

    // Populate stage dropdown
    updateTeacherStageOptions();
}

function updateTeacherStageOptions() {
    const departmentId = document.getElementById('teacherDepartment').value;
    const stageSelect = document.getElementById('teacherStage');
    stageSelect.innerHTML = '<option value="">-- اختر المرحلة --</option>';

    if (departmentId) {
        const stages = db.getStagesByDepartmentId(parseInt(departmentId));
        stages.forEach(stage => {
            const option = document.createElement('option');
            option.value = stage.id;
            option.textContent = stage.name;
            stageSelect.appendChild(option);
        });
    }
}

function closeTeacherModal() {
    document.getElementById('teacherModal').classList.remove('active');
}

function editTeacher(id) {
    const teacher = db.getTeacherById(id);
    if (teacher) {
        document.getElementById('teacherModal').classList.add('active');
        document.getElementById('teacherModalTitle').textContent = 'تعديل بيانات المدرس';
        document.getElementById('teacherId').value = teacher.id;
        document.getElementById('teacherName').value = teacher.name;
        document.getElementById('teacherSpecialization').value = teacher.specialization;
        document.getElementById('teacherSubject').value = teacher.subject || '';
        document.getElementById('teacherEmail').value = teacher.email;
        document.getElementById('teacherPhone').value = teacher.phone;
        document.getElementById('teacherUsername').value = teacher.username;
        document.getElementById('teacherPassword').value = teacher.password;

        // Populate classification dropdowns first
        populateTeacherClassificationDropdowns();

        // Then set the selected values
        document.getElementById('teacherDepartment').value = teacher.departmentId || '';
        updateTeacherStageOptions();
        document.getElementById('teacherStage').value = teacher.stageId || '';
        document.getElementById('teacherBranch').value = teacher.branch || '';
    }
}

function deleteTeacher(id) {
    if (confirm('هل أنت متأكد من حذف هذا المدرس؟')) {
        db.deleteTeacher(id);
        loadTeachers();
    }
}

// Schedule modal functions
function openScheduleModal() {
    document.getElementById('scheduleModal').classList.add('active');
    document.getElementById('scheduleModalTitle').textContent = 'إضافة محاضرة';
    document.getElementById('scheduleForm').reset();
    document.getElementById('scheduleId').value = '';

    // Populate classification dropdowns
    populateScheduleClassificationDropdowns();

    // Populate teacher select
    updateTeacherSelect();
}

function populateScheduleClassificationDropdowns() {
    // Populate department dropdown
    const departmentSelect = document.getElementById('scheduleDepartment');
    departmentSelect.innerHTML = '<option value="">-- اختر القسم --</option>';
    const departments = db.getDepartments();
    departments.forEach(dept => {
        const option = document.createElement('option');
        option.value = dept.id;
        option.textContent = dept.name;
        departmentSelect.appendChild(option);
    });

    // Add onchange handler to update stages (only if not already set)
    if (!departmentSelect.onchange) {
        departmentSelect.onchange = function() {
            updateScheduleStageOptions();
            updateTeacherSelect();
        };
    }

    // Populate stage dropdown
    updateScheduleStageOptions();

    // Add onchange handler to update teacher select (only if not already set)
    const stageSelect = document.getElementById('scheduleStage');
    if (!stageSelect.onchange) {
        stageSelect.onchange = function() {
            updateTeacherSelect();
        };
    }
}

function updateScheduleStageOptions() {
    const departmentId = document.getElementById('scheduleDepartment').value;
    const stageSelect = document.getElementById('scheduleStage');
    stageSelect.innerHTML = '<option value="">-- اختر المرحلة --</option>';

    if (departmentId) {
        const stages = db.getStagesByDepartmentId(parseInt(departmentId));
        stages.forEach(stage => {
            const option = document.createElement('option');
            option.value = stage.id;
            option.textContent = stage.name;
            stageSelect.appendChild(option);
        });
    }
}

function closeScheduleModal() {
    document.getElementById('scheduleModal').classList.remove('active');
}

function editSchedule(id) {
    const schedule = db.getSchedule();
    const item = schedule.find(s => s.id === id);
    if (item) {
        document.getElementById('scheduleModal').classList.add('active');
        document.getElementById('scheduleModalTitle').textContent = 'تعديل المحاضرة';
        document.getElementById('scheduleId').value = item.id;
        document.getElementById('scheduleDay').value = item.day;
        document.getElementById('scheduleTime').value = item.time;
        document.getElementById('scheduleSubject').value = item.subject;

        // Populate classification dropdowns first
        populateScheduleClassificationDropdowns();

        // Then set the selected values
        document.getElementById('scheduleDepartment').value = item.departmentId || '';
        updateScheduleStageOptions();
        document.getElementById('scheduleStage').value = item.stageId || '';
        document.getElementById('scheduleBranch').value = item.branch || '';

        // Populate teacher select
        updateTeacherSelect();
        document.getElementById('scheduleTeacher').value = item.teacherId;
    }
}

function deleteSchedule(id) {
    if (confirm('هل أنت متأكد من حذف هذه المحاضرة؟')) {
        db.deleteScheduleItem(id);
        loadSchedule();
    }
}

// Face registration function
function registerFace(id, type) {
    // Store the ID and type for the face registration page
    localStorage.setItem('faceRegistrationTarget', JSON.stringify({ id, type }));
    window.location.href = 'face-registration.html';
}

// Form submissions
document.getElementById('studentForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const studentData = {
        name: document.getElementById('studentName').value,
        idNumber: document.getElementById('studentIdNumber').value,
        departmentId: document.getElementById('studentDepartment').value ? parseInt(document.getElementById('studentDepartment').value) : null,
        stageId: document.getElementById('studentStage').value ? parseInt(document.getElementById('studentStage').value) : null,
        branch: document.getElementById('studentBranch').value,
        email: document.getElementById('studentEmail').value,
        phone: document.getElementById('studentPhone').value,
        username: document.getElementById('studentUsername').value,
        password: document.getElementById('studentPassword').value,
        faceData: null
    };

    const studentId = document.getElementById('studentId').value;

    if (studentId) {
        // Update existing student
        db.updateStudent(parseInt(studentId), studentData);
        // Also update user account
        const student = db.getStudentById(parseInt(studentId));
        const users = db.getUsers();
        const userIndex = users.findIndex(u => u.studentId === student.id);
        if (userIndex !== -1) {
            db.updateUser(users[userIndex].id, {
                username: studentData.username,
                password: studentData.password,
                name: studentData.name
            });
        }
    } else {
        // Add new student
        const newStudent = db.addStudent(studentData);
        // Create user account
        db.addUser({
            username: studentData.username,
            password: studentData.password,
            type: 'student',
            name: studentData.name,
            faceData: null,
            studentId: newStudent.id
        });
    }

    closeStudentModal();
    loadStudents();
});

document.getElementById('teacherForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const teacherData = {
        name: document.getElementById('teacherName').value,
        specialization: document.getElementById('teacherSpecialization').value,
        subject: document.getElementById('teacherSubject').value,
        departmentId: document.getElementById('teacherDepartment').value ? parseInt(document.getElementById('teacherDepartment').value) : null,
        stageId: document.getElementById('teacherStage').value ? parseInt(document.getElementById('teacherStage').value) : null,
        branch: document.getElementById('teacherBranch').value,
        email: document.getElementById('teacherEmail').value,
        phone: document.getElementById('teacherPhone').value,
        username: document.getElementById('teacherUsername').value,
        password: document.getElementById('teacherPassword').value,
        faceData: null
    };

    const teacherId = document.getElementById('teacherId').value;

    if (teacherId) {
        // Update existing teacher
        db.updateTeacher(parseInt(teacherId), teacherData);
        // Also update user account
        const teacher = db.getTeacherById(parseInt(teacherId));
        const users = db.getUsers();
        const userIndex = users.findIndex(u => u.teacherId === teacher.id);
        if (userIndex !== -1) {
            db.updateUser(users[userIndex].id, {
                username: teacherData.username,
                password: teacherData.password,
                name: teacherData.name
            });
        }
    } else {
        // Add new teacher
        const newTeacher = db.addTeacher(teacherData);
        // Create user account
        db.addUser({
            username: teacherData.username,
            password: teacherData.password,
            type: 'teacher',
            name: teacherData.name,
            faceData: null,
            teacherId: newTeacher.id
        });
    }

    closeTeacherModal();
    loadTeachers();
});

document.getElementById('scheduleForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const scheduleData = {
        day: document.getElementById('scheduleDay').value,
        time: document.getElementById('scheduleTime').value,
        subject: document.getElementById('scheduleSubject').value,
        departmentId: document.getElementById('scheduleDepartment').value ? parseInt(document.getElementById('scheduleDepartment').value) : null,
        stageId: document.getElementById('scheduleStage').value ? parseInt(document.getElementById('scheduleStage').value) : null,
        branch: document.getElementById('scheduleBranch').value,
        teacherId: parseInt(document.getElementById('scheduleTeacher').value)
    };

    const scheduleId = document.getElementById('scheduleId').value;

    if (scheduleId) {
        db.updateScheduleItem(parseInt(scheduleId), scheduleData);
    } else {
        db.addScheduleItem(scheduleData);
    }

    closeScheduleModal();
    loadSchedule();
});

// Staff form submission
document.getElementById('staffForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const staffData = {
        name: document.getElementById('staffName').value,
        department: document.getElementById('staffDepartment').value,
        position: document.getElementById('staffPosition').value,
        email: document.getElementById('staffEmail').value,
        phone: document.getElementById('staffPhone').value,
        username: document.getElementById('staffUsername').value,
        password: document.getElementById('staffPassword').value,
        faceData: null
    };

    const staffId = document.getElementById('staffId').value;
    const staffType = document.getElementById('staffType').value;

    if (staffId) {
        // Update existing staff
        switch(staffType) {
            case 'administrative':
                db.updateAdministrativeStaff(parseInt(staffId), staffData);
                break;
            case 'security':
                db.updateSecurityStaff(parseInt(staffId), staffData);
                break;
            case 'service':
                db.updateServiceStaff(parseInt(staffId), staffData);
                break;
        }
        // Also update user account
        const users = db.getUsers();
        const userIndex = users.findIndex(u => u.staffId === parseInt(staffId) && u.staffType === staffType);
        if (userIndex !== -1) {
            db.updateUser(users[userIndex].id, {
                username: staffData.username,
                password: staffData.password,
                name: staffData.name
            });
        }
    } else {
        // Add new staff
        let newStaff;
        switch(staffType) {
            case 'administrative':
                newStaff = db.addAdministrativeStaff(staffData);
                break;
            case 'security':
                newStaff = db.addSecurityStaff(staffData);
                break;
            case 'service':
                newStaff = db.addServiceStaff(staffData);
                break;
        }
        // Create user account
        const typeNames = {
            'administrative': 'administrative',
            'security': 'security',
            'service': 'service'
        };
        db.addUser({
            username: staffData.username,
            password: staffData.password,
            type: typeNames[staffType],
            name: staffData.name,
            faceData: null,
            staffId: newStaff.id,
            staffType: staffType
        });
    }

    closeStaffModal();
    loadStaff();
});

// Department form submission
document.getElementById('departmentForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const departmentId = document.getElementById('departmentId').value;

    // Collect selected stage IDs
    const selectedStageIds = [];
    document.querySelectorAll('.stage-checkbox:checked').forEach(checkbox => {
        selectedStageIds.push(parseInt(checkbox.value));
    });

    const departmentData = {
        name: document.getElementById('departmentName').value,
        description: document.getElementById('departmentDescription').value,
        stageIds: selectedStageIds
    };

    if (departmentId) {
        db.updateDepartment(parseInt(departmentId), departmentData);
    } else {
        db.addDepartment(departmentData);
    }

    closeDepartmentModal();
    loadDepartments();
});

// Stage form submission
document.getElementById('stageForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const stageId = document.getElementById('stageId').value;

    const stageData = {
        departmentId: document.getElementById('stageDepartment').value ? parseInt(document.getElementById('stageDepartment').value) : null,
        name: document.getElementById('stageName').value,
        description: document.getElementById('stageDescription').value
    };

    if (stageId) {
        db.updateStage(parseInt(stageId), stageData);
    } else {
        db.addStage(stageData);
    }

    closeStageModal();
    loadStages();
});

// Branch form submission
document.getElementById('branchForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const branchId = document.getElementById('branchId').value;

    const branchData = {
        stageId: document.getElementById('branchStage').value ? parseInt(document.getElementById('branchStage').value) : null,
        name: document.getElementById('branchName').value,
        description: document.getElementById('branchDescription').value
    };

    if (branchId) {
        db.updateBranch(parseInt(branchId), branchData);
    } else {
        db.addBranch(branchData);
    }

    closeBranchModal();
    loadBranches();
});

// ==================== User Management Functions ====================

let allUsers = [];

async function loadUsers() {
    try {
        const response = await fetch('/api/users/', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            }
        });

        if (!response.ok) {
            console.error('Failed to load users');
            return;
        }

        const data = await response.json();
        allUsers = data.results || data;

        // Apply filters
        const typeFilter = document.getElementById('userTypeFilter').value;
        const statusFilter = document.getElementById('userStatusFilter').value;

        let filteredUsers = allUsers;

        if (typeFilter) {
            filteredUsers = filteredUsers.filter(user => user.user_type === typeFilter);
        }

        if (statusFilter) {
            filteredUsers = filteredUsers.filter(user =>
                statusFilter === 'active' ? user.is_active : !user.is_active
            );
        }

        renderUsersTable(filteredUsers);
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function renderUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    tbody.innerHTML = '';

    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">لا يوجد مستخدمين</td></tr>';
        return;
    }

    users.forEach(user => {
        const row = document.createElement('tr');
        const typeLabels = {
            'student': 'طالب',
            'teacher': 'مدرس',
            'administrative': 'موظف إداري',
            'security': 'موظف أمني',
            'service': 'موظف خدمة',
            'gate': 'بوابة',
            'registration': 'قسم التسجيل',
            'admin': 'مشرف'
        };

        row.innerHTML = `
            <td>${escapeHtml(user.name)}</td>
            <td>${typeLabels[user.user_type] || user.user_type}</td>
            <td>${escapeHtml(user.code || '-')}</td>
            <td>${escapeHtml(user.department_name || '-')}</td>
            <td>
                <span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
                    ${user.is_active ? 'نشط' : 'غير نشط'}
                </span>
            </td>
            <td>${new Date(user.created_at).toLocaleDateString('ar-EG')}</td>
            <td>
                <button class="btn btn-add" onclick="editUser(${user.id})">تعديل</button>
                <button class="btn btn-delete" onclick="toggleUserStatus(${user.id})">
                    ${user.is_active ? 'تعطيل' : 'تفعيل'}
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function searchUsers() {
    const searchTerm = document.getElementById('userSearchInput').value.toLowerCase();
    if (!searchTerm) {
        loadUsers();
        return;
    }

    const filteredUsers = allUsers.filter(user =>
        user.name.toLowerCase().includes(searchTerm) ||
        (user.code && user.code.toLowerCase().includes(searchTerm)) ||
        (user.email && user.email.toLowerCase().includes(searchTerm))
    );

    renderUsersTable(filteredUsers);
}

function openUserModal(userId = null) {
    const modal = document.getElementById('userModal');
    const title = document.getElementById('userModalTitle');
    const form = document.getElementById('userForm');

    form.reset();
    document.getElementById('userId').value = '';

    if (userId) {
        title.textContent = 'تعديل المستخدم';
        const user = allUsers.find(u => u.id === userId);
        if (user) {
            document.getElementById('userId').value = user.id;
            document.getElementById('userName').value = user.name;
            document.getElementById('userType').value = user.user_type;
            document.getElementById('userCode').value = user.code || '';
            document.getElementById('userEmail').value = user.email || '';
            document.getElementById('userPhone').value = user.phone || '';
            document.getElementById('userDepartment').value = user.department || '';
            document.getElementById('userStage').value = user.stage || '';
            document.getElementById('userBranch').value = user.branch || '';
            document.getElementById('userUsername').value = user.username;
            document.getElementById('userStatus').value = user.is_active ? 'active' : 'inactive';
        }
    } else {
        title.textContent = 'إضافة مستخدم جديد';
    }

    modal.style.display = 'block';
    loadDepartmentsSelect();
}

function closeUserModal() {
    document.getElementById('userModal').style.display = 'none';
}

async function editUser(userId) {
    openUserModal(userId);
}

async function toggleUserStatus(userId) {
    if (!confirm('هل أنت متأكد من تغيير حالة هذا المستخدم؟')) {
        return;
    }

    try {
        const user = allUsers.find(u => u.id === userId);
        const newStatus = !user.is_active;

        const response = await fetch(`/api/users/${userId}/${newStatus ? 'reactivate' : 'deactivate'}/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            }
        });

        if (response.ok) {
            alert('تم تغيير حالة المستخدم بنجاح');
            loadUsers();
        } else {
            alert('تعذّر تغيير حالة المستخدم');
        }
    } catch (error) {
        console.error('Error toggling user status:', error);
        alert('حدث خطأ أثناء تغيير حالة المستخدم');
    }
}

async function loadDepartmentsSelect() {
    const select = document.getElementById('userDepartment');
    try {
        const response = await fetch('/api/departments/', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            const departments = data.results || data;
            select.innerHTML = '<option value="">-- اختر القسم --</option>' +
                departments.map(dept => `<option value="${dept.id}">${dept.name}</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading departments:', error);
    }
}

// User form submission
document.getElementById('userForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const userId = document.getElementById('userId').value;
    const userData = {
        name: document.getElementById('userName').value,
        user_type: document.getElementById('userType').value,
        code: document.getElementById('userCode').value,
        email: document.getElementById('userEmail').value,
        phone: document.getElementById('userPhone').value,
        department: document.getElementById('userDepartment').value || null,
        stage: document.getElementById('userStage').value || null,
        branch: document.getElementById('userBranch').value || null,
        username: document.getElementById('userUsername').value,
        is_active: document.getElementById('userStatus').value === 'active'
    };

    const password = document.getElementById('userPassword').value;
    if (password) {
        userData.password = password;
    }

    try {
        let response;
        if (userId) {
            response = await fetch(`/api/users/${userId}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
                },
                body: JSON.stringify(userData)
            });
        } else {
            if (!password) {
                alert('كلمة المرور مطلوبة للمستخدمين الجدد');
                return;
            }
            response = await fetch('/api/users/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
                },
                body: JSON.stringify(userData)
            });
        }

        if (response.ok) {
            alert(userId ? 'تم تحديث المستخدم بنجاح' : 'تم إضافة المستخدم بنجاح');
            closeUserModal();
            loadUsers();
        } else {
            const error = await response.json();
            alert('حدث خطأ: ' + (error.error || error.detail || 'فشل العملية'));
        }
    } catch (error) {
        console.error('Error saving user:', error);
        alert('حدث خطأ أثناء حفظ المستخدم');
    }
});

// Initialize
(async () => {
    await loadOverview();
})();