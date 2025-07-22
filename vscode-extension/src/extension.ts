import * as vscode from 'vscode';
import { VoidCatEngineClient } from './VoidCatEngineClient';
import { DashboardPanel } from './panels/DashboardPanel';
import { EnhancedDashboardPanel } from './panels/EnhancedDashboardPanel';
import { TaskManagerPanel } from './panels/TaskManagerPanel';
import { EnhancedTaskManagerPanel } from './panels/EnhancedTaskManagerPanel';
import { MemoryBrowserPanel } from './panels/MemoryBrowserPanel';
import { DiagnosticsPanel } from './panels/DiagnosticsPanel';
import { CodeAnalysisProvider } from './providers/CodeAnalysisProvider';
import { TaskManagerProvider } from './providers/TaskManagerProvider';
import { MemoryBrowserProvider } from './providers/MemoryBrowserProvider';
import { VoidCatCommands } from './commands/VoidCatCommands';

export class VoidCatExtension {
    private static instance: VoidCatExtension;
    private context: vscode.ExtensionContext;
    private engineClient: VoidCatEngineClient;
    private codeAnalysisProvider: CodeAnalysisProvider;
    private taskManagerProvider: TaskManagerProvider;
    private memoryBrowserProvider: MemoryBrowserProvider;
    private commands: VoidCatCommands;
    private statusBarItem: vscode.StatusBarItem;

    private constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.engineClient = new VoidCatEngineClient();
        this.codeAnalysisProvider = new CodeAnalysisProvider(this.engineClient);
        this.taskManagerProvider = new TaskManagerProvider(this.engineClient);
        this.memoryBrowserProvider = new MemoryBrowserProvider(this.engineClient);
        this.commands = new VoidCatCommands(this.engineClient);
        this.statusBarItem = this.createStatusBarItem();
    }

    public static getInstance(context?: vscode.ExtensionContext): VoidCatExtension {
        if (!VoidCatExtension.instance && context) {
            VoidCatExtension.instance = new VoidCatExtension(context);
        }
        return VoidCatExtension.instance;
    }

    public async initialize(): Promise<void> {
        console.log('VoidCat Reasoning Core extension initializing...');
        
        try {
            // Initialize engine connection
            await this.engineClient.initialize();
            
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
            if (config.get<boolean>('engine.autoStart', true)) {
                await this.startEngine();
            }
            
            // Show welcome message
            this.showWelcomeMessage();
            
            console.log('VoidCat Reasoning Core extension initialized successfully!');
            
        } catch (error) {
            console.error('VoidCat extension initialization failed:', error);
            this.updateStatusBar('error');
            vscode.window.showErrorMessage(`VoidCat initialization failed: ${error}`);
        }
    }

    private registerCommands(): void {
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
            vscode.commands.registerCommand('voidcat.showBasicDashboard', () => DashboardPanel.createOrShow(this.context.extensionUri, this.engineClient)),
            vscode.commands.registerCommand('voidcat.showEnhancedDashboard', () => this.showEnhancedDashboard()),
            vscode.commands.registerCommand('voidcat.showTaskManager', () => EnhancedTaskManagerPanel.createOrShow(this.context.extensionUri, this.engineClient)),
            vscode.commands.registerCommand('voidcat.showBasicTaskManager', () => TaskManagerPanel.createOrShow(this.context.extensionUri, this.engineClient)),
            vscode.commands.registerCommand('voidcat.showMemoryBrowser', () => MemoryBrowserPanel.createOrShow(this.context.extensionUri, this.engineClient)),
            vscode.commands.registerCommand('voidcat.showDiagnostics', () => DiagnosticsPanel.createOrShow(this.context.extensionUri, this.engineClient)),
            
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

    private registerViewProviders(): void {
        // Register tree view providers for the activity bar
        vscode.window.registerTreeDataProvider('voidcat.dashboard', this.taskManagerProvider);
        vscode.window.registerTreeDataProvider('voidcat.taskManager', this.taskManagerProvider);
        vscode.window.registerTreeDataProvider('voidcat.memoryBrowser', this.memoryBrowserProvider);
    }

    private registerContextMenus(): void {
        // Context menu commands for code analysis
        const contextMenuDisposables = [
            vscode.commands.registerCommand('voidcat.contextAnalyze', async (uri: vscode.Uri) => {
                if (uri && uri.fsPath) {
                    await this.commands.analyzeFileByPath(uri.fsPath);
                }
            }),
            vscode.commands.registerCommand('voidcat.contextExplain', async () => {
                await this.commands.explainCode();
            }),
            vscode.commands.registerCommand('voidcat.contextImprove', async () => {
                await this.commands.suggestImprovements();
            })
        ];

        this.context.subscriptions.push(...contextMenuDisposables);
    }

    private createStatusBarItem(): vscode.StatusBarItem {
        const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
        statusBarItem.text = "$(robot) VoidCat";
        statusBarItem.tooltip = "VoidCat Reasoning Core - Click to open dashboard";
        statusBarItem.command = 'voidcat.showEnhancedDashboard';
        statusBarItem.show();
        
        this.context.subscriptions.push(statusBarItem);
        return statusBarItem;
    }

    private updateStatusBar(state: 'connecting' | 'connected' | 'disconnected' | 'error'): void {
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

    private async showEnhancedDashboard(): Promise<void> {
        try {
            EnhancedDashboardPanel.createOrShow(this.context.extensionUri, this.engineClient);
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to open enhanced dashboard: ${error}`);
            console.error('Enhanced dashboard error:', error);
        }
    }

    private async quickDashboard(): Promise<void> {
        const choice = await vscode.window.showQuickPick([
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
                    await this.showEnhancedDashboard();
                    break;
                case '📊 Basic Dashboard':
                    DashboardPanel.createOrShow(this.context.extensionUri, this.engineClient);
                    break;
                case '📋 Task Manager':
                    EnhancedTaskManagerPanel.createOrShow(this.context.extensionUri, this.engineClient);
                    break;
                case '🧠 Memory Browser':
                    MemoryBrowserPanel.createOrShow(this.context.extensionUri, this.engineClient);
                    break;
                case '🔧 Diagnostics':
                    DiagnosticsPanel.createOrShow(this.context.extensionUri, this.engineClient);
                    break;
            }
        }
    }

    private async quickQuery(): Promise<void> {
        const query = await vscode.window.showInputBox({
            prompt: 'Enter your query for VoidCat reasoning engine',
            placeHolder: 'What would you like to analyze or understand?',
            title: 'VoidCat Quick Query'
        });

        if (query) {
            await this.commands.executeQueryWithText(query);
        }
    }

    private async quickAnalysis(): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showInformationMessage('No active editor. Please open a file to analyze.');
            return;
        }

        const choice = await vscode.window.showQuickPick([
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
                    await this.commands.analyzeCurrentFile();
                    break;
                case '📝 Explain Selection':
                    await this.commands.explainCode();
                    break;
                case '⚡ Suggest Improvements':
                    await this.commands.suggestImprovements();
                    break;
                case '🔍 Semantic Search':
                    await this.commands.semanticSearch();
                    break;
            }
        }
    }

    private async startEngine(): Promise<void> {
        try {
            this.updateStatusBar('connecting');
            await this.engineClient.connect();
            this.updateStatusBar('connected');
            vscode.window.showInformationMessage('VoidCat engine connected successfully! 🐾');
        } catch (error) {
            this.updateStatusBar('error');
            vscode.window.showErrorMessage(`Failed to connect to VoidCat engine: ${error}`);
        }
    }

    private async restartEngine(): Promise<void> {
        try {
            this.updateStatusBar('connecting');
            this.engineClient.dispose();
            this.engineClient = new VoidCatEngineClient();
            await this.engineClient.initialize();
            this.updateStatusBar('connected');
            vscode.window.showInformationMessage('VoidCat engine restarted successfully! 🐾');
        } catch (error) {
            this.updateStatusBar('error');
            vscode.window.showErrorMessage(`Failed to restart VoidCat engine: ${error}`);
        }
    }

    private showWelcomeMessage(): void {
        const config = vscode.workspace.getConfiguration('voidcat');
        const showWelcome = config.get<boolean>('general.showWelcomeMessage', true);
        
        if (showWelcome) {
            vscode.window.showInformationMessage(
                '🐾 VoidCat Reasoning Core is ready! Click the robot icon in the status bar to get started.',
                'Open Dashboard',
                "Don't show again"
            ).then(selection => {
                if (selection === 'Open Dashboard') {
                    this.showEnhancedDashboard();
                } else if (selection === "Don't show again") {
                    config.update('general.showWelcomeMessage', false, vscode.ConfigurationTarget.Global);
                }
            });
        }
    }

    private openConfiguration(): void {
        vscode.commands.executeCommand('workbench.action.openSettings', 'voidcat');
    }

    private showLogs(): void {
        vscode.commands.executeCommand('workbench.action.toggleDevTools');
    }

    private showAbout(): void {
        vscode.window.showInformationMessage(
            '🐾 VoidCat Reasoning Core v2.0\n\nAdvanced AI-powered development assistant with task management, memory system, and intelligent code analysis.\n\nBuilt with strategic foresight for the AI community.',
            'View Documentation',
            'Open Dashboard'
        ).then(selection => {
            if (selection === 'View Documentation') {
                vscode.env.openExternal(vscode.Uri.parse('https://github.com/sorrowscry86/voidcat-reasoning-core'));
            } else if (selection === 'Open Dashboard') {
                this.showEnhancedDashboard();
            }
        });
    }

    public getEngineClient(): VoidCatEngineClient {
        return this.engineClient;
    }

    public dispose(): void {
        this.engineClient.dispose();
        this.statusBarItem.dispose();
    }
}

// Main extension activation function
export async function activate(context: vscode.ExtensionContext) {
    try {
        console.log('🐾 VoidCat Reasoning Core extension activating...');
        const extension = VoidCatExtension.getInstance(context);
        await extension.initialize();
        console.log('🐾 VoidCat Reasoning Core extension activated successfully!');
    } catch (error) {
        console.error('🐾 VoidCat extension activation failed:', error);
        vscode.window.showErrorMessage(`VoidCat activation failed: ${error}`);
    }
}

export function deactivate() {
    console.log('🐾 VoidCat Reasoning Core extension deactivating...');
    const extension = VoidCatExtension.getInstance();
    if (extension) {
        extension.dispose();
    }
    console.log('🐾 VoidCat Reasoning Core extension deactivated.');
}
