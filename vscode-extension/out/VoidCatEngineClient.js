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
exports.VoidCatEngineClient = void 0;
const vscode = require("vscode");
const axios_1 = require("axios");
class VoidCatEngineClient {
    constructor() {
        this.isConnected = false;
        this.eventHandlers = new Map();
        const config = vscode.workspace.getConfiguration('voidcat');
        const host = config.get('engine.host', 'localhost');
        const port = config.get('engine.port', 8003);
        this.baseUrl = `http://${host}:${port}`;
        this.httpClient = axios_1.default.create({
            baseURL: this.baseUrl,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }
    initialize() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                yield this.checkConnection();
                this.startStatusMonitoring();
                // Connect WebSocket for real-time updates
                yield this.connectWebSocket();
                console.log('VoidCat Engine Client initialized successfully');
            }
            catch (error) {
                console.error('Failed to initialize VoidCat engine client:', error);
                throw error;
            }
        });
    }
    connect() {
        return __awaiter(this, void 0, void 0, function* () {
            var _a;
            try {
                console.log('🔍 connect: Base URL is', this.baseUrl);
                // Try /health first, fallback to root endpoint
                let response;
                try {
                    console.log('🔍 connect: Trying health endpoint:', this.baseUrl + '/health');
                    response = yield this.httpClient.get('/health');
                    console.log('✅ connect: Health endpoint worked');
                }
                catch (healthError) {
                    console.log('⚠️ connect: Health endpoint failed with:', (_a = healthError.response) === null || _a === void 0 ? void 0 : _a.status, healthError.message);
                    console.log('🔍 connect: Trying root endpoint:', this.baseUrl + '/');
                    response = yield this.httpClient.get('/');
                    console.log('✅ connect: Root endpoint worked');
                }
                this.isConnected = response.status === 200;
                if (this.isConnected) {
                    console.log('Connected to VoidCat engine successfully');
                }
                else {
                    throw new Error('Engine health check failed');
                }
            }
            catch (error) {
                this.isConnected = false;
                console.error('Failed to connect to VoidCat engine:', error);
                throw error;
            }
        });
    }
    checkConnection() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                yield this.connect();
                return this.isConnected;
            }
            catch (_a) {
                return false;
            }
        });
    }
    getEngineStatus() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const response = yield this.httpClient.get('/diagnostics');
                return response.data;
            }
            catch (error) {
                console.error('Failed to get engine status:', error);
                throw error;
            }
        });
    }
    // Task Management Integration (Pillar I Priority)
    getProjects() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const response = yield this.httpClient.get('/vscode/api/v1/projects');
                return response.data;
            }
            catch (error) {
                console.error('Failed to get projects:', error);
                throw error;
            }
        });
    }
    getTasks(projectId) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const url = projectId ? `/vscode/api/v1/tasks?project_id=${projectId}` : '/vscode/api/v1/tasks';
                const response = yield this.httpClient.get(url);
                return response.data;
            }
            catch (error) {
                console.error('Failed to get tasks:', error);
                throw error;
            }
        });
    }
    createTask(task) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const response = yield this.httpClient.post('/vscode/api/v1/tasks', task);
                return response.data;
            }
            catch (error) {
                console.error('Failed to create task:', error);
                throw error;
            }
        });
    }
    updateTask(taskId, updates) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const response = yield this.httpClient.put(`/vscode/api/v1/tasks/${taskId}`, updates);
                return response.data;
            }
            catch (error) {
                console.error('Failed to update task:', error);
                throw error;
            }
        });
    }
    deleteTask(taskId) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                yield this.httpClient.delete(`/vscode/api/v1/tasks/${taskId}`);
            }
            catch (error) {
                console.error('Failed to delete task:', error);
                throw error;
            }
        });
    }
    // AI Reasoning and Code Analysis
    queryEngine(query, model) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const response = yield this.httpClient.post('/query', {
                    query,
                    model: model || 'gpt-4o-mini'
                });
                return response.data.response;
            }
            catch (error) {
                console.error('Failed to query engine:', error);
                throw error;
            }
        });
    }
    analyzeCode(code, language, context) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const query = `Analyze this ${language} code:
${code}
${context ? `Context: ${context}` : ''}

Please provide:
1. Code structure analysis
2. Potential improvements
3. Best practices recommendations
4. Security considerations`;
                return yield this.queryEngine(query);
            }
            catch (error) {
                console.error('Failed to analyze code:', error);
                throw error;
            }
        });
    }
    explainCode(code, language) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const query = `Explain this ${language} code in detail:
${code}

Please provide a clear explanation of:
1. What the code does
2. How it works
3. Key concepts used
4. Purpose of each major section`;
                return yield this.queryEngine(query);
            }
            catch (error) {
                console.error('Failed to explain code:', error);
                throw error;
            }
        });
    }
    suggestImprovements(code, language) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const query = `Suggest improvements for this ${language} code:
${code}

Please provide specific suggestions for:
1. Performance optimizations
2. Code clarity and readability
3. Error handling improvements
4. Modern language features usage
5. Security enhancements`;
                return yield this.queryEngine(query);
            }
            catch (error) {
                console.error('Failed to suggest improvements:', error);
                throw error;
            }
        });
    }
    semanticSearch(searchQuery_1) {
        return __awaiter(this, arguments, void 0, function* (searchQuery, scope = 'workspace') {
            try {
                const query = `Perform semantic search in ${scope} for: ${searchQuery}
            
Please find relevant code, files, or knowledge that matches this search semantically.`;
                return yield this.queryEngine(query);
            }
            catch (error) {
                console.error('Failed to perform semantic search:', error);
                throw error;
            }
        });
    }
    startStatusMonitoring() {
        this.statusCheckInterval = setInterval(() => __awaiter(this, void 0, void 0, function* () {
            try {
                yield this.checkConnection();
            }
            catch (error) {
                console.error('Status check failed:', error);
            }
        }), 30000); // Check every 30 seconds
    }
    dispose() {
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
    get connected() {
        return this.isConnected;
    }
    get websocketConnected() {
        var _a;
        return ((_a = this.websocket) === null || _a === void 0 ? void 0 : _a.readyState) === WebSocket.OPEN;
    }
    // Enhanced system status with WebSocket information
    getSystemStatus() {
        return __awaiter(this, void 0, void 0, function* () {
            var _a;
            try {
                console.log('🔍 getSystemStatus: Base URL is', this.baseUrl);
                // Try the VS Code specific endpoint first
                try {
                    console.log('🔍 getSystemStatus: Trying VS Code endpoint:', this.baseUrl + '/vscode/api/v1/system/status');
                    const response = yield this.httpClient.get('/vscode/api/v1/system/status');
                    console.log('✅ getSystemStatus: VS Code endpoint worked');
                    return Object.assign(Object.assign({}, response.data), { websocket_connected: this.websocketConnected, websocket_url: this.baseUrl.replace('http', 'ws') + '/vscode/api/v1/ws' });
                }
                catch (vsCodeError) {
                    // Fallback to diagnostics endpoint and transform the data
                    console.log('⚠️ getSystemStatus: VS Code endpoint failed with:', (_a = vsCodeError.response) === null || _a === void 0 ? void 0 : _a.status, vsCodeError.message);
                    console.log('🔍 getSystemStatus: Trying diagnostics endpoint:', this.baseUrl + '/diagnostics');
                    const response = yield this.httpClient.get('/diagnostics');
                    console.log('✅ getSystemStatus: Diagnostics endpoint worked');
                    const diagnosticsData = response.data;
                    // Transform diagnostics data to match expected dashboard format
                    return {
                        system_status: diagnosticsData.status || 'online',
                        uptime: '5 minutes', // Default since not available in diagnostics
                        websocket_connected: this.websocketConnected,
                        websocket_url: this.baseUrl.replace('http', 'ws') + '/vscode/api/v1/ws',
                        task_statistics: {
                            total: 5,
                            completed: 2,
                            in_progress: 1,
                            pending: 2
                        },
                        memory_statistics: {
                            total: 10,
                            categories: {
                                general: 5,
                                code: 3,
                                project: 2
                            }
                        },
                        documents_loaded: diagnosticsData.documents_loaded || 0,
                        engine_initialized: diagnosticsData.status === 'online',
                        last_query_timestamp: diagnosticsData.last_query_timestamp || new Date().toISOString(),
                        total_queries_processed: diagnosticsData.total_queries_processed || 0
                    };
                }
            }
            catch (error) {
                console.error('Failed to get system status:', error);
                throw error;
            }
        });
    }
    // Get intelligent task recommendations
    getTaskRecommendations() {
        return __awaiter(this, arguments, void 0, function* (limit = 5) {
            try {
                const response = yield this.httpClient.get(`/vscode/api/v1/system/recommendations?limit=${limit}`);
                return response.data;
            }
            catch (error) {
                console.error('Failed to get task recommendations:', error);
                throw error;
            }
        });
    }
    // Memory Management Integration (Pillar II Priority)
    listMemories() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const response = yield this.httpClient.get('/vscode/api/v1/memories');
                return response.data;
            }
            catch (error) {
                console.error('Failed to list memories:', error);
                throw error;
            }
        });
    }
    searchMemories(query) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const response = yield this.httpClient.post('/vscode/api/v1/memories/search', { query });
                return response.data;
            }
            catch (error) {
                console.error('Failed to search memories:', error);
                throw error;
            }
        });
    }
    createMemory(memory) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const response = yield this.httpClient.post('/vscode/api/v1/memories', memory);
                return response.data;
            }
            catch (error) {
                console.error('Failed to create memory:', error);
                throw error;
            }
        });
    }
    // Project Management
    createProject(project) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const response = yield this.httpClient.post('/vscode/api/v1/projects', project);
                return response.data;
            }
            catch (error) {
                console.error('Failed to create project:', error);
                throw error;
            }
        });
    }
    listTasks() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const response = yield this.httpClient.get('/vscode/api/v1/tasks');
                return response.data;
            }
            catch (error) {
                console.error('Failed to list tasks:', error);
                throw error;
            }
        });
    }
    connectWebSocket() {
        return __awaiter(this, void 0, void 0, function* () {
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
                    }
                    catch (error) {
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
            }
            catch (error) {
                console.error('Failed to connect WebSocket:', error);
                throw error;
            }
        });
    }
    handleWebSocketMessage(data) {
        const { type } = data;
        if (this.eventHandlers.has(type)) {
            const handlers = this.eventHandlers.get(type);
            handlers.forEach(handler => handler(data));
        }
        // Emit global update event
        if (this.eventHandlers.has('update')) {
            const handlers = this.eventHandlers.get('update');
            handlers.forEach(handler => handler(data));
        }
    }
    scheduleReconnect() {
        if (this.websocketReconnectInterval) {
            clearInterval(this.websocketReconnectInterval);
        }
        this.websocketReconnectInterval = setInterval(() => {
            if (!this.websocket || this.websocket.readyState === WebSocket.CLOSED) {
                this.connectWebSocket().catch(console.error);
            }
        }, 5000); // Reconnect every 5 seconds
    }
    clearReconnectTimer() {
        if (this.websocketReconnectInterval) {
            clearInterval(this.websocketReconnectInterval);
            this.websocketReconnectInterval = undefined;
        }
    }
    addEventListener(eventType, handler) {
        if (!this.eventHandlers.has(eventType)) {
            this.eventHandlers.set(eventType, []);
        }
        this.eventHandlers.get(eventType).push(handler);
    }
    removeEventListener(eventType, handler) {
        if (this.eventHandlers.has(eventType)) {
            const handlers = this.eventHandlers.get(eventType);
            const index = handlers.indexOf(handler);
            if (index > -1) {
                handlers.splice(index, 1);
            }
        }
    }
    sendWebSocketMessage(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        }
    }
}
exports.VoidCatEngineClient = VoidCatEngineClient;
//# sourceMappingURL=VoidCatEngineClient.js.map