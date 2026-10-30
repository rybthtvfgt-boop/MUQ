// API Client for Django REST Framework
// Configure this based on your backend URL
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000/api'
    : window.location.origin + '/api'; // Use same origin for production

// SECURITY NOTE: JWT tokens are stored in localStorage for simplicity.
// Alternative approach: Use HttpOnly cookies with CSRF protection for better security.
// Trade-off: localStorage is vulnerable to XSS but easier to implement.
// Cookies with HttpOnly are immune to XSS but require CSRF token management.
// Current implementation mitigates XSS risk with proper HTML escaping in dashboards.

class APIClient {
    constructor() {
        this.accessToken = localStorage.getItem('accessToken');
        this.refreshToken = localStorage.getItem('refreshToken');
        this.requestQueue = [];
        this.isProcessingQueue = false;
        this.lastRequestTime = 0;
        this.minRequestInterval = 200; // 200ms between requests (5 requests per second)
    }

    async request(endpoint, options = {}) {
        return new Promise((resolve, reject) => {
            this.requestQueue.push({ endpoint, options, resolve, reject });
            this.processQueue();
        });
    }

    async processQueue() {
        if (this.isProcessingQueue || this.requestQueue.length === 0) {
            return;
        }

        this.isProcessingQueue = true;

        while (this.requestQueue.length > 0) {
            const { endpoint, options, resolve, reject } = this.requestQueue.shift();

            // Rate limiting: wait if needed
            const now = Date.now();
            const timeSinceLastRequest = now - this.lastRequestTime;
            if (timeSinceLastRequest < this.minRequestInterval) {
                await new Promise(r => setTimeout(r, this.minRequestInterval - timeSinceLastRequest));
            }

            try {
                const response = await this.executeRequest(endpoint, options);
                this.lastRequestTime = Date.now();

                // Handle rate limiting (429)
                if (response.status === 429) {
    
                    await new Promise(r => setTimeout(r, 5000));
                    const retryResponse = await this.executeRequest(endpoint, options);
                    resolve(retryResponse);
                } else {
                    resolve(response);
                }
            } catch (error) {
                reject(error);
            }
        }

        this.isProcessingQueue = false;
    }

    async executeRequest(endpoint, options) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        const response = await fetch(url, {
            ...options,
            headers,
        });

        if (response.status === 401) {
            // Try to refresh token
            const refreshed = await this.refreshAccessToken();
            if (refreshed) {
                headers['Authorization'] = `Bearer ${this.accessToken}`;
                return fetch(url, { ...options, headers });
            }
        }

        return response;
    }

    async refreshAccessToken() {
        if (!this.refreshToken) {
            this.logout();
            return false;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: this.refreshToken }),
            });

            if (response.ok) {
                const data = await response.json();
                this.accessToken = data.access;
                localStorage.setItem('accessToken', data.access);
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error);
        }

        this.logout();
        return false;
    }

    async login(username, password) {
        const response = await fetch(`${API_BASE_URL}/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        if (response.ok) {
            const data = await response.json();
            this.accessToken = data.access;
            this.refreshToken = data.refresh;
            localStorage.setItem('accessToken', data.access);
            localStorage.setItem('refreshToken', data.refresh);
            localStorage.setItem('currentUser', JSON.stringify(data.user));
            return { success: true, user: data.user };
        }

        const error = await response.json();
        return { success: false, error: error.error || 'Login failed' };
    }

    async logout() {
        try {
            await this.request('/auth/logout/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: this.refreshToken }),
            });
        } catch (error) {
            console.error('Logout error:', error);
        }

        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('currentUser');
    }

    async getCurrentUser() {
        const response = await this.request('/auth/me/');
        if (response.ok) {
            return await response.json();
        }
        return null;
    }

    // Users
    async getUsers() {
        const response = await this.request('/users/');
        if (response.ok) {
            const data = await response.json();
            return data.results || data;
        }
        return [];
    }

    async getStudents() {
        // Filter users with student type
        const users = await this.getUsers();
        return users.filter(user => user.user_type === 'student');
    }

    async createUser(userData) {
        const response = await this.request('/users/', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
        if (response.ok) {
            return await response.json();
        }
        const error = await response.json();
        throw new Error(error.error || 'Failed to create user');
    }

    async updateUser(userId, userData) {
        const response = await this.request(`/users/${userId}/`, {
            method: 'PATCH',
            body: JSON.stringify(userData),
        });
        if (response.ok) {
            return await response.json();
        }
        const error = await response.json();
        throw new Error(error.error || 'Failed to update user');
    }

    async deleteUser(userId) {
        const response = await this.request(`/users/${userId}/`, {
            method: 'DELETE',
        });
        return response.ok;
    }

    // Departments
    async getDepartments() {
        const response = await this.request('/departments/');
        if (response.ok) {
            const data = await response.json();
            return data.results || data;
        }
        return [];
    }

    async createDepartment(departmentData) {
        const response = await this.request('/departments/', {
            method: 'POST',
            body: JSON.stringify(departmentData),
        });
        if (response.ok) {
            return await response.json();
        }
        const error = await response.json();
        throw new Error(error.error || 'Failed to create department');
    }

    async updateDepartment(departmentId, departmentData) {
        const response = await this.request(`/departments/${departmentId}/`, {
            method: 'PATCH',
            body: JSON.stringify(departmentData),
        });
        if (response.ok) {
            return await response.json();
        }
        const error = await response.json();
        throw new Error(error.error || 'Failed to update department');
    }

    async deleteDepartment(departmentId) {
        const response = await this.request(`/departments/${departmentId}/`, {
            method: 'DELETE',
        });
        return response.ok;
    }

    // Stages
    async getStages() {
        const response = await this.request('/stages/');
        if (response.ok) {
            const data = await response.json();
            return data.results || data;
        }
        return [];
    }

    async createStage(stageData) {
        const response = await this.request('/stages/', {
            method: 'POST',
            body: JSON.stringify(stageData),
        });
        if (response.ok) {
            return await response.json();
        }
        const error = await response.json();
        throw new Error(error.error || 'Failed to create stage');
    }

    async updateStage(stageId, stageData) {
        const response = await this.request(`/stages/${stageId}/`, {
            method: 'PATCH',
            body: JSON.stringify(stageData),
        });
        if (response.ok) {
            return await response.json();
        }
        const error = await response.json();
        throw new Error(error.error || 'Failed to update stage');
    }

    async deleteStage(stageId) {
        const response = await this.request(`/stages/${stageId}/`, {
            method: 'DELETE',
        });
        return response.ok;
    }

    // Branches
    async getBranches() {
        const response = await this.request('/branches/');
        if (response.ok) {
            const data = await response.json();
            return data.results || data;
        }
        return [];
    }

    async createBranch(branchData) {
        const response = await this.request('/branches/', {
            method: 'POST',
            body: JSON.stringify(branchData),
        });
        if (response.ok) {
            return await response.json();
        }
        const error = await response.json();
        throw new Error(error.error || 'Failed to create branch');
    }

    async updateBranch(branchId, branchData) {
        const response = await this.request(`/branches/${branchId}/`, {
            method: 'PATCH',
            body: JSON.stringify(branchData),
        });
        if (response.ok) {
            return await response.json();
        }
        const error = await response.json();
        throw new Error(error.error || 'Failed to update branch');
    }

    async deleteBranch(branchId) {
        const response = await this.request(`/branches/${branchId}/`, {
            method: 'DELETE',
        });
        return response.ok;
    }

    // Attendance
    async getAttendance() {
        const response = await this.request('/attendance/');
        if (response.ok) {
            const data = await response.json();
            return data.results || data;
        }
        return [];
    }

    async createAttendance(attendanceData) {
        const response = await this.request('/attendance/', {
            method: 'POST',
            body: JSON.stringify(attendanceData),
        });
        if (response.ok) {
            return await response.json();
        }
        const error = await response.json();
        throw new Error(error.error || 'Failed to create attendance record');
    }

    async updateAttendance(attendanceId, attendanceData) {
        const response = await this.request(`/attendance/${attendanceId}/`, {
            method: 'PATCH',
            body: JSON.stringify(attendanceData),
        });
        if (response.ok) {
            return await response.json();
        }
        const error = await response.json();
        throw new Error(error.error || 'Failed to update attendance');
    }

    async deleteAttendance(attendanceId) {
        const response = await this.request(`/attendance/${attendanceId}/`, {
            method: 'DELETE',
        });
        return response.ok;
    }

    // Schedule
    async getSchedule() {
        const response = await this.request('/schedule/');
        if (response.ok) {
            const data = await response.json();
            return data.results || data;
        }
        return [];
    }

    async createScheduleItem(scheduleData) {
        const response = await this.request('/schedule/', {
            method: 'POST',
            body: JSON.stringify(scheduleData),
        });
        if (response.ok) {
            return await response.json();
        }
        const error = await response.json();
        throw new Error(error.error || 'Failed to create schedule item');
    }

    async updateScheduleItem(scheduleId, scheduleData) {
        const response = await this.request(`/schedule/${scheduleId}/`, {
            method: 'PATCH',
            body: JSON.stringify(scheduleData),
        });
        if (response.ok) {
            return await response.json();
        }
        const error = await response.json();
        throw new Error(error.error || 'Failed to update schedule');
    }

    async deleteScheduleItem(scheduleId) {
        const response = await this.request(`/schedule/${scheduleId}/`, {
            method: 'DELETE',
        });
        return response.ok;
    }

    // Face Profiles
    async getFaceProfiles() {
        const response = await this.request('/face-profiles/');
        if (response.ok) {
            const data = await response.json();
            return data.results || data;
        }
        return [];
    }

    async createFaceProfile(profileData) {
        const response = await this.request('/face-profiles/', {
            method: 'POST',
            body: JSON.stringify(profileData),
        });
        if (response.ok) {
            return await response.json();
        }
        const error = await response.json();
        throw new Error(error.error || 'Failed to create face profile');
    }

    async updateFaceProfile(profileId, profileData) {
        const response = await this.request(`/face-profiles/${profileId}/`, {
            method: 'PATCH',
            body: JSON.stringify(profileData),
        });
        if (response.ok) {
            return await response.json();
        }
        const error = await response.json();
        throw new Error(error.error || 'Failed to update face profile');
    }

    async deleteFaceProfile(profileId) {
        const response = await this.request(`/face-profiles/${profileId}/`, {
            method: 'DELETE',
        });
        return response.ok;
    }
}

const api = new APIClient();
