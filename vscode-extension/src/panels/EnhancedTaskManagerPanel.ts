import * as vscode from 'vscode';
import { VoidCatEngineClient, VoidCatTask, VoidCatProject } from '../VoidCatEngineClient';

export interface TaskHierarchy {
    task: VoidCatTask;
    children: TaskHierarchy[];
    level: number;
    parentTask?: VoidCatTask;
}

export interface TaskFilter {
    status?: string[];
    priority?: { min: number; max: number };
    assignee?: string;
    project?: string;
    tags?: string[];
    search?: string;
    dueDate?: { start?: Date; end?: Date };
}

export interface TaskStats {
    total: number;
    completed: number;
    inProgress: number;
    pending: number;
    blocked: number;
    overdue: number;
    completionRate: number;
    avgCompletionTime: number;
}

export class EnhancedTaskManagerPanel {
    public static currentPanel: EnhancedTaskManagerPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private readonly _engineClient: VoidCatEngineClient;
    private _disposables: vscode.Disposable[] = [];
    private _tasks: VoidCatTask[] = [];
    private _projects: VoidCatProject[] = [];
    private _taskHierarchy: TaskHierarchy[] = [];
    private _currentFilter: TaskFilter = {};
    private _selectedTasks: string[] = [];
    private _autoRefreshInterval?: NodeJS.Timer;
    private _isDragDropEnabled: boolean = true;

    public static createOrShow(extensionUri: vscode.Uri, engineClient: VoidCatEngineClient) {
        const column = vscode.window.activeTextEditor?.viewColumn || vscode.ViewColumn.One;

        if (EnhancedTaskManagerPanel.currentPanel) {
            EnhancedTaskManagerPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'voidcatEnhancedTaskManager',
            'VoidCat Task Manager',
            column,
            {
                enableScripts: true,
                localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')],
                retainContextWhenHidden: true
            }
        );

        EnhancedTaskManagerPanel.currentPanel = new EnhancedTaskManagerPanel(panel, extensionUri, engineClient);
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, engineClient: VoidCatEngineClient) {
        this._panel = panel;
        this._extensionUri = extensionUri;
        this._engineClient = engineClient;

        this._panel.webview.html = this._getHtmlForWebview();
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Enhanced message handling
        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                await this.handleWebviewMessage(message);
            },
            null,
            this._disposables
        );

        // Initialize the panel
        this.initialize();
    }

    private async initialize(): Promise<void> {
        try {
            // Load initial data
            await this.loadAllData();
            
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

        } catch (error) {
            console.error('Task Manager initialization failed:', error);
            this._panel.webview.postMessage({
                command: 'error',
                message: 'Failed to initialize Task Manager: ' + error
            });
        }
    }

    private async handleWebviewMessage(message: any): Promise<void> {
        try {
            switch (message.command) {
                // Data Operations
                case 'loadData':
                    await this.loadAllData();
                    break;
                case 'refreshData':
                    await this.refreshData();
                    break;
                
                // Task CRUD Operations
                case 'createTask':
                    await this.createTask(message.taskData);
                    break;
                case 'updateTask':
                    await this.updateTask(message.taskId, message.updates);
                    break;
                case 'deleteTask':
                    await this.deleteTask(message.taskId);
                    break;
                case 'duplicateTask':
                    await this.duplicateTask(message.taskId);
                    break;
                case 'bulkUpdateTasks':
                    await this.bulkUpdateTasks(message.taskIds, message.updates);
                    break;
                
                // Task Hierarchy Operations
                case 'moveTask':
                    await this.moveTask(message.taskId, message.newParentId, message.newPosition);
                    break;
                case 'reorderTasks':
                    await this.reorderTasks(message.taskIds, message.newOrder);
                    break;
                case 'promoteTask':
                    await this.promoteTask(message.taskId);
                    break;
                case 'demoteTask':
                    await this.demoteTask(message.taskId, message.newParentId);
                    break;
                
                // Project Operations
                case 'createProject':
                    await this.createProject(message.projectData);
                    break;
                case 'updateProject':
                    await this.updateProject(message.projectId, message.updates);
                    break;
                case 'deleteProject':
                    await this.deleteProject(message.projectId);
                    break;
                
                // Filtering and Search
                case 'applyFilter':
                    await this.applyFilter(message.filter);
                    break;
                case 'clearFilter':
                    await this.clearFilter();
                    break;
                case 'searchTasks':
                    await this.searchTasks(message.searchTerm);
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
                    await this.exportTasks(message.format);
                    break;
                case 'importTasks':
                    await this.importTasks(message.data);
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
        } catch (error) {
            console.error('Error handling webview message:', error);
            this._panel.webview.postMessage({
                command: 'error',
                message: 'Operation failed: ' + error
            });
        }
    }

    private async loadAllData(): Promise<void> {
        try {
            // Load projects and tasks
            const [projects, tasks] = await Promise.all([
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

        } catch (error) {
            console.error('Failed to load task data:', error);
            this._panel.webview.postMessage({
                command: 'error',
                message: 'Failed to load task data: ' + error
            });
        }
    }

    private buildTaskHierarchy(tasks: VoidCatTask[]): TaskHierarchy[] {
        const taskMap = new Map<string, VoidCatTask>();
        const rootTasks: TaskHierarchy[] = [];

        // Create task map
        tasks.forEach(task => {
            taskMap.set(task.id, task);
        });

        // Build hierarchy
        const processTask = (task: VoidCatTask, level: number = 0): TaskHierarchy => {
            const children: TaskHierarchy[] = [];
            
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

    private calculateTaskStats(tasks: VoidCatTask[]): TaskStats {
        const stats: TaskStats = {
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
    private async createTask(taskData: Partial<VoidCatTask>): Promise<void> {
        try {
            const newTask = await this._engineClient.createTask(taskData);
            this._tasks.push(newTask);
            await this.loadAllData();
            
            this._panel.webview.postMessage({
                command: 'taskCreated',
                task: newTask,
                message: `Task "${newTask.name}" created successfully`
            });

        } catch (error) {
            console.error('Failed to create task:', error);
            throw error;
        }
    }

    private async updateTask(taskId: string, updates: Partial<VoidCatTask>): Promise<void> {
        try {
            const updatedTask = await this._engineClient.updateTask(taskId, updates);
            
            const index = this._tasks.findIndex(t => t.id === taskId);
            if (index !== -1) {
                this._tasks[index] = updatedTask;
            }
            
            await this.loadAllData();
            
            this._panel.webview.postMessage({
                command: 'taskUpdated',
                task: updatedTask,
                message: `Task "${updatedTask.name}" updated successfully`
            });

        } catch (error) {
            console.error('Failed to update task:', error);
            throw error;
        }
    }

    private async deleteTask(taskId: string): Promise<void> {
        try {
            await this._engineClient.deleteTask(taskId);
            this._tasks = this._tasks.filter(t => t.id !== taskId);
            this._selectedTasks = this._selectedTasks.filter(id => id !== taskId);
            
            await this.loadAllData();
            
            this._panel.webview.postMessage({
                command: 'taskDeleted',
                taskId: taskId,
                message: 'Task deleted successfully'
            });

        } catch (error) {
            console.error('Failed to delete task:', error);
            throw error;
        }
    }

    private async duplicateTask(taskId: string): Promise<void> {
        try {
            const originalTask = this._tasks.find(t => t.id === taskId);
            if (!originalTask) {
                throw new Error('Task not found');
            }

            const duplicateData: Partial<VoidCatTask> = {
                name: `${originalTask.name} (Copy)`,
                description: originalTask.description,
                priority: originalTask.priority,
                complexity: originalTask.complexity,
                estimatedHours: originalTask.estimatedHours,
                tags: [...(originalTask.tags || [])],
                parentId: originalTask.parentId,
                status: 'pending'
            };

            await this.createTask(duplicateData);

        } catch (error) {
            console.error('Failed to duplicate task:', error);
            throw error;
        }
    }

    private async bulkUpdateTasks(taskIds: string[], updates: Partial<VoidCatTask>): Promise<void> {
        try {
            const updatePromises = taskIds.map(id => this._engineClient.updateTask(id, updates));
            await Promise.all(updatePromises);
            
            await this.loadAllData();
            
            this._panel.webview.postMessage({
                command: 'bulkUpdateComplete',
                taskIds: taskIds,
                message: `${taskIds.length} tasks updated successfully`
            });

        } catch (error) {
            console.error('Failed to bulk update tasks:', error);
            throw error;
        }
    }

    // Hierarchy Operations  
    private async moveTask(taskId: string, newParentId: string | null, newPosition?: number): Promise<void> {
        try {
            const updates: Partial<VoidCatTask> = {
                parentId: newParentId || undefined
            };

            await this.updateTask(taskId, updates);

        } catch (error) {
            console.error('Failed to move task:', error);
            throw error;
        }
    }

    private async reorderTasks(taskIds: string[], newOrder: number[]): Promise<void> {
        // Implementation would depend on having an order field in tasks
        console.log('Reorder tasks:', taskIds, newOrder);
        // For now, just reload data to reflect any changes
        await this.loadAllData();
    }

    private async promoteTask(taskId: string): Promise<void> {
        try {
            const task = this._tasks.find(t => t.id === taskId);
            if (!task || !task.parentId) {
                return; // Already at root level
            }

            const parentTask = this._tasks.find(t => t.id === task.parentId);
            const newParentId = parentTask?.parentId || null;

            await this.moveTask(taskId, newParentId);

        } catch (error) {
            console.error('Failed to promote task:', error);
            throw error;
        }
    }

    private async demoteTask(taskId: string, newParentId: string): Promise<void> {
        try {
            await this.moveTask(taskId, newParentId);
        } catch (error) {
            console.error('Failed to demote task:', error);
            throw error;
        }
    }

    // Project Operations
    private async createProject(projectData: Partial<VoidCatProject>): Promise<void> {
        try {
            // Assuming the engine client has a createProject method
            // const newProject = await this._engineClient.createProject(projectData);
            // For now, show a message that this feature is coming
            this._panel.webview.postMessage({
                command: 'info',
                message: 'Project creation feature coming soon'
            });
        } catch (error) {
            console.error('Failed to create project:', error);
            throw error;
        }
    }

    private async updateProject(projectId: string, updates: Partial<VoidCatProject>): Promise<void> {
        try {
            // Implementation would call engine client
            console.log('Update project:', projectId, updates);
        } catch (error) {
            console.error('Failed to update project:', error);
            throw error;
        }
    }

    private async deleteProject(projectId: string): Promise<void> {
        try {
            // Implementation would call engine client
            console.log('Delete project:', projectId);
        } catch (error) {
            console.error('Failed to delete project:', error);
            throw error;
        }
    }

    // Filtering and Search
    private async applyFilter(filter: TaskFilter): Promise<void> {
        this._currentFilter = filter;
        await this.loadAllData(); // Reload with filter applied
    }

    private async clearFilter(): Promise<void> {
        this._currentFilter = {};
        await this.loadAllData();
    }

    private async searchTasks(searchTerm: string): Promise<void> {
        this._currentFilter.search = searchTerm;
        await this.loadAllData();
    }

    // Selection Operations
    private selectTask(taskId: string, multiSelect: boolean = false): void {
        if (multiSelect) {
            if (this._selectedTasks.includes(taskId)) {
                this._selectedTasks = this._selectedTasks.filter(id => id !== taskId);
            } else {
                this._selectedTasks.push(taskId);
            }
        } else {
            this._selectedTasks = [taskId];
        }

        this._panel.webview.postMessage({
            command: 'selectionChanged',
            selectedTasks: this._selectedTasks
        });
    }

    private selectAllTasks(): void {
        this._selectedTasks = this._tasks.map(t => t.id);
        this._panel.webview.postMessage({
            command: 'selectionChanged',
            selectedTasks: this._selectedTasks
        });
    }

    private clearSelection(): void {
        this._selectedTasks = [];
        this._panel.webview.postMessage({
            command: 'selectionChanged',
            selectedTasks: this._selectedTasks
        });
    }

    // View Operations
    private expandAllTasks(): void {
        this._panel.webview.postMessage({
            command: 'expandAll'
        });
    }

    private collapseAllTasks(): void {
        this._panel.webview.postMessage({
            command: 'collapseAll'
        });
    }

    private setViewMode(mode: string): void {
        this._panel.webview.postMessage({
            command: 'setViewMode',
            mode: mode
        });
    }

    // Export/Import Operations
    private async exportTasks(format: string): Promise<void> {
        try {
            let exportData: string;
            
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

            const document = await vscode.workspace.openTextDocument({
                content: exportData,
                language: format === 'json' ? 'json' : 'csv'
            });

            await vscode.window.showTextDocument(document);

            this._panel.webview.postMessage({
                command: 'exportComplete',
                format: format,
                message: `Tasks exported as ${format.toUpperCase()}`
            });

        } catch (error) {
            console.error('Failed to export tasks:', error);
            throw error;
        }
    }

    private convertTasksToCSV(tasks: VoidCatTask[]): string {
        const headers = ['ID', 'Name', 'Description', 'Status', 'Priority', 'Complexity', 'Estimated Hours', 'Actual Hours', 'Tags', 'Created At', 'Updated At'];
        const rows = tasks.map(task => [
            task.id,
            task.name,
            task.description || '',
            task.status,
            task.priority.toString(),
            task.complexity.toString(),
            task.estimatedHours?.toString() || '',
            task.actualHours?.toString() || '',
            (task.tags || []).join(';'),
            task.createdAt,
            task.updatedAt
        ]);

        return [headers, ...rows].map(row => 
            row.map(cell => `"${(cell || '').toString().replace(/"/g, '""')}"`).join(',')
        ).join('\n');
    }

    private async importTasks(data: any): Promise<void> {
        try {
            // Implementation for importing tasks
            console.log('Import tasks:', data);
            this._panel.webview.postMessage({
                command: 'info',
                message: 'Task import feature coming soon'
            });
        } catch (error) {
            console.error('Failed to import tasks:', error);
            throw error;
        }
    }

    // Settings and Configuration
    private updateSettings(settings: any): void {
        // Apply settings to the task manager
        if (settings.autoRefresh !== undefined) {
            if (settings.autoRefresh) {
                this.startAutoRefresh();
            } else {
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

    private toggleAutoRefresh(): void {
        if (this._autoRefreshInterval) {
            this.stopAutoRefresh();
        } else {
            this.startAutoRefresh();
        }
    }

    private toggleDragDrop(): void {
        this._isDragDropEnabled = !this._isDragDropEnabled;
        this._panel.webview.postMessage({
            command: 'dragDropToggled',
            enabled: this._isDragDropEnabled
        });
    }

    // Utility Methods
    private startAutoRefresh(): void {
        if (this._autoRefreshInterval) {
            clearInterval(this._autoRefreshInterval);
        }

        this._autoRefreshInterval = setInterval(async () => {
            await this.refreshData();
        }, 30000); // Refresh every 30 seconds
    }

    private stopAutoRefresh(): void {
        if (this._autoRefreshInterval) {
            clearInterval(this._autoRefreshInterval);
            this._autoRefreshInterval = undefined;
        }
    }

    private async refreshData(): Promise<void> {
        await this.loadAllData();
        this._panel.webview.postMessage({
            command: 'dataRefreshed',
            timestamp: new Date().toISOString()
        });
    }

    private handleRealtimeTaskUpdate(data: any): void {
        // Handle real-time updates from WebSocket
        this._panel.webview.postMessage({
            command: 'realtimeUpdate',
            type: 'task',
            data: data
        });
        
        // Refresh data to get latest state
        this.refreshData();
    }

    private _getHtmlForWebview(): string {
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

    public dispose(): void {
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
