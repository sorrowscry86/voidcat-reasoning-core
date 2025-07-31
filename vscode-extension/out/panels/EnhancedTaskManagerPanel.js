"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.EnhancedTaskManagerPanel = void 0;
const vscode = require("vscode");
class EnhancedTaskManagerPanel {
    static createOrShow(extensionUri, engineClient) {
        var _a;
        const column = ((_a = vscode.window.activeTextEditor) === null || _a === void 0 ? void 0 : _a.viewColumn) || vscode.ViewColumn.One;
        if (EnhancedTaskManagerPanel.currentPanel) {
            EnhancedTaskManagerPanel.currentPanel._panel.reveal(column);
            return;
        }
        const panel = vscode.window.createWebviewPanel('voidcatEnhancedTaskManager', 'VoidCat Task Manager', column, {
            enableScripts: true,
            localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')],
            retainContextWhenHidden: true
        });
        EnhancedTaskManagerPanel.currentPanel = new EnhancedTaskManagerPanel(panel, extensionUri, engineClient);
    }
    constructor(panel, extensionUri, engineClient) {
        this._disposables = [];
        this._tasks = [];
        this._projects = [];
        this._taskHierarchy = [];
        this._currentFilter = {};
        this._selectedTasks = [];
        this._isDragDropEnabled = true;
        this._panel = panel;
        this._extensionUri = extensionUri;
        this._engineClient = engineClient;
        this._panel.webview.html = this._getHtmlForWebview();
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        // Enhanced message handling
        this._panel.webview.onDidReceiveMessage((message) => __awaiter(this, void 0, void 0, function* () {
            yield this.handleWebviewMessage(message);
        }), null, this._disposables);
        // Initialize the panel
        this.initialize();
    }
    initialize() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                // Load initial data
                yield this.loadAllData();
                // Setup auto-refresh
                this.startAutoRefresh();
                // Setup WebSocket event listeners for real-time updates
                this._engineClient.addEventListener('taskUpdate', (data) => {
                    this.handleRealtimeTaskUpdate(data);
                });
                this._panel.webview.postMessage({
                    command: 'initialized',
                    message: 'Task Manager initialized successfully'
                });
            }
            catch (error) {
                console.error('Task Manager initialization failed:', error);
                this._panel.webview.postMessage({
                    command: 'error',
                    message: 'Failed to initialize Task Manager: ' + error
                });
            }
        });
    }
    handleWebviewMessage(message) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                switch (message.command) {
                    // Data Operations
                    case 'loadData':
                        yield this.loadAllData();
                        break;
                    case 'refreshData':
                        yield this.refreshData();
                        break;
                    // Task CRUD Operations
                    case 'createTask':
                        yield this.createTask(message.taskData);
                        break;
                    case 'updateTask':
                        yield this.updateTask(message.taskId, message.updates);
                        break;
                    case 'deleteTask':
                        yield this.deleteTask(message.taskId);
                        break;
                    case 'duplicateTask':
                        yield this.duplicateTask(message.taskId);
                        break;
                    case 'bulkUpdateTasks':
                        yield this.bulkUpdateTasks(message.taskIds, message.updates);
                        break;
                    // Task Hierarchy Operations
                    case 'moveTask':
                        yield this.moveTask(message.taskId, message.newParentId, message.newPosition);
                        break;
                    case 'reorderTasks':
                        yield this.reorderTasks(message.taskIds, message.newOrder);
                        break;
                    case 'promoteTask':
                        yield this.promoteTask(message.taskId);
                        break;
                    case 'demoteTask':
                        yield this.demoteTask(message.taskId, message.newParentId);
                        break;
                    // Project Operations
                    case 'createProject':
                        yield this.createProject(message.projectData);
                        break;
                    case 'updateProject':
                        yield this.updateProject(message.projectId, message.updates);
                        break;
                    case 'deleteProject':
                        yield this.deleteProject(message.projectId);
                        break;
                    // Filtering and Search
                    case 'applyFilter':
                        yield this.applyFilter(message.filter);
                        break;
                    case 'clearFilter':
                        yield this.clearFilter();
                        break;
                    case 'searchTasks':
                        yield this.searchTasks(message.searchTerm);
                        break;
                    // Selection Operations
                    case 'selectTask':
                        this.selectTask(message.taskId, message.multiSelect);
                        break;
                    case 'selectAll':
                        this.selectAllTasks();
                        break;
                    case 'clearSelection':
                        this.clearSelection();
                        break;
                    // View Operations
                    case 'expandAll':
                        this.expandAllTasks();
                        break;
                    case 'collapseAll':
                        this.collapseAllTasks();
                        break;
                    case 'setViewMode':
                        this.setViewMode(message.mode);
                        break;
                    // Export/Import Operations
                    case 'exportTasks':
                        yield this.exportTasks(message.format);
                        break;
                    case 'importTasks':
                        yield this.importTasks(message.data);
                        break;
                    // Settings and Configuration
                    case 'updateSettings':
                        this.updateSettings(message.settings);
                        break;
                    case 'toggleAutoRefresh':
                        this.toggleAutoRefresh();
                        break;
                    case 'toggleDragDrop':
                        this.toggleDragDrop();
                        break;
                    default:
                        console.warn('Unknown task manager command:', message.command);
                }
            }
            catch (error) {
                console.error('Error handling webview message:', error);
                this._panel.webview.postMessage({
                    command: 'error',
                    message: 'Operation failed: ' + error
                });
            }
        });
    }
    loadAllData() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                // Load projects and tasks
                const [projects, tasks] = yield Promise.all([
                    this._engineClient.getProjects(),
                    this._engineClient.getTasks()
                ]);
                this._projects = projects;
                this._tasks = tasks;
                // Build task hierarchy
                this._taskHierarchy = this.buildTaskHierarchy(tasks);
                // Calculate statistics
                const stats = this.calculateTaskStats(tasks);
                // Send updated data to webview
                this._panel.webview.postMessage({
                    command: 'updateData',
                    data: {
                        tasks: this._tasks,
                        projects: this._projects,
                        hierarchy: this._taskHierarchy,
                        stats: stats,
                        filter: this._currentFilter,
                        selectedTasks: this._selectedTasks
                    }
                });
            }
            catch (error) {
                console.error('Failed to load task data:', error);
                this._panel.webview.postMessage({
                    command: 'error',
                    message: 'Failed to load task data: ' + error
                });
            }
        });
    }
    buildTaskHierarchy(tasks) {
        const taskMap = new Map();
        const rootTasks = [];
        // Create task map
        tasks.forEach(task => {
            taskMap.set(task.id, task);
        });
        // Build hierarchy
        const processTask = (task, level = 0) => {
            const children = [];
            // Find child tasks
            tasks.forEach(childTask => {
                if (childTask.parentId === task.id) {
                    children.push(processTask(childTask, level + 1));
                }
            });
            // Sort children by priority and creation date
            children.sort((a, b) => {
                if (a.task.priority !== b.task.priority) {
                    return b.task.priority - a.task.priority; // Higher priority first
                }
                return new Date(a.task.createdAt).getTime() - new Date(b.task.createdAt).getTime();
            });
            return {
                task,
                children,
                level,
                parentTask: task.parentId ? taskMap.get(task.parentId) : undefined
            };
        };
        // Find root tasks (tasks without parentId)
        tasks.forEach(task => {
            if (!task.parentId) {
                rootTasks.push(processTask(task));
            }
        });
        // Sort root tasks by priority and creation date
        rootTasks.sort((a, b) => {
            if (a.task.priority !== b.task.priority) {
                return b.task.priority - a.task.priority;
            }
            return new Date(a.task.createdAt).getTime() - new Date(b.task.createdAt).getTime();
        });
        return rootTasks;
    }
    calculateTaskStats(tasks) {
        const stats = {
            total: tasks.length,
            completed: 0,
            inProgress: 0,
            pending: 0,
            blocked: 0,
            overdue: 0,
            completionRate: 0,
            avgCompletionTime: 0
        };
        let totalCompletionTime = 0;
        let completedTasksWithTime = 0;
        const now = new Date();
        tasks.forEach(task => {
            switch (task.status) {
                case 'completed':
                    stats.completed++;
                    if (task.actualHours) {
                        totalCompletionTime += task.actualHours;
                        completedTasksWithTime++;
                    }
                    break;
                case 'in-progress':
                    stats.inProgress++;
                    break;
                case 'pending':
                    stats.pending++;
                    break;
                case 'blocked':
                    stats.blocked++;
                    break;
            }
            // Check for overdue tasks (simplified - would need due date field)
            // For now, consider tasks in-progress for more than estimatedHours as potentially overdue
            if (task.status === 'in-progress' && task.estimatedHours && task.actualHours) {
                if (task.actualHours > task.estimatedHours * 1.5) {
                    stats.overdue++;
                }
            }
        });
        stats.completionRate = stats.total > 0 ? (stats.completed / stats.total) * 100 : 0;
        stats.avgCompletionTime = completedTasksWithTime > 0 ? totalCompletionTime / completedTasksWithTime : 0;
        return stats;
    }
    // Task CRUD Operations
    createTask(taskData) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const newTask = yield this._engineClient.createTask(taskData);
                this._tasks.push(newTask);
                yield this.loadAllData();
                this._panel.webview.postMessage({
                    command: 'taskCreated',
                    task: newTask,
                    message: `Task "${newTask.name}" created successfully`
                });
            }
            catch (error) {
                console.error('Failed to create task:', error);
                throw error;
            }
        });
    }
    updateTask(taskId, updates) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const updatedTask = yield this._engineClient.updateTask(taskId, updates);
                const index = this._tasks.findIndex(t => t.id === taskId);
                if (index !== -1) {
                    this._tasks[index] = updatedTask;
                }
                yield this.loadAllData();
                this._panel.webview.postMessage({
                    command: 'taskUpdated',
                    task: updatedTask,
                    message: `Task "${updatedTask.name}" updated successfully`
                });
            }
            catch (error) {
                console.error('Failed to update task:', error);
                throw error;
            }
        });
    }
    deleteTask(taskId) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                yield this._engineClient.deleteTask(taskId);
                this._tasks = this._tasks.filter(t => t.id !== taskId);
                this._selectedTasks = this._selectedTasks.filter(id => id !== taskId);
                yield this.loadAllData();
                this._panel.webview.postMessage({
                    command: 'taskDeleted',
                    taskId: taskId,
                    message: 'Task deleted successfully'
                });
            }
            catch (error) {
                console.error('Failed to delete task:', error);
                throw error;
            }
        });
    }
    duplicateTask(taskId) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const originalTask = this._tasks.find(t => t.id === taskId);
                if (!originalTask) {
                    throw new Error('Task not found');
                }
                const duplicateData = {
                    name: `${originalTask.name} (Copy)`,
                    description: originalTask.description,
                    priority: originalTask.priority,
                    complexity: originalTask.complexity,
                    estimatedHours: originalTask.estimatedHours,
                    tags: [...(originalTask.tags || [])],
                    parentId: originalTask.parentId,
                    status: 'pending'
                };
                yield this.createTask(duplicateData);
            }
            catch (error) {
                console.error('Failed to duplicate task:', error);
                throw error;
            }
        });
    }
    bulkUpdateTasks(taskIds, updates) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const updatePromises = taskIds.map(id => this._engineClient.updateTask(id, updates));
                yield Promise.all(updatePromises);
                yield this.loadAllData();
                this._panel.webview.postMessage({
                    command: 'bulkUpdateComplete',
                    taskIds: taskIds,
                    message: `${taskIds.length} tasks updated successfully`
                });
            }
            catch (error) {
                console.error('Failed to bulk update tasks:', error);
                throw error;
            }
        });
    }
    // Hierarchy Operations  
    moveTask(taskId, newParentId, newPosition) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const updates = {
                    parentId: newParentId || undefined
                };
                yield this.updateTask(taskId, updates);
            }
            catch (error) {
                console.error('Failed to move task:', error);
                throw error;
            }
        });
    }
    reorderTasks(taskIds, newOrder) {
        return __awaiter(this, void 0, void 0, function* () {
            // Implementation would depend on having an order field in tasks
            console.log('Reorder tasks:', taskIds, newOrder);
            // For now, just reload data to reflect any changes
            yield this.loadAllData();
        });
    }
    promoteTask(taskId) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const task = this._tasks.find(t => t.id === taskId);
                if (!task || !task.parentId) {
                    return; // Already at root level
                }
                const parentTask = this._tasks.find(t => t.id === task.parentId);
                const newParentId = (parentTask === null || parentTask === void 0 ? void 0 : parentTask.parentId) || null;
                yield this.moveTask(taskId, newParentId);
            }
            catch (error) {
                console.error('Failed to promote task:', error);
                throw error;
            }
        });
    }
    demoteTask(taskId, newParentId) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                yield this.moveTask(taskId, newParentId);
            }
            catch (error) {
                console.error('Failed to demote task:', error);
                throw error;
            }
        });
    }
    // Project Operations
    createProject(projectData) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                // Assuming the engine client has a createProject method
                // const newProject = await this._engineClient.createProject(projectData);
                // For now, show a message that this feature is coming
                this._panel.webview.postMessage({
                    command: 'info',
                    message: 'Project creation feature coming soon'
                });
            }
            catch (error) {
                console.error('Failed to create project:', error);
                throw error;
            }
        });
    }
    updateProject(projectId, updates) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                // Implementation would call engine client
                console.log('Update project:', projectId, updates);
            }
            catch (error) {
                console.error('Failed to update project:', error);
                throw error;
            }
        });
    }
    deleteProject(projectId) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                // Implementation would call engine client
                console.log('Delete project:', projectId);
            }
            catch (error) {
                console.error('Failed to delete project:', error);
                throw error;
            }
        });
    }
    // Filtering and Search
    applyFilter(filter) {
        return __awaiter(this, void 0, void 0, function* () {
            this._currentFilter = filter;
            yield this.loadAllData(); // Reload with filter applied
        });
    }
    clearFilter() {
        return __awaiter(this, void 0, void 0, function* () {
            this._currentFilter = {};
            yield this.loadAllData();
        });
    }
    searchTasks(searchTerm) {
        return __awaiter(this, void 0, void 0, function* () {
            this._currentFilter.search = searchTerm;
            yield this.loadAllData();
        });
    }
    // Selection Operations
    selectTask(taskId, multiSelect = false) {
        if (multiSelect) {
            if (this._selectedTasks.includes(taskId)) {
                this._selectedTasks = this._selectedTasks.filter(id => id !== taskId);
            }
            else {
                this._selectedTasks.push(taskId);
            }
        }
        else {
            this._selectedTasks = [taskId];
        }
        this._panel.webview.postMessage({
            command: 'selectionChanged',
            selectedTasks: this._selectedTasks
        });
    }
    selectAllTasks() {
        this._selectedTasks = this._tasks.map(t => t.id);
        this._panel.webview.postMessage({
            command: 'selectionChanged',
            selectedTasks: this._selectedTasks
        });
    }
    clearSelection() {
        this._selectedTasks = [];
        this._panel.webview.postMessage({
            command: 'selectionChanged',
            selectedTasks: this._selectedTasks
        });
    }
    // View Operations
    expandAllTasks() {
        this._panel.webview.postMessage({
            command: 'expandAll'
        });
    }
    collapseAllTasks() {
        this._panel.webview.postMessage({
            command: 'collapseAll'
        });
    }
    setViewMode(mode) {
        this._panel.webview.postMessage({
            command: 'setViewMode',
            mode: mode
        });
    }
    // Export/Import Operations
    exportTasks(format) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                let exportData;
                switch (format) {
                    case 'json':
                        exportData = JSON.stringify({
                            tasks: this._tasks,
                            projects: this._projects,
                            hierarchy: this._taskHierarchy,
                            exportDate: new Date().toISOString()
                        }, null, 2);
                        break;
                    case 'csv':
                        exportData = this.convertTasksToCSV(this._tasks);
                        break;
                    default:
                        throw new Error('Unsupported export format');
                }
                const document = yield vscode.workspace.openTextDocument({
                    content: exportData,
                    language: format === 'json' ? 'json' : 'csv'
                });
                yield vscode.window.showTextDocument(document);
                this._panel.webview.postMessage({
                    command: 'exportComplete',
                    format: format,
                    message: `Tasks exported as ${format.toUpperCase()}`
                });
            }
            catch (error) {
                console.error('Failed to export tasks:', error);
                throw error;
            }
        });
    }
    convertTasksToCSV(tasks) {
        const headers = ['ID', 'Name', 'Description', 'Status', 'Priority', 'Complexity', 'Estimated Hours', 'Actual Hours', 'Tags', 'Created At', 'Updated At'];
        const rows = tasks.map(task => {
            var _a, _b;
            return [
                task.id,
                task.name,
                task.description || '',
                task.status,
                task.priority.toString(),
                task.complexity.toString(),
                ((_a = task.estimatedHours) === null || _a === void 0 ? void 0 : _a.toString()) || '',
                ((_b = task.actualHours) === null || _b === void 0 ? void 0 : _b.toString()) || '',
                (task.tags || []).join(';'),
                task.createdAt,
                task.updatedAt
            ];
        });
        return [headers, ...rows].map(row => row.map(cell => `"${(cell || '').toString().replace(/"/g, '""')}"`).join(',')).join('\n');
    }
    importTasks(data) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                // Implementation for importing tasks
                console.log('Import tasks:', data);
                this._panel.webview.postMessage({
                    command: 'info',
                    message: 'Task import feature coming soon'
                });
            }
            catch (error) {
                console.error('Failed to import tasks:', error);
                throw error;
            }
        });
    }
    // Settings and Configuration
    updateSettings(settings) {
        // Apply settings to the task manager
        if (settings.autoRefresh !== undefined) {
            if (settings.autoRefresh) {
                this.startAutoRefresh();
            }
            else {
                this.stopAutoRefresh();
            }
        }
        if (settings.dragDropEnabled !== undefined) {
            this._isDragDropEnabled = settings.dragDropEnabled;
        }
        this._panel.webview.postMessage({
            command: 'settingsUpdated',
            settings: settings
        });
    }
    toggleAutoRefresh() {
        if (this._autoRefreshInterval) {
            this.stopAutoRefresh();
        }
        else {
            this.startAutoRefresh();
        }
    }
    toggleDragDrop() {
        this._isDragDropEnabled = !this._isDragDropEnabled;
        this._panel.webview.postMessage({
            command: 'dragDropToggled',
            enabled: this._isDragDropEnabled
        });
    }
    // Utility Methods
    startAutoRefresh() {
        if (this._autoRefreshInterval) {
            clearInterval(this._autoRefreshInterval);
        }
        this._autoRefreshInterval = setInterval(() => __awaiter(this, void 0, void 0, function* () {
            yield this.refreshData();
        }), 30000); // Refresh every 30 seconds
    }
    stopAutoRefresh() {
        if (this._autoRefreshInterval) {
            clearInterval(this._autoRefreshInterval);
            this._autoRefreshInterval = undefined;
        }
    }
    refreshData() {
        return __awaiter(this, void 0, void 0, function* () {
            yield this.loadAllData();
            this._panel.webview.postMessage({
                command: 'dataRefreshed',
                timestamp: new Date().toISOString()
            });
        });
    }
    handleRealtimeTaskUpdate(data) {
        // Handle real-time updates from WebSocket
        this._panel.webview.postMessage({
            command: 'realtimeUpdate',
            type: 'task',
            data: data
        });
        // Refresh data to get latest state
        this.refreshData();
    }
    _getHtmlForWebview() {
        const scriptPathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'media', 'task-manager.js');
        const scriptUri = this._panel.webview.asWebviewUri(scriptPathOnDisk);
        const stylePathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'media', 'task-manager.css');
        const styleUri = this._panel.webview.asWebviewUri(stylePathOnDisk);
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${this._panel.webview.cspSource} 'unsafe-inline'; script-src ${this._panel.webview.cspSource} 'unsafe-inline';">
            <link href="${styleUri}" rel="stylesheet">
            <title>VoidCat Task Manager</title>
        </head>
        <body>
            <div class="task-manager-container">
                <!-- Task Manager Header -->
                <header class="task-manager-header">
                    <div class="header-left">
                        <h1>📋 VoidCat Task Manager</h1>
                        <div class="task-stats-summary" id="taskStatsSummary">
                            <span class="stat-item">
                                <span class="stat-value" id="totalTasks">0</span>
                                <span class="stat-label">Total</span>
                            </span>
                            <span class="stat-item">
                                <span class="stat-value" id="completedTasks">0</span>
                                <span class="stat-label">Completed</span>
                            </span>
                            <span class="stat-item">
                                <span class="stat-value" id="completionRate">0%</span>
                                <span class="stat-label">Complete</span>
                            </span>
                        </div>
                    </div>
                    <div class="header-right">
                        <div class="header-actions">
                            <button class="action-btn primary" onclick="createNewTask()">
                                <span class="btn-icon">➕</span>
                                <span class="btn-text">New Task</span>
                            </button>
                            <button class="action-btn" onclick="createNewProject()">
                                <span class="btn-icon">📁</span>
                                <span class="btn-text">New Project</span>
                            </button>
                            <button class="action-btn" onclick="refreshTasks()">
                                <span class="btn-icon">🔄</span>
                                <span class="btn-text">Refresh</span>
                            </button>
                            <button class="action-btn" onclick="showFilterDialog()">
                                <span class="btn-icon">🔍</span>
                                <span class="btn-text">Filter</span>
                            </button>
                            <div class="dropdown">
                                <button class="action-btn dropdown-toggle" onclick="toggleViewMenu()">
                                    <span class="btn-icon">⚙️</span>
                                    <span class="btn-text">View</span>
                                </button>
                                <div class="dropdown-menu" id="viewMenu">
                                    <a href="#" onclick="setViewMode('hierarchical')">📊 Hierarchical</a>
                                    <a href="#" onclick="setViewMode('flat')">📋 Flat List</a>
                                    <a href="#" onclick="setViewMode('kanban')">📌 Kanban</a>
                                    <div class="dropdown-divider"></div>
                                    <a href="#" onclick="expandAllTasks()">⬇️ Expand All</a>
                                    <a href="#" onclick="collapseAllTasks()">⬆️ Collapse All</a>
                                    <div class="dropdown-divider"></div>
                                    <a href="#" onclick="exportTasks('json')">📄 Export JSON</a>
                                    <a href="#" onclick="exportTasks('csv')">📊 Export CSV</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </header>

                <!-- Main Task Manager Content -->
                <div class="task-manager-content">
                    <!-- Filter Bar -->
                    <div class="filter-bar" id="filterBar">
                        <div class="filter-controls">
                            <div class="search-box">
                                <input type="text" id="searchInput" placeholder="Search tasks..." onkeyup="handleSearch()" />
                                <button class="search-btn" onclick="clearSearch()">✕</button>
                            </div>
                            <div class="filter-controls">
                                <select id="statusFilter" onchange="applyFilters()">
                                    <option value="">All Status</option>
                                    <option value="pending">Pending</option>
                                    <option value="in-progress">In Progress</option>
                                    <option value="completed">Completed</option>
                                    <option value="blocked">Blocked</option>
                                </select>
                                <select id="priorityFilter" onchange="applyFilters()">
                                    <option value="">All Priority</option>
                                    <option value="high">High (8-10)</option>
                                    <option value="medium">Medium (5-7)</option>
                                    <option value="low">Low (1-4)</option>
                                </select>
                                <select id="projectFilter" onchange="applyFilters()">
                                    <option value="">All Projects</option>
                                </select>
                                <button class="filter-btn" onclick="clearAllFilters()">Clear Filters</button>
                            </div>
                        </div>
                        <div class="active-filters" id="activeFilters">
                            <!-- Active filter tags will be displayed here -->
                        </div>
                    </div>

                    <!-- Task List Container -->
                    <div class="task-list-container">
                        <!-- Task Statistics Panel -->
                        <div class="task-stats-panel" id="taskStatsPanel">
                            <h3>📊 Statistics</h3>
                            <div class="stats-grid">
                                <div class="stat-card">
                                    <div class="stat-value" id="statTotal">0</div>
                                    <div class="stat-label">Total Tasks</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-value" id="statCompleted">0</div>
                                    <div class="stat-label">Completed</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-value" id="statInProgress">0</div>
                                    <div class="stat-label">In Progress</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-value" id="statPending">0</div>
                                    <div class="stat-label">Pending</div>
                                </div>
                            </div>
                            <div class="progress-visualization">
                                <div class="progress-bar">
                                    <div class="progress-fill" id="overallProgress"></div>
                                </div>
                                <div class="progress-text" id="progressText">0% Complete</div>
                            </div>
                        </div>

                        <!-- Task Hierarchy Display -->
                        <div class="task-hierarchy" id="taskHierarchy">
                            <div class="hierarchy-header">
                                <h3>🌳 Task Hierarchy</h3>
                                <div class="hierarchy-controls">
                                    <button class="control-btn" onclick="expandAllTasks()" title="Expand All">⬇️</button>
                                    <button class="control-btn" onclick="collapseAllTasks()" title="Collapse All">⬆️</button>
                                    <button class="control-btn" onclick="toggleDragDrop()" title="Toggle Drag & Drop" id="dragDropToggle">🔄</button>
                                </div>
                            </div>
                            <div class="task-tree" id="taskTree">
                                <!-- Task hierarchy will be rendered here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Task Creation/Edit Modal -->
            <div class="modal-overlay" id="taskModal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3 id="modalTitle">Create New Task</h3>
                        <button class="modal-close" onclick="closeTaskModal()">✕</button>
                    </div>
                    <div class="modal-body">
                        <form id="taskForm">
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="taskName">Task Name *</label>
                                    <input type="text" id="taskName" required />
                                </div>
                                <div class="form-group">
                                    <label for="taskProject">Project</label>
                                    <select id="taskProject"></select>
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="taskDescription">Description</label>
                                <textarea id="taskDescription" rows="3"></textarea>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="taskStatus">Status</label>
                                    <select id="taskStatus">
                                        <option value="pending">Pending</option>
                                        <option value="in-progress">In Progress</option>
                                        <option value="completed">Completed</option>
                                        <option value="blocked">Blocked</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="taskPriority">Priority</label>
                                    <input type="range" id="taskPriority" min="1" max="10" value="5" />
                                    <span id="priorityValue">5</span>
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="taskComplexity">Complexity</label>
                                    <input type="range" id="taskComplexity" min="1" max="10" value="5" />
                                    <span id="complexityValue">5</span>
                                </div>
                                <div class="form-group">
                                    <label for="taskEstimatedHours">Estimated Hours</label>
                                    <input type="number" id="taskEstimatedHours" min="0" step="0.5" />
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="taskTags">Tags (comma-separated)</label>
                                <input type="text" id="taskTags" placeholder="tag1, tag2, tag3" />
                            </div>
                            <div class="form-group">
                                <label for="taskParent">Parent Task</label>
                                <select id="taskParent">
                                    <option value="">No Parent (Root Level)</option>
                                </select>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button class="btn secondary" onclick="closeTaskModal()">Cancel</button>
                        <button class="btn primary" onclick="saveTask()">Save Task</button>
                    </div>
                </div>
            </div>

            <!-- Loading Overlay -->
            <div class="loading-overlay" id="loadingOverlay">
                <div class="loading-spinner"></div>
                <div class="loading-text">Loading tasks...</div>
            </div>

            <!-- Notification Container -->
            <div class="notification-container" id="notificationContainer"></div>

            <script src="${scriptUri}"></script>
        </body>
        </html>`;
    }
    dispose() {
        this.stopAutoRefresh();
        EnhancedTaskManagerPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}
exports.EnhancedTaskManagerPanel = EnhancedTaskManagerPanel;
//# sourceMappingURL=EnhancedTaskManagerPanel.js.map