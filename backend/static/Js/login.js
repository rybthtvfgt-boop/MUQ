// Login with API Client
const HOME_BY_TYPE = {
    admin: 'admin-dashboard.html',
    teacher: 'teacher-dashboard.html',
    student: 'student-dashboard.html',
    administrative: 'staff-dashboard.html',
    security: 'staff-dashboard.html',
    service: 'staff-dashboard.html',
    gate: 'gate-entry.html',
    registration: 'face-registration-new.html'
};

const PORTALS = {
    gate: { label: 'بوابة الدخول', page: 'gate-entry.html' },
    registration: { label: 'بوابة التسجيل', page: 'face-registration-new.html' }
};

function getQueryParam(name) {
    return new URLSearchParams(window.location.search).get(name);
}

function canOpenPortal(user, portalKey) {
    return user.user_type === portalKey || user.user_type === 'admin';
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
}

// البوابة المطلوبة عبر ?next= — تُتجاهل أي قيمة غير معروفة لمنع إعادة التوجيه الخارجية
const requestedPortalKey = PORTALS[getQueryParam('next')] ? getQueryParam('next') : null;

if (requestedPortalKey) {
    document.getElementById('userType').value = requestedPortalKey;
}

// Login form handler
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const userType = document.getElementById('userType').value;

    showError('جاري تسجيل الدخول...');

    try {
        const result = await api.login(username, password);

        if (!result.success) {
            showError(result.error || 'اسم المستخدم أو كلمة المرور غير صحيحة');
            return;
        }

        const user = result.user;

        // Verify user type matches selection (skip for admin)
        if (userType !== 'admin' && user.user_type !== userType) {
            await api.logout();
            showError('نوع المستخدم غير مطابق. هذا الحساب هو: ' + user.user_type);
            return;
        }

        if (requestedPortalKey && !canOpenPortal(user, requestedPortalKey)) {
            await api.logout();
            showError(`هذا الحساب غير مخوّل بفتح ${PORTALS[requestedPortalKey].label}.`);
            return;
        }

        // Redirect based on actual user type from server, not form selection
        const targetPage = requestedPortalKey ? PORTALS[requestedPortalKey].page : HOME_BY_TYPE[user.user_type];
        if (targetPage) {
            window.location.href = targetPage;
        } else {
            showError('نوع المستخدم غير معروف: ' + user.user_type);
            await api.logout();
        }
    } catch (error) {
        console.error('Login error:', error);
        showError('حدث خطأ أثناء تسجيل الدخول. تأكد من تشغيل السيرفر.');
    }
});

// Check if user is already logged in
window.addEventListener('load', async function() {
    const deniedParam = getQueryParam('denied');

    if (PORTALS[deniedParam]) {
        showError(`حسابك الحالي غير مخوّل بفتح ${PORTALS[deniedParam].label}. سجّل الدخول بحساب آخر.`);
        return;
    }

    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) return;

    if (requestedPortalKey) {
        try {
            const user = await api.getCurrentUser();
            if (user && canOpenPortal(user, requestedPortalKey)) {
                window.location.href = PORTALS[requestedPortalKey].page;
            } else {
                await api.logout();
                showError(`حسابك الحالي غير مخوّل بفتح ${PORTALS[requestedPortalKey].label}. سجّل الدخول بحساب آخر.`);
            }
        } catch (error) {
            await api.logout();
        }
        return;
    }

    try {
        const user = await api.getCurrentUser();
        if (user && HOME_BY_TYPE[user.user_type]) {
            window.location.href = HOME_BY_TYPE[user.user_type];
        } else if (user) {
            await api.logout();
            showError('نوع المستخدم غير معروف: ' + user.user_type);
        }
    } catch (error) {
        await api.logout();
    }
});
