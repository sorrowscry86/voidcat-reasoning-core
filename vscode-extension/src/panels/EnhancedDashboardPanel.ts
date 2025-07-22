import * as vscode from 'vscode';
import { VoidCatEngineClient } from '../VoidCatEngineClient';

export interface DashboardMetrics {
    engineStatus: {
        status: string;
        uptime: string;
        queries: number;
        responseTime: number;
        memoryUsage: number;
        cpuUsage: number;
    };
    taskStatistics: {
        total: number;
        completed: number;
        inProgress: number;
        pending: number;
        blocked: number;
        efficiency: number;
    };
    memoryStatistics: {
        total: number;
        categories: { [key: string]: number };
        recentlyAccessed: string[];
        searchQueries: number;
    };
    performanceMetrics: {
        queryResponseTimes: number[];
        systemLoad: number;
        documentsLoaded: number;
        vectorFeatures: number;
    };
    recentActivity: Array<{
        timestamp: string;
        type: string;
        description: string;
        icon: string;
    }>;
}

export class EnhancedDashboardPanel {
    public static currentPanel: EnhancedDashboardPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private readonly _engineClient: VoidCatEngineClient;
    private _disposables: vscode.Disposable[] = [];
    private _refreshInterval?: NodeJS.Timer;
    private _websocketConnected: boolean = false;
    private _lastUpdateTimestamp: number = 0;
    private _metrics: DashboardMetrics | null = null;

    public static createOrShow(extensionUri: vscode.Uri, engineClient: VoidCatEngineClient) {
        const column = vscode.window.activeTextEditor?.viewColumn || vscode.ViewColumn.One;

        if (EnhancedDashboardPanel.currentPanel) {
            EnhancedDashboardPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'voidcatEnhancedDashboard',
            'VoidCat Enhanced Dashboard',
            column,
            {
                enableScripts: true,
                localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
            }
        );

        EnhancedDashboardPanel.currentPanel = new EnhancedDashboardPanel(panel, extensionUri, engineClient);
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, engineClient: VoidCatEngineClient) {
        this._panel = panel;
        this._extensionUri = extensionUri;
        this._engineClient = engineClient;

        this._panel.webview.html = this._getHtmlForWebview();
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Setup message handling
        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                switch (message.command) {
                    case 'refresh':
                        await this.loadDashboardData();
                        break;
                    case 'toggleAutoRefresh':
                        this.toggleAutoRefresh();
                        break;
                    case 'exportMetrics':
                        await this.exportMetrics();
                        break;
                    case 'resetMetrics':
                        await this.resetMetrics();
                        break;
                }
            },
            null,
            this._disposables
        );

        // Initialize dashboard
        this.initialize();
    }

    private async initialize(): Promise<void> {
        try {
            // Setup WebSocket event listeners
            this._engineClient.addEventListener('update', (data) => {
                this.handleRealtimeUpdate(data);
            });

            this._engineClient.addEventListener('taskUpdate', (data) => {
                this.handleTaskUpdate(data);
            });

            this._engineClient.addEventListener('memoryUpdate', (data) => {
                this.handleMemoryUpdate(data);
            });

            // Start auto-refresh and load initial data
            this.startAutoRefresh();
            await this.loadDashboardData();

            // Show initialization success
            this._panel.webview.postMessage({
                command: 'showNotification',
                type: 'success',
                message: 'Dashboard initialized successfully'
            });

        } catch (error) {
            console.error('Failed to initialize enhanced dashboard:', error);
            this._panel.webview.postMessage({
                command: 'showError',
                message: 'Failed to initialize dashboard: ' + error
            });
        }
    }

    private async loadDashboardData(): Promise<void> {
        try {
            this._panel.webview.postMessage({
                command: 'setLoading',
                loading: true
            });

            // Fetch comprehensive system status
            const systemStatus = await this._engineClient.getSystemStatus();
            
            // Fetch task statistics
            const tasks = await this._engineClient.getTasks();
            const taskStats = this.calculateTaskStatistics(tasks);

            // Fetch performance metrics
            const performanceMetrics = await this.fetchPerformanceMetrics();

            // Fetch recent activity
            const recentActivity = await this.fetchRecentActivity();

            // Compile metrics
            this._metrics = {
                engineStatus: {
                    status: systemStatus.system_status || 'unknown',
                    uptime: systemStatus.uptime || 'N/A',
                    queries: systemStatus.total_queries || 0,
                    responseTime: systemStatus.avg_response_time || 0,
                    memoryUsage: systemStatus.memory_usage || 0,
                    cpuUsage: systemStatus.cpu_usage || 0
                },
                taskStatistics: taskStats,
                memoryStatistics: {
                    total: systemStatus.memory_statistics?.total || 0,
                    categories: systemStatus.memory_statistics?.categories || {},
                    recentlyAccessed: systemStatus.memory_statistics?.recently_accessed || [],
                    searchQueries: systemStatus.memory_statistics?.search_queries || 0
                },
                performanceMetrics,
                recentActivity
            };

            // Update WebSocket connection status
            this._websocketConnected = this._engineClient.websocketConnected;
            this._lastUpdateTimestamp = Date.now();

            // Send data to webview
            this._panel.webview.postMessage({
                command: 'updateDashboard',
                data: {
                    ...this._metrics,
                    websocketConnected: this._websocketConnected,
                    lastUpdate: this._lastUpdateTimestamp
                }
            });

            this._panel.webview.postMessage({
                command: 'setLoading',
                loading: false
            });

        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this._panel.webview.postMessage({
                command: 'updateDashboard',
                data: { error: 'Failed to load dashboard data: ' + error }
            });
            
            this._panel.webview.postMessage({
                command: 'setLoading',
                loading: false
            });
        }
    }

    private calculateTaskStatistics(tasks: any[]): DashboardMetrics['taskStatistics'] {
        const stats = {
            total: tasks.length,
            completed: tasks.filter(t => t.status === 'completed').length,
            inProgress: tasks.filter(t => t.status === 'in-progress').length,
            pending: tasks.filter(t => t.status === 'pending').length,
            blocked: tasks.filter(t => t.status === 'blocked').length,
            efficiency: 0
        };

        if (stats.total > 0) {
            stats.efficiency = Math.round((stats.completed / stats.total) * 100);
        }

        return stats;
    }

    private async fetchPerformanceMetrics(): Promise<DashboardMetrics['performanceMetrics']> {
        try {
            // Simulate performance metrics (in real implementation, this would come from backend)
            return {
                queryResponseTimes: [120, 95, 110, 130, 85, 105, 115, 90, 125, 100],
                systemLoad: Math.random() * 100,
                documentsLoaded: Math.floor(Math.random() * 1000),
                vectorFeatures: Math.floor(Math.random() * 10000)
            };
        } catch (error) {
            console.error('Failed to fetch performance metrics:', error);
            return {
                queryResponseTimes: [],
                systemLoad: 0,
                documentsLoaded: 0,
                vectorFeatures: 0
            };
        }
    }

    private async fetchRecentActivity(): Promise<DashboardMetrics['recentActivity']> {
        try {
            // Simulate recent activity (in real implementation, this would come from backend)
            const activities = [
                { timestamp: new Date(Date.now() - 120000).toISOString(), type: 'task', description: 'Task completed: Visual Dashboard Component', icon: '✅' },
                { timestamp: new Date(Date.now() - 300000).toISOString(), type: 'query', description: 'AI query processed successfully', icon: '🧠' },
                { timestamp: new Date(Date.now() - 600000).toISOString(), type: 'memory', description: 'New memory stored: Dashboard metrics', icon: '💾' },
                { timestamp: new Date(Date.now() - 900000).toISOString(), type: 'system', description: 'Engine status check completed', icon: '🔧' },
                { timestamp: new Date(Date.now() - 1800000).toISOString(), type: 'websocket', description: 'WebSocket connection established', icon: '🌐' }
            ];

            return activities;
        } catch (error) {
            console.error('Failed to fetch recent activity:', error);
            return [];
        }
    }

    private handleRealtimeUpdate(data: any): void {
        if (data.type === 'system_status') {
            this._panel.webview.postMessage({
                command: 'updateRealtime',
                type: 'system',
                data: data.payload
            });
        }
    }

    private handleTaskUpdate(data: any): void {
        this._panel.webview.postMessage({
            command: 'updateRealtime',
            type: 'task',
            data: data.payload
        });
    }

    private handleMemoryUpdate(data: any): void {
        this._panel.webview.postMessage({
            command: 'updateRealtime',
            type: 'memory',
            data: data.payload
        });
    }

    private startAutoRefresh(): void {
        if (this._refreshInterval) {
            clearInterval(this._refreshInterval);
        }

        // Refresh dashboard every 10 seconds
        this._refreshInterval = setInterval(async () => {
            await this.loadDashboardData();
        }, 10000);
    }

    private toggleAutoRefresh(): void {
        if (this._refreshInterval) {
            clearInterval(this._refreshInterval);
            this._refreshInterval = undefined;
            this._panel.webview.postMessage({
                command: 'showNotification',
                type: 'info',
                message: 'Auto-refresh disabled'
            });
        } else {
            this.startAutoRefresh();
            this._panel.webview.postMessage({
                command: 'showNotification',
                type: 'info',
                message: 'Auto-refresh enabled'
            });
        }
    }

    private async exportMetrics(): Promise<void> {
        try {
            if (!this._metrics) {
                throw new Error('No metrics available to export');
            }

            const exportData = {
                timestamp: new Date().toISOString(),
                metrics: this._metrics,
                websocketConnected: this._websocketConnected,
                lastUpdate: this._lastUpdateTimestamp
            };

            const document = await vscode.workspace.openTextDocument({
                content: JSON.stringify(exportData, null, 2),
                language: 'json'
            });

            await vscode.window.showTextDocument(document);

            this._panel.webview.postMessage({
                command: 'showNotification',
                type: 'success',
                message: 'Metrics exported successfully'
            });
        } catch (error) {
            console.error('Failed to export metrics:', error);
            this._panel.webview.postMessage({
                command: 'showNotification',
                type: 'error',
                message: 'Failed to export metrics: ' + error
            });
        }
    }

    private async resetMetrics(): Promise<void> {
        try {
            // Reset local metrics
            this._metrics = null;
            this._lastUpdateTimestamp = 0;

            // Reload dashboard data
            await this.loadDashboardData();

            this._panel.webview.postMessage({
                command: 'showNotification',
                type: 'success',
                message: 'Metrics reset successfully'
            });
        } catch (error) {
            console.error('Failed to reset metrics:', error);
            this._panel.webview.postMessage({
                command: 'showNotification',
                type: 'error',
                message: 'Failed to reset metrics: ' + error
            });
        }
    }

    private _getHtmlForWebview(): string {
        const scriptPathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'media', 'enhanced-dashboard.js');
        const scriptUri = this._panel.webview.asWebviewUri(scriptPathOnDisk);
        
        const stylePathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'media', 'enhanced-dashboard.css');
        const styleUri = this._panel.webview.asWebviewUri(stylePathOnDisk);

        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${this._panel.webview.cspSource} 'unsafe-inline'; script-src ${this._panel.webview.cspSource} 'unsafe-inline';">
            <link href="${styleUri}" rel="stylesheet">
            <title>VoidCat Enhanced Dashboard</title>
        </head>
        <body>
            <div class="enhanced-dashboard-container">
                <!-- Loading overlay -->
                <div id="loadingOverlay" class="loading-overlay">
                    <div class="loading-spinner"></div>
                    <div class="loading-text">Loading dashboard...</div>
                </div>

                <!-- Notification system -->
                <div id="notificationContainer" class="notification-container"></div>

                <!-- Dashboard header -->
                <header class="enhanced-dashboard-header">
                    <div class="header-left">
                        <h1>🐾 VoidCat Enhanced Dashboard</h1>
                        <div class="status-indicators">
                            <div class="status-indicator" id="connectionStatus">
                                <span class="status-dot connecting"></span>
                                <span class="status-text">Connecting...</span>
                            </div>
                            <div class="status-indicator" id="websocketStatus">
                                <span class="status-dot disconnected"></span>
                                <span class="status-text">WebSocket: Disconnected</span>
                            </div>
                        </div>
                    </div>
                    <div class="header-right">
                        <button class="action-btn" id="refreshBtn" onclick="refreshDashboard()">
                            <span class="btn-icon">🔄</span>
                            <span class="btn-text">Refresh</span>
                        </button>
                        <button class="action-btn" id="autoRefreshBtn" onclick="toggleAutoRefresh()">
                            <span class="btn-icon">⏱️</span>
                            <span class="btn-text">Auto-Refresh</span>
                        </button>
                        <button class="action-btn" id="exportBtn" onclick="exportMetrics()">
                            <span class="btn-icon">📊</span>
                            <span class="btn-text">Export</span>
                        </button>
                    </div>
                </header>

                <!-- Dashboard content -->
                <div class="enhanced-dashboard-content">
                    <!-- Quick stats row -->
                    <div class="quick-stats-row">
                        <div class="quick-stat-card">
                            <div class="stat-icon">🚀</div>
                            <div class="stat-content">
                                <div class="stat-value" id="quickEngineStatus">--</div>
                                <div class="stat-label">Engine Status</div>
                            </div>
                        </div>
                        <div class="quick-stat-card">
                            <div class="stat-icon">📋</div>
                            <div class="stat-content">
                                <div class="stat-value" id="quickTaskProgress">--</div>
                                <div class="stat-label">Task Progress</div>
                            </div>
                        </div>
                        <div class="quick-stat-card">
                            <div class="stat-icon">🧠</div>
                            <div class="stat-content">
                                <div class="stat-value" id="quickMemoryUsage">--</div>
                                <div class="stat-label">Memory Usage</div>
                            </div>
                        </div>
                        <div class="quick-stat-card">
                            <div class="stat-icon">⚡</div>
                            <div class="stat-content">
                                <div class="stat-value" id="quickPerformance">--</div>
                                <div class="stat-label">Performance</div>
                            </div>
                        </div>
                    </div>

                    <!-- Main dashboard grid -->
                    <div class="enhanced-dashboard-grid">
                        <!-- Enhanced Engine Status Card -->
                        <div class="dashboard-card enhanced-engine-card">
                            <div class="card-header">
                                <h3>🚀 Engine Status & Performance</h3>
                                <div class="card-actions">
                                    <button class="card-action-btn" onclick="refreshEngineStatus()">🔄</button>
                                    <button class="card-action-btn" onclick="toggleEngineDetails()">📊</button>
                                </div>
                            </div>
                            <div class="card-content">
                                <div class="engine-status-grid">
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
                                        <span class="status-label">Response Time:</span>
                                        <span class="status-value" id="avgResponseTime">--</span>
                                    </div>
                                    <div class="status-item">
                                        <span class="status-label">Memory:</span>
                                        <span class="status-value" id="memoryUsage">--</span>
                                    </div>
                                    <div class="status-item">
                                        <span class="status-label">CPU:</span>
                                        <span class="status-value" id="cpuUsage">--</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Enhanced Task Management Card -->
                        <div class="dashboard-card enhanced-task-card">
                            <div class="card-header">
                                <h3>📋 Task Management Analytics</h3>
                                <div class="card-actions">
                                    <button class="card-action-btn" onclick="refreshTaskStats()">🔄</button>
                                    <button class="card-action-btn" onclick="openTaskManager()">🔗</button>
                                </div>
                            </div>
                            <div class="card-content">
                                <div class="task-analytics">
                                    <div class="task-efficiency-circle">
                                        <svg class="efficiency-circle" viewBox="0 0 100 100">
                                            <circle cx="50" cy="50" r="45" fill="none" stroke="var(--border-color)" stroke-width="8"/>
                                            <circle id="efficiencyProgress" cx="50" cy="50" r="45" fill="none" stroke="var(--primary-color)" stroke-width="8" stroke-linecap="round"/>
                                        </svg>
                                        <div class="efficiency-text">
                                            <div class="efficiency-value" id="taskEfficiency">--</div>
                                            <div class="efficiency-label">Efficiency</div>
                                        </div>
                                    </div>
                                    <div class="task-breakdown">
                                        <div class="task-stat">
                                            <div class="task-stat-count" id="completedTasks">--</div>
                                            <div class="task-stat-label">Completed</div>
                                        </div>
                                        <div class="task-stat">
                                            <div class="task-stat-count" id="inProgressTasks">--</div>
                                            <div class="task-stat-label">In Progress</div>
                                        </div>
                                        <div class="task-stat">
                                            <div class="task-stat-count" id="pendingTasks">--</div>
                                            <div class="task-stat-label">Pending</div>
                                        </div>
                                        <div class="task-stat">
                                            <div class="task-stat-count" id="blockedTasks">--</div>
                                            <div class="task-stat-label">Blocked</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Enhanced Performance Chart Card -->
                        <div class="dashboard-card enhanced-performance-card">
                            <div class="card-header">
                                <h3>⚡ Performance Metrics</h3>
                                <div class="card-actions">
                                    <button class="card-action-btn" onclick="refreshPerformanceChart()">🔄</button>
                                </div>
                            </div>
                            <div class="card-content">
                                <div class="performance-chart-container">
                                    <canvas id="performanceChart" width="400" height="200"></canvas>
                                </div>
                                <div class="performance-stats">
                                    <div class="perf-stat">
                                        <div class="perf-stat-value" id="avgResponseTimeMs">--</div>
                                        <div class="perf-stat-label">Avg Response (ms)</div>
                                    </div>
                                    <div class="perf-stat">
                                        <div class="perf-stat-value" id="systemLoadPercent">--</div>
                                        <div class="perf-stat-label">System Load (%)</div>
                                    </div>
                                    <div class="perf-stat">
                                        <div class="perf-stat-value" id="documentsLoadedCount">--</div>
                                        <div class="perf-stat-label">Documents Loaded</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Enhanced Memory System Card -->
                        <div class="dashboard-card enhanced-memory-card">
                            <div class="card-header">
                                <h3>🧠 Memory System Analytics</h3>
                                <div class="card-actions">
                                    <button class="card-action-btn" onclick="refreshMemoryStats()">🔄</button>
                                    <button class="card-action-btn" onclick="openMemoryBrowser()">🔗</button>
                                </div>
                            </div>
                            <div class="card-content">
                                <div class="memory-analytics">
                                    <div class="memory-overview">
                                        <div class="memory-stat">
                                            <div class="memory-stat-value" id="totalMemories">--</div>
                                            <div class="memory-stat-label">Total Memories</div>
                                        </div>
                                        <div class="memory-stat">
                                            <div class="memory-stat-value" id="memoryCategories">--</div>
                                            <div class="memory-stat-label">Categories</div>
                                        </div>
                                        <div class="memory-stat">
                                            <div class="memory-stat-value" id="memorySearches">--</div>
                                            <div class="memory-stat-label">Searches</div>
                                        </div>
                                    </div>
                                    <div class="memory-categories" id="memoryCategoryList">
                                        <!-- Categories will be populated here -->
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Enhanced Recent Activity Card -->
                        <div class="dashboard-card enhanced-activity-card">
                            <div class="card-header">
                                <h3>📈 Recent Activity Timeline</h3>
                                <div class="card-actions">
                                    <button class="card-action-btn" onclick="refreshActivity()">🔄</button>
                                    <button class="card-action-btn" onclick="clearActivity()">🗑️</button>
                                </div>
                            </div>
                            <div class="card-content">
                                <div class="activity-timeline" id="activityTimeline">
                                    <!-- Activity items will be populated here -->
                                </div>
                            </div>
                        </div>

                        <!-- System Health Monitor Card -->
                        <div class="dashboard-card system-health-card">
                            <div class="card-header">
                                <h3>🏥 System Health Monitor</h3>
                                <div class="card-actions">
                                    <button class="card-action-btn" onclick="runHealthCheck()">🔍</button>
                                </div>
                            </div>
                            <div class="card-content">
                                <div class="health-monitor-grid">
                                    <div class="health-component">
                                        <div class="health-icon" id="engineHealthIcon">🔴</div>
                                        <div class="health-label">Engine Core</div>
                                        <div class="health-status" id="engineHealthStatus">Checking...</div>
                                    </div>
                                    <div class="health-component">
                                        <div class="health-icon" id="taskHealthIcon">🔴</div>
                                        <div class="health-label">Task System</div>
                                        <div class="health-status" id="taskHealthStatus">Checking...</div>
                                    </div>
                                    <div class="health-component">
                                        <div class="health-icon" id="memoryHealthIcon">🔴</div>
                                        <div class="health-label">Memory System</div>
                                        <div class="health-status" id="memoryHealthStatus">Checking...</div>
                                    </div>
                                    <div class="health-component">
                                        <div class="health-icon" id="websocketHealthIcon">🔴</div>
                                        <div class="health-label">WebSocket</div>
                                        <div class="health-status" id="websocketHealthStatus">Checking...</div>
                                    </div>
                                </div>
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
        
        EnhancedDashboardPanel.currentPanel = undefined;
        this._panel.dispose();
        
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}
