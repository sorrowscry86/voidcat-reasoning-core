#!/usr/bin/env node
/**
 * WebSocket Connection Test
 * =========================
 * 
 * Simple test to verify WebSocket connectivity to the VoidCat backend
 */

const WebSocket = require('ws');

console.log('🔌 Testing WebSocket connection to VoidCat backend...');
console.log('📍 Connecting to: ws://localhost:8003/vscode/api/v1/ws');
console.log('=' * 60);

const ws = new WebSocket('ws://localhost:8003/vscode/api/v1/ws');

ws.on('open', function open() {
    console.log('✅ WebSocket connection established!');
    console.log('🎉 Connection successful - your VS Code extension should be able to connect');
    
    // Send a test message
    ws.send(JSON.stringify({
        type: 'test_message',
        message: 'Hello from test client!',
        timestamp: new Date().toISOString()
    }));
});

ws.on('message', function message(data) {
    try {
        const parsed = JSON.parse(data);
        console.log('📨 Received message:', parsed);
    } catch (e) {
        console.log('📨 Received raw message:', data.toString());
    }
});

ws.on('close', function close() {
    console.log('🔌 WebSocket connection closed');
    process.exit(0);
});

ws.on('error', function error(err) {
    console.error('❌ WebSocket connection failed:', err.message);
    process.exit(1);
});

// Keep the connection open for a few seconds to test
setTimeout(() => {
    console.log('🏁 Test completed, closing connection...');
    ws.close();
}, 5000);