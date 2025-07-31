// Quick test to verify the backend connection works
const axios = require('axios');

async function testConnection() {
    console.log('🧪 Testing VoidCat Backend Connection...');
    console.log('=' * 50);
    
    const baseUrl = 'http://localhost:8003';
    
    try {
        // Test diagnostics endpoint
        console.log('📊 Testing diagnostics endpoint...');
        const response = await axios.get(`${baseUrl}/diagnostics`);
        console.log('✅ Diagnostics response:', JSON.stringify(response.data, null, 2));
        
        // Test the data transformation
        const diagnosticsData = response.data;
        const transformedData = {
            system_status: diagnosticsData.status || 'online',
            uptime: '5 minutes',
            websocket_connected: false,
            task_statistics: {
                total: 5,
                completed: 2,
                in_progress: 1,
                pending: 2
            },
            memory_statistics: {
                total: 10,
                categories: {
                    general: 5,
                    code: 3,
                    project: 2
                }
            },
            documents_loaded: diagnosticsData.documents_loaded || 0,
            engine_initialized: diagnosticsData.status === 'online',
            last_query_timestamp: diagnosticsData.last_query_timestamp || new Date().toISOString(),
            total_queries_processed: diagnosticsData.total_queries_processed || 0
        };
        
        console.log('🔄 Transformed data for dashboard:', JSON.stringify(transformedData, null, 2));
        console.log('✅ Connection test successful! Dashboard should now populate.');
        
    } catch (error) {
        console.error('❌ Connection test failed:', error.message);
        if (error.response) {
            console.error('Response status:', error.response.status);
            console.error('Response data:', error.response.data);
        }
    }
}

testConnection();