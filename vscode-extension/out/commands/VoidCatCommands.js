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
exports.VoidCatCommands = void 0;
const vscode = require("vscode");
class VoidCatCommands {
    constructor(engineClient) {
        this.engineClient = engineClient;
    }
    executeQuery() {
        return __awaiter(this, void 0, void 0, function* () {
            const query = yield vscode.window.showInputBox({
                prompt: 'Enter your query for VoidCat engine',
                placeHolder: 'Ask VoidCat anything...'
            });
            if (!query)
                return;
            try {
                const result = yield this.engineClient.queryEngine(query);
                // Show result in a new document
                const doc = yield vscode.workspace.openTextDocument({
                    content: `VoidCat Query Result:\n\nQuery: ${query}\n\nResponse:\n${result}`,
                    language: 'markdown'
                });
                yield vscode.window.showTextDocument(doc);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Query failed: ${error}`);
            }
        });
    }
    analyzeCurrentFile() {
        return __awaiter(this, void 0, void 0, function* () {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No file is currently open');
                return;
            }
            const document = editor.document;
            const code = document.getText();
            const language = document.languageId;
            try {
                const result = yield this.engineClient.analyzeCode(code, language);
                // Show analysis result
                const doc = yield vscode.workspace.openTextDocument({
                    content: `VoidCat File Analysis:\n\nFile: ${document.fileName}\nLanguage: ${language}\n\nAnalysis:\n${result}`,
                    language: 'markdown'
                });
                yield vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Analysis failed: ${error}`);
            }
        });
    }
    analyzeSelection() {
        return __awaiter(this, void 0, void 0, function* () {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No file is currently open');
                return;
            }
            const selection = editor.selection;
            if (selection.isEmpty) {
                vscode.window.showWarningMessage('No text selected');
                return;
            }
            const selectedText = editor.document.getText(selection);
            const language = editor.document.languageId;
            try {
                const result = yield this.engineClient.analyzeCode(selectedText, language);
                const doc = yield vscode.workspace.openTextDocument({
                    content: `VoidCat Selection Analysis:\n\nSelected Code:\n${selectedText}\n\nLanguage: ${language}\n\nAnalysis:\n${result}`,
                    language: 'markdown'
                });
                yield vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Selection analysis failed: ${error}`);
            }
        });
    }
    explainCode() {
        return __awaiter(this, void 0, void 0, function* () {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No file is currently open');
                return;
            }
            const selection = editor.selection;
            const code = selection.isEmpty ? editor.document.getText() : editor.document.getText(selection);
            const language = editor.document.languageId;
            try {
                const result = yield this.engineClient.explainCode(code, language);
                const doc = yield vscode.workspace.openTextDocument({
                    content: `VoidCat Code Explanation:\n\nCode:\n${code}\n\nLanguage: ${language}\n\nExplanation:\n${result}`,
                    language: 'markdown'
                });
                yield vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Code explanation failed: ${error}`);
            }
        });
    }
    suggestImprovements() {
        return __awaiter(this, void 0, void 0, function* () {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No file is currently open');
                return;
            }
            const selection = editor.selection;
            const code = selection.isEmpty ? editor.document.getText() : editor.document.getText(selection);
            const language = editor.document.languageId;
            try {
                const result = yield this.engineClient.suggestImprovements(code, language);
                const doc = yield vscode.workspace.openTextDocument({
                    content: `VoidCat Code Improvements:\n\nCode:\n${code}\n\nLanguage: ${language}\n\nSuggestions:\n${result}`,
                    language: 'markdown'
                });
                yield vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Improvement suggestions failed: ${error}`);
            }
        });
    }
    semanticSearch() {
        return __awaiter(this, void 0, void 0, function* () {
            const query = yield vscode.window.showInputBox({
                prompt: 'Enter your semantic search query',
                placeHolder: 'Search for code patterns, functions, or concepts...'
            });
            if (!query)
                return;
            const scope = yield vscode.window.showQuickPick(['workspace', 'file', 'knowledge_base'], {
                placeHolder: 'Select search scope'
            });
            if (!scope)
                return;
            try {
                const result = yield this.engineClient.semanticSearch(query, scope);
                const doc = yield vscode.workspace.openTextDocument({
                    content: `VoidCat Semantic Search Results:\n\nQuery: ${query}\nScope: ${scope}\n\nResults:\n${result}`,
                    language: 'markdown'
                });
                yield vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Semantic search failed: ${error}`);
            }
        });
    }
    createTask() {
        return __awaiter(this, void 0, void 0, function* () {
            const name = yield vscode.window.showInputBox({
                prompt: 'Enter task name',
                placeHolder: 'Task name...'
            });
            if (!name)
                return;
            const description = yield vscode.window.showInputBox({
                prompt: 'Enter task description',
                placeHolder: 'Task description...'
            });
            if (!description)
                return;
            try {
                const task = yield this.engineClient.createTask({
                    name,
                    description,
                    status: 'pending',
                    priority: 5,
                    complexity: 3
                });
                vscode.window.showInformationMessage(`Task "${task.name}" created successfully!`);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to create task: ${error}`);
            }
        });
    }
    createProject() {
        return __awaiter(this, void 0, void 0, function* () {
            const name = yield vscode.window.showInputBox({
                prompt: 'Enter project name',
                placeHolder: 'Project name...'
            });
            if (!name)
                return;
            const description = yield vscode.window.showInputBox({
                prompt: 'Enter project description',
                placeHolder: 'Project description...'
            });
            if (!description)
                return;
            try {
                const project = yield this.engineClient.createProject({ name, description });
                vscode.window.showInformationMessage(`Project "${project.name}" created successfully!`);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to create project: ${error}`);
            }
        });
    }
    listTasks() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const tasks = yield this.engineClient.listTasks();
                const taskList = tasks.map(task => `- ${task.name}: ${task.status}`).join('\n');
                const doc = yield vscode.workspace.openTextDocument({
                    content: `VoidCat Tasks:\n\n${taskList}`,
                    language: 'markdown'
                });
                yield vscode.window.showTextDocument(doc);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to list tasks: ${error}`);
            }
        });
    }
    completeTask() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const tasks = yield this.engineClient.listTasks();
                const taskItems = tasks.filter(t => t.status !== 'done').map(task => ({
                    label: task.name,
                    description: task.description,
                    task: task
                }));
                const selected = yield vscode.window.showQuickPick(taskItems, {
                    placeHolder: 'Select task to complete'
                });
                if (selected) {
                    yield this.engineClient.updateTask(selected.task.id, { status: 'completed' });
                    vscode.window.showInformationMessage(`Task "${selected.task.name}" completed!`);
                }
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to complete task: ${error}`);
            }
        });
    }
    searchMemory() {
        return __awaiter(this, void 0, void 0, function* () {
            const query = yield vscode.window.showInputBox({
                prompt: 'Enter memory search query',
                placeHolder: 'Search memories...'
            });
            if (!query)
                return;
            try {
                const memories = yield this.engineClient.searchMemories(query);
                const memoryList = memories.map(m => `- ${m.title}: ${m.content.substring(0, 100)}...`).join('\n');
                const doc = yield vscode.workspace.openTextDocument({
                    content: `VoidCat Memory Search Results:\n\nQuery: ${query}\n\n${memoryList}`,
                    language: 'markdown'
                });
                yield vscode.window.showTextDocument(doc);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to search memories: ${error}`);
            }
        });
    }
    createMemory() {
        return __awaiter(this, void 0, void 0, function* () {
            const title = yield vscode.window.showInputBox({
                prompt: 'Enter memory title',
                placeHolder: 'Memory title...'
            });
            if (!title)
                return;
            const content = yield vscode.window.showInputBox({
                prompt: 'Enter memory content',
                placeHolder: 'Memory content...'
            });
            if (!content)
                return;
            try {
                const memory = yield this.engineClient.createMemory({ title, content });
                vscode.window.showInformationMessage(`Memory "${memory.title}" created successfully!`);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to create memory: ${error}`);
            }
        });
    }
    analyzeFileByPath(filePath) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const document = yield vscode.workspace.openTextDocument(filePath);
                const code = document.getText();
                const language = document.languageId;
                const result = yield this.engineClient.analyzeCode(code, language);
                const doc = yield vscode.workspace.openTextDocument({
                    content: `VoidCat File Analysis:\n\nFile: ${filePath}\nLanguage: ${language}\n\nAnalysis:\n${result}`,
                    language: 'markdown'
                });
                yield vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Analysis failed: ${error}`);
            }
        });
    }
    executeQueryWithText(query) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const result = yield this.engineClient.queryEngine(query);
                const doc = yield vscode.workspace.openTextDocument({
                    content: `VoidCat Query Result:\n\nQuery: ${query}\n\nResponse:\n${result}`,
                    language: 'markdown'
                });
                yield vscode.window.showTextDocument(doc);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Query failed: ${error}`);
            }
        });
    }
}
exports.VoidCatCommands = VoidCatCommands;
//# sourceMappingURL=VoidCatCommands.js.map