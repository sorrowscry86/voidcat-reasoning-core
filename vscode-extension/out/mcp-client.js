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
exports.MCPClient = void 0;
class MCPClient {
    constructor(baseUrl = 'http://localhost:8002') {
        this.baseUrl = baseUrl;
    }
    executeCommand(command, params) {
        return __awaiter(this, void 0, void 0, function* () {
            // This would normally make an HTTP request to the MCP server
            // For now, we'll return mock data
            return {
                data: {
                    success: true,
                    result: params
                }
            };
        });
    }
    addCategory(categoryName) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const response = yield this.executeCommand('voidcat_memory_store', {
                    content: `User-defined category: ${categoryName}`,
                    category: 'system_configuration',
                    title: `Category: ${categoryName}`,
                    tags: ['category_definition', categoryName]
                });
                return response.data;
            }
            catch (error) {
                console.error('Error adding category:', error);
                throw error;
            }
        });
    }
    listCategories() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                // This is a placeholder. In a real system, you'd have a dedicated MCP tool
                // to list defined categories or extract them from existing memories.
                // For now, we'll return a hardcoded list plus any dynamically added ones.
                const hardcodedCategories = [
                    "user_preferences", "conversation_history", "learned_heuristics",
                    "behavior_patterns", "context_associations", "task_insights",
                    "system_configuration", "interaction_feedback"
                ];
                // In a real scenario, you might search for memories with tag 'category_definition'
                // and extract their titles or content to get dynamic categories.
                // For simplicity, we'll just return the hardcoded ones for now.
                return hardcodedCategories;
            }
            catch (error) {
                console.error('Error listing categories:', error);
                throw error;
            }
        });
    }
    getMemoryStats() {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const response = yield this.executeCommand('voidcat_memory_stats', {});
                return response.data;
            }
            catch (error) {
                console.error('Error getting memory stats:', error);
                throw error;
            }
        });
    }
    listMemories(query, category) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const response = yield this.executeCommand('voidcat_memory_list', {
                    query: query || '',
                    category: category || ''
                });
                return response.data || [];
            }
            catch (error) {
                console.error('Error listing memories:', error);
                throw error;
            }
        });
    }
}
exports.MCPClient = MCPClient;
//# sourceMappingURL=mcp-client.js.map