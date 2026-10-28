// Data Migration - Legacy Migration Helper
// This file is kept for backward compatibility with the migration page.
// The system now uses Django REST API directly via api-client.js.
// This migration tool is not recommended for production use.

const dataMigration = {
    async migrateAll() {
        console.warn('Legacy migration tool detected. Use Django API instead.');
        return { 
            success: false, 
            error: 'Legacy migration tool is deprecated. Please use Django API directly.' 
        };
    }
};
