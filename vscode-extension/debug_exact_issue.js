// Debug the exact issue by testing what the extension is doing
const axios = require('axios');

async function debugExactIssue() {
    console.log('🔍 Debugging the exact issue from the logs...');
    console.log('=' * 60);
    
    const baseUrl = 'http://localhost:8003';
    
    // Create axios instance exactly like the extension does
    const httpClient = axios.create({
        baseURL: baseUrl,
        timeout: 30000,
        headers: {
            'Content-Type': 'application/json'
        }
    });
    
    console.log('🔍 Base URL:', baseUrl);
    
    // Test the exact sequence from the logs
    try {
        console.log('\n1️⃣ Testing connection sequence...');
        
        // Health endpoint (should fail)
        try {
            console.log('🔍 Trying health endpoint:', baseUrl + '/health');
            const healthResponse = await httpClient.get('/health');
            console.log('✅ Health endpoint worked (unexpected!)');
        } catch (healthError) {
            console.log('⚠️ Health endpoint failed with:', healthError.response?.status, healthError.message);
            
            // Root endpoint (should work)
            try {
                console.log('🔍 Trying root endpoint:', baseUrl + '/');
                const rootResponse = await httpClient.get('/');
                console.log('✅ Root endpoint worked');
                console.log('📊 Root response data:', rootResponse.data);
            } catch (rootError) {
                console.log('❌ Root endpoint failed:', rootError.response?.status, rootError.message);
                throw rootError;
            }
        }
        
        console.log('\n2️⃣ Testing system status sequence...');
        
        // VS Code endpoint (should fail)
        try {
            console.log('🔍 Trying VS Code endpoint:', baseUrl + '/vscode/api/v1/system/status');
            const vsCodeResponse = await httpClient.get('/vscode/api/v1/system/status');
            console.log('✅ VS Code endpoint worked (unexpected!)');
        } catch (vsCodeError) {
            console.log('⚠️ VS Code endpoint failed with:', vsCodeError.response?.status, vsCodeError.message);
            
            // Check if we're getting HTML instead of JSON
            if (vsCodeError.response && vsCodeError.response.data) {
                const responseData = vsCodeError.response.data;
                if (typeof responseData === 'string' && responseData.includes('<!DOCTYPE')) {
                    console.log('🚨 Getting HTML response instead of JSON!');
                    console.log('📄 HTML response preview:', responseData.substring(0, 200) + '...');
                }
            }
            
            // Diagnostics endpoint (should work)
            try {
                console.log('🔍 Trying diagnostics endpoint:', baseUrl + '/diagnostics');
                const diagnosticsResponse = await httpClient.get('/diagnostics');
                console.log('✅ Diagnostics endpoint worked');
                console.log('📊 Diagnostics data:', diagnosticsResponse.data);
                
                // Transform the data
                const diagnosticsData = diagnosticsResponse.data;
                const transformedData = {
                    system_status: diagnosticsData.status || 'online',
                    uptime: '5 minutes',
                    websocket_connected: false,
                    websocket_url: baseUrl.replace('http', 'ws') + '/vscode/api/v1/ws',
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
                
            } catch (diagnosticsError) {
                console.log('❌ Diagnostics endpoint failed:', diagnosticsError.response?.status, diagnosticsError.message);
                
                // Check if we're getting HTML instead of JSON
                if (diagnosticsError.response && diagnosticsError.response.data) {
                    const responseData = diagnosticsError.response.data;
                    if (typeof responseData === 'string' && responseData.includes('<!DOCTYPE')) {
                        console.log('🚨 Getting HTML response instead of JSON from diagnostics!');
                        console.log('📄 HTML response preview:', responseData.substring(0, 200) + '...');
                    }
                }
                throw diagnosticsError;
            }
        }
        
        console.log('\n🎉 All tests completed successfully!');
        console.log('✅ The issue might be in the extension configuration or timing.');
        
    } catch (error) {
        console.error('\n💥 Critical error:', error.message);
        if (error.response) {
            console.error('Response status:', error.response.status);
            console.error('Response headers:', error.response.headers);
            console.error('Response data type:', typeof error.response.data);
            if (typeof error.response.data === 'string') {
                console.error('Response data preview:', error.response.data.substring(0, 500));
            } else {
                console.error('Response data:', error.response.data);
            }
        }
    }
}

debugExactIssue();