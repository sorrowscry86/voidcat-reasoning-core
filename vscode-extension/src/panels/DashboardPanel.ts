import * as vscode from 'vscode';
import { VoidCatEngineClient, VoidCatEngineStatus } from '../VoidCatEngineClient';

export class DashboardPanel {
    public static currentPanel: DashboardPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];
    private _refreshInterval?: NodeJS.Timer;

    public static createOrShow(extensionUri: vscode.Uri, engineClient: VoidCatEngineClient) {
        const column = vscode.window.activeTextEditor?.viewColumn || vscode.ViewColumn.One;

        if (DashboardPanel.currentPanel) {
            DashboardPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'voidcatDashboard',
            'VoidCat Dashboard',
            column,
            {
                enableScripts: true,
                localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
            }
        );

        DashboardPanel.currentPanel = new DashboardPanel(panel, extensionUri, engineClient);
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, private engineClient: VoidCatEngineClient) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        this._panel.webview.html = this._getHtmlForWebview();
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Auto-refresh dashboard data
        this.startAutoRefresh();
        this.loadDashboardData();
    }
    private async loadDashboardData(): Promise<void> {
        try {
            const status = await this.engineClient.getSystemStatus();
            
            // Send data to webview
            this._panel.webview.postMessage({
                command: 'updateDashboard',
                data: status
            });
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this._panel.webview.postMessage({
                command: 'updateDashboard',
                data: { error: 'Failed to load dashboard data' }
            });
        }
    }

    private startAutoRefresh(): void {
        // Refresh dashboard every 5 seconds
        this._refreshInterval = setInterval(async () => {
            await this.loadDashboardData();
        }, 5000);
    }

    private _getHtmlForWebview(): string {
        const scriptPathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'media', 'dashboard.js');
        const scriptUri = this._panel.webview.asWebviewUri(scriptPathOnDisk);
        
        const stylePathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'media', 'dashboard.css');
        const styleUri = this._panel.webview.asWebviewUri(stylePathOnDisk);

        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${this._panel.webview.cspSource} 'unsafe-inline'; script-src ${this._panel.webview.cspSource} 'unsafe-inline';">
            <link href="${styleUri}" rel="stylesheet">
            <title>VoidCat Dashboard</title>
        </head>
        <body>
            <div class="dashboard-container">
                <header class="dashboard-header">
                    <h1>🐾 VoidCat Reasoning Core Dashboard</h1>
                    <div class="status-indicator" id="connectionStatus">
                        <span class="status-dot connecting"></span>
                        <span class="status-text">Connecting...</span>
                    </div>
                </header>

                <div class="dashboard-grid">
                    <!-- Engine Status Card -->
                    <div class="dashboard-card" id="engineStatusCard">
                        <div class="card-header">
                            <h3>🚀 Engine Status</h3>
                            <div class="card-actions">
                                <button class="refresh-btn" onclick="refreshDashboard()">🔄</button>
                            </div>
                        </div>
                        <div class="card-content">
                            <div class="status-grid">
                                <div class="status-item">
                                    <span class="status-label">Status:</span>
                                    <span class="status-value" id="engineStatus">Unknown</span>
                                </div>
                                <div class="status-item">
                                    <span class="status-label">Uptime:</span>
                                    <span class="status-value" id="engineUptime">--</span>
                                </div>
                                <div class="status-item">
                                    <span class="status-label">Queries:</span>
                                    <span class="status-value" id="totalQueries">--</span>
                                </div>
                                <div class="status-item">
                                    <span class="status-label">WebSocket:</span>
                                    <span class="status-value" id="websocketStatus">Disconnected</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Task Management Card -->
                    <div class="dashboard-card" id="taskStatsCard">
                        <div class="card-header">
                            <h3>📋 Task Management</h3>
                        </div>
                        <div class="card-content">
                            <div class="task-stats">
                                <div class="stat-item">
                                    <div class="stat-number" id="totalTasks">--</div>
                                    <div class="stat-label">Total Tasks</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-number" id="completedTasks">--</div>
                                    <div class="stat-label">Completed</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-number" id="inProgressTasks">--</div>
                                    <div class="stat-label">In Progress</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-number" id="pendingTasks">--</div>
                                    <div class="stat-label">Pending</div>
                                </div>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" id="taskProgress"></div>
                            </div>
                        </div>
                    </div>

                    <!-- Memory System Card -->
                    <div class="dashboard-card" id="memoryStatsCard">
                        <div class="card-header">
                            <h3>🧠 Memory System</h3>
                        </div>
                        <div class="card-content">
                            <div class="memory-stats">
                                <div class="stat-item">
                                    <div class="stat-number" id="totalMemories">--</div>
                                    <div class="stat-label">Total Memories</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-number" id="memoryCategories">--</div>
                                    <div class="stat-label">Categories</div>
                                </div>
                            </div>
                            <div class="memory-categories" id="memoryCategoryList">
                                <!-- Categories will be populated here -->
                            </div>
                        </div>
                    </div>

                    <!-- Performance Metrics Card -->
                    <div class="dashboard-card" id="performanceCard">
                        <div class="card-header">
                            <h3>⚡ Performance Metrics</h3>
                        </div>
                        <div class="card-content">
                            <div class="metrics-grid">
                                <div class="metric-item">
                                    <div class="metric-chart">
                                        <canvas id="queryChart" width="200" height="100"></canvas>
                                    </div>
                                    <div class="metric-label">Query Response Time</div>
                                </div>
                                <div class="metric-item">
                                    <div class="metric-value" id="documentsLoaded">--</div>
                                    <div class="metric-label">Documents Loaded</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- System Health Card -->
                    <div class="dashboard-card" id="systemHealthCard">
                        <div class="card-header">
                            <h3>🏥 System Health</h3>
                        </div>
                        <div class="card-content">
                            <div class="health-indicators">
                                <div class="health-item">
                                    <div class="health-icon" id="engineHealthIcon">🔴</div>
                                    <div class="health-label">Engine</div>
                                </div>
                                <div class="health-item">
                                    <div class="health-icon" id="taskHealthIcon">🔴</div>
                                    <div class="health-label">Tasks</div>
                                </div>
                                <div class="health-item">
                                    <div class="health-icon" id="memoryHealthIcon">🔴</div>
                                    <div class="health-label">Memory</div>
                                </div>
                                <div class="health-item">
                                    <div class="health-icon" id="apiHealthIcon">🔴</div>
                                    <div class="health-label">API</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Recent Activity Card -->
                    <div class="dashboard-card" id="recentActivityCard">
                        <div class="card-header">
                            <h3>📈 Recent Activity</h3>
                        </div>
                        <div class="card-content">
                            <div class="activity-list" id="activityList">
                                <!-- Activity items will be populated here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script src="${scriptUri}"></script>
        </body>
        </html>`;
    }

    public dispose(): void {
        if (this._refreshInterval) {
            clearInterval(this._refreshInterval);
        }
        
        DashboardPanel.currentPanel = undefined;
        this._panel.dispose();
        
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}