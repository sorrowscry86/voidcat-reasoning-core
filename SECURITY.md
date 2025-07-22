# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of VoidCat Reasoning Core seriously. If you believe you've found a security vulnerability, please follow these steps:

1. **Do not disclose the vulnerability publicly**
2. **Email us at [team@voidcat-reasoning.com](mailto:team@voidcat-reasoning.com)** with details about the vulnerability
3. Include the following information:
   - Type of vulnerability
   - Full path to source file(s) related to the issue
   - Steps to reproduce
   - Potential impact

## Security Measures

VoidCat Reasoning Core implements several security measures:

- Input validation for all API parameters
- Path traversal prevention for file operations
- Rate limiting to prevent abuse
- Secure serialization practices
- Environment variable management for sensitive data
- HTTPS enforcement in production environments

## Dependencies

We regularly monitor and update our dependencies to address known vulnerabilities. Our CI/CD pipeline includes automated security scanning.
