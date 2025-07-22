// This script will be run in the webview

(function () {
    const vscode = acquireVsCodeApi();

    const diagnosticsContainer = document.getElementById('diagnostics-container');

    function fetchDiagnostics() {
        // This is where we would make a call to the MCP server to get the diagnostics data
        // For now, we'll just use some dummy data
        const dummyData = {
            "status": "running",
            "memoryUsage": "256MB",
            "cpuUsage": "15%",
            "activeTasks": 5
        };

        diagnosticsContainer.innerHTML = `
            <p><strong>Status:</strong> ${dummyData.status}</p>
            <p><strong>Memory Usage:</strong> ${dummyData.memoryUsage}</p>
            <p><strong>CPU Usage:</strong> ${dummyData.cpuUsage}</p>
            <p><strong>Active Tasks:</strong> ${dummyData.activeTasks}</p>
        `;
    }

    fetchDiagnostics();

    // Fetch diagnostics every 5 seconds
    setInterval(fetchDiagnostics, 5000);
}());
