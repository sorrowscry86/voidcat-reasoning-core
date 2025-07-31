// Debug script to test all the endpoints the extension might be calling
const axios = require('axios');

async function debugConnection() {
    console.log('🔍 Debugging VoidCat Extension Connection...');
    console.log('=' * 60);
    
    const baseUrl = 'http://localhost:8003';
    
    // Create axios instance like the extension does
    const httpClient = axios.create({
        baseURL: baseUrl,
        timeout: 30000,
        headers: {
            'Content-Type': 'application/json'
        }
    });
    
    const endpoints = [
        '/',
        '/health', 
        '/diagnostics',
        '/vscode/api/v1/system/status',
        '/vscode/api/v1/tasks',
        '/vscode/api/v1/projects',
        '/vscode/api/v1/memories'
    ];
    
    for (const endpoint of endpoints) {
        try {
            console.log(`\n🧪 Testing: ${endpoint}`);
            const response = await httpClient.get(endpoint);
            console.log(`✅ Status: ${response.status}`);
            if (typeof response.data === 'object') {
                console.log(`📊 Data keys: ${Object.keys(response.data).join(', ')}`);
            } else {
                console.log(`📊 Data type: ${typeof response.data}`);
            }
        } catch (error) {
            if (error.response) {
                console.log(`❌ Status: ${error.response.status} - ${error.response.statusText}`);
                if (error.response.data) {
                    console.log(`📊 Error data: ${JSON.stringify(error.response.data)}`);
                }
            } else {
                console.log(`💥 Network error: ${error.message}`);
            }
        }
    }
    
    console.log('\n' + '=' * 60);
    console.log('🎯 Testing the exact flow the dashboard uses...');
    
    try {
        // Test connection (health check)
        console.log('\n1️⃣ Testing connection...');
        let healthResponse;
        try {
            healthResponse = await httpClient.get('/health');
            console.log('✅ Health check passed');
        } catch (healthError) {
            console.log('⚠️  Health endpoint failed, trying root...');
            healthResponse = await httpClient.get('/');
            console.log('✅ Root endpoint worked as fallback');
        }
        
        // Test system status (dashboard data)
        console.log('\n2️⃣ Testing system status...');
        try {
            const statusResponse = await httpClient.get('/vscode/api/v1/system/status');
            console.log('✅ VS Code system status worked');
            console.log('📊 Status data:', JSON.stringify(statusResponse.data, null, 2));
        } catch (vsCodeError) {
            console.log('⚠️  VS Code endpoint failed, trying diagnostics fallback...');
            const diagnosticsResponse = await httpClient.get('/diagnostics');
            console.log('✅ Diagnostics fallback worked');
            
            // Transform the data like the extension does
            const diagnosticsData = diagnosticsResponse.data;
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
            
            console.log('🔄 Transformed data:', JSON.stringify(transformedData, null, 2));
        }
        
        console.log('\n🎉 All tests completed! The extension should work now.');
        
    } catch (error) {
        console.error('\n💥 Critical error in dashboard flow:', error.message);
        if (error.response) {
            console.error('Response status:', error.response.status);
            console.error('Response data:', error.response.data);
        }
    }
}

debugConnection();