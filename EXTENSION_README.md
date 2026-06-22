# OpenWebUI Extensions Integration for Umbuzo

This document describes the OpenWebUI extensions integration that enhances the Umbuzo chatbot with additional capabilities through modular extensions.

## Overview

The extension system allows Umbuzo to integrate with various tools and services, providing users with enhanced functionality beyond basic chat capabilities. Extensions can perform tasks like web search, code execution, mathematical calculations, and more.

## Features

### Core Extensions

1. **Web Search Extension**
   - Search the web for current information
   - Uses DuckDuckGo search engine
   - Configurable number of results
   - Safe and privacy-focused

2. **Code Execution Extension**
   - Execute code in multiple programming languages
   - Supports Python, JavaScript, and Bash
   - Sandboxed execution with timeout limits
   - Syntax highlighting in results

3. **Calculator Extension**
   - Advanced mathematical calculations
   - Symbolic math support with SymPy
   - Configurable precision
   - Supports complex expressions

4. **File Analysis Extension**
   - Analyze uploaded files
   - Support for text, JSON, CSV, and other formats
   - Metadata extraction and content preview
   - Size and type validation

5. **Image Generation Extension** (Placeholder)
   - Framework for image generation
   - Requires external API integration
   - Configurable styles and sizes

## Architecture

### Frontend Components

- **ExtensionManager**: Core extension management system
- **ExtensionsUI**: User interface for extension management
- **Smart Detection**: Automatic extension usage based on user queries
- **Extension Panel**: GUI for configuring and testing extensions

### Backend Components

- **Extension API Endpoints**: RESTful APIs for extension execution
- **Security Controls**: Sandboxed execution and input validation
- **Async Processing**: Non-blocking extension execution
- **Error Handling**: Comprehensive error reporting and fallback

## Installation

### Prerequisites

```bash
pip install fastapi uvicorn
pip install duckduckgo-search sympy matplotlib seaborn
```

### Dependencies

Add these to your `requirements.txt`:

```
# Extension dependencies
duckduckgo-search>=4.0.0
sympy>=1.12.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

## Usage

### Starting the Server

```bash
python fastapi_server.py
```

The server will start on `http://localhost:8000` with all extensions loaded.

### Accessing Extensions

1. **Via Web Interface**:
   - Open `http://localhost:8000` in your browser
   - Click the extensions button (🔧) in the top navigation
   - Enable/disable extensions and configure settings

2. **Via Chat Commands**:
   - Extensions are automatically detected based on query patterns
   - Examples:
     - "Search for latest news about AI" → Web Search
     - "Calculate 2 + 2 * 3" → Calculator
     - "Run this Python code: print('Hello')" → Code Execution

### Extension Configuration

Each extension can be configured through the UI:

- **Web Search**: Results count, search engine preference
- **Code Execution**: Supported languages, timeout settings
- **Calculator**: Precision, math library options
- **File Analysis**: File size limits, supported formats

## API Reference

### Extension Endpoints

#### GET `/api/extensions/list`
Get list of available extensions.

**Response**:
```json
{
  "extensions": [
    {
      "id": "web_search",
      "name": "Web Search",
      "description": "Search the web for current information",
      "type": "tool",
      "capabilities": ["web_search"],
      "enabled": true
    }
  ],
  "timestamp": "2024-01-23T08:00:00.000Z"
}
```

#### POST `/api/extensions/web-search`
Perform web search.

**Request**:
```json
{
  "query": "latest AI developments",
  "max_results": 5,
  "search_engine": "duckduckgo"
}
```

**Response**:
```json
{
  "results": [
    {
      "title": "Latest AI Developments",
      "url": "https://example.com/ai-news",
      "snippet": "Recent breakthroughs in AI technology...",
      "source": "DuckDuckGo"
    }
  ],
  "query": "latest AI developments",
  "total_results": 5,
  "timestamp": "2024-01-23T08:00:00.000Z"
}
```

#### POST `/api/extensions/code-execution`
Execute code.

**Request**:
```json
{
  "code": "print('Hello, World!')",
  "language": "python",
  "timeout": 30
}
```

**Response**:
```json
{
  "output": "Hello, World!\n",
  "error": "",
  "return_code": 0,
  "execution_time": 0.05,
  "language": "python",
  "timestamp": "2024-01-23T08:00:00.000Z"
}
```

#### POST `/api/extensions/calculator`
Perform calculation.

**Request**:
```json
{
  "expression": "2 + 2 * 3",
  "precision": 6
}
```

**Response**:
```json
{
  "result": 8.0,
  "steps": ["Evaluated: 2 + 2 * 3 = 8"],
  "expression": "2 + 2 * 3",
  "precision": 6,
  "timestamp": "2024-01-23T08:00:00.000Z"
}
```

## Security Considerations

### Sandboxed Execution

- Code execution is limited to safe languages (Python, JavaScript, Bash)
- File system access is restricted
- Network access is controlled
- Execution timeouts prevent resource exhaustion

### Input Validation

- All inputs are validated and sanitized
- File uploads have size and type restrictions
- Mathematical expressions are parsed safely
- Search queries are filtered for malicious content

### Permission System

- Extensions can be individually enabled/disabled
- Configuration changes require user interaction
- No automatic execution without user consent

## Development

### Adding New Extensions

1. **Register Extension** in `extensions.js`:
```javascript
extensionManager.registerExtension({
    id: 'my_extension',
    name: 'My Extension',
    description: 'Description of my extension',
    version: '1.0.0',
    author: 'Developer',
    type: 'tool',
    capabilities: ['my_capability'],
    config: { enabled: true },
    execute: this.myExtensionFunction.bind(this)
});
```

2. **Implement Backend Endpoint** in `fastapi_server.py`:
```python
@app.post("/api/extensions/my-extension")
async def my_extension_endpoint(request: Request):
    # Implementation here
    pass
```

3. **Add UI Components** in `extensions-ui.js` if needed

### Extension Patterns

Extensions should follow these patterns:

- **Idempotent**: Multiple calls with same input produce same result
- **Stateless**: No persistent state between calls
- **Fast**: Quick execution to maintain responsive UI
- **Safe**: Input validation and error handling
- **Documented**: Clear API documentation

## Troubleshooting

### Common Issues

1. **Extension Not Working**
   - Check if extension is enabled in the UI
   - Verify backend dependencies are installed
   - Check browser console for JavaScript errors

2. **Code Execution Timeout**
   - Increase timeout in extension settings
   - Check for infinite loops in code
   - Verify system resources

3. **Web Search Fails**
   - Check internet connectivity
   - Verify DuckDuckGo service availability
   - Check for firewall/proxy issues

4. **File Upload Issues**
   - Verify file size is within limits
   - Check supported file types
   - Ensure proper file permissions

### Debug Mode

Enable debug logging in `config.js`:

```javascript
ENABLE_DEBUG_LOGGING: true,
```

Check browser developer tools and server logs for detailed error information.

## Future Enhancements

- **Extension Marketplace**: Community extension sharing
- **Custom Extensions**: User-created extensions
- **Extension Dependencies**: Automatic dependency management
- **Extension Updates**: Automatic update notifications
- **Extension Permissions**: Granular permission controls
- **Extension Analytics**: Usage statistics and performance metrics

## Contributing

To contribute new extensions:

1. Follow the extension development guidelines
2. Test thoroughly with various inputs
3. Provide comprehensive documentation
4. Include security considerations
5. Add appropriate error handling

## License

This extension system is part of the Umbuzo chatbot project and follows the same licensing terms.
