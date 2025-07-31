// Check what VS Code configuration the extension is actually reading
const vscode = require('vscode');

// This simulates what the extension does
function checkConfig() {
    try {
        const config = vscode.workspace.getConfiguration('voidcat');
        const host = config.get('engine.host', 'localhost');
        const port = config.get('engine.port', 8003);
        
        console.log('🔍 VS Code Configuration:');
        console.log('  Host:', host);
        console.log('  Port:', port);
        console.log('  Base URL would be:', `http://${host}:${port}`);
        
        // Check if there are any actual settings
        const allSettings = config.inspect('engine.port');
        console.log('🔍 Port setting details:', allSettings);
        
    } catch (error) {
        console.log('❌ Cannot check VS Code config outside of extension context');
        console.log('This is expected when running outside VS Code');
    }
}

checkConfig();