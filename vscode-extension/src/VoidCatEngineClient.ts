import * as vscode from 'vscode';
import axios, { AxiosInstance } from 'axios';

export interface VoidCatEngineStatus {
    status: string;
    engineInitialized: boolean;
    documentsLoaded: number;
    lastQueryTimestamp: string;
    totalQueriesProcessed: number;
    taskManagerAvailable: boolean;
    memorySystemAvailable: boolean;
}

export interface VoidCatTask {
    id: string;
    name: string;
    description: string;
    status: 'pending' | 'in-progress' | 'completed' | 'blocked';
    priority: number;
    complexity: number;
    estimatedHours?: number;
    actualHours?: number;
    parentId?: string;
    dependsOn?: string[];
    tags?: string[];
    createdAt: string;
    updatedAt: string;
}

export interface VoidCatProject {
    id: string;
    name: string;
    description: string;
    createdAt: string;
    updatedAt: string;
}

export class VoidCatEngineClient {
    private httpClient: AxiosInstance;
    private baseUrl: string;
    private isConnected: boolean = false;
    private statusCheckInterval?: NodeJS.Timer;

    constructor() {
        const config = vscode.workspace.getConfiguration('voidcat');
        const host = config.get<string>('engine.host', 'localhost');
        const port = config.get<number>('engine.port', 8002);
        
        this.baseUrl = `http://${host}:${port}`;
        this.httpClient = axios.create({
            baseURL: this.baseUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
    public async initialize(): Promise<void> {
        try {
            await this.checkConnection();
            this.startStatusMonitoring();
            
            // Connect WebSocket for real-time updates
            await this.connectWebSocket();
            
            console.log('VoidCat Engine Client initialized successfully');
        } catch (error) {
            console.error('Failed to initialize VoidCat engine client:', error);
            throw error;
        }
    }

    public async connect(): Promise<void> {
        try {
            const response = await this.httpClient.get('/health');
            this.isConnected = response.status === 200;
            
            if (this.isConnected) {
                console.log('Connected to VoidCat engine successfully');
            } else {
                throw new Error('Engine health check failed');
            }
        } catch (error) {
            this.isConnected = false;
            console.error('Failed to connect to VoidCat engine:', error);
            throw error;
        }
    }

    public async checkConnection(): Promise<boolean> {
        try {
            await this.connect();
            return this.isConnected;
        } catch {
            return false;
        }
    }

    public async getEngineStatus(): Promise<VoidCatEngineStatus> {
        try {
            const response = await this.httpClient.get('/diagnostics');
            return response.data;
        } catch (error) {
            console.error('Failed to get engine status:', error);
            throw error;
        }
    }
    // Task Management Integration (Pillar I Priority)
    public async getProjects(): Promise<VoidCatProject[]> {
        try {
            const response = await this.httpClient.get('/vscode/api/v1/projects');
            return response.data;
        } catch (error) {
            console.error('Failed to get projects:', error);
            throw error;
        }
    }

    public async getTasks(projectId?: string): Promise<VoidCatTask[]> {
        try {
            const url = projectId ? `/vscode/api/v1/tasks?project_id=${projectId}` : '/vscode/api/v1/tasks';
            const response = await this.httpClient.get(url);
            return response.data;
        } catch (error) {
            console.error('Failed to get tasks:', error);
            throw error;
        }
    }

    public async createTask(task: Partial<VoidCatTask>): Promise<VoidCatTask> {
        try {
            const response = await this.httpClient.post('/vscode/api/v1/tasks', task);
            return response.data;
        } catch (error) {
            console.error('Failed to create task:', error);
            throw error;
        }
    }

    public async updateTask(taskId: string, updates: Partial<VoidCatTask>): Promise<VoidCatTask> {
        try {
            const response = await this.httpClient.put(`/vscode/api/v1/tasks/${taskId}`, updates);
            return response.data;
        } catch (error) {
            console.error('Failed to update task:', error);
            throw error;
        }
    }

    public async deleteTask(taskId: string): Promise<void> {
        try {
            await this.httpClient.delete(`/vscode/api/v1/tasks/${taskId}`);
        } catch (error) {
            console.error('Failed to delete task:', error);
            throw error;
        }
    }
    // AI Reasoning and Code Analysis
    public async queryEngine(query: string, model?: string): Promise<string> {
        try {
            const response = await this.httpClient.post('/query', {
                query,
                model: model || 'gpt-4o-mini'
            });
            return response.data.response;
        } catch (error) {
            console.error('Failed to query engine:', error);
            throw error;
        }
    }

    public async analyzeCode(code: string, language: string, context?: string): Promise<string> {
        try {
            const query = `Analyze this ${language} code:
${code}
${context ? `Context: ${context}` : ''}

Please provide:
1. Code structure analysis
2. Potential improvements
3. Best practices recommendations
4. Security considerations`;
            
            return await this.queryEngine(query);
        } catch (error) {
            console.error('Failed to analyze code:', error);
            throw error;
        }
    }

    public async explainCode(code: string, language: string): Promise<string> {
        try {
            const query = `Explain this ${language} code in detail:
${code}

Please provide a clear explanation of:
1. What the code does
2. How it works
3. Key concepts used
4. Purpose of each major section`;
            
            return await this.queryEngine(query);
        } catch (error) {
            console.error('Failed to explain code:', error);
            throw error;
        }
    }
    public async suggestImprovements(code: string, language: string): Promise<string> {
        try {
            const query = `Suggest improvements for this ${language} code:
${code}

Please provide specific suggestions for:
1. Performance optimizations
2. Code clarity and readability
3. Error handling improvements
4. Modern language features usage
5. Security enhancements`;
            
            return await this.queryEngine(query);
        } catch (error) {
            console.error('Failed to suggest improvements:', error);
            throw error;
        }
    }

    public async semanticSearch(searchQuery: string, scope: 'workspace' | 'file' | 'knowledge_base' = 'workspace'): Promise<string> {
        try {
            const query = `Perform semantic search in ${scope} for: ${searchQuery}
            
Please find relevant code, files, or knowledge that matches this search semantically.`;
            
            return await this.queryEngine(query);
        } catch (error) {
            console.error('Failed to perform semantic search:', error);
            throw error;
        }
    }

    private startStatusMonitoring(): void {
        this.statusCheckInterval = setInterval(async () => {
            try {
                await this.checkConnection();
            } catch (error) {
                console.error('Status check failed:', error);
            }
        }, 30000); // Check every 30 seconds
    }

    public dispose(): void {
        if (this.statusCheckInterval) {
            clearInterval(this.statusCheckInterval);
        }
        
        if (this.websocketReconnectInterval) {
            clearInterval(this.websocketReconnectInterval);
        }
        
        if (this.websocket) {
            this.websocket.close();
        }
        
        this.isConnected = false;
        this.eventHandlers.clear();
    }

    public get connected(): boolean {
        return this.isConnected;
    }

    public get websocketConnected(): boolean {
        return this.websocket?.readyState === WebSocket.OPEN;
    }

    // Enhanced system status with WebSocket information
    public async getSystemStatus(): Promise<any> {
        try {
            const response = await this.httpClient.get('/vscode/api/v1/system/status');
            return {
                ...response.data,
                websocket_connected: this.websocketConnected,
                websocket_url: this.baseUrl.replace('http', 'ws') + '/vscode/api/v1/ws'
            };
        } catch (error) {
            console.error('Failed to get system status:', error);
            throw error;
        }
    }

    // Get intelligent task recommendations
    public async getTaskRecommendations(limit: number = 5): Promise<any> {
        try {
            const response = await this.httpClient.get(`/vscode/api/v1/system/recommendations?limit=${limit}`);
            return response.data;
        } catch (error) {
            console.error('Failed to get task recommendations:', error);
            throw error;
        }
    }

    // Memory Management Integration (Pillar II Priority)
    public async listMemories(): Promise<any[]> {
        try {
            const response = await this.httpClient.get('/vscode/api/v1/memories');
            return response.data;
        } catch (error) {
            console.error('Failed to list memories:', error);
            throw error;
        }
    }
}
    // WebSocket connection for real-time updates
    private websocket?: WebSocket;
    private websocketReconnectInterval?: NodeJS.Timer;
    private eventHandlers: Map<string, ((data: any) => void)[]> = new Map();

    public async connectWebSocket(): Promise<void> {
        try {
            const wsUrl = this.baseUrl.replace('http', 'ws') + '/vscode/api/v1/ws';
            this.websocket = new WebSocket(wsUrl);

            this.websocket.onopen = () => {
                console.log('WebSocket connected to VoidCat engine');
                this.clearReconnectTimer();
            };

            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            this.websocket.onclose = () => {
                console.log('WebSocket disconnected from VoidCat engine');
                this.scheduleReconnect();
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            throw error;
        }
    }

    private handleWebSocketMessage(data: any): void {
        const { type } = data;
        
        if (this.eventHandlers.has(type)) {
            const handlers = this.eventHandlers.get(type)!;
            handlers.forEach(handler => handler(data));
        }
        
        // Emit global update event
        if (this.eventHandlers.has('update')) {
            const handlers = this.eventHandlers.get('update')!;
            handlers.forEach(handler => handler(data));
        }
    }

    private scheduleReconnect(): void {
        if (this.websocketReconnectInterval) {
            clearInterval(this.websocketReconnectInterval);
        }
        
        this.websocketReconnectInterval = setInterval(() => {
            if (!this.websocket || this.websocket.readyState === WebSocket.CLOSED) {
                this.connectWebSocket().catch(console.error);
            }
        }, 5000); // Reconnect every 5 seconds
    }

    private clearReconnectTimer(): void {
        if (this.websocketReconnectInterval) {
            clearInterval(this.websocketReconnectInterval);
            this.websocketReconnectInterval = undefined;
        }
    }

    public addEventListener(eventType: string, handler: (data: any) => void): void {
        if (!this.eventHandlers.has(eventType)) {
            this.eventHandlers.set(eventType, []);
        }
        this.eventHandlers.get(eventType)!.push(handler);
    }

    public removeEventListener(eventType: string, handler: (data: any) => void): void {
        if (this.eventHandlers.has(eventType)) {
            const handlers = this.eventHandlers.get(eventType)!;
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }

    public sendWebSocketMessage(message: any): void {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        }
    }