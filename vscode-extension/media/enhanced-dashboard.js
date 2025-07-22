// VoidCat Enhanced Dashboard JavaScript
(function() {
    'use strict';

    // VS Code API
    const vscode = acquireVsCodeApi();

    // Dashboard state
    let dashboardData = null;
    let isConnected = false;
    let websocketConnected = false;
    let autoRefreshEnabled = true;
    let charts = {};
    let animations = {};
    let notifications = [];

    // Initialize enhanced dashboard
    function initializeEnhancedDashboard() {
        console.log('Initializing VoidCat Enhanced Dashboard...');
        
        // Set up event listeners
        setupEventListeners();
        
        // Initialize charts and animations
        initializeCharts();
        initializeAnimations();
        
        // Setup notification system
        setupNotificationSystem();
        
        // Request initial data
        requestDashboardUpdate();
        
        console.log('Enhanced dashboard initialized successfully');
    }

    // Setup enhanced event listeners
    function setupEventListeners() {
        // Listen for messages from the extension
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.command) {
                case 'updateDashboard':
                    updateDashboard(message.data);
                    break;
                case 'updateRealtime':
                    updateRealtime(message.type, message.data);
                    break;
                case 'setLoading':
                    setLoading(message.loading);
                    break;
                case 'showNotification':
                    showNotification(message.type, message.message);
                    break;
                case 'showError':
                    showError(message.message);
                    break;
                default:
                    console.warn('Unknown message command:', message.command);
            }
        });

        // Setup keyboard shortcuts
        window.addEventListener('keydown', event => {
            if (event.ctrlKey || event.metaKey) {
                switch (event.key) {
                    case 'r':
                        event.preventDefault();
                        refreshDashboard();
                        break;
                    case 'e':
                        event.preventDefault();
                        exportMetrics();
                        break;
                    case 't':
                        event.preventDefault();
                        toggleAutoRefresh();
                        break;
                }
            }
        });
    }

    // Initialize enhanced charts
    function initializeCharts() {
        const performanceChartCanvas = document.getElementById('performanceChart');
        if (performanceChartCanvas) {
            const ctx = performanceChartCanvas.getContext('2d');
            
            charts.performanceChart = {
                canvas: performanceChartCanvas,
                ctx: ctx,
                data: [],
                labels: [],
                gradients: {},
                render: function() {
                    const width = this.canvas.width;
                    const height = this.canvas.height;
                    
                    // Clear canvas
                    this.ctx.clearRect(0, 0, width, height);
                    
                    // Create gradients if not exists
                    if (!this.gradients.background) {
                        this.gradients.background = this.ctx.createLinearGradient(0, 0, 0, height);
                        this.gradients.background.addColorStop(0, 'rgba(0, 122, 204, 0.2)');
                        this.gradients.background.addColorStop(1, 'rgba(0, 122, 204, 0.02)');
                    }
                    
                    // Draw background gradient
                    this.ctx.fillStyle = this.gradients.background;
                    this.ctx.fillRect(0, 0, width, height);
                    
                    // Draw grid
                    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
                    this.ctx.lineWidth = 1;
                    
                    // Horizontal grid lines
                    for (let i = 0; i <= 5; i++) {
                        const y = (height / 5) * i;
                        this.ctx.beginPath();
                        this.ctx.moveTo(0, y);
                        this.ctx.lineTo(width, y);
                        this.ctx.stroke();
                    }
                    
                    // Vertical grid lines
                    for (let i = 0; i <= 10; i++) {
                        const x = (width / 10) * i;
                        this.ctx.beginPath();
                        this.ctx.moveTo(x, 0);
                        this.ctx.lineTo(x, height);
                        this.ctx.stroke();
                    }
                    
                    // Draw data line with smooth curves
                    if (this.data.length > 1) {
                        const maxValue = Math.max(...this.data, 200);
                        
                        // Fill area under curve
                        this.ctx.fillStyle = 'rgba(0, 122, 204, 0.3)';
                        this.ctx.beginPath();
                        this.ctx.moveTo(0, height);
                        
                        for (let i = 0; i < this.data.length; i++) {
                            const x = (width / (this.data.length - 1)) * i;
                            const y = height - (this.data[i] / maxValue) * height;
                            
                            if (i === 0) {
                                this.ctx.lineTo(x, y);
                            } else {
                                // Smooth curve
                                const prevX = (width / (this.data.length - 1)) * (i - 1);
                                const prevY = height - (this.data[i - 1] / maxValue) * height;
                                const cpX = (prevX + x) / 2;
                                this.ctx.quadraticCurveTo(cpX, prevY, x, y);
                            }
                        }
                        
                        this.ctx.lineTo(width, height);
                        this.ctx.fill();
                        
                        // Draw main line
                        this.ctx.strokeStyle = '#007acc';
                        this.ctx.lineWidth = 3;
                        this.ctx.beginPath();
                        
                        for (let i = 0; i < this.data.length; i++) {
                            const x = (width / (this.data.length - 1)) * i;
                            const y = height - (this.data[i] / maxValue) * height;
                            
                            if (i === 0) {
                                this.ctx.moveTo(x, y);
                            } else {
                                // Smooth curve
                                const prevX = (width / (this.data.length - 1)) * (i - 1);
                                const prevY = height - (this.data[i - 1] / maxValue) * height;
                                const cpX = (prevX + x) / 2;
                                this.ctx.quadraticCurveTo(cpX, prevY, x, y);
                            }
                        }
                        
                        this.ctx.stroke();
                        
                        // Draw data points
                        this.ctx.fillStyle = '#007acc';
                        for (let i = 0; i < this.data.length; i++) {
                            const x = (width / (this.data.length - 1)) * i;
                            const y = height - (this.data[i] / maxValue) * height;
                            
                            this.ctx.beginPath();
                            this.ctx.arc(x, y, 4, 0, 2 * Math.PI);
                            this.ctx.fill();
                        }
                    }
                },
                addDataPoint: function(value) {
                    this.data.push(value);
                    this.labels.push(new Date().toLocaleTimeString());
                    
                    if (this.data.length > 20) {
                        this.data.shift();
                        this.labels.shift();
                    }
                    
                    this.render();
                }
            };
        }
    }

    // Initialize animations
    function initializeAnimations() {
        animations.taskEfficiency = {
            element: document.getElementById('efficiencyProgress'),
            currentValue: 0,
            targetValue: 0,
            animate: function() {
                if (this.currentValue !== this.targetValue) {
                    const diff = this.targetValue - this.currentValue;
                    this.currentValue += diff * 0.1;
                    
                    if (Math.abs(diff) < 0.1) {
                        this.currentValue = this.targetValue;
                    }
                    
                    const circumference = 2 * Math.PI * 45;
                    const progress = (this.currentValue / 100) * circumference;
                    
                    if (this.element) {
                        this.element.style.strokeDasharray = `${progress} ${circumference}`;
                        this.element.style.transform = 'rotate(-90deg)';
                    }
                    
                    requestAnimationFrame(() => this.animate());
                }
            },
            setValue: function(value) {
                this.targetValue = Math.max(0, Math.min(100, value));
                this.animate();
            }
        };
    }

    // Setup notification system
    function setupNotificationSystem() {
        const style = document.createElement('style');
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                z-index: 1000;
                opacity: 0;
                transform: translateX(100%);
                transition: all 0.3s ease;
            }
            
            .notification.show {
                opacity: 1;
                transform: translateX(0);
            }
            
            .notification.success {
                background-color: #28a745;
                border-left: 4px solid #1e7e34;
            }
            
            .notification.info {
                background-color: #17a2b8;
                border-left: 4px solid #117a8b;
            }
            
            .notification.warning {
                background-color: #ffc107;
                border-left: 4px solid #e0a800;
                color: #000;
            }
            
            .notification.error {
                background-color: #dc3545;
                border-left: 4px solid #c82333;
            }
        `;
        document.head.appendChild(style);
    }

    // Show notification
    function showNotification(type, message) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // Show error
    function showError(message) {
        showNotification('error', message);
    }

    // Set loading state
    function setLoading(loading) {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            if (loading) {
                loadingOverlay.classList.add('show');
            } else {
                loadingOverlay.classList.remove('show');
            }
        }
    }

    // Update dashboard with new data
    function updateDashboard(data) {
        console.log('Updating enhanced dashboard with data:', data);
        
        dashboardData = data;
        
        if (data.error) {
            showError(data.error);
            return;
        }
        
        updateConnectionStatus(true);
        updateWebSocketStatus(data.websocketConnected);
        updateQuickStats(data);
        updateEngineStatus(data.engineStatus);
        updateTaskStatistics(data.taskStatistics);
        updateMemoryStatistics(data.memoryStatistics);
        updatePerformanceMetrics(data.performanceMetrics);
        updateSystemHealth(data);
        updateRecentActivity(data.recentActivity);
        
        // Update last update timestamp
        if (data.lastUpdate) {
            const lastUpdateTime = new Date(data.lastUpdate).toLocaleTimeString();
            document.title = `VoidCat Enhanced Dashboard - Updated: ${lastUpdateTime}`;
        }
    }

    // Update realtime data
    function updateRealtime(type, data) {
        console.log('Realtime update:', type, data);
        
        switch (type) {
            case 'system':
                updateEngineStatus(data);
                break;
            case 'task':
                updateTaskStatistics(data);
                break;
            case 'memory':
                updateMemoryStatistics(data);
                break;
        }
    }

    // Update connection status
    function updateConnectionStatus(connected) {
        const statusIndicator = document.getElementById('connectionStatus');
        const statusDot = statusIndicator.querySelector('.status-dot');
        const statusText = statusIndicator.querySelector('.status-text');
        
        if (connected) {
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'Connected';
            isConnected = true;
        } else {
            statusDot.className = 'status-dot disconnected';
            statusText.textContent = 'Disconnected';
            isConnected = false;
        }
    }

    // Update WebSocket status
    function updateWebSocketStatus(connected) {
        const statusIndicator = document.getElementById('websocketStatus');
        const statusDot = statusIndicator.querySelector('.status-dot');
        const statusText = statusIndicator.querySelector('.status-text');
        
        if (connected) {
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'WebSocket: Connected';
            websocketConnected = true;
        } else {
            statusDot.className = 'status-dot disconnected';
            statusText.textContent = 'WebSocket: Disconnected';
            websocketConnected = false;
        }
    }

    // Update quick stats
    function updateQuickStats(data) {
        const quickEngineStatus = document.getElementById('quickEngineStatus');
        const quickTaskProgress = document.getElementById('quickTaskProgress');
        const quickMemoryUsage = document.getElementById('quickMemoryUsage');
        const quickPerformance = document.getElementById('quickPerformance');
        
        if (quickEngineStatus && data.engineStatus) {
            quickEngineStatus.textContent = data.engineStatus.status || 'Unknown';
            quickEngineStatus.className = 'stat-value ' + getStatusClass(data.engineStatus.status);
        }
        
        if (quickTaskProgress && data.taskStatistics) {
            const efficiency = data.taskStatistics.efficiency || 0;
            quickTaskProgress.textContent = `${efficiency}%`;
            quickTaskProgress.className = 'stat-value ' + getEfficiencyClass(efficiency);
        }
        
        if (quickMemoryUsage && data.engineStatus) {
            const memUsage = data.engineStatus.memoryUsage || 0;
            quickMemoryUsage.textContent = `${memUsage}%`;
            quickMemoryUsage.className = 'stat-value ' + getUsageClass(memUsage);
        }
        
        if (quickPerformance && data.engineStatus) {
            const responseTime = data.engineStatus.responseTime || 0;
            const perfScore = responseTime > 0 ? Math.max(0, 100 - responseTime) : 0;
            quickPerformance.textContent = `${perfScore}%`;
            quickPerformance.className = 'stat-value ' + getPerformanceClass(perfScore);
        }
    }

    // Update engine status
    function updateEngineStatus(engineStatus) {
        if (!engineStatus) return;
        
        const statusElement = document.getElementById('engineStatus');
        const uptimeElement = document.getElementById('engineUptime');
        const queriesElement = document.getElementById('totalQueries');
        const responseTimeElement = document.getElementById('avgResponseTime');
        const memoryElement = document.getElementById('memoryUsage');
        const cpuElement = document.getElementById('cpuUsage');
        
        if (statusElement) {
            statusElement.textContent = engineStatus.status || 'Unknown';
            statusElement.className = 'status-value ' + getStatusClass(engineStatus.status);
        }
        
        if (uptimeElement) {
            uptimeElement.textContent = engineStatus.uptime || '--';
        }
        
        if (queriesElement) {
            queriesElement.textContent = engineStatus.queries || 0;
        }
        
        if (responseTimeElement) {
            responseTimeElement.textContent = engineStatus.responseTime ? 
                `${engineStatus.responseTime}ms` : '--';
        }
        
        if (memoryElement) {
            memoryElement.textContent = engineStatus.memoryUsage ? 
                `${engineStatus.memoryUsage}%` : '--';
        }
        
        if (cpuElement) {
            cpuElement.textContent = engineStatus.cpuUsage ? 
                `${engineStatus.cpuUsage}%` : '--';
        }
    }

    // Update task statistics with enhanced animations
    function updateTaskStatistics(taskStats) {
        if (!taskStats) return;
        
        const completedElement = document.getElementById('completedTasks');
        const inProgressElement = document.getElementById('inProgressTasks');
        const pendingElement = document.getElementById('pendingTasks');
        const blockedElement = document.getElementById('blockedTasks');
        const efficiencyElement = document.getElementById('taskEfficiency');
        
        if (completedElement) {
            animateNumber(completedElement, taskStats.completed || 0);
        }
        
        if (inProgressElement) {
            animateNumber(inProgressElement, taskStats.inProgress || 0);
        }
        
        if (pendingElement) {
            animateNumber(pendingElement, taskStats.pending || 0);
        }
        
        if (blockedElement) {
            animateNumber(blockedElement, taskStats.blocked || 0);
        }
        
        if (efficiencyElement) {
            const efficiency = taskStats.efficiency || 0;
            efficiencyElement.textContent = `${efficiency}%`;
            
            // Animate efficiency circle
            if (animations.taskEfficiency) {
                animations.taskEfficiency.setValue(efficiency);
            }
        }
    }

    // Update memory statistics
    function updateMemoryStatistics(memoryStats) {
        if (!memoryStats) return;
        
        const totalElement = document.getElementById('totalMemories');
        const categoriesElement = document.getElementById('memoryCategories');
        const searchesElement = document.getElementById('memorySearches');
        const categoryListElement = document.getElementById('memoryCategoryList');
        
        if (totalElement) {
            animateNumber(totalElement, memoryStats.total || 0);
        }
        
        if (categoriesElement) {
            const categoryCount = Object.keys(memoryStats.categories || {}).length;
            animateNumber(categoriesElement, categoryCount);
        }
        
        if (searchesElement) {
            animateNumber(searchesElement, memoryStats.searchQueries || 0);
        }
        
        if (categoryListElement && memoryStats.categories) {
            updateMemoryCategories(categoryListElement, memoryStats.categories);
        }
    }

    // Update memory categories
    function updateMemoryCategories(container, categories) {
        container.innerHTML = '';
        
        Object.entries(categories).forEach(([category, count]) => {
            const tag = document.createElement('span');
            tag.className = 'memory-category-tag';
            tag.textContent = `${category} (${count})`;
            
            // Add click handler for category filtering
            tag.addEventListener('click', () => {
                showNotification('info', `Filtering memories by category: ${category}`);
                // Here you would implement category filtering
            });
            
            container.appendChild(tag);
        });
    }

    // Update performance metrics
    function updatePerformanceMetrics(performanceMetrics) {
        if (!performanceMetrics) return;
        
        const avgResponseElement = document.getElementById('avgResponseTimeMs');
        const systemLoadElement = document.getElementById('systemLoadPercent');
        const documentsElement = document.getElementById('documentsLoadedCount');
        
        if (avgResponseElement && performanceMetrics.queryResponseTimes) {
            const avgTime = performanceMetrics.queryResponseTimes.reduce((a, b) => a + b, 0) / 
                           performanceMetrics.queryResponseTimes.length;
            avgResponseElement.textContent = `${Math.round(avgTime)}ms`;
        }
        
        if (systemLoadElement) {
            const load = Math.round(performanceMetrics.systemLoad || 0);
            systemLoadElement.textContent = `${load}%`;
        }
        
        if (documentsElement) {
            animateNumber(documentsElement, performanceMetrics.documentsLoaded || 0);
        }
        
        // Update performance chart
        if (charts.performanceChart && performanceMetrics.queryResponseTimes) {
            const latestResponseTime = performanceMetrics.queryResponseTimes[
                performanceMetrics.queryResponseTimes.length - 1
            ];
            charts.performanceChart.addDataPoint(latestResponseTime);
        }
    }

    // Update system health
    function updateSystemHealth(data) {
        updateHealthComponent('engine', data.engineStatus?.status === 'online');
        updateHealthComponent('task', data.taskStatistics?.total > 0);
        updateHealthComponent('memory', data.memoryStatistics?.total > 0);
        updateHealthComponent('websocket', data.websocketConnected);
    }

    // Update health component
    function updateHealthComponent(component, isHealthy) {
        const iconElement = document.getElementById(`${component}HealthIcon`);
        const statusElement = document.getElementById(`${component}HealthStatus`);
        
        if (iconElement) {
            iconElement.textContent = isHealthy ? '🟢' : '🔴';
        }
        
        if (statusElement) {
            statusElement.textContent = isHealthy ? 'Healthy' : 'Issue Detected';
            statusElement.className = 'health-status ' + (isHealthy ? 'healthy' : 'unhealthy');
        }
    }

    // Update recent activity
    function updateRecentActivity(recentActivity) {
        const timelineElement = document.getElementById('activityTimeline');
        if (!timelineElement || !recentActivity) return;
        
        timelineElement.innerHTML = '';
        
        recentActivity.forEach(activity => {
            const activityItem = document.createElement('div');
            activityItem.className = 'activity-timeline-item';
            
            const timestamp = new Date(activity.timestamp);
            const timeAgo = getTimeAgo(timestamp);
            
            activityItem.innerHTML = `
                <div class="activity-icon">${activity.icon}</div>
                <div class="activity-content">
                    <div class="activity-description">${activity.description}</div>
                    <div class="activity-timestamp">${timeAgo}</div>
                </div>
            `;
            
            timelineElement.appendChild(activityItem);
        });
    }

    // Helper functions
    function getStatusClass(status) {
        switch (status) {
            case 'online': return 'status-success';
            case 'offline': return 'status-error';
            case 'degraded': return 'status-warning';
            default: return 'status-unknown';
        }
    }

    function getEfficiencyClass(efficiency) {
        if (efficiency >= 80) return 'efficiency-excellent';
        if (efficiency >= 60) return 'efficiency-good';
        if (efficiency >= 40) return 'efficiency-fair';
        return 'efficiency-poor';
    }

    function getUsageClass(usage) {
        if (usage >= 90) return 'usage-critical';
        if (usage >= 70) return 'usage-high';
        if (usage >= 50) return 'usage-medium';
        return 'usage-low';
    }

    function getPerformanceClass(score) {
        if (score >= 80) return 'performance-excellent';
        if (score >= 60) return 'performance-good';
        if (score >= 40) return 'performance-fair';
        return 'performance-poor';
    }

    function getTimeAgo(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffDays > 0) return `${diffDays}d ago`;
        if (diffHours > 0) return `${diffHours}h ago`;
        if (diffMins > 0) return `${diffMins}m ago`;
        return 'Just now';
    }

    function animateNumber(element, targetValue) {
        const currentValue = parseInt(element.textContent) || 0;
        const increment = (targetValue - currentValue) / 20;
        
        let currentStep = 0;
        const animation = setInterval(() => {
            currentStep++;
            const newValue = currentValue + (increment * currentStep);
            
            if (currentStep >= 20) {
                element.textContent = targetValue;
                clearInterval(animation);
            } else {
                element.textContent = Math.round(newValue);
            }
        }, 50);
    }

    // Global functions
    window.refreshDashboard = function() {
        console.log('Manual dashboard refresh requested');
        vscode.postMessage({ command: 'refresh' });
        showNotification('info', 'Refreshing dashboard...');
    };

    window.toggleAutoRefresh = function() {
        autoRefreshEnabled = !autoRefreshEnabled;
        vscode.postMessage({ command: 'toggleAutoRefresh' });
        
        const btn = document.getElementById('autoRefreshBtn');
        if (btn) {
            btn.classList.toggle('active', autoRefreshEnabled);
        }
        
        showNotification('info', autoRefreshEnabled ? 'Auto-refresh enabled' : 'Auto-refresh disabled');
    };

    window.exportMetrics = function() {
        vscode.postMessage({ command: 'exportMetrics' });
        showNotification('info', 'Exporting metrics...');
    };

    window.resetMetrics = function() {
        if (confirm('Are you sure you want to reset all metrics?')) {
            vscode.postMessage({ command: 'resetMetrics' });
            showNotification('info', 'Resetting metrics...');
        }
    };

    window.refreshEngineStatus = function() {
        showNotification('info', 'Refreshing engine status...');
        refreshDashboard();
    };

    window.refreshTaskStats = function() {
        showNotification('info', 'Refreshing task statistics...');
        refreshDashboard();
    };

    window.refreshMemoryStats = function() {
        showNotification('info', 'Refreshing memory statistics...');
        refreshDashboard();
    };

    window.refreshPerformanceChart = function() {
        showNotification('info', 'Refreshing performance chart...');
        refreshDashboard();
    };

    window.refreshActivity = function() {
        showNotification('info', 'Refreshing activity timeline...');
        refreshDashboard();
    };

    window.clearActivity = function() {
        if (confirm('Are you sure you want to clear the activity timeline?')) {
            showNotification('info', 'Activity timeline cleared');
            // Implementation would clear activity data
        }
    };

    window.runHealthCheck = function() {
        showNotification('info', 'Running system health check...');
        refreshDashboard();
    };

    window.openTaskManager = function() {
        vscode.postMessage({ command: 'openTaskManager' });
    };

    window.openMemoryBrowser = function() {
        vscode.postMessage({ command: 'openMemoryBrowser' });
    };

    window.requestDashboardUpdate = function() {
        vscode.postMessage({ command: 'refresh' });
    };

    // Initialize dashboard when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeEnhancedDashboard);
    } else {
        initializeEnhancedDashboard();
    }

    // Add CSS for loading overlay
    const style = document.createElement('style');
    style.textContent = `
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        }
        
        .loading-overlay.show {
            opacity: 1;
            visibility: visible;
        }
        
        .loading-spinner {
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top: 4px solid #007acc;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        .loading-text {
            margin-top: 20px;
            color: white;
            font-size: 1.1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);

})();
