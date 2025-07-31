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
exports.CodeAnalysisProvider = void 0;
const vscode = require("vscode");
class CodeAnalysisProvider {
    constructor(engineClient) {
        this.disposables = [];
        this.debounceTimer = null;
        this.engineClient = engineClient;
        this.setupEventListeners();
    }
    setupEventListeners() {
        // Listen for document changes for auto-analysis
        this.disposables.push(vscode.workspace.onDidChangeTextDocument(this.onDocumentChanged.bind(this)));
        // Listen for document saves
        this.disposables.push(vscode.workspace.onDidSaveTextDocument(this.onDocumentSaved.bind(this)));
    }
    onDocumentChanged(event) {
        return __awaiter(this, void 0, void 0, function* () {
            const config = vscode.workspace.getConfiguration('voidcat');
            if (!config.get('analysis.autoAnalyze', false)) {
                return;
            }
            // Debounce analysis to avoid excessive calls
            this.debounceAnalysis(event.document);
        });
    }
    onDocumentSaved(document) {
        return __awaiter(this, void 0, void 0, function* () {
            if (this.isCodeFile(document)) {
                yield this.analyzeDocument(document);
            }
        });
    }
    isCodeFile(document) {
        const codeExtensions = ['.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.cs', '.go', '.rs', '.cpp', '.c', '.h', '.hpp'];
        return codeExtensions.some(ext => document.fileName.endsWith(ext));
    }
    debounceAnalysis(document) {
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        this.debounceTimer = setTimeout(() => {
            this.analyzeDocument(document);
        }, 2000); // 2 second delay
    }
    analyzeDocument(document) {
        return __awaiter(this, void 0, void 0, function* () {
            if (!this.isCodeFile(document))
                return;
            try {
                const code = document.getText();
                const language = document.languageId;
                const analysis = yield this.engineClient.analyzeCode(code, language);
                // Create diagnostic collection for the analysis
                this.showAnalysisResult(document, analysis);
            }
            catch (error) {
                console.error('Code analysis failed:', error);
            }
        });
    }
    showAnalysisResult(document, analysis) {
        // Show analysis in output channel
        const outputChannel = vscode.window.createOutputChannel('VoidCat Analysis');
        outputChannel.clear();
        outputChannel.appendLine(`Analysis for: ${document.fileName}`);
        outputChannel.appendLine('='.repeat(50));
        outputChannel.appendLine(analysis);
        outputChannel.show();
    }
    dispose() {
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        this.disposables.forEach(d => d.dispose());
    }
}
exports.CodeAnalysisProvider = CodeAnalysisProvider;
//# sourceMappingURL=CodeAnalysisProvider.js.map