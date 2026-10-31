// Database compatibility layer
// This file provides backward compatibility for existing HTML pages
// It wraps the Django API client (api-client.js) to maintain the old interface

// Import the API client functionality
// The api-client.js must be loaded before this file

class Database {
    constructor() {
        this.api = window.api;
    }

    // Ensure api is available
    checkApi() {
        if (!this.api) {
            console.error('API client not loaded. Make sure api-client.js is loaded before database.js');
            return false;
        }
        return true;
    }

    // Users
    async getUsers() {
        if (!this.checkApi()) return [];
        return await this.api.getUsers();
    }

    async getStudents() {
        if (!this.checkApi()) return [];
        return await this.api.getStudents();
    }

    async getTeachers() {
        const users = await this.api.getUsers();
        return users.filter(user => user.user_type === 'teacher');
    }

    async getAdministrativeStaff() {
        const users = await this.api.getUsers();
        return users.filter(user => user.user_type === 'administrative');
    }

    async getSecurityStaff() {
        const users = await this.api.getUsers();
        return users.filter(user => user.user_type === 'security');
    }

    async getServiceStaff() {
        const users = await this.api.getUsers();
        return users.filter(user => user.user_type === 'service');
    }

    async createUser(userData) {
        if (!this.checkApi()) return null;
        return await this.api.createUser(userData);
    }

    async updateUser(userId, userData) {
        if (!this.checkApi()) return null;
        return await this.api.updateUser(userId, userData);
    }

    async deleteUser(userId) {
        if (!this.checkApi()) return false;
        return await this.api.deleteUser(userId);
    }

    async addUser(userData) {
        // Alias for createUser for backward compatibility
        return await this.createUser(userData);
    }

    // Departments
    async getDepartments() {
        if (!this.checkApi()) return [];
        return await this.api.getDepartments();
    }

    async createDepartment(departmentData) {
        if (!this.checkApi()) return null;
        return await this.api.createDepartment(departmentData);
    }

    async updateDepartment(departmentId, departmentData) {
        if (!this.checkApi()) return null;
        return await this.api.updateDepartment(departmentId, departmentData);
    }

    async deleteDepartment(departmentId) {
        if (!this.checkApi()) return false;
        return await this.api.deleteDepartment(departmentId);
    }

    async addDepartment(departmentData) {
        // Alias for createDepartment for backward compatibility
        return await this.createDepartment(departmentData);
    }

    // Stages
    async getStages() {
        if (!this.checkApi()) return [];
        return await this.api.getStages();
    }

    async createStage(stageData) {
        if (!this.checkApi()) return null;
        return await this.api.createStage(stageData);
    }

    async updateStage(stageId, stageData) {
        if (!this.checkApi()) return null;
        return await this.api.updateStage(stageId, stageData);
    }

    async deleteStage(stageId) {
        if (!this.checkApi()) return false;
        return await this.api.deleteStage(stageId);
    }

    // Branches
    async getBranches() {
        if (!this.checkApi()) return [];
        return await this.api.getBranches();
    }

    async createBranch(branchData) {
        if (!this.checkApi()) return null;
        return await this.api.createBranch(branchData);
    }

    async updateBranch(branchId, branchData) {
        if (!this.checkApi()) return null;
        return await this.api.updateBranch(branchId, branchData);
    }

    async deleteBranch(branchId) {
        if (!this.checkApi()) return false;
        return await this.api.deleteBranch(branchId);
    }

    // Attendance
    async getAttendance() {
        if (!this.checkApi()) return [];
        return await this.api.getAttendance();
    }

    async createAttendance(attendanceData) {
        if (!this.checkApi()) return null;
        return await this.api.createAttendance(attendanceData);
    }

    async updateAttendance(attendanceId, attendanceData) {
        if (!this.checkApi()) return null;
        return await this.api.updateAttendance(attendanceId, attendanceData);
    }

    async deleteAttendance(attendanceId) {
        if (!this.checkApi()) return false;
        return await this.api.deleteAttendance(attendanceId);
    }

    // Schedule
    async getSchedule() {
        if (!this.checkApi()) return [];
        return await this.api.getSchedule();
    }

    async createScheduleItem(scheduleData) {
        if (!this.checkApi()) return null;
        return await this.api.createScheduleItem(scheduleData);
    }

    async updateScheduleItem(scheduleId, scheduleData) {
        if (!this.checkApi()) return null;
        return await this.api.updateScheduleItem(scheduleId, scheduleData);
    }

    async deleteScheduleItem(scheduleId) {
        if (!this.checkApi()) return false;
        return await this.api.deleteScheduleItem(scheduleId);
    }

    // Face Profiles
    async getFaceProfiles() {
        if (!this.checkApi()) return [];
        return await this.api.getFaceProfiles();
    }

    async createFaceProfile(profileData) {
        if (!this.checkApi()) return null;
        return await this.api.createFaceProfile(profileData);
    }

    async updateFaceProfile(profileId, profileData) {
        if (!this.checkApi()) return null;
        return await this.api.updateFaceProfile(profileId, profileData);
    }

    async deleteFaceProfile(profileId) {
        if (!this.checkApi()) return false;
        return await this.api.deleteFaceProfile(profileId);
    }

    // Authentication helpers
    async login(username, password) {
        if (!this.checkApi()) return { success: false, error: 'API not loaded' };
        return await this.api.login(username, password);
    }

    async logout() {
        if (!this.checkApi()) return;
        return await this.api.logout();
    }

    async getCurrentUser() {
        if (!this.checkApi()) return null;
        return await this.api.getCurrentUser();
    }
}

// Create global database instance
const db = new Database();
