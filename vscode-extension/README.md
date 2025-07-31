# VoidCat Reasoning Core - VS Code Extension

## Overview

The VoidCat Reasoning Core VS Code Extension provides seamless integration between Visual Studio Code and the VoidCat Reasoning Engine, enabling intelligent code analysis, documentation generation, and AI-powered development assistance directly within your IDE.

## Features

### 🧠 Intelligent Code Analysis
- **Real-time Code Understanding**: Analyze code context and provide intelligent insights
- **Documentation Generation**: Automatically generate comprehensive documentation for your code
- **Code Quality Assessment**: Identify potential improvements and best practices
- **Security Analysis**: Detect potential security vulnerabilities in your code

### 🔍 Advanced Search & Retrieval
- **Semantic Code Search**: Find code snippets based on functionality, not just keywords
- **Context-Aware Suggestions**: Get relevant code examples and documentation
- **Cross-Project Knowledge**: Access insights from your entire codebase
- **Smart Refactoring Suggestions**: AI-powered refactoring recommendations

### 📊 Development Insights
- **Project Analytics**: Understand your codebase structure and complexity
- **Development Patterns**: Identify common patterns and anti-patterns
- **Performance Insights**: Get suggestions for performance optimization
- **Dependency Analysis**: Understand your project's dependency graph

### 🤖 AI-Powered Assistance
- **Natural Language Queries**: Ask questions about your code in plain English
- **Code Explanation**: Get detailed explanations of complex code sections
- **Bug Detection**: Identify potential bugs and issues before they become problems
- **Test Generation**: Generate unit tests for your functions and classes

## Installation

### Prerequisites
- Visual Studio Code 1.85.0 or higher
- Node.js 18.0 or higher
- Python 3.11 or higher
- VoidCat Reasoning Core API running (see main README.md)

### Install from VSIX (Development)

1. **Build the Extension**:
   ```bash
   cd vscode-extension
   npm install
   npm run compile
   ```

2. **Package the Extension**:
   ```bash
   npm install -g vsce
   vsce package
   ```

3. **Install in VS Code**:
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Click the "..." menu and select "Install from VSIX..."
   - Select the generated `.vsix` file

### Install from Marketplace (Coming Soon)
The extension will be available on the VS Code Marketplace once published.

## Configuration

### Extension Settings

Configure the extension through VS Code settings (`Ctrl+,`):

```json
{
  "voidcat.apiUrl": "http://localhost:8000",
  "voidcat.apiKey": "your-openai-api-key",
  "voidcat.enableRealTimeAnalysis": true,
  "voidcat.maxContextLines": 100,
  "voidcat.analysisDelay": 2000,
  "voidcat.enableSecurityScanning": true,
  "voidcat.enablePerformanceHints": true
}
```

### Settings Reference

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `voidcat.apiUrl` | string | `http://localhost:8000` | VoidCat API endpoint URL |
| `voidcat.apiKey` | string | `""` | OpenAI API key for processing |
| `voidcat.enableRealTimeAnalysis` | boolean | `true` | Enable real-time code analysis |
| `voidcat.maxContextLines` | number | `100` | Maximum lines of context to analyze |
| `voidcat.analysisDelay` | number | `2000` | Delay (ms) before triggering analysis |
| `voidcat.enableSecurityScanning` | boolean | `true` | Enable security vulnerability detection |
| `voidcat.enablePerformanceHints` | boolean | `true` | Enable performance optimization hints |

## Usage

### Command Palette Commands

Access VoidCat features through the Command Palette (`Ctrl+Shift+P`):

- **VoidCat: Analyze Current File** - Analyze the currently open file
- **VoidCat: Generate Documentation** - Generate documentation for selected code
- **VoidCat: Explain Code** - Get an explanation of selected code
- **VoidCat: Find Similar Code** - Find similar code patterns in your project
- **VoidCat: Security Scan** - Perform security analysis on current file
- **VoidCat: Generate Tests** - Generate unit tests for selected functions
- **VoidCat: Optimize Performance** - Get performance optimization suggestions
- **VoidCat: Open Diagnostics Panel** - Open the VoidCat diagnostics panel

### Context Menu Integration

Right-click on code to access VoidCat features:
- **Analyze with VoidCat** - Quick analysis of selected code
- **Generate Documentation** - Create documentation for the selection
- **Explain This Code** - Get a detailed explanation
- **Find Similar Patterns** - Search for similar code patterns

### Diagnostics Panel

The VoidCat Diagnostics Panel provides:
- **Code Quality Metrics** - Complexity, maintainability scores
- **Security Issues** - Potential vulnerabilities and fixes
- **Performance Insights** - Optimization opportunities
- **Documentation Coverage** - Missing or incomplete documentation
- **Test Coverage** - Areas needing test coverage

### Hover Information

Hover over functions, classes, or variables to get:
- **AI-Generated Explanations** - What the code does
- **Usage Examples** - How to use the code
- **Related Documentation** - Links to relevant docs
- **Potential Issues** - Warnings about potential problems

## Features in Detail

### Real-Time Code Analysis

The extension continuously analyzes your code as you type, providing:

- **Syntax and Logic Validation** - Beyond basic syntax checking
- **Best Practice Recommendations** - Coding standards and patterns
- **Security Vulnerability Detection** - Common security issues
- **Performance Bottleneck Identification** - Slow or inefficient code

### Documentation Generation

Automatically generate comprehensive documentation:

```python
def complex_function(data, options=None):
    # VoidCat can generate documentation like:
    """
    Process complex data with configurable options.
    
    Args:
        data (List[Dict]): Input data to process
        options (Dict, optional): Configuration options
    
    Returns:
        Dict: Processed results with metadata
    
    Raises:
        ValueError: If data format is invalid
        ProcessingError: If processing fails
    """
```

### Intelligent Code Search

Search your codebase using natural language:
- "Find functions that handle file uploads"
- "Show me error handling patterns"
- "Find database connection code"
- "Locate authentication logic"

### Security Analysis

Detect common security issues:
- **SQL Injection** - Unsafe database queries
- **XSS Vulnerabilities** - Cross-site scripting risks
- **Path Traversal** - Unsafe file operations
- **Hardcoded Secrets** - API keys and passwords in code
- **Insecure Dependencies** - Vulnerable third-party packages

## Keyboard Shortcuts

| Shortcut | Command | Description |
|----------|---------|-------------|
| `Ctrl+Alt+V` | Analyze Current File | Quick analysis of current file |
| `Ctrl+Alt+D` | Generate Documentation | Generate docs for selection |
| `Ctrl+Alt+E` | Explain Code | Explain selected code |
| `Ctrl+Alt+S` | Security Scan | Run security analysis |
| `Ctrl+Alt+T` | Generate Tests | Generate unit tests |
| `Ctrl+Alt+P` | Open Diagnostics Panel | Show VoidCat panel |

## Troubleshooting

### Common Issues

1. **Extension Not Loading**
   - Check VS Code version compatibility
   - Ensure all dependencies are installed
   - Check the Output panel for error messages

2. **API Connection Issues**
   - Verify VoidCat API is running on the configured URL
   - Check network connectivity
   - Validate API key configuration

3. **Analysis Not Working**
   - Check if real-time analysis is enabled
   - Verify file types are supported
   - Check analysis delay settings

4. **Performance Issues**
   - Reduce `maxContextLines` setting
   - Increase `analysisDelay` setting
   - Disable real-time analysis for large files

### Debug Mode

Enable debug logging:

1. Open VS Code settings
2. Search for "voidcat.debug"
3. Enable debug mode
4. Check the Output panel for detailed logs

### Log Files

Extension logs are available in:
- **Windows**: `%APPDATA%\Code\logs\voidcat-extension.log`
- **macOS**: `~/Library/Application Support/Code/logs/voidcat-extension.log`
- **Linux**: `~/.config/Code/logs/voidcat-extension.log`

## Development

### Building from Source

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/voidcat-reasoning-core.git
   cd voidcat-reasoning-core/vscode-extension
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Compile TypeScript**:
   ```bash
   npm run compile
   ```

4. **Run in Development Mode**:
   - Press `F5` in VS Code to launch Extension Development Host
   - Test your changes in the new VS Code window

### Project Structure

```
vscode-extension/
├── src/
│   ├── extension.ts          # Main extension entry point
│   ├── commands/             # Command implementations
│   ├── providers/            # Language providers
│   ├── panels/               # WebView panels
│   └── utils/                # Utility functions
├── resources/                # Icons and assets
├── package.json              # Extension manifest
├── tsconfig.json             # TypeScript configuration
└── webpack.config.js         # Build configuration
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## API Integration

The extension communicates with the VoidCat Reasoning Core API:

### Authentication

```typescript
const apiClient = new VoidCatApiClient({
    baseUrl: 'http://localhost:8000',
    apiKey: process.env.OPENAI_API_KEY
});
```

### Making Requests

```typescript
// Analyze code
const analysis = await apiClient.analyzeCode({
    code: selectedText,
    language: document.languageId,
    context: surroundingCode
});

// Generate documentation
const docs = await apiClient.generateDocumentation({
    code: functionCode,
    style: 'google'  // or 'numpy', 'sphinx'
});
```

## Privacy and Security

### Data Handling
- **Code Analysis**: Code is sent to the VoidCat API for analysis
- **No Persistent Storage**: Code is not stored permanently
- **Encryption**: All API communications use HTTPS
- **API Key Security**: API keys are stored securely in VS Code settings

### Privacy Controls
- **Opt-out Options**: Disable features you don't want to use
- **Local Processing**: Some features can run locally
- **Data Retention**: Configure how long analysis results are cached

## Support

### Getting Help
- **Documentation**: Check this README and the main project docs
- **Issues**: Report bugs on the GitHub repository
- **Discussions**: Join community discussions
- **Email**: Contact the development team

### Feature Requests
We welcome feature requests! Please:
1. Check existing issues first
2. Provide detailed use cases
3. Include mockups or examples if possible

## Changelog

### Version 1.0.0 (Current)
- Initial release
- Real-time code analysis
- Documentation generation
- Security scanning
- Performance insights
- Diagnostics panel

### Planned Features
- **Code Completion**: AI-powered code suggestions
- **Refactoring Tools**: Automated code refactoring
- **Team Collaboration**: Share insights with team members
- **Custom Rules**: Define custom analysis rules
- **Integration**: Connect with other development tools

## License

This extension is licensed under the MIT License. See the main project LICENSE file for details.

---

**Happy Coding with VoidCat! 🚀**