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
exports.TaskManagerPanel = void 0;
const vscode = require("vscode");
class TaskManagerPanel {
    static createOrShow(extensionUri, engineClient) {
        var _a;
        const column = ((_a = vscode.window.activeTextEditor) === null || _a === void 0 ? void 0 : _a.viewColumn) || vscode.ViewColumn.One;
        // If we already have a panel, show it
        if (TaskManagerPanel.currentPanel) {
            TaskManagerPanel.currentPanel._panel.reveal(column);
            return;
        }
        // Create new panel
        const panel = vscode.window.createWebviewPanel('voidcatTaskManager', 'VoidCat Task Manager', column, {
            enableScripts: true,
            localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
        });
        TaskManagerPanel.currentPanel = new TaskManagerPanel(panel, extensionUri, engineClient);
    }
    constructor(panel, extensionUri, engineClient) {
        this.engineClient = engineClient;
        this._disposables = [];
        this._tasks = [];
        this._projects = [];
        this._panel = panel;
        this._extensionUri = extensionUri;
        // Set initial HTML content
        this._panel.webview.html = this._getHtmlForWebview();
        // Listen for when the panel is disposed
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage((message) => __awaiter(this, void 0, void 0, function* () {
            yield this.handleWebviewMessage(message);
        }), null, this._disposables);
        // Load initial data
        this.loadTasks();
    }
    handleWebviewMessage(message) {
        return __awaiter(this, void 0, void 0, function* () {
            switch (message.command) {
                case 'loadTasks':
                    yield this.loadTasks();
                    break;
                case 'createTask':
                    yield this.createTask(message.task);
                    break;
                case 'updateTask':
                    yield this.updateTask(message.taskId, message.updates);
                    break;
                case 'deleteTask':
                    yield this.deleteTask(message.taskId);
                    break;
                case 'refreshData':
                    yield this.refreshData();
                    break;
                default:
                    console.warn('Unknown message command:', message.command);
            }
        });
    }
    loadTasks() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                this._projects = yield this.engineClient.getProjects();
                this._tasks = yield this.engineClient.getTasks();
                // Send updated data to webview
                this._panel.webview.postMessage({
                    command: 'updateData',
                    tasks: this._tasks,
                    projects: this._projects
                });
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to load tasks: ${error}`);
            }
        });
    }
    createTask(taskData) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const newTask = yield this.engineClient.createTask(taskData);
                this._tasks.push(newTask);
                // Refresh the webview
                yield this.loadTasks();
                vscode.window.showInformationMessage(`Task "${newTask.name}" created successfully!`);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to create task: ${error}`);
            }
        });
    }
    updateTask(taskId, updates) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const updatedTask = yield this.engineClient.updateTask(taskId, updates);
                // Update local task data
                const index = this._tasks.findIndex(t => t.id === taskId);
                if (index !== -1) {
                    this._tasks[index] = updatedTask;
                }
                // Refresh the webview
                yield this.loadTasks();
                vscode.window.showInformationMessage(`Task "${updatedTask.name}" updated successfully!`);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to update task: ${error}`);
            }
        });
    }
    deleteTask(taskId) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                yield this.engineClient.deleteTask(taskId);
                // Remove from local data
                this._tasks = this._tasks.filter(t => t.id !== taskId);
                // Refresh the webview
                yield this.loadTasks();
                vscode.window.showInformationMessage('Task deleted successfully!');
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to delete task: ${error}`);
            }
        });
    }
    refreshData() {
        return __awaiter(this, void 0, void 0, function* () {
            yield this.loadTasks();
        });
    }
    _getHtmlForWebview() {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>VoidCat Task Manager</title>
            <style>
                body { font-family: var(--vscode-font-family); padding: 20px; }
                .task { margin: 10px 0; padding: 10px; border: 1px solid var(--vscode-panel-border); }
                .task-name { font-weight: bold; }
                .task-status { color: var(--vscode-descriptionForeground); }
            </style>
        </head>
        <body>
            <h1>Task Manager</h1>
            <div id="tasks">Loading tasks...</div>
            <script>
                const vscode = acquireVsCodeApi();
                // Task manager functionality would go here
            </script>
        </body>
        </html>`;
    }
    dispose() {
        TaskManagerPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}
exports.TaskManagerPanel = TaskManagerPanel;
//# sourceMappingURL=TaskManagerPanel.js.map