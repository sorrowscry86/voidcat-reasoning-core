# Changelog

All notable changes to the VoidCat Reasoning Core project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security
- **CRITICAL**: Removed API keys from .env file
- Enhanced .gitignore patterns for better security
- Updated check_api_keys.py to not display parts of API keys

### Added
- Added Team Information to README.md
- Created dedicated tests directory for better organization

### Changed
- Updated SECURITY.md with current supported versions
- Improved repository structure and organization
- Removed temporary and unused files

## [2.1.0] - 2025-07-30

### Security
- **CRITICAL**: Replaced insecure pickle deserialization with secure JSON serialization
- **CRITICAL**: Fixed path traversal vulnerabilities in file operations
- **CRITICAL**: Removed potential command injection vulnerabilities
- Enhanced input validation across all API endpoints
- Improved CORS configuration security

### Added
- Comprehensive security audit script (`security_audit.py`)
- Enhanced memory storage with TF-IDF indexing and semantic search
- Advanced hybrid vectorization with compression support
- Sequential thinking capabilities for complex reasoning
- Context7 integration for enhanced documentation retrieval
- Comprehensive test suite with 91+ tests
- Docker containerization with security best practices
- VS Code extension for enhanced development experience
- MCP (Model Control Protocol) integration for Claude Desktop
- Advanced task management with hierarchical organization
- Persistent memory system with intelligent archiving
- Rate limiting and comprehensive error handling

### Changed
- **BREAKING**: Memory storage format changed from pickle to secure JSON
- **BREAKING**: Cache file extensions changed from .pkl to .json
- Enhanced engine architecture with improved RAG capabilities
- Upgraded to Python 3.13 for development (3.11 for Docker)
- Improved API gateway with comprehensive error handling
- Enhanced test coverage and reliability
- Optimized vector storage and retrieval performance

### Fixed
- All failing tests now pass (91/91 tests passing)
- Memory integration issues with VoidCatEnhancedEngine
- Missing methods in VoidCatStorage class (find_tasks_by_tag, list_projects)
- Priority enum validation issues
- Unicode encoding issues in file operations
- Windows asyncio compatibility issues
- Path handling inconsistencies across platforms

### Removed
- Insecure pickle serialization dependencies
- Deprecated legacy engine implementations
- Unused archived code files

## [2.0.0] - 2025-01-28

### Added
- Enhanced memory storage engine with advanced indexing
- Hybrid vectorization combining TF-IDF and semantic embeddings
- Comprehensive backup and archiving system
- Advanced task management with dependencies and priorities
- MCP server integration for Claude Desktop
- Docker containerization support
- Comprehensive test suite

### Changed
- Complete architecture overhaul for better scalability
- Enhanced API gateway with FastAPI
- Improved error handling and logging
- Better documentation and code organization

### Security
- Implemented secure file operations
- Added input validation and sanitization
- Enhanced API security measures

## [1.0.0] - 2024-12-15

### Added
- Initial VoidCat Reasoning Core implementation
- Basic RAG (Retrieval Augmented Generation) capabilities
- OpenAI API integration
- Simple knowledge base processing
- Basic API endpoints
- Initial documentation

### Features
- Document processing and indexing
- Query processing with context retrieval
- Basic web API interface
- Configuration management
- Error handling

---

## Version History Summary

- **v2.0.0+**: Enhanced security, comprehensive testing, advanced features
- **v1.0.0**: Initial release with basic RAG capabilities

## Migration Notes

### From v1.x to v2.x
- **Memory Storage**: Old pickle-based storage will be automatically migrated to secure JSON format
- **API Changes**: Some endpoint signatures may have changed - check API documentation
- **Configuration**: Review .env.example for new configuration options
- **Dependencies**: Run `pip install -r requirements.txt` to update dependencies

## Security Advisories

### 2025-01-28 - Critical Security Update
- **CVE-PENDING**: Insecure deserialization vulnerability fixed
- **Impact**: Potential remote code execution through malicious pickle files
- **Resolution**: Upgrade to v2.0.0+ immediately
- **Workaround**: None - upgrade required

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.