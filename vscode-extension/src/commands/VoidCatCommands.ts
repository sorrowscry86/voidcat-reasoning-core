import * as vscode from 'vscode';
import { VoidCatEngineClient } from '../VoidCatEngineClient';

export class VoidCatCommands {
    constructor(private engineClient: VoidCatEngineClient) {}

    async executeQuery(): Promise<void> {
        const query = await vscode.window.showInputBox({
            prompt: 'Enter your query for VoidCat engine',
            placeHolder: 'Ask VoidCat anything...'
        });

        if (!query) return;

        try {
            const result = await this.engineClient.queryEngine(query);
            
            // Show result in a new document
            const doc = await vscode.workspace.openTextDocument({
                content: `VoidCat Query Result:\n\nQuery: ${query}\n\nResponse:\n${result}`,
                language: 'markdown'
            });
            
            await vscode.window.showTextDocument(doc);
        } catch (error) {
            vscode.window.showErrorMessage(`Query failed: ${error}`);
        }
    }

    async analyzeCurrentFile(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No file is currently open');
            return;
        }

        const document = editor.document;
        const code = document.getText();
        const language = document.languageId;

        try {
            const result = await this.engineClient.analyzeCode(code, language);
            
            // Show analysis result
            const doc = await vscode.workspace.openTextDocument({
                content: `VoidCat File Analysis:\n\nFile: ${document.fileName}\nLanguage: ${language}\n\nAnalysis:\n${result}`,
                language: 'markdown'
            });
            
            await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
        } catch (error) {
            vscode.window.showErrorMessage(`Analysis failed: ${error}`);
        }
    }
    async analyzeSelection(): Promise<void> {
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
            const result = await this.engineClient.analyzeCode(selectedText, language);
            
            const doc = await vscode.workspace.openTextDocument({
                content: `VoidCat Selection Analysis:\n\nSelected Code:\n${selectedText}\n\nLanguage: ${language}\n\nAnalysis:\n${result}`,
                language: 'markdown'
            });
            
            await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
        } catch (error) {
            vscode.window.showErrorMessage(`Selection analysis failed: ${error}`);
        }
    }

    async explainCode(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No file is currently open');
            return;
        }

        const selection = editor.selection;
        const code = selection.isEmpty ? editor.document.getText() : editor.document.getText(selection);
        const language = editor.document.languageId;

        try {
            const result = await this.engineClient.explainCode(code, language);
            
            const doc = await vscode.workspace.openTextDocument({
                content: `VoidCat Code Explanation:\n\nCode:\n${code}\n\nLanguage: ${language}\n\nExplanation:\n${result}`,
                language: 'markdown'
            });
            
            await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
        } catch (error) {
            vscode.window.showErrorMessage(`Code explanation failed: ${error}`);
        }
    }
    async suggestImprovements(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No file is currently open');
            return;
        }

        const selection = editor.selection;
        const code = selection.isEmpty ? editor.document.getText() : editor.document.getText(selection);
        const language = editor.document.languageId;

        try {
            const result = await this.engineClient.suggestImprovements(code, language);
            
            const doc = await vscode.workspace.openTextDocument({
                content: `VoidCat Code Improvements:\n\nCode:\n${code}\n\nLanguage: ${language}\n\nSuggestions:\n${result}`,
                language: 'markdown'
            });
            
            await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
        } catch (error) {
            vscode.window.showErrorMessage(`Improvement suggestions failed: ${error}`);
        }
    }

    async semanticSearch(): Promise<void> {
        const query = await vscode.window.showInputBox({
            prompt: 'Enter your semantic search query',
            placeHolder: 'Search for code patterns, functions, or concepts...'
        });

        if (!query) return;

        const scope = await vscode.window.showQuickPick(['workspace', 'file', 'knowledge_base'], {
            placeHolder: 'Select search scope'
        });

        if (!scope) return;

        try {
            const result = await this.engineClient.semanticSearch(query, scope as any);
            
            const doc = await vscode.workspace.openTextDocument({
                content: `VoidCat Semantic Search Results:\n\nQuery: ${query}\nScope: ${scope}\n\nResults:\n${result}`,
                language: 'markdown'
            });
            
            await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
        } catch (error) {
            vscode.window.showErrorMessage(`Semantic search failed: ${error}`);
        }
    }

    async createTask(): Promise<void> {
        const name = await vscode.window.showInputBox({
            prompt: 'Enter task name',
            placeHolder: 'Task name...'
        });

        if (!name) return;

        const description = await vscode.window.showInputBox({
            prompt: 'Enter task description',
            placeHolder: 'Task description...'
        });

        if (!description) return;

        try {
            const task = await this.engineClient.createTask({
                name,
                description,
                status: 'pending',
                priority: 5,
                complexity: 3
            });
            
            vscode.window.showInformationMessage(`Task "${task.name}" created successfully!`);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to create task: ${error}`);
        }
    }
}