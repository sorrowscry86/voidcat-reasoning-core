import * as vscode from 'vscode';
import { VoidCatEngineClient, VoidCatTask, VoidCatProject } from '../VoidCatEngineClient';

export class TaskManagerPanel {
    public static currentPanel: TaskManagerPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];
    private _tasks: VoidCatTask[] = [];
    private _projects: VoidCatProject[] = [];

    public static createOrShow(extensionUri: vscode.Uri, engineClient: VoidCatEngineClient) {
        const column = vscode.window.activeTextEditor?.viewColumn || vscode.ViewColumn.One;

        // If we already have a panel, show it
        if (TaskManagerPanel.currentPanel) {
            TaskManagerPanel.currentPanel._panel.reveal(column);
            return;
        }

        // Create new panel
        const panel = vscode.window.createWebviewPanel(
            'voidcatTaskManager',
            'VoidCat Task Manager',
            column,
            {
                enableScripts: true,
                localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
            }
        );

        TaskManagerPanel.currentPanel = new TaskManagerPanel(panel, extensionUri, engineClient);
    }

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, private engineClient: VoidCatEngineClient) {
        this._panel = panel;
        this._extensionUri = extensionUri;

        // Set initial HTML content
        this._panel.webview.html = this._getHtmlForWebview();

        // Listen for when the panel is disposed
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            async (message) => {
                await this.handleWebviewMessage(message);
            },
            null,
            this._disposables
        );

        // Load initial data
        this.loadTasks();
    }
    private async handleWebviewMessage(message: any): Promise<void> {
        switch (message.command) {
            case 'loadTasks':
                await this.loadTasks();
                break;
            case 'createTask':
                await this.createTask(message.task);
                break;
            case 'updateTask':
                await this.updateTask(message.taskId, message.updates);
                break;
            case 'deleteTask':
                await this.deleteTask(message.taskId);
                break;
            case 'refreshData':
                await this.refreshData();
                break;
            default:
                console.warn('Unknown message command:', message.command);
        }
    }

    private async loadTasks(): Promise<void> {
        try {
            this._projects = await this.engineClient.getProjects();
            this._tasks = await this.engineClient.getTasks();
            
            // Send updated data to webview
            this._panel.webview.postMessage({
                command: 'updateData',
                tasks: this._tasks,
                projects: this._projects
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to load tasks: ${error}`);
        }
    }

    private async createTask(taskData: Partial<VoidCatTask>): Promise<void> {
        try {
            const newTask = await this.engineClient.createTask(taskData);
            this._tasks.push(newTask);
            
            // Refresh the webview
            await this.loadTasks();
            
            vscode.window.showInformationMessage(`Task "${newTask.name}" created successfully!`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create task: ${error}`);
        }
    }
    private async updateTask(taskId: string, updates: Partial<VoidCatTask>): Promise<void> {
        try {
            const updatedTask = await this.engineClient.updateTask(taskId, updates);
            
            // Update local task data
            const index = this._tasks.findIndex(t => t.id === taskId);
            if (index !== -1) {
                this._tasks[index] = updatedTask;
            }
            
            // Refresh the webview
            await this.loadTasks();
            
            vscode.window.showInformationMessage(`Task "${updatedTask.name}" updated successfully!`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to update task: ${error}`);
        }
    }

    private async deleteTask(taskId: string): Promise<void> {
        try {
            await this.engineClient.deleteTask(taskId);
            
            // Remove from local data
            this._tasks = this._tasks.filter(t => t.id !== taskId);
            
            // Refresh the webview
            await this.loadTasks();
            
            vscode.window.showInformationMessage('Task deleted successfully!');
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to delete task: ${error}`);
        }
    }

    private async refreshData(): Promise<void> {
        await this.loadTasks();
    }