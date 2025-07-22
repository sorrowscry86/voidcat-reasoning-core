/**
 * VoidCat Enhanced Task Manager - Frontend JavaScript
 * Comprehensive task management interface with hierarchical visualization,
 * drag-and-drop support, real-time updates, and advanced filtering
 */

// Global state management
const TaskManager = {
    vscode: null,
    state: {
        tasks: [],
        projects: [],
        hierarchy: [],
        stats: {},
        filter: {},
        selectedTasks: [],
        viewMode: 'hierarchical',
        dragDropEnabled: true,
        autoRefreshEnabled: true,
        expandedTasks: new Set(),
        sortConfig: { field: 'priority', direction: 'desc' }
    },
    
    // Initialize the task manager
    init() {
        this.vscode = acquireVsCodeApi();
        this.setupEventListeners();
        this.loadData();
        console.log('🚀 VoidCat Task Manager initialized');
    },
    
    // Setup event listeners for UI interactions
    setupEventListeners() {
        // Priority and complexity sliders
        const prioritySlider = document.getElementById('taskPriority');
        const complexitySlider = document.getElementById('taskComplexity');
        
        if (prioritySlider) {
            prioritySlider.addEventListener('input', (e) => {
                document.getElementById('priorityValue').textContent = e.target.value;
            });
        }
        
        if (complexitySlider) {
            complexitySlider.addEventListener('input', (e) => {
                document.getElementById('complexityValue').textContent = e.target.value;
            });
        }
        
        // Search input with debouncing
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.handleSearch(e.target.value);
                }, 300);
            });
        }
        
        // Handle messages from the extension
        window.addEventListener('message', (event) => {
            this.handleMessage(event.data);
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
        
        // Prevent default drag behavior on document
        document.addEventListener('dragover', (e) => e.preventDefault());
        document.addEventListener('drop', (e) => e.preventDefault());
    },
    
    // Handle messages from the VS Code extension
    handleMessage(message) {
        switch (message.command) {
            case 'updateData':
                this.updateData(message.data);
                break;
            case 'taskCreated':
                this.showNotification('✅ ' + message.message, 'success');
                break;
            case 'taskUpdated':
                this.showNotification('✅ ' + message.message, 'success');
                break;
            case 'taskDeleted':
                this.showNotification('🗑️ ' + message.message, 'info');
                break;
            case 'bulkUpdateComplete':
                this.showNotification('✅ ' + message.message, 'success');
                break;
            case 'error':
                this.showNotification('❌ ' + message.message, 'error');
                break;
            case 'info':
                this.showNotification('ℹ️ ' + message.message, 'info');
                break;
            case 'selectionChanged':
                this.updateSelection(message.selectedTasks);
                break;
            case 'dataRefreshed':
                this.showNotification('🔄 Data refreshed', 'info', 2000);
                break;
            case 'realtimeUpdate':
                this.handleRealtimeUpdate(message);
                break;
            case 'expandAll':
                this.expandAllTasks();
                break;
            case 'collapseAll':
                this.collapseAllTasks();
                break;
            case 'setViewMode':
                this.setViewMode(message.mode);
                break;
            case 'dragDropToggled':
                this.state.dragDropEnabled = message.enabled;
                this.updateDragDropUI();
                break;
            case 'settingsUpdated':
                this.applySettings(message.settings);
                break;
            default:
                console.log('Unknown message:', message);
        }
    },
    
    // Update the task data and refresh UI
    updateData(data) {
        this.state.tasks = data.tasks || [];
        this.state.projects = data.projects || [];
        this.state.hierarchy = data.hierarchy || [];
        this.state.stats = data.stats || {};
        this.state.filter = data.filter || {};
        this.state.selectedTasks = data.selectedTasks || [];
        
        this.hideLoadingOverlay();
        this.renderTaskHierarchy();
        this.updateStatistics();
        this.updateProjectFilters();
        this.updateActiveFilters();
        
        console.log(`📊 Loaded ${this.state.tasks.length} tasks, ${this.state.projects.length} projects`);
    },
    
    // Render the task hierarchy tree
    renderTaskHierarchy() {
        const treeContainer = document.getElementById('taskTree');
        if (!treeContainer) return;
        
        treeContainer.innerHTML = '';
        
        if (this.state.hierarchy.length === 0) {
            treeContainer.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📋</div>
                    <div class="empty-title">No tasks found</div>
                    <div class="empty-description">Create your first task to get started</div>
                    <button class="btn primary" onclick="TaskManager.createNewTask()">
                        ➕ Create Task
                    </button>
                </div>
            `;
            return;
        }
        
        this.state.hierarchy.forEach(hierarchyItem => {
            const taskElement = this.createTaskElement(hierarchyItem);
            treeContainer.appendChild(taskElement);
        });
        
        // Initialize drag and drop if enabled
        if (this.state.dragDropEnabled) {
            this.initializeDragAndDrop();
        }
    },
    
    // Create a task element for the hierarchy
    createTaskElement(hierarchyItem, level = 0) {
        const { task, children } = hierarchyItem;
        const isExpanded = this.state.expandedTasks.has(task.id);
        const hasChildren = children && children.length > 0;
        const isSelected = this.state.selectedTasks.includes(task.id);
        
        const taskDiv = document.createElement('div');
        taskDiv.className = `task-item level-${level} ${isSelected ? 'selected' : ''}`;
        taskDiv.dataset.taskId = task.id;
        taskDiv.dataset.level = level;
        
        // Status indicator
        const statusIcon = this.getStatusIcon(task.status);
        const priorityClass = this.getPriorityClass(task.priority);
        
        // Progress calculation
        const progress = task.actualHours && task.estimatedHours 
            ? Math.min((task.actualHours / task.estimatedHours) * 100, 100)
            : 0;
        
        taskDiv.innerHTML = `
            <div class="task-row" draggable="${this.state.dragDropEnabled}">
                <div class="task-left">
                    <button class="expand-btn ${hasChildren ? 'has-children' : ''} ${isExpanded ? 'expanded' : ''}"
                            onclick="TaskManager.toggleTaskExpansion('${task.id}')">
                        ${hasChildren ? (isExpanded ? '▼' : '▶') : '•'}
                    </button>
                    <div class="task-checkbox">
                        <input type="checkbox" 
                               ${isSelected ? 'checked' : ''}
                               onchange="TaskManager.toggleTaskSelection('${task.id}', event)">
                    </div>
                    <div class="task-status ${task.status}">
                        ${statusIcon}
                    </div>
                    <div class="task-info">
                        <div class="task-name-row">
                            <span class="task-name" onclick="TaskManager.editTask('${task.id}')" title="Click to edit">
                                ${this.escapeHtml(task.name)}
                            </span>
                            <div class="task-badges">
                                <span class="priority-badge ${priorityClass}">${task.priority}</span>
                                <span class="complexity-badge">C${task.complexity}</span>
                                ${(task.tags || []).map(tag => `<span class="tag-badge">${this.escapeHtml(tag)}</span>`).join('')}
                            </div>
                        </div>
                        ${task.description ? `<div class="task-description">${this.escapeHtml(task.description)}</div>` : ''}
                        <div class="task-meta">
                            <span class="task-hours">
                                ⏱️ ${task.actualHours || 0}h / ${task.estimatedHours || 0}h
                            </span>
                            ${task.createdAt ? `<span class="task-date">📅 ${this.formatDate(task.createdAt)}</span>` : ''}
                            ${hasChildren ? `<span class="child-count">👥 ${children.length} subtasks</span>` : ''}
                        </div>
                    </div>
                </div>
                <div class="task-right">
                    <div class="task-progress">
                        <div class="progress-bar mini">
                            <div class="progress-fill" style="width: ${progress}%"></div>
                        </div>
                        <span class="progress-text">${Math.round(progress)}%</span>
                    </div>
                    <div class="task-actions">
                        <button class="action-btn" onclick="TaskManager.editTask('${task.id}')" title="Edit Task">
                            ✏️
                        </button>
                        <button class="action-btn" onclick="TaskManager.duplicateTask('${task.id}')" title="Duplicate Task">
                            📄
                        </button>
                        <button class="action-btn" onclick="TaskManager.createSubtask('${task.id}')" title="Add Subtask">
                            ➕
                        </button>
                        <div class="dropdown">
                            <button class="action-btn dropdown-toggle" onclick="TaskManager.toggleTaskMenu('${task.id}')" title="More Actions">
                                ⋮
                            </button>
                            <div class="dropdown-menu" id="taskMenu-${task.id}">
                                <a href="#" onclick="TaskManager.changeTaskStatus('${task.id}', 'pending')">📝 Mark Pending</a>
                                <a href="#" onclick="TaskManager.changeTaskStatus('${task.id}', 'in-progress')">🔄 Mark In Progress</a>
                                <a href="#" onclick="TaskManager.changeTaskStatus('${task.id}', 'completed')">✅ Mark Complete</a>
                                <a href="#" onclick="TaskManager.changeTaskStatus('${task.id}', 'blocked')">🚫 Mark Blocked</a>
                                <div class="dropdown-divider"></div>
                                <a href="#" onclick="TaskManager.promoteTask('${task.id}')">⬆️ Promote Level</a>
                                <a href="#" onclick="TaskManager.showDemoteDialog('${task.id}')">⬇️ Demote Level</a>
                                <div class="dropdown-divider"></div>
                                <a href="#" onclick="TaskManager.deleteTask('${task.id}')" class="danger">🗑️ Delete</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add children if expanded
        if (hasChildren && isExpanded) {
            const childrenContainer = document.createElement('div');
            childrenContainer.className = 'task-children';
            
            children.forEach(child => {
                const childElement = this.createTaskElement(child, level + 1);
                childrenContainer.appendChild(childElement);
            });
            
            taskDiv.appendChild(childrenContainer);
        }
        
        return taskDiv;
    },
    
    // Update task statistics display
    updateStatistics() {
        const stats = this.state.stats;
        
        // Update header summary
        this.setElementText('totalTasks', stats.total || 0);
        this.setElementText('completedTasks', stats.completed || 0);
        this.setElementText('completionRate', `${Math.round(stats.completionRate || 0)}%`);
        
        // Update detailed stats panel
        this.setElementText('statTotal', stats.total || 0);
        this.setElementText('statCompleted', stats.completed || 0);
        this.setElementText('statInProgress', stats.inProgress || 0);
        this.setElementText('statPending', stats.pending || 0);
        
        // Update progress visualization
        const progressFill = document.getElementById('overallProgress');
        const progressText = document.getElementById('progressText');
        if (progressFill && progressText) {
            const completionRate = stats.completionRate || 0;
            progressFill.style.width = `${completionRate}%`;
            progressText.textContent = `${Math.round(completionRate)}% Complete`;
        }
    },
    
    // Utility functions
    getStatusIcon(status) {
        const icons = {
            'pending': '📝',
            'in-progress': '🔄',
            'completed': '✅',
            'blocked': '🚫'
        };
        return icons[status] || '📝';
    },
    
    getPriorityClass(priority) {
        if (priority >= 8) return 'high';
        if (priority >= 5) return 'medium';
        return 'low';
    },
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    },
    
    setElementText(id, text) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = text;
        }
    },
    
    // Task interaction methods
    toggleTaskExpansion(taskId) {
        if (this.state.expandedTasks.has(taskId)) {
            this.state.expandedTasks.delete(taskId);
        } else {
            this.state.expandedTasks.add(taskId);
        }
        this.renderTaskHierarchy();
    },
    
    toggleTaskSelection(taskId, event) {
        const isMultiSelect = event.ctrlKey || event.metaKey;
        this.vscode.postMessage({
            command: 'selectTask',
            taskId: taskId,
            multiSelect: isMultiSelect
        });
    },
    
    toggleTaskMenu(taskId) {
        const menu = document.getElementById(`taskMenu-${taskId}`);
        if (menu) {
            menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
        }
        
        // Close other menus
        document.querySelectorAll('.dropdown-menu').forEach(m => {
            if (m.id !== `taskMenu-${taskId}`) {
                m.style.display = 'none';
            }
        });
    },
    
    changeTaskStatus(taskId, newStatus) {
        this.vscode.postMessage({
            command: 'updateTask',
            taskId: taskId,
            updates: { status: newStatus }
        });
        this.closeAllMenus();
    },
    
    promoteTask(taskId) {
        this.vscode.postMessage({
            command: 'promoteTask',
            taskId: taskId
        });
        this.closeAllMenus();
    },
    
    // Task management functions (called from HTML)
    loadData() {
        this.showLoadingOverlay();
        this.vscode.postMessage({ command: 'loadData' });
    },
    
    refreshTasks() {
        this.showLoadingOverlay();
        this.vscode.postMessage({ command: 'refreshData' });
    },
    
    createNewTask(parentId = null) {
        this.openTaskModal(null, parentId);
    },
    
    createNewProject() {
        this.showNotification('📁 Project creation feature coming soon!', 'info');
    },
    
    createSubtask(parentId) {
        this.openTaskModal(null, parentId);
    },
    
    editTask(taskId) {
        const task = this.findTaskById(taskId);
        if (task) {
            this.openTaskModal(task);
        }
    },
    
    duplicateTask(taskId) {
        this.vscode.postMessage({
            command: 'duplicateTask',
            taskId: taskId
        });
    },
    
    deleteTask(taskId) {
        const task = this.findTaskById(taskId);
        if (task && confirm(`Are you sure you want to delete "${task.name}"?`)) {
            this.vscode.postMessage({
                command: 'deleteTask',
                taskId: taskId
            });
        }
    },
    
    // Modal management
    openTaskModal(task = null, parentId = null) {
        const modal = document.getElementById('taskModal');
        const title = document.getElementById('modalTitle');
        const form = document.getElementById('taskForm');
        
        if (!modal || !title || !form) return;
        
        // Set modal title
        title.textContent = task ? 'Edit Task' : 'Create New Task';
        
        // Populate form fields
        this.populateTaskForm(task, parentId);
        
        // Show modal
        modal.style.display = 'flex';
        
        // Focus on name field
        setTimeout(() => {
            const nameField = document.getElementById('taskName');
            if (nameField) nameField.focus();
        }, 100);
    },
    
    populateTaskForm(task, parentId) {
        // Update project dropdown
        this.updateProjectDropdown();
        this.updateParentTaskDropdown(task?.id);
        
        if (task) {
            // Edit mode - populate with existing data
            this.setFormValue('taskName', task.name);
            this.setFormValue('taskDescription', task.description || '');
            this.setFormValue('taskStatus', task.status);
            this.setFormValue('taskPriority', task.priority);
            this.setFormValue('taskComplexity', task.complexity);
            this.setFormValue('taskEstimatedHours', task.estimatedHours || '');
            this.setFormValue('taskTags', (task.tags || []).join(', '));
            this.setFormValue('taskParent', task.parentId || '');
            
            // Update slider displays
            document.getElementById('priorityValue').textContent = task.priority;
            document.getElementById('complexityValue').textContent = task.complexity;
        } else {
            // Create mode - set defaults
            form.reset();
            this.setFormValue('taskStatus', 'pending');
            this.setFormValue('taskPriority', 5);
            this.setFormValue('taskComplexity', 5);
            this.setFormValue('taskParent', parentId || '');
            
            // Update slider displays
            document.getElementById('priorityValue').textContent = '5';
            document.getElementById('complexityValue').textContent = '5';
        }
    },
    
    updateProjectDropdown() {
        const select = document.getElementById('taskProject');
        if (!select) return;
        
        select.innerHTML = '<option value="">No Project</option>';
        this.state.projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            select.appendChild(option);
        });
    },
    
    updateParentTaskDropdown(currentTaskId = null) {
        const select = document.getElementById('taskParent');
        if (!select) return;
        
        select.innerHTML = '<option value="">No Parent (Root Level)</option>';
        
        // Add all tasks except the current one (prevent circular references)
        this.state.tasks.forEach(task => {
            if (task.id !== currentTaskId) {
                const option = document.createElement('option');
                option.value = task.id;
                option.textContent = task.name;
                select.appendChild(option);
            }
        });
    },
    
    setFormValue(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.value = value;
        }
    },
    
    closeTaskModal() {
        const modal = document.getElementById('taskModal');
        if (modal) {
            modal.style.display = 'none';
        }
    },
    
    saveTask() {
        const form = document.getElementById('taskForm');
        if (!form || !form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const formData = new FormData(form);
        const taskData = {
            name: document.getElementById('taskName').value,
            description: document.getElementById('taskDescription').value,
            status: document.getElementById('taskStatus').value,
            priority: parseInt(document.getElementById('taskPriority').value),
            complexity: parseInt(document.getElementById('taskComplexity').value),
            estimatedHours: parseFloat(document.getElementById('taskEstimatedHours').value) || undefined,
            tags: document.getElementById('taskTags').value
                .split(',')
                .map(tag => tag.trim())
                .filter(tag => tag),
            parentId: document.getElementById('taskParent').value || undefined
        };
        
        // Check if this is an edit or create operation
        const modal = document.getElementById('taskModal');
        const title = document.getElementById('modalTitle');
        const isEdit = title && title.textContent.includes('Edit');
        
        if (isEdit) {
            // Get task ID from current selection or form data
            const taskId = this.state.selectedTasks[0]; // Assuming single selection for edit
            if (taskId) {
                this.vscode.postMessage({
                    command: 'updateTask',
                    taskId: taskId,
                    updates: taskData
                });
            }
        } else {
            this.vscode.postMessage({
                command: 'createTask',
                taskData: taskData
            });
        }
        
        this.closeTaskModal();
    },
    
    // Filter and search functionality
    applyFilters() {
        const filter = {
            status: this.getSelectValues('statusFilter'),
            priority: this.getPriorityRange(),
            project: this.getSelectValues('projectFilter'),
            search: document.getElementById('searchInput')?.value || ''
        };
        
        this.vscode.postMessage({
            command: 'applyFilter',
            filter: filter
        });
    },
    
    clearAllFilters() {
        // Reset all filter controls
        this.setFormValue('statusFilter', '');
        this.setFormValue('priorityFilter', '');
        this.setFormValue('projectFilter', '');
        this.setFormValue('searchInput', '');
        
        this.vscode.postMessage({
            command: 'clearFilter'
        });
    },
    
    handleSearch(searchTerm) {
        this.vscode.postMessage({
            command: 'searchTasks',
            searchTerm: searchTerm
        });
    },
    
    clearSearch() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = '';
            this.handleSearch('');
        }
    },
    
    // View mode functions
    expandAllTasks() {
        this.state.tasks.forEach(task => {
            this.state.expandedTasks.add(task.id);
        });
        this.renderTaskHierarchy();
    },
    
    collapseAllTasks() {
        this.state.expandedTasks.clear();
        this.renderTaskHierarchy();
    },
    
    setViewMode(mode) {
        this.state.viewMode = mode;
        // Implementation would change the rendering based on mode
        console.log('View mode changed to:', mode);
    },
    
    toggleViewMenu() {
        const menu = document.getElementById('viewMenu');
        if (menu) {
            menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
        }
    },
    
    // Export functions
    exportTasks(format) {
        this.vscode.postMessage({
            command: 'exportTasks',
            format: format
        });
    },
    
    // Utility functions
    findTaskById(taskId) {
        return this.state.tasks.find(task => task.id === taskId);
    },
    
    getSelectValues(selectId) {
        const select = document.getElementById(selectId);
        return select ? [select.value].filter(v => v) : [];
    },
    
    getPriorityRange() {
        const priorityFilter = document.getElementById('priorityFilter')?.value;
        if (!priorityFilter) return undefined;
        
        switch (priorityFilter) {
            case 'high': return { min: 8, max: 10 };
            case 'medium': return { min: 5, max: 7 };
            case 'low': return { min: 1, max: 4 };
            default: return undefined;
        }
    },
    
    updateProjectFilters() {
        const select = document.getElementById('projectFilter');
        if (!select) return;
        
        // Store current value
        const currentValue = select.value;
        
        // Clear and repopulate
        select.innerHTML = '<option value="">All Projects</option>';
        this.state.projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            select.appendChild(option);
        });
        
        // Restore selection
        select.value = currentValue;
    },
    
    updateActiveFilters() {
        const container = document.getElementById('activeFilters');
        if (!container) return;
        
        container.innerHTML = '';
        const filter = this.state.filter;
        
        // Show active filters as tags
        Object.entries(filter).forEach(([key, value]) => {
            if (value && value !== '' && (!Array.isArray(value) || value.length > 0)) {
                const tag = document.createElement('span');
                tag.className = 'filter-tag';
                tag.innerHTML = `${key}: ${Array.isArray(value) ? value.join(', ') : value} <button onclick="TaskManager.removeFilter('${key}')">×</button>`;
                container.appendChild(tag);
            }
        });
    },
    
    removeFilter(filterKey) {
        // Implementation to remove specific filter
        console.log('Remove filter:', filterKey);
    },
    
    updateSelection(selectedTasks) {
        this.state.selectedTasks = selectedTasks;
        // Update UI to reflect selection
        document.querySelectorAll('.task-item').forEach(item => {
            const taskId = item.dataset.taskId;
            const checkbox = item.querySelector('input[type="checkbox"]');
            
            if (checkbox) {
                checkbox.checked = selectedTasks.includes(taskId);
            }
            
            if (selectedTasks.includes(taskId)) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    },
    
    // Drag and drop functionality
    initializeDragAndDrop() {
        const taskRows = document.querySelectorAll('.task-row[draggable="true"]');
        
        taskRows.forEach(row => {
            row.addEventListener('dragstart', this.handleDragStart.bind(this));
            row.addEventListener('dragover', this.handleDragOver.bind(this));
            row.addEventListener('drop', this.handleDrop.bind(this));
            row.addEventListener('dragend', this.handleDragEnd.bind(this));
        });
    },
    
    handleDragStart(e) {
        const taskItem = e.target.closest('.task-item');
        if (taskItem) {
            e.dataTransfer.setData('text/plain', taskItem.dataset.taskId);
            taskItem.classList.add('dragging');
        }
    },
    
    handleDragOver(e) {
        e.preventDefault();
        const taskItem = e.target.closest('.task-item');
        if (taskItem) {
            taskItem.classList.add('drag-over');
        }
    },
    
    handleDrop(e) {
        e.preventDefault();
        const draggedTaskId = e.dataTransfer.getData('text/plain');
        const targetTaskItem = e.target.closest('.task-item');
        
        if (targetTaskItem && draggedTaskId) {
            const targetTaskId = targetTaskItem.dataset.taskId;
            
            if (draggedTaskId !== targetTaskId) {
                this.vscode.postMessage({
                    command: 'moveTask',
                    taskId: draggedTaskId,
                    newParentId: targetTaskId
                });
            }
        }
        
        this.clearDragStyles();
    },
    
    handleDragEnd(e) {
        this.clearDragStyles();
    },
    
    clearDragStyles() {
        document.querySelectorAll('.task-item').forEach(item => {
            item.classList.remove('dragging', 'drag-over');
        });
    },
    
    updateDragDropUI() {
        const button = document.getElementById('dragDropToggle');
        if (button) {
            button.textContent = this.state.dragDropEnabled ? '🔄' : '🔒';
            button.title = this.state.dragDropEnabled ? 'Disable Drag & Drop' : 'Enable Drag & Drop';
        }
        
        // Update draggable attribute on task rows
        document.querySelectorAll('.task-row').forEach(row => {
            row.draggable = this.state.dragDropEnabled;
        });
    },
    
    toggleDragDrop() {
        this.vscode.postMessage({
            command: 'toggleDragDrop'
        });
    },
    
    // Keyboard shortcuts
    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + N: New task
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            this.createNewTask();
        }
        
        // Ctrl/Cmd + R: Refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            this.refreshTasks();
        }
        
        // Escape: Close modals
        if (e.key === 'Escape') {
            this.closeTaskModal();
            this.closeAllMenus();
        }
        
        // Ctrl/Cmd + F: Focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            const searchInput = document.getElementById('searchInput');
            if (searchInput) searchInput.focus();
        }
    },
    
    closeAllMenus() {
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.style.display = 'none';
        });
    },
    
    // Loading and notification utilities
    showLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    },
    
    hideLoadingOverlay() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    },
    
    showNotification(message, type = 'info', duration = 5000) {
        const container = document.getElementById('notificationContainer');
        if (!container) return;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        container.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, duration);
    },
    
    handleRealtimeUpdate(message) {
        console.log('Real-time update:', message);
        // Handle real-time updates from WebSocket
        this.loadData(); // Refresh data to get latest state
    },
    
    applySettings(settings) {
        // Apply various settings
        if (settings.autoRefresh !== undefined) {
            this.state.autoRefreshEnabled = settings.autoRefresh;
        }
        
        if (settings.dragDropEnabled !== undefined) {
            this.state.dragDropEnabled = settings.dragDropEnabled;
            this.updateDragDropUI();
        }
    }
};

// Global functions called from HTML
function createNewTask() { TaskManager.createNewTask(); }
function createNewProject() { TaskManager.createNewProject(); }
function refreshTasks() { TaskManager.refreshTasks(); }
function showFilterDialog() { /* Implementation */ }
function expandAllTasks() { TaskManager.expandAllTasks(); }
function collapseAllTasks() { TaskManager.collapseAllTasks(); }
function setViewMode(mode) { TaskManager.setViewMode(mode); }
function exportTasks(format) { TaskManager.exportTasks(format); }
function toggleViewMenu() { TaskManager.toggleViewMenu(); }
function applyFilters() { TaskManager.applyFilters(); }
function clearAllFilters() { TaskManager.clearAllFilters(); }
function handleSearch() { TaskManager.handleSearch(); }
function clearSearch() { TaskManager.clearSearch(); }
function closeTaskModal() { TaskManager.closeTaskModal(); }
function saveTask() { TaskManager.saveTask(); }
function toggleDragDrop() { TaskManager.toggleDragDrop(); }

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    TaskManager.init();
});
