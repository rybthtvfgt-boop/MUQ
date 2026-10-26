// Database API - Legacy Migration Helper
// This file is kept for backward compatibility with the migration page.
// The system now uses Django REST API directly via api-client.js.
// This migration tool is not recommended for production use.

const dbAPI = {
    // Placeholder methods to prevent errors
    async getDepartments() {
        console.warn('Legacy migration tool detected. Use Django API instead.');
        return { error: 'Use Django API instead of legacy migration' };
    }
};
