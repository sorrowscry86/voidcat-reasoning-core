import * as vscode from 'vscode';
import { VoidCatEngineClient } from '../VoidCatEngineClient';

export class MemoryBrowserProvider implements vscode.TreeDataProvider<MemoryItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<MemoryItem | undefined | null | void> = new vscode.EventEmitter<MemoryItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<MemoryItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private memories: any[] = []; // Store memories fetched from the engine

    constructor(private engineClient: VoidCatEngineClient) {
        this.loadMemories();
    }

    refresh(): void {
        this.loadMemories();
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: MemoryItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: MemoryItem): Thenable<MemoryItem[]> {
        if (element) {
            // No children for individual memories in this flat list view
            return Promise.resolve([]);
        } else {
            // Return all memories as top-level items
            return Promise.resolve(this.memories.map(memory => this.createMemoryItem(memory)));
        }
    }

    private async loadMemories(): Promise<void> {
        try {
            this.memories = await this.engineClient.listMemories();
        } catch (error) {
            console.error('Failed to load memories:', error);
            this.memories = []; // Clear memories on error
        }
    }

    private createMemoryItem(memory: any): MemoryItem {
        const title = memory.title || `Memory ${memory.memory_id.substring(0, 8)}`;
        const description = memory.content ? memory.content.substring(0, 100) + '...' : 'No content';
        const tooltip = `Category: ${memory.category}\nImportance: ${memory.importance}\nCreated: ${new Date(memory.created_at).toLocaleString()}\nContent: ${memory.content}`;

        return new MemoryItem(
            title,
            description,
            tooltip,
            vscode.TreeItemCollapsibleState.None, // Memories are not collapsible in this view
            memory.memory_id
        );
    }
}

export class MemoryItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly tooltip: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly id: string
    ) {
        super(label, collapsibleState);
        this.description = description;
        this.tooltip = tooltip;
        this.contextValue = 'memoryItem'; // Context value for when clause in package.json
    }
}
