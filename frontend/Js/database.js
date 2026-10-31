// Database compatibility layer
// This file provides backward compatibility for existing HTML pages
// It wraps the Django API client (api-client.js) to maintain the old interface

// Import the API client functionality
// The api-client.js must be loaded before this file

class Database {
    constructor() {
        this.api = window.api;
    }

    // Users
    async getUsers() {
        return await this.api.getUsers();
    }

    async getStudents() {
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
        return await this.api.createUser(userData);
    }

    async updateUser(userId, userData) {
        return await this.api.updateUser(userId, userData);
    }

    async deleteUser(userId) {
        return await this.api.deleteUser(userId);
    }

    async addUser(userData) {
        // Alias for createUser for backward compatibility
        return await this.createUser(userData);
    }

    // Departments
    async getDepartments() {
        return await this.api.getDepartments();
    }

    async createDepartment(departmentData) {
        return await this.api.createDepartment(departmentData);
    }

    async updateDepartment(departmentId, departmentData) {
        return await this.api.updateDepartment(departmentId, departmentData);
    }

    async deleteDepartment(departmentId) {
        return await this.api.deleteDepartment(departmentId);
    }

    async addDepartment(departmentData) {
        // Alias for createDepartment for backward compatibility
        return await this.createDepartment(departmentData);
    }

    // Stages
    async getStages() {
        return await this.api.getStages();
    }

    async createStage(stageData) {
        return await this.api.createStage(stageData);
    }

    async updateStage(stageId, stageData) {
        return await this.api.updateStage(stageId, stageData);
    }

    async deleteStage(stageId) {
        return await this.api.deleteStage(stageId);
    }

    // Branches
    async getBranches() {
        return await this.api.getBranches();
    }

    async createBranch(branchData) {
        return await this.api.createBranch(branchData);
    }

    async updateBranch(branchId, branchData) {
        return await this.api.updateBranch(branchId, branchData);
    }

    async deleteBranch(branchId) {
        return await this.api.deleteBranch(branchId);
    }

    // Attendance
    async getAttendance() {
        return await this.api.getAttendance();
    }

    async createAttendance(attendanceData) {
        return await this.api.createAttendance(attendanceData);
    }

    async updateAttendance(attendanceId, attendanceData) {
        return await this.api.updateAttendance(attendanceId, attendanceData);
    }

    async deleteAttendance(attendanceId) {
        return await this.api.deleteAttendance(attendanceId);
    }

    // Schedule
    async getSchedule() {
        return await this.api.getSchedule();
    }

    async createScheduleItem(scheduleData) {
        return await this.api.createScheduleItem(scheduleData);
    }

    async updateScheduleItem(scheduleId, scheduleData) {
        return await this.api.updateScheduleItem(scheduleId, scheduleData);
    }

    async deleteScheduleItem(scheduleId) {
        return await this.api.deleteScheduleItem(scheduleId);
    }

    // Face Profiles
    async getFaceProfiles() {
        return await this.api.getFaceProfiles();
    }

    async createFaceProfile(profileData) {
        return await this.api.createFaceProfile(profileData);
    }

    async updateFaceProfile(profileId, profileData) {
        return await this.api.updateFaceProfile(profileId, profileData);
    }

    async deleteFaceProfile(profileId) {
        return await this.api.deleteFaceProfile(profileId);
    }

    // Authentication helpers
    async login(username, password) {
        return await this.api.login(username, password);
    }

    async logout() {
        return await this.api.logout();
    }

    async getCurrentUser() {
        return await this.api.getCurrentUser();
    }
}

// Create global database instance
const db = new Database();
