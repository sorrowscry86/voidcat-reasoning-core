import * as vscode from 'vscode';
import { VoidCatEngineClient } from '../VoidCatEngineClient';

export class CodeAnalysisProvider {
    private engineClient: VoidCatEngineClient;
    private disposables: vscode.Disposable[] = [];

    constructor(engineClient: VoidCatEngineClient) {
        this.engineClient = engineClient;
        this.setupEventListeners();
    }

    private setupEventListeners(): void {
        // Listen for document changes for auto-analysis
        this.disposables.push(
            vscode.workspace.onDidChangeTextDocument(this.onDocumentChanged.bind(this))
        );

        // Listen for document saves
        this.disposables.push(
            vscode.workspace.onDidSaveTextDocument(this.onDocumentSaved.bind(this))
        );
    }

    private async onDocumentChanged(event: vscode.TextDocumentChangeEvent): Promise<void> {
        const config = vscode.workspace.getConfiguration('voidcat');
        if (!config.get<boolean>('analysis.autoAnalyze', false)) {
            return;
        }

        // Debounce analysis to avoid excessive calls
        this.debounceAnalysis(event.document);
    }

    private async onDocumentSaved(document: vscode.TextDocument): Promise<void> {
        if (this.isCodeFile(document)) {
            await this.analyzeDocument(document);
        }
    }

    private isCodeFile(document: vscode.TextDocument): boolean {
        const codeExtensions = ['.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.cs', '.go', '.rs', '.cpp', '.c', '.h', '.hpp'];
        return codeExtensions.some(ext => document.fileName.endsWith(ext));
    }
    private debounceTimer: NodeJS.Timer | null = null;

    private debounceAnalysis(document: vscode.TextDocument): void {
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        this.debounceTimer = setTimeout(() => {
            this.analyzeDocument(document);
        }, 2000); // 2 second delay
    }

    public async analyzeDocument(document: vscode.TextDocument): Promise<void> {
        if (!this.isCodeFile(document)) return;

        try {
            const code = document.getText();
            const language = document.languageId;
            const analysis = await this.engineClient.analyzeCode(code, language);

            // Create diagnostic collection for the analysis
            this.showAnalysisResult(document, analysis);
        } catch (error) {
            console.error('Code analysis failed:', error);
        }
    }

    private showAnalysisResult(document: vscode.TextDocument, analysis: string): void {
        // Show analysis in output channel
        const outputChannel = vscode.window.createOutputChannel('VoidCat Analysis');
        outputChannel.clear();
        outputChannel.appendLine(`Analysis for: ${document.fileName}`);
        outputChannel.appendLine('='.repeat(50));
        outputChannel.appendLine(analysis);
        outputChannel.show();
    }

    public dispose(): void {
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        this.disposables.forEach(d => d.dispose());
    }
}