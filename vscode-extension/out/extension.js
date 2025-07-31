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
exports.VoidCatExtension = void 0;
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = require("vscode");
const VoidCatEngineClient_1 = require("./VoidCatEngineClient");
const DashboardPanel_1 = require("./panels/DashboardPanel");
const EnhancedDashboardPanel_1 = require("./panels/EnhancedDashboardPanel");
const TaskManagerPanel_1 = require("./panels/TaskManagerPanel");
const EnhancedTaskManagerPanel_1 = require("./panels/EnhancedTaskManagerPanel");
const CodeAnalysisProvider_1 = require("./providers/CodeAnalysisProvider");
const TaskManagerProvider_1 = require("./providers/TaskManagerProvider");
const MemoryBrowserProvider_1 = require("./providers/MemoryBrowserProvider");
const VoidCatCommands_1 = require("./commands/VoidCatCommands");
class VoidCatExtension {
    constructor(context) {
        this.context = context;
        this.engineClient = new VoidCatEngineClient_1.VoidCatEngineClient();
        this.codeAnalysisProvider = new CodeAnalysisProvider_1.CodeAnalysisProvider(this.engineClient);
        this.taskManagerProvider = new TaskManagerProvider_1.TaskManagerProvider(this.engineClient);
        this.memoryBrowserProvider = new MemoryBrowserProvider_1.MemoryBrowserProvider(this.engineClient);
        this.commands = new VoidCatCommands_1.VoidCatCommands(this.engineClient);
        this.statusBarItem = this.createStatusBarItem();
    }
    static getInstance(context) {
        if (!VoidCatExtension.instance && context) {
            VoidCatExtension.instance = new VoidCatExtension(context);
        }
        return VoidCatExtension.instance;
    }
    initialize() {
        return __awaiter(this, void 0, void 0, function* () {
            console.log('VoidCat Reasoning Core extension initializing...');
            try {
                // Initialize engine connection
                yield this.engineClient.initialize();
                // Update status bar to show connected state
                this.updateStatusBar('connected');
                // Register all commands
                this.registerCommands();
                // Register view providers
                this.registerViewProviders();
                // Register context menu contributions
                this.registerContextMenus();
                // Set context that extension is initialized
                vscode.commands.executeCommand('setContext', 'voidcat:initialized', true);
                // Auto-start if configured
                const config = vscode.workspace.getConfiguration('voidcat');
                if (config.get('engine.autoStart', true)) {
                    yield this.startEngine();
                }
                // Show welcome message
                this.showWelcomeMessage();
                console.log('VoidCat Reasoning Core extension initialized successfully!');
            }
            catch (error) {
                console.error('VoidCat extension initialization failed:', error);
                this.updateStatusBar('error');
                vscode.window.showErrorMessage(`VoidCat initialization failed: ${error}`);
            }
        });
    }
    registerCommands() {
        const disposables = [
            // Core engine commands
            vscode.commands.registerCommand('voidcat.initialize', () => this.initialize()),
            vscode.commands.registerCommand('voidcat.query', () => this.commands.executeQuery()),
            vscode.commands.registerCommand('voidcat.restart', () => this.restartEngine()),
            // Code analysis commands
            vscode.commands.registerCommand('voidcat.analyzeFile', () => this.commands.analyzeCurrentFile()),
            vscode.commands.registerCommand('voidcat.analyzeSelection', () => this.commands.analyzeSelection()),
            vscode.commands.registerCommand('voidcat.explainCode', () => this.commands.explainCode()),
            vscode.commands.registerCommand('voidcat.suggestImprovements', () => this.commands.suggestImprovements()),
            vscode.commands.registerCommand('voidcat.semanticSearch', () => this.commands.semanticSearch()),
            // Panel commands - Enhanced Dashboard Priority
            vscode.commands.registerCommand('voidcat.showDashboard', () => this.showEnhancedDashboard()),
            vscode.commands.registerCommand('voidcat.showBasicDashboard', () => DashboardPanel_1.DashboardPanel.createOrShow(this.context.extensionUri, this.engineClient)),
            vscode.commands.registerCommand('voidcat.showEnhancedDashboard', () => this.showEnhancedDashboard()),
            vscode.commands.registerCommand('voidcat.showTaskManager', () => EnhancedTaskManagerPanel_1.EnhancedTaskManagerPanel.createOrShow(this.context.extensionUri, this.engineClient)),
            vscode.commands.registerCommand('voidcat.showBasicTaskManager', () => TaskManagerPanel_1.TaskManagerPanel.createOrShow(this.context.extensionUri, this.engineClient)),
            // Temporarily disabled - needs MCPClient interface fix
            // vscode.commands.registerCommand('voidcat.showMemoryBrowser', () => MemoryBrowserPanel.createOrShow(this.context.extensionUri, this.engineClient)),
            // vscode.commands.registerCommand('voidcat.showDiagnostics', () => EngineDiagnosticsPanel.createOrShow(this.context.extensionUri, this.engineClient)),
            // Task management commands (Pillar I Integration Priority)
            vscode.commands.registerCommand('voidcat.createTask', () => this.commands.createTask()),
            vscode.commands.registerCommand('voidcat.createProject', () => this.commands.createProject()),
            vscode.commands.registerCommand('voidcat.listTasks', () => this.commands.listTasks()),
            vscode.commands.registerCommand('voidcat.completeTask', () => this.commands.completeTask()),
            // Memory commands (Pillar II Integration Priority)
            vscode.commands.registerCommand('voidcat.searchMemory', () => this.commands.searchMemory()),
            vscode.commands.registerCommand('voidcat.createMemory', () => this.commands.createMemory()),
            // Quick access commands
            vscode.commands.registerCommand('voidcat.quickDashboard', () => this.quickDashboard()),
            vscode.commands.registerCommand('voidcat.quickQuery', () => this.quickQuery()),
            vscode.commands.registerCommand('voidcat.quickAnalysis', () => this.quickAnalysis()),
            // Configuration commands
            vscode.commands.registerCommand('voidcat.configure', () => this.openConfiguration()),
            vscode.commands.registerCommand('voidcat.showLogs', () => this.showLogs()),
            vscode.commands.registerCommand('voidcat.about', () => this.showAbout())
        ];
        // Add all disposables to context subscriptions
        this.context.subscriptions.push(...disposables);
    }
    registerViewProviders() {
        // Register tree view providers for the activity bar
        vscode.window.registerTreeDataProvider('voidcat.dashboard', this.taskManagerProvider);
        vscode.window.registerTreeDataProvider('voidcat.taskManager', this.taskManagerProvider);
        vscode.window.registerTreeDataProvider('voidcat.memoryBrowser', this.memoryBrowserProvider);
    }
    registerContextMenus() {
        // Context menu commands for code analysis
        const contextMenuDisposables = [
            vscode.commands.registerCommand('voidcat.contextAnalyze', (uri) => __awaiter(this, void 0, void 0, function* () {
                if (uri && uri.fsPath) {
                    yield this.commands.analyzeFileByPath(uri.fsPath);
                }
            })),
            vscode.commands.registerCommand('voidcat.contextExplain', () => __awaiter(this, void 0, void 0, function* () {
                yield this.commands.explainCode();
            })),
            vscode.commands.registerCommand('voidcat.contextImprove', () => __awaiter(this, void 0, void 0, function* () {
                yield this.commands.suggestImprovements();
            }))
        ];
        this.context.subscriptions.push(...contextMenuDisposables);
    }
    createStatusBarItem() {
        const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
        statusBarItem.text = "$(robot) VoidCat";
        statusBarItem.tooltip = "VoidCat Reasoning Core - Click to open dashboard";
        statusBarItem.command = 'voidcat.showEnhancedDashboard';
        statusBarItem.show();
        this.context.subscriptions.push(statusBarItem);
        return statusBarItem;
    }
    updateStatusBar(state) {
        switch (state) {
            case 'connecting':
                this.statusBarItem.text = "$(loading~spin) VoidCat";
                this.statusBarItem.tooltip = "VoidCat - Connecting...";
                this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
                break;
            case 'connected':
                this.statusBarItem.text = "$(check) VoidCat";
                this.statusBarItem.tooltip = "VoidCat - Connected and Ready";
                this.statusBarItem.backgroundColor = undefined;
                break;
            case 'disconnected':
                this.statusBarItem.text = "$(x) VoidCat";
                this.statusBarItem.tooltip = "VoidCat - Disconnected";
                this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
                break;
            case 'error':
                this.statusBarItem.text = "$(warning) VoidCat";
                this.statusBarItem.tooltip = "VoidCat - Error (Click to retry)";
                this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
                this.statusBarItem.command = 'voidcat.restart';
                break;
        }
    }
    showEnhancedDashboard() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                EnhancedDashboardPanel_1.EnhancedDashboardPanel.createOrShow(this.context.extensionUri, this.engineClient);
            }
            catch (error) {
                vscode.window.showErrorMessage(`Failed to open enhanced dashboard: ${error}`);
                console.error('Enhanced dashboard error:', error);
            }
        });
    }
    quickDashboard() {
        return __awaiter(this, void 0, void 0, function* () {
            const choice = yield vscode.window.showQuickPick([
                { label: '🚀 Enhanced Dashboard', description: 'Full-featured dashboard with real-time metrics', detail: 'Recommended' },
                { label: '📊 Basic Dashboard', description: 'Simple dashboard view', detail: 'Lightweight' },
                { label: '📋 Task Manager', description: 'Manage tasks and projects', detail: 'Pillar I' },
                { label: '🧠 Memory Browser', description: 'Browse and search memories', detail: 'Pillar II' },
                { label: '🔧 Diagnostics', description: 'System diagnostics and status', detail: 'Debug' }
            ], {
                placeHolder: 'Choose a VoidCat panel to open',
                title: 'VoidCat Quick Dashboard'
            });
            if (choice) {
                switch (choice.label) {
                    case '🚀 Enhanced Dashboard':
                        yield this.showEnhancedDashboard();
                        break;
                    case '📊 Basic Dashboard':
                        DashboardPanel_1.DashboardPanel.createOrShow(this.context.extensionUri, this.engineClient);
                        break;
                    case '📋 Task Manager':
                        EnhancedTaskManagerPanel_1.EnhancedTaskManagerPanel.createOrShow(this.context.extensionUri, this.engineClient);
                        break;
                    case '🧠 Memory Browser':
                        // Temporarily disabled - needs MCPClient interface fix
                        vscode.window.showInformationMessage('Memory Browser feature temporarily disabled during development');
                        break;
                    case '🔧 Diagnostics':
                        // Temporarily disabled - needs MCPClient interface fix
                        vscode.window.showInformationMessage('Diagnostics feature temporarily disabled during development');
                        break;
                }
            }
        });
    }
    quickQuery() {
        return __awaiter(this, void 0, void 0, function* () {
            const query = yield vscode.window.showInputBox({
                prompt: 'Enter your query for VoidCat reasoning engine',
                placeHolder: 'What would you like to analyze or understand?',
                title: 'VoidCat Quick Query'
            });
            if (query) {
                yield this.commands.executeQueryWithText(query);
            }
        });
    }
    quickAnalysis() {
        return __awaiter(this, void 0, void 0, function* () {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showInformationMessage('No active editor. Please open a file to analyze.');
                return;
            }
            const choice = yield vscode.window.showQuickPick([
                { label: '🔍 Analyze File', description: 'Complete file analysis' },
                { label: '📝 Explain Selection', description: 'Explain selected code' },
                { label: '⚡ Suggest Improvements', description: 'Get improvement suggestions' },
                { label: '🔍 Semantic Search', description: 'Search related code' }
            ], {
                placeHolder: 'Choose analysis type',
                title: 'VoidCat Quick Analysis'
            });
            if (choice) {
                switch (choice.label) {
                    case '🔍 Analyze File':
                        yield this.commands.analyzeCurrentFile();
                        break;
                    case '📝 Explain Selection':
                        yield this.commands.explainCode();
                        break;
                    case '⚡ Suggest Improvements':
                        yield this.commands.suggestImprovements();
                        break;
                    case '🔍 Semantic Search':
                        yield this.commands.semanticSearch();
                        break;
                }
            }
        });
    }
    startEngine() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                this.updateStatusBar('connecting');
                yield this.engineClient.connect();
                this.updateStatusBar('connected');
                vscode.window.showInformationMessage('VoidCat engine connected successfully! 🐾');
            }
            catch (error) {
                this.updateStatusBar('error');
                vscode.window.showErrorMessage(`Failed to connect to VoidCat engine: ${error}`);
            }
        });
    }
    restartEngine() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                this.updateStatusBar('connecting');
                this.engineClient.dispose();
                this.engineClient = new VoidCatEngineClient_1.VoidCatEngineClient();
                yield this.engineClient.initialize();
                this.updateStatusBar('connected');
                vscode.window.showInformationMessage('VoidCat engine restarted successfully! 🐾');
            }
            catch (error) {
                this.updateStatusBar('error');
                vscode.window.showErrorMessage(`Failed to restart VoidCat engine: ${error}`);
            }
        });
    }
    showWelcomeMessage() {
        const config = vscode.workspace.getConfiguration('voidcat');
        const showWelcome = config.get('general.showWelcomeMessage', true);
        if (showWelcome) {
            vscode.window.showInformationMessage('🐾 VoidCat Reasoning Core is ready! Click the robot icon in the status bar to get started.', 'Open Dashboard', "Don't show again").then(selection => {
                if (selection === 'Open Dashboard') {
                    this.showEnhancedDashboard();
                }
                else if (selection === "Don't show again") {
                    config.update('general.showWelcomeMessage', false, vscode.ConfigurationTarget.Global);
                }
            });
        }
    }
    openConfiguration() {
        vscode.commands.executeCommand('workbench.action.openSettings', 'voidcat');
    }
    showLogs() {
        vscode.commands.executeCommand('workbench.action.toggleDevTools');
    }
    showAbout() {
        vscode.window.showInformationMessage('🐾 VoidCat Reasoning Core v2.0\n\nAdvanced AI-powered development assistant with task management, memory system, and intelligent code analysis.\n\nBuilt with strategic foresight for the AI community.', 'View Documentation', 'Open Dashboard').then(selection => {
            if (selection === 'View Documentation') {
                vscode.env.openExternal(vscode.Uri.parse('https://github.com/sorrowscry86/voidcat-reasoning-core'));
            }
            else if (selection === 'Open Dashboard') {
                this.showEnhancedDashboard();
            }
        });
    }
    getEngineClient() {
        return this.engineClient;
    }
    dispose() {
        this.engineClient.dispose();
        this.statusBarItem.dispose();
    }
}
exports.VoidCatExtension = VoidCatExtension;
// Main extension activation function
function activate(context) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            console.log('🐾 VoidCat Reasoning Core extension activating...');
            const extension = VoidCatExtension.getInstance(context);
            yield extension.initialize();
            console.log('🐾 VoidCat Reasoning Core extension activated successfully!');
        }
        catch (error) {
            console.error('🐾 VoidCat extension activation failed:', error);
            vscode.window.showErrorMessage(`VoidCat activation failed: ${error}`);
        }
    });
}
function deactivate() {
    console.log('🐾 VoidCat Reasoning Core extension deactivating...');
    const extension = VoidCatExtension.getInstance();
    if (extension) {
        extension.dispose();
    }
    console.log('🐾 VoidCat Reasoning Core extension deactivated.');
}
//# sourceMappingURL=extension.js.map