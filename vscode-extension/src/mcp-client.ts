public async addCategory(categoryName: string): Promise<any> {
        try {
            const response = await this.executeCommand('voidcat_memory_store', {
                content: `User-defined category: ${categoryName}`,
                category: 'system_configuration',
                title: `Category: ${categoryName}`,
                tags: ['category_definition', categoryName]
            });
            return response.data;
        } catch (error) {
            console.error('Error adding category:', error);
            throw error;
        }
    }

    public async listCategories(): Promise<string[]> {
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
        } catch (error) {
            console.error('Error listing categories:', error);
            throw error;
        }
    }

    public async getMemoryStats(): Promise<any> {
        try {
            const response = await this.executeCommand('voidcat_memory_stats', {});
            return response.data;
        } catch (error) {
            console.error('Error getting memory stats:', error);
            throw error;
        }
    }