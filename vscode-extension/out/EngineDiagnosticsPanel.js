"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EngineDiagnosticsPanel = void 0;
const vscode = require("vscode");
class EngineDiagnosticsPanel {
    static createOrShow(extensionUri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;
        // If we already have a panel, show it.
        if (EngineDiagnosticsPanel.currentPanel) {
            EngineDiagnosticsPanel.currentPanel._panel.reveal(column);
            return;
        }
        // Otherwise, create a new panel.
        const panel = vscode.window.createWebviewPanel('engineDiagnostics', // Identifies the type of the webview. Used internally
        'Engine Diagnostics', // Title of the panel displayed to the user
        column || vscode.ViewColumn.One, {
            // Enable javascript in the webview
            enableScripts: true,
            // And restrict the webview to only loading content from our extension's `media` directory.
            localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
        });
        EngineDiagnosticsPanel.currentPanel = new EngineDiagnosticsPanel(panel, extensionUri);
    }
    constructor(panel, extensionUri) {
        this._disposables = [];
        this._panel = panel;
        this._extensionUri = extensionUri;
        // Set the webview's initial html content
        this._panel.webview.html = this._getHtmlForWebview();
        // Listen for when the panel is disposed
        // This happens when the user closes the panel or when the panel is closed programatically
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        // Handle messages from the webview
        this._panel.webview.onDidReceiveMessage(message => {
            switch (message.command) {
                case 'alert':
                    vscode.window.showErrorMessage(message.text);
                    return;
            }
        }, null, this._disposables);
    }
    dispose() {
        EngineDiagnosticsPanel.currentPanel = undefined;
        // Clean up our resources
        this._panel.dispose();
        while (this._disposables.length) {
            const x = this._disposables.pop();
            if (x) {
                x.dispose();
            }
        }
    }
    _getHtmlForWebview() {
        // Local path to main script run in the webview
        const scriptPathOnDisk = vscode.Uri.joinPath(this._extensionUri, 'media', 'main.js');
        // And the uri we use to load this script in the webview
        const scriptUri = this._panel.webview.asWebviewUri(scriptPathOnDisk);
        return `<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Engine Diagnostics</title>
            </head>
            <body>
                <h1>Engine Diagnostics</h1>
                <div id="diagnostics-container"></div>
                <script src="${scriptUri}"></script>
            </body>
            </html>`;
    }
}
exports.EngineDiagnosticsPanel = EngineDiagnosticsPanel;
//# sourceMappingURL=EngineDiagnosticsPanel.js.map