// Authentication check for all protected pages
async function checkAuth(requiredType = null) {
    const accessToken = localStorage.getItem('accessToken');

    if (!accessToken) {
        window.location.href = 'login.html';
        return false;
    }

    try {
        const user = await api.getCurrentUser();
        if (!user) {
            await api.logout();
            window.location.href = 'login.html';
            return false;
        }

        // Check if user type matches required type
        if (requiredType && user.user_type !== requiredType && user.user_type !== 'admin') {
            alert('ليس لديك صلاحية للوصول إلى هذه الصفحة');
            window.location.href = 'login.html';
            return false;
        }

        // Store current user
        localStorage.setItem('currentUser', JSON.stringify(user));
        return user;
    } catch (error) {
        console.error('Auth check failed:', error);
        await api.logout();
        window.location.href = 'login.html';
        return false;
    }
}

// Get current user from localStorage
function getCurrentUser() {
    const raw = localStorage.getItem('currentUser');
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch (e) {
        return null;
    }
}

// Logout function
async function logout() {
    await api.logout();
    window.location.href = 'login.html';
}

// Run auth check on page load
document.addEventListener('DOMContentLoaded', async function() {
    const requiredType = document.body.getAttribute('data-required-type');
    if (requiredType) {
        await checkAuth(requiredType);
    }
});
