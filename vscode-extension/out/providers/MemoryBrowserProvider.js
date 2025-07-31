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
exports.MemoryItem = exports.MemoryBrowserProvider = void 0;
const vscode = require("vscode");
class MemoryBrowserProvider {
    constructor(engineClient) {
        this.engineClient = engineClient;
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this.memories = []; // Store memories fetched from the engine
        this.loadMemories();
    }
    refresh() {
        this.loadMemories();
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        return element;
    }
    getChildren(element) {
        if (element) {
            // No children for individual memories in this flat list view
            return Promise.resolve([]);
        }
        else {
            // Return all memories as top-level items
            return Promise.resolve(this.memories.map(memory => this.createMemoryItem(memory)));
        }
    }
    loadMemories() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                this.memories = yield this.engineClient.listMemories();
            }
            catch (error) {
                console.error('Failed to load memories:', error);
                this.memories = []; // Clear memories on error
            }
        });
    }
    createMemoryItem(memory) {
        const title = memory.title || `Memory ${memory.memory_id.substring(0, 8)}`;
        const description = memory.content ? memory.content.substring(0, 100) + '...' : 'No content';
        const tooltip = `Category: ${memory.category}\nImportance: ${memory.importance}\nCreated: ${new Date(memory.created_at).toLocaleString()}\nContent: ${memory.content}`;
        return new MemoryItem(title, description, tooltip, vscode.TreeItemCollapsibleState.None, // Memories are not collapsible in this view
        memory.memory_id);
    }
}
exports.MemoryBrowserProvider = MemoryBrowserProvider;
class MemoryItem extends vscode.TreeItem {
    constructor(label, description, tooltip, collapsibleState, id) {
        super(label, collapsibleState);
        this.label = label;
        this.description = description;
        this.tooltip = tooltip;
        this.collapsibleState = collapsibleState;
        this.id = id;
        this.description = description;
        this.tooltip = tooltip;
        this.contextValue = 'memoryItem'; // Context value for when clause in package.json
    }
}
exports.MemoryItem = MemoryItem;
//# sourceMappingURL=MemoryBrowserProvider.js.map