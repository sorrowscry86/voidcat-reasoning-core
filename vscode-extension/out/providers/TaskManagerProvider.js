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
exports.TaskItem = exports.TaskManagerProvider = void 0;
const vscode = require("vscode");
class TaskManagerProvider {
    constructor(engineClient) {
        this.engineClient = engineClient;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this.tasks = [];
        this.projects = [];
        this.loadData();
    }
    refresh() {
        this.loadData();
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (!element) {
            // Return root items (projects and top-level tasks)
            return Promise.resolve(this.getRootItems());
        }
        else {
            // Return children of the selected item
            return Promise.resolve(this.getChildItems(element));
        }
    }
    getRootItems() {
        const items = [];
        // Add projects
        this.projects.forEach(project => {
            items.push(new TaskItem(project.name, `Project: ${project.description}`, vscode.TreeItemCollapsibleState.Expanded, 'project', project.id));
        });
        // Add top-level tasks (tasks without parent)
        const topLevelTasks = this.tasks.filter(task => !task.parentId);
        topLevelTasks.forEach(task => {
            items.push(this.createTaskItem(task));
        });
        return items;
    }
    getChildItems(element) {
        const items = [];
        if (element.type === 'project') {
            // Return tasks belonging to this project
            const projectTasks = this.tasks.filter(task => task.parentId === element.id);
            projectTasks.forEach(task => {
                items.push(this.createTaskItem(task));
            });
        }
        else if (element.type === 'task') {
            // Return subtasks of this task
            const subtasks = this.tasks.filter(task => task.parentId === element.id);
            subtasks.forEach(task => {
                items.push(this.createTaskItem(task));
            });
        }
        return items;
    }
    createTaskItem(task) {
        const hasChildren = this.tasks.some(t => t.parentId === task.id);
        const collapsibleState = hasChildren ?
            vscode.TreeItemCollapsibleState.Collapsed :
            vscode.TreeItemCollapsibleState.None;
        const statusIcon = this.getStatusIcon(task.status);
        const priorityIcon = this.getPriorityIcon(task.priority);
        return new TaskItem(`${statusIcon} ${priorityIcon} ${task.name}`, `${task.description} (${task.status})`, collapsibleState, 'task', task.id);
    }
    getStatusIcon(status) {
        switch (status) {
            case 'completed': return '✅';
            case 'in-progress': return '🔄';
            case 'blocked': return '🚫';
            default: return '⏳';
        }
    }
    getPriorityIcon(priority) {
        if (priority >= 8)
            return '🔥';
        if (priority >= 6)
            return '⚡';
        if (priority >= 4)
            return '📋';
        return '📝';
    }
    loadData() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                this.projects = yield this.engineClient.getProjects();
                this.tasks = yield this.engineClient.getTasks();
            }
            catch (error) {
                console.error('Failed to load task data:', error);
            }
        });
    }
}
exports.TaskManagerProvider = TaskManagerProvider;
class TaskItem extends vscode.TreeItem {
    constructor(label, tooltip, collapsibleState, type, id) {
        super(label, collapsibleState);
        this.label = label;
        this.tooltip = tooltip;
        this.collapsibleState = collapsibleState;
        this.type = type;
        this.id = id;
        this.tooltip = tooltip;
        this.description = tooltip;
        this.contextValue = type;
    }
}
exports.TaskItem = TaskItem;
//# sourceMappingURL=TaskManagerProvider.js.map