import * as vscode from 'vscode';
import { VoidCatEngineClient, VoidCatTask, VoidCatProject } from '../VoidCatEngineClient';

export class TaskManagerProvider implements vscode.TreeDataProvider<TaskItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<TaskItem | undefined | null | void> = new vscode.EventEmitter<TaskItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<TaskItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private tasks: VoidCatTask[] = [];
    private projects: VoidCatProject[] = [];

    constructor(private engineClient: VoidCatEngineClient) {
        this.loadData();
    }

    refresh(): void {
        this.loadData();
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: TaskItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: TaskItem): Thenable<TaskItem[]> {
        if (!element) {
            // Return root items (projects and top-level tasks)
            return Promise.resolve(this.getRootItems());
        } else {
            // Return children of the selected item
            return Promise.resolve(this.getChildItems(element));
        }
    }

    private getRootItems(): TaskItem[] {
        const items: TaskItem[] = [];
        
        // Add projects
        this.projects.forEach(project => {
            items.push(new TaskItem(
                project.name,
                `Project: ${project.description}`,
                vscode.TreeItemCollapsibleState.Expanded,
                'project',
                project.id
            ));
        });

        // Add top-level tasks (tasks without parent)
        const topLevelTasks = this.tasks.filter(task => !task.parentId);
        topLevelTasks.forEach(task => {
            items.push(this.createTaskItem(task));
        });

        return items;
    }
    private getChildItems(element: TaskItem): TaskItem[] {
        const items: TaskItem[] = [];
        
        if (element.type === 'project') {
            // Return tasks belonging to this project
            const projectTasks = this.tasks.filter(task => task.parentId === element.id);
            projectTasks.forEach(task => {
                items.push(this.createTaskItem(task));
            });
        } else if (element.type === 'task') {
            // Return subtasks of this task
            const subtasks = this.tasks.filter(task => task.parentId === element.id);
            subtasks.forEach(task => {
                items.push(this.createTaskItem(task));
            });
        }
        
        return items;
    }

    private createTaskItem(task: VoidCatTask): TaskItem {
        const hasChildren = this.tasks.some(t => t.parentId === task.id);
        const collapsibleState = hasChildren ? 
            vscode.TreeItemCollapsibleState.Collapsed : 
            vscode.TreeItemCollapsibleState.None;

        const statusIcon = this.getStatusIcon(task.status);
        const priorityIcon = this.getPriorityIcon(task.priority);
        
        return new TaskItem(
            `${statusIcon} ${priorityIcon} ${task.name}`,
            `${task.description} (${task.status})`,
            collapsibleState,
            'task',
            task.id
        );
    }

    private getStatusIcon(status: string): string {
        switch (status) {
            case 'completed': return '✅';
            case 'in-progress': return '🔄';
            case 'blocked': return '🚫';
            default: return '⏳';
        }
    }

    private getPriorityIcon(priority: number): string {
        if (priority >= 8) return '🔥';
        if (priority >= 6) return '⚡';
        if (priority >= 4) return '📋';
        return '📝';
    }

    private async loadData(): Promise<void> {
        try {
            this.projects = await this.engineClient.getProjects();
            this.tasks = await this.engineClient.getTasks();
        } catch (error) {
            console.error('Failed to load task data:', error);
        }
    }
}

export class TaskItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly tooltip: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly type: 'project' | 'task',
        public readonly id: string
    ) {
        super(label, collapsibleState);
        this.tooltip = tooltip;
        this.description = tooltip;
        this.contextValue = type;
    }
}