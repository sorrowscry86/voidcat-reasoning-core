import * as fs from 'fs';
import * as vscode from 'vscode';
import { MCPClient } from '../mcp-client';

export class MemoryBrowserPanel {
    public static currentPanel: MemoryBrowserPanel | undefined;

    private readonly _panel: vscode.WebviewPanel;
    private readonly _extensionUri: vscode.Uri;
    private _disposables: vscode.Disposable[] = [];

    public static createOrShow(extensionUri: vscode.Uri, mcpClient: MCPClient) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        // If we already have a panel, show it.
        if (MemoryBrowserPanel.currentPanel) {
            MemoryBrowserPanel.currentPanel._panel.reveal(column);
            return;
        }

        // Otherwise, create a new panel.
        const panel = vscode.window.createWebviewPanel(
            'memoryBrowser', // Identifies the type of the webview. Used internally
            'Memory Browser', // Title of the panel displayed to the user
            column || vscode.ViewColumn.One,
            {
                // Enable javascript in the webview
                enableScripts: true,

                // And restrict the webview to only loading content from our extension's `media` directory.
                localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
            }
        );

        MemoryBrowserPanel.currentPanel = new MemoryBrowserPanel(panel, extensionUri, mcpClient);
    }

    private _mcpClient: MCPClient;

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri, mcpClient: MCPClient) {
        this._panel = panel;
        this._extensionUri = extensionUri;
        this._mcpClient = mcpClient;

        // Set the webview's initial html content
        this._panel.webview.html = this._getHtmlForWebview();

        // Listen for when the panel is disposed
        // This happens when the user closes the panel or when the panel is closed programatically
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'alert':
                        vscode.window.showErrorMessage(message.text);
                        return;
                    case 'refreshMemories':
                        this._updateWebview();
                        return;
                    case 'searchMemories':
                        this._updateWebview(message.query, message.category);
                        return;
                    case 'addCategory':
                        this._addCategory(message.categoryName);
                        return;
                }
            },
            null,
            this._disposables
        );

        this._updateWebview();
        this._updateCategories();
        this._updateVisualization();
        this._updateAnalytics();
    }

    private async _addCategory(categoryName: string) {
        try {
            await this._mcpClient.addCategory(categoryName);
            vscode.window.showInformationMessage(`Category '${categoryName}' added.`);
            this._updateCategories();
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to add category: ${error}`);
        }
    }

    private async _updateCategories() {
        try {
            const categories = await this._mcpClient.listCategories();
            this._panel.webview.postMessage({
                command: 'updateCategories',
                categories: categories
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to load categories: ${error}`);
        }
    }

    private async _updateWebview(query: string = "", category: string = "") {
        try {
            const memories = await this._mcpClient.listMemories(query, category);
            this._panel.webview.postMessage({
                command: 'updateMemories',
                memories: memories
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to load memories: ${error}`);
        }
    }

    public dispose() {
        MemoryBrowserPanel.currentPanel = undefined;

        // Clean up our resources
        this._panel.dispose();

        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }

    private _getHtmlForWebview() {
        const scriptPathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'media', 'memory-browser.js');
        const scriptUri = this._panel.webview.asWebviewUri(scriptPathOnDisk);

        const stylePathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'media', 'memory-browser.css');
        const styleUri = this._panel.webview.asWebviewUri(stylePathOnDisk);

        const htmlPathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'media', 'memory-browser.html');
        let html = fs.readFileSync(htmlPathOnDisk.fsPath, 'utf8');

        html = html.replace('{{styleUri}}', styleUri.toString());
        html = html.replace('{{scriptUri}}', scriptUri.toString());

        return html;
    }

    private async _updateVisualization() {
        try {
            const stats = await this._mcpClient.getMemoryStats();
            this._panel.webview.postMessage({
                command: 'updateVisualization',
                data: stats.category_distribution
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to load memory visualization: ${error}`);
        }
    }

    private async _updateAnalytics() {
        try {
            const stats = await this._mcpClient.getMemoryStats(); // Assuming getMemoryStats returns all relevant analytics
            this._panel.webview.postMessage({
                command: 'updateAnalytics',
                data: stats // Send the entire stats object for analytics
            });
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to load memory analytics: ${error}`);
        }
    }
}
