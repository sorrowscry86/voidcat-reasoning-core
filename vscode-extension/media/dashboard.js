// VoidCat Dashboard JavaScript
(function() {
    'use strict';

    // VS Code API
    const vscode = acquireVsCodeApi();

    // Dashboard state
    let dashboardData = null;
    let isConnected = false;
    let charts = {};
    let updateInterval = null;

    // Initialize dashboard
    function initializeDashboard() {
        console.log('Initializing VoidCat Dashboard...');
        
        // Set up event listeners
        setupEventListeners();
        
        // Initialize charts
        initializeCharts();
        
        // Request initial data
        requestDashboardUpdate();
        
        // Set up periodic updates
        startPeriodicUpdates();
        
        console.log('Dashboard initialized successfully');
    }

    // Setup event listeners
    function setupEventListeners() {
        // Listen for messages from the extension
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.command) {
                case 'updateDashboard':
                    updateDashboard(message.data);
                    break;
                default:
                    console.warn('Unknown message command:', message.command);
            }
        });
    }

    // Initialize charts
    function initializeCharts() {
        const queryChartCanvas = document.getElementById('queryChart');
        if (queryChartCanvas) {
            const ctx = queryChartCanvas.getContext('2d');
            
            // Simple chart implementation (can be replaced with Chart.js)
            charts.queryChart = {
                canvas: queryChartCanvas,
                ctx: ctx,
                data: [],
                render: function() {
                    const width = this.canvas.width;
                    const height = this.canvas.height;
                    
                    // Clear canvas
                    this.ctx.clearRect(0, 0, width, height);
                    
                    // Draw grid
                    this.ctx.strokeStyle = '#333';
                    this.ctx.lineWidth = 1;
                    
                    // Vertical lines
                    for (let i = 0; i <= 10; i++) {
                        const x = (width / 10) * i;
                        this.ctx.beginPath();
                        this.ctx.moveTo(x, 0);
                        this.ctx.lineTo(x, height);
                        this.ctx.stroke();
                    }
                    
                    // Horizontal lines
                    for (let i = 0; i <= 5; i++) {
                        const y = (height / 5) * i;
                        this.ctx.beginPath();
                        this.ctx.moveTo(0, y);
                        this.ctx.lineTo(width, y);
                        this.ctx.stroke();
                    }
                    
                    // Draw data line
                    if (this.data.length > 1) {
                        this.ctx.strokeStyle = '#007acc';
                        this.ctx.lineWidth = 2;
                        this.ctx.beginPath();
                        
                        for (let i = 0; i < this.data.length; i++) {
                            const x = (width / (this.data.length - 1)) * i;
                            const y = height - (this.data[i] / 100) * height;
                            
                            if (i === 0) {
                                this.ctx.moveTo(x, y);
                            } else {
                                this.ctx.lineTo(x, y);
                            }
                        }
                        
                        this.ctx.stroke();
                    }
                }
            };
        }
    }

    // Update dashboard with new data
    function updateDashboard(data) {
        console.log('Updating dashboard with data:', data);
        
        dashboardData = data;
        
        if (data.error) {
            handleError(data.error);
            return;
        }
        
        updateConnectionStatus(true);
        updateEngineStatus(data);
        updateTaskStatistics(data);
        updateMemoryStatistics(data);
        updatePerformanceMetrics(data);
        updateSystemHealth(data);
        updateRecentActivity(data);
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

    // Update engine status
    function updateEngineStatus(data) {
        const engineStatus = document.getElementById('engineStatus');
        const engineUptime = document.getElementById('engineUptime');
        const totalQueries = document.getElementById('totalQueries');
        const websocketStatus = document.getElementById('websocketStatus');
        
        if (engineStatus) {
            engineStatus.textContent = data.system_status || 'Unknown';
            engineStatus.className = 'status-value ' + (data.system_status === 'online' ? 'status-success' : 'status-error');
        }
        
        if (engineUptime) {
            engineUptime.textContent = data.uptime || '--';
        }
        
        if (totalQueries) {
            totalQueries.textContent = data.task_statistics?.total || '--';
        }
        
        if (websocketStatus) {
            websocketStatus.textContent = data.websocket_connected ? 'Connected' : 'Disconnected';
            websocketStatus.className = 'status-value ' + (data.websocket_connected ? 'status-success' : 'status-error');
        }
    }

    // Update task statistics
    function updateTaskStatistics(data) {
        const taskStats = data.task_statistics;
        if (!taskStats) return;
        
        const totalTasks = document.getElementById('totalTasks');
        const completedTasks = document.getElementById('completedTasks');
        const inProgressTasks = document.getElementById('inProgressTasks');
        const pendingTasks = document.getElementById('pendingTasks');
        const taskProgress = document.getElementById('taskProgress');
        
        if (totalTasks) totalTasks.textContent = taskStats.total || 0;
        if (completedTasks) completedTasks.textContent = taskStats.completed || 0;
        if (inProgressTasks) inProgressTasks.textContent = taskStats.in_progress || 0;
        if (pendingTasks) pendingTasks.textContent = taskStats.pending || 0;
        
        // Update progress bar
        if (taskProgress && taskStats.total > 0) {
            const progressPercentage = (taskStats.completed / taskStats.total) * 100;
            taskProgress.style.width = progressPercentage + '%';
        }
    }

    // Update memory statistics
    function updateMemoryStatistics(data) {
        const memoryStats = data.memory_statistics;
        if (!memoryStats) return;
        
        const totalMemories = document.getElementById('totalMemories');
        const memoryCategories = document.getElementById('memoryCategories');
        const memoryCategoryList = document.getElementById('memoryCategoryList');
        
        if (totalMemories) totalMemories.textContent = memoryStats.total || 0;
        if (memoryCategories) memoryCategories.textContent = Object.keys(memoryStats.categories || {}).length;
        
        // Update category list
        if (memoryCategoryList && memoryStats.categories) {
            memoryCategoryList.innerHTML = '';
            
            Object.entries(memoryStats.categories).forEach(([category, count]) => {
                const tag = document.createElement('span');
                tag.className = 'memory-category-tag';
                tag.textContent = `${category} (${count})`;
                memoryCategoryList.appendChild(tag);
            });
        }
    }

    // Update performance metrics
    function updatePerformanceMetrics(data) {
        const documentsLoaded = document.getElementById('documentsLoaded');
        
        if (documentsLoaded) {
            documentsLoaded.textContent = data.documents_loaded || '--';
        }
        
        // Update query chart
        if (charts.queryChart) {
            // Add new data point (simulated for now)
            const responseTime = Math.random() * 100;
            charts.queryChart.data.push(responseTime);
            
            // Keep only last 10 data points
            if (charts.queryChart.data.length > 10) {
                charts.queryChart.data.shift();
            }
            
            charts.queryChart.render();
        }
    }

    // Update system health
    function updateSystemHealth(data) {
        const engineHealthIcon = document.getElementById('engineHealthIcon');
        const taskHealthIcon = document.getElementById('taskHealthIcon');
        const memoryHealthIcon = document.getElementById('memoryHealthIcon');
        const apiHealthIcon = document.getElementById('apiHealthIcon');
        
        // Engine health
        if (engineHealthIcon) {
            engineHealthIcon.textContent = data.system_status === 'online' ? '🟢' : '🔴';
        }
        
        // Task health
        if (taskHealthIcon) {
            const taskStats = data.task_statistics;
            const isHealthy = taskStats && taskStats.total > 0;
            taskHealthIcon.textContent = isHealthy ? '🟢' : '🟡';
        }
        
        // Memory health
        if (memoryHealthIcon) {
            const memoryStats = data.memory_statistics;
            const isHealthy = memoryStats && memoryStats.total > 0;
            memoryHealthIcon.textContent = isHealthy ? '🟢' : '🟡';
        }
        
        // API health
        if (apiHealthIcon) {
            apiHealthIcon.textContent = data.websocket_connected ? '🟢' : '🟡';
        }
    }

    // Update recent activity
    function updateRecentActivity(data) {
        const activityList = document.getElementById('activityList');
        if (!activityList) return;
        
        // Clear existing activity
        activityList.innerHTML = '';
        
        // Add sample activity items (these would come from actual data)
        const activities = [
            { icon: '✅', title: 'Task completed', time: '2 minutes ago' },
            { icon: '🔄', title: 'Dashboard refreshed', time: '5 minutes ago' },
            { icon: '📝', title: 'Memory added', time: '10 minutes ago' },
            { icon: '🚀', title: 'Engine started', time: '1 hour ago' }
        ];
        
        activities.forEach(activity => {
            const activityItem = document.createElement('div');
            activityItem.className = 'activity-item';
            
            activityItem.innerHTML = `
                <div class="activity-icon">${activity.icon}</div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-time">${activity.time}</div>
                </div>
            `;
            
            activityList.appendChild(activityItem);
        });
    }

    // Handle errors
    function handleError(error) {
        console.error('Dashboard error:', error);
        updateConnectionStatus(false);
        
        // Show error message in dashboard
        const errorMessage = document.createElement('div');
        errorMessage.className = 'error-message';
        errorMessage.textContent = 'Error: ' + error;
        
        document.body.appendChild(errorMessage);
        
        setTimeout(() => {
            errorMessage.remove();
        }, 5000);
    }

    // Request dashboard update
    function requestDashboardUpdate() {
        console.log('Requesting dashboard update...');
        // This would typically send a message to the extension
        // For now, we'll simulate it
    }

    // Start periodic updates
    function startPeriodicUpdates() {
        if (updateInterval) {
            clearInterval(updateInterval);
        }
        
        updateInterval = setInterval(() => {
            requestDashboardUpdate();
        }, 5000); // Update every 5 seconds
    }

    // Stop periodic updates
    function stopPeriodicUpdates() {
        if (updateInterval) {
            clearInterval(updateInterval);
            updateInterval = null;
        }
    }

    // Global refresh function
    window.refreshDashboard = function() {
        console.log('Manual dashboard refresh requested');
        requestDashboardUpdate();
    };

    // Initialize dashboard when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeDashboard);
    } else {
        initializeDashboard();
    }

    // Cleanup on unload
    window.addEventListener('beforeunload', () => {
        stopPeriodicUpdates();
    });

})();