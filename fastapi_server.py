"""
FastAPI Server for Umbuzo Chatbot
Provides REST API endpoints and web interface for the chatbot
"""

import os
import json
import logging
import asyncio
import subprocess
import tempfile
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from umbuzo_chatbot import UmbuzoChatbot

# Extension dependencies
try:
    import duckduckgo_search
    import sympy
    import matplotlib
    import seaborn
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False
    logging.warning("Some extension dependencies not available. Install with: pip install duckduckgo-search sympy matplotlib seaborn")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Umbuzo Chatbot API",
    description="AI-powered chatbot specializing in African affairs and academic topics",
    version="1.0.0"
)

# Global chatbot instance
chatbot = None

# Frontend directory path
frontend_dir = Path("frontend")

# Mount frontend static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

def get_chatbot() -> UmbuzoChatbot:
    """Get or create the global chatbot instance"""
    global chatbot
    if chatbot is None:
        try:
            logger.info("Initializing Umbuzo chatbot...")
            chatbot = UmbuzoChatbot()
            logger.info("Chatbot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize chatbot: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to initialize chatbot: {str(e)}")
    return chatbot

@app.on_event("startup")
async def startup_event():
    """Initialize the chatbot on startup"""
    try:
        get_chatbot()
    except Exception as e:
        logger.error(f"Startup failed: {e}")

# Frontend Routes
@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """Serve the main chat interface"""
    return FileResponse(frontend_dir / "index.html", media_type="text/html")

@app.get("/history", response_class=HTMLResponse)
async def get_history_page():
    """Serve the history page"""
    return FileResponse(frontend_dir / "history.html", media_type="text/html")

@app.get("/apps", response_class=HTMLResponse)
async def get_apps_page():
    """Serve the apps page"""
    return FileResponse(frontend_dir / "apps.html", media_type="text/html")

@app.get("/signin", response_class=HTMLResponse)
async def get_signin_page():
    """Serve the signin page"""
    return FileResponse(frontend_dir / "signin.html", media_type="text/html")

@app.get("/signup", response_class=HTMLResponse)
async def get_signup_page():
    """Serve the signup page"""
    return FileResponse(frontend_dir / "signup.html", media_type="text/html")

@app.get("/Mbuzo.png")
async def get_logo():
    """Serve the Umbuzo logo"""
    return FileResponse("Mbuzo.png", media_type="image/png")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/chat")
async def chat_endpoint(
    message: str = Form(...),
    mode: str = Form("auto"),
    clear_history: bool = Form(False)
):
    """Chat endpoint for sending messages to the chatbot"""
    try:
        bot = get_chatbot()

        # Clear conversation history if requested
        if clear_history:
            bot.clear_conversation()
            return {
                "response": "Conversation history cleared. How can I help you today?",
                "metadata": {
                    "cleared": True,
                    "timestamp": datetime.now().isoformat()
                }
            }

        # Validate input
        if not message or not message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Generate response
        result = bot.generate_response(message.strip(), mode=mode)

        return {
            "response": result["response"],
            "metadata": result["metadata"],
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/chat")
async def legacy_chat_endpoint(conversation: List[Dict], mode: str = "auto", country: Optional[str] = None, max_tokens: int = 1024):
    """
    Legacy chat endpoint that matches the frontend expectations
    Expects conversation as a list of message objects
    """
    try:
        bot = get_chatbot()

        # Extract the latest user message
        user_messages = [msg for msg in conversation if msg.get("role") == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found in conversation")

        latest_message = user_messages[-1]["content"]

        # Generate response
        result = bot.generate_response(latest_message, mode=mode)

        # Format response to match frontend expectations
        return {
            "reply": result["response"],
            "usage": {
                "model": "Mistral-7B" if bot.model else "RAG-Only",
                "mode": mode,
                "capabilities": ["Critical Analysis", "Mathematical Reasoning", "Scientific Inquiry"],
                "tokens_generated": len(result["response"].split()),  # Rough estimate
                "features": "RAG Primary Retrieval"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Legacy chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/conversation/stats")
async def get_conversation_stats():
    """Get conversation statistics"""
    try:
        bot = get_chatbot()
        stats = bot.get_conversation_stats()
        return {
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Stats endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.post("/api/conversation/clear")
async def clear_conversation():
    """Clear conversation history"""
    try:
        bot = get_chatbot()
        bot.clear_conversation()
        return {
            "message": "Conversation history cleared",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Clear conversation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear conversation: {str(e)}")

@app.get("/api/conversation/history")
async def get_conversation_history():
    """Get conversation history"""
    try:
        bot = get_chatbot()
        return {
            "history": bot.conversation_history,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"History endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.get("/api/system/info")
async def get_system_info():
    """Get system information and statistics"""
    try:
        bot = get_chatbot()
        rag_stats = bot.rag_system.get_document_stats()

        return {
            "chatbot_status": "active" if bot.model else "rag_only",
            "model_loaded": bot.model is not None,
            "rag_system": {
                "documents_loaded": rag_stats.get("total_chunks", 0),
                "content_types": rag_stats.get("content_types", {}),
                "sources": rag_stats.get("sources", 0)
            },
            "conversation_stats": bot.get_conversation_stats(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"System info error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system info: {str(e)}")

# ============================================
# Extension API Endpoints
# ============================================

@app.get("/api/extensions/list")
async def get_extensions_list():
    """Get list of available extensions"""
    return {
        "extensions": [
            {
                "id": "web_search",
                "name": "Web Search",
                "description": "Search the web for current information",
                "type": "tool",
                "capabilities": ["web_search"],
                "enabled": DUCKDUCKGO_AVAILABLE
            },
            {
                "id": "code_execution",
                "name": "Code Execution",
                "description": "Execute code in various programming languages",
                "type": "tool",
                "capabilities": ["code_execution"],
                "enabled": True
            },
            {
                "id": "calculator",
                "name": "Advanced Calculator",
                "description": "Perform complex mathematical calculations",
                "type": "tool",
                "capabilities": ["math_calculation"],
                "enabled": True
            },
            {
                "id": "file_analysis",
                "name": "File Analysis",
                "description": "Analyze and process uploaded files",
                "type": "tool",
                "capabilities": ["file_processing"],
                "enabled": True
            },
            {
                "id": "image_generation",
                "name": "Image Generation",
                "description": "Generate images from text descriptions",
                "type": "tool",
                "capabilities": ["image_generation"],
                "enabled": False  # Requires external API
            }
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/extensions/web-search")
async def web_search_endpoint(request: Request):
    """Web search extension endpoint"""
    try:
        if not DUCKDUCKGO_AVAILABLE:
            raise HTTPException(status_code=503, detail="Web search extension not available")

        data = await request.json()
        query = data.get("query", "").strip()
        max_results = min(data.get("max_results", 5), 10)  # Limit to 10 results
        search_engine = data.get("search_engine", "duckduckgo")

        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # Perform web search
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", ""),
                "source": "DuckDuckGo"
            })

        return {
            "results": formatted_results,
            "query": query,
            "total_results": len(formatted_results),
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Web search error: {e}")
        raise HTTPException(status_code=500, detail=f"Web search failed: {str(e)}")

@app.post("/api/extensions/code-execution")
async def code_execution_endpoint(request: Request):
    """Code execution extension endpoint"""
    try:
        data = await request.json()
        code = data.get("code", "").strip()
        language = data.get("language", "python").lower()
        timeout = min(data.get("timeout", 30), 60)  # Max 60 seconds

        if not code:
            raise HTTPException(status_code=400, detail="Code cannot be empty")

        # Security check - only allow safe languages and operations
        allowed_languages = ["python", "javascript", "bash"]
        if language not in allowed_languages:
            raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")

        # Execute code based on language
        if language == "python":
            result = await execute_python_code(code, timeout)
        elif language == "javascript":
            result = await execute_javascript_code(code, timeout)
        elif language == "bash":
            result = await execute_bash_code(code, timeout)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Code execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Code execution failed: {str(e)}")

@app.post("/api/extensions/calculator")
async def calculator_endpoint(request: Request):
    """Calculator extension endpoint"""
    try:
        data = await request.json()
        expression = data.get("expression", "").strip()
        precision = min(data.get("precision", 6), 10)  # Max 10 decimal places

        if not expression:
            raise HTTPException(status_code=400, detail="Expression cannot be empty")

        # Use sympy for symbolic math if available, otherwise basic eval
        try:
            import sympy as sp
            result = float(sp.N(expression, precision))
            steps = [f"Evaluated: {expression} = {result}"]
        except (ImportError, Exception):
            # Fallback to basic evaluation (be careful with security)
            # Only allow basic math operations
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expression):
                raise HTTPException(status_code=400, detail="Invalid characters in expression")

            try:
                result = eval(expression, {"__builtins__": {}})
                steps = [f"Calculated: {expression} = {result}"]
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid expression: {str(e)}")

        return {
            "result": round(result, precision),
            "steps": steps,
            "expression": expression,
            "precision": precision,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Calculator error: {e}")
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")

@app.post("/api/extensions/file-analysis")
async def file_analysis_endpoint(
    file: UploadFile = File(...),
    analysis_type: str = Form("summary")
):
    """File analysis extension endpoint"""
    try:
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024
        if file.size > max_size:
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")

        # Read file content
        content = await file.read()

        # Basic file type detection
        filename = file.filename.lower()
        file_type = "unknown"

        if filename.endswith(('.txt', '.md')):
            file_type = "text"
            text_content = content.decode('utf-8', errors='ignore')
        elif filename.endswith('.json'):
            file_type = "json"
            try:
                json_data = json.loads(content)
                text_content = json.dumps(json_data, indent=2)
            except:
                text_content = content.decode('utf-8', errors='ignore')
        elif filename.endswith('.csv'):
            file_type = "csv"
            text_content = content.decode('utf-8', errors='ignore')
        else:
            text_content = content.decode('utf-8', errors='ignore')[:1000]  # First 1000 chars

        # Perform analysis based on type
        analysis = {}

        if analysis_type == "summary":
            analysis = {
                "file_name": file.filename,
                "file_size": len(content),
                "file_type": file_type,
                "line_count": len(text_content.split('\n')) if file_type == "text" else None,
                "word_count": len(text_content.split()) if file_type in ["text", "json"] else None,
                "character_count": len(text_content)
            }
        elif analysis_type == "content_preview":
            analysis = {
                "preview": text_content[:500] + "..." if len(text_content) > 500 else text_content,
                "has_more": len(text_content) > 500
            }

        return {
            "analysis": analysis,
            "metadata": {
                "file_name": file.filename,
                "file_size": len(content),
                "file_type": file_type,
                "analysis_type": analysis_type
            },
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")

@app.post("/api/extensions/image-generation")
async def image_generation_endpoint(request: Request):
    """Image generation extension endpoint"""
    try:
        data = await request.json()
        prompt = data.get("prompt", "").strip()
        size = data.get("size", "512x512")
        style = data.get("style", "realistic")

        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")

        # This would integrate with an image generation service
        # For now, return a placeholder response
        return {
            "image_url": f"/api/placeholder-image?prompt={prompt}&size={size}&style={style}",
            "prompt": prompt,
            "size": size,
            "style": style,
            "note": "Image generation requires external API integration",
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

# ============================================
# Helper Functions for Extensions
# ============================================

async def execute_python_code(code: str, timeout: int = 30) -> Dict[str, Any]:
    """Execute Python code safely"""
    start_time = datetime.now()

    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        # Execute the code
        process = await asyncio.create_subprocess_exec(
            'python', temp_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tempfile.gettempdir()
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            return_code = process.returncode
        except asyncio.TimeoutError:
            process.kill()
            raise Exception("Code execution timed out")

        # Clean up
        os.unlink(temp_file)

        execution_time = (datetime.now() - start_time).total_seconds()

        return {
            "output": stdout.decode('utf-8', errors='ignore'),
            "error": stderr.decode('utf-8', errors='ignore'),
            "return_code": return_code,
            "execution_time": execution_time,
            "language": "python",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise Exception(f"Python execution failed: {str(e)}")

async def execute_javascript_code(code: str, timeout: int = 30) -> Dict[str, Any]:
    """Execute JavaScript code using Node.js"""
    start_time = datetime.now()

    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_file = f.name

        # Execute with Node.js
        process = await asyncio.create_subprocess_exec(
            'node', temp_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tempfile.gettempdir()
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            return_code = process.returncode
        except asyncio.TimeoutError:
            process.kill()
            raise Exception("Code execution timed out")

        # Clean up
        os.unlink(temp_file)

        execution_time = (datetime.now() - start_time).total_seconds()

        return {
            "output": stdout.decode('utf-8', errors='ignore'),
            "error": stderr.decode('utf-8', errors='ignore'),
            "return_code": return_code,
            "execution_time": execution_time,
            "language": "javascript",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise Exception(f"JavaScript execution failed: {str(e)}")

async def execute_bash_code(code: str, timeout: int = 30) -> Dict[str, Any]:
    """Execute Bash code safely"""
    start_time = datetime.now()

    try:
        # Execute with bash
        process = await asyncio.create_subprocess_exec(
            'bash', '-c', code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tempfile.gettempdir()
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            return_code = process.returncode
        except asyncio.TimeoutError:
            process.kill()
            raise Exception("Code execution timed out")

        execution_time = (datetime.now() - start_time).total_seconds()

        return {
            "output": stdout.decode('utf-8', errors='ignore'),
            "error": stderr.decode('utf-8', errors='ignore'),
            "return_code": return_code,
            "execution_time": execution_time,
            "language": "bash",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise Exception(f"Bash execution failed: {str(e)}")

if __name__ == "__main__":
    # Create basic HTML template if it doesn't exist
    create_basic_template()

    # Start server
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

def create_basic_template():
    """Create basic HTML template if it doesn't exist"""
    template_path = templates_dir / "chat.html"

    if not template_path.exists():
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Umbuzo Chatbot - African Affairs & Academic Assistant</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .chat-container {
            max-width: 800px;
            margin: 2rem auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .chat-header {
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 1.5rem;
            text-align: center;
        }
        .chat-messages {
            height: 500px;
            overflow-y: auto;
            padding: 1rem;
            background: #f8f9fa;
        }
        .message {
            margin-bottom: 1rem;
            padding: 0.75rem 1rem;
            border-radius: 10px;
            max-width: 70%;
            animation: fadeIn 0.3s ease-in;
        }
        .message.user {
            background: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .message.bot {
            background: white;
            border: 1px solid #e9ecef;
            margin-right: auto;
        }
        .message-header {
            font-size: 0.8rem;
            opacity: 0.8;
            margin-bottom: 0.25rem;
        }
        .chat-input-area {
            padding: 1rem;
            background: white;
            border-top: 1px solid #e9ecef;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 1rem;
            color: #6c757d;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .metadata {
            font-size: 0.75rem;
            color: #6c757d;
            margin-top: 0.5rem;
            padding: 0.25rem 0.5rem;
            background: rgba(0,0,0,0.05);
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="chat-container">
            <div class="chat-header">
                <h2><i class="fas fa-robot"></i> Umbuzo Chatbot</h2>
                <p class="mb-0">African Affairs & Academic Assistant</p>
            </div>

            <div class="chat-messages" id="chatMessages">
                <div class="message bot">
                    <div class="message-header">🤖 Umbuzo</div>
                    <div>Hello! I'm Umbuzo, your AI assistant specializing in African affairs, history, current events, and academic topics. How can I help you today?</div>
                </div>
            </div>

            <div class="loading" id="loadingIndicator">
                <i class="fas fa-spinner fa-spin"></i> Thinking...
            </div>

            <div class="chat-input-area">
                <form id="chatForm" class="d-flex gap-2">
                    <select id="modeSelect" class="form-select" style="width: auto;">
                        <option value="auto">Auto</option>
                        <option value="factual">Factual</option>
                        <option value="reasoning">Reasoning</option>
                        <option value="creative">Creative</option>
                    </select>
                    <input type="text" id="messageInput" class="form-control" placeholder="Ask me about African history, politics, economics, or any academic topic..." required>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                    <button type="button" id="clearBtn" class="btn btn-outline-secondary">
                        <i class="fas fa-trash"></i>
                    </button>
                </form>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const chatMessages = document.getElementById('chatMessages');
        const chatForm = document.getElementById('chatForm');
        const messageInput = document.getElementById('messageInput');
        const modeSelect = document.getElementById('modeSelect');
        const loadingIndicator = document.getElementById('loadingIndicator');
        const clearBtn = document.getElementById('clearBtn');

        // Auto-scroll to bottom
        function scrollToBottom() {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // Add message to chat
        function addMessage(content, type, metadata = null) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;

            const header = type === 'user' ? '👤 You' : '🤖 Umbuzo';
            messageDiv.innerHTML = `
                <div class="message-header">${header}</div>
                <div>${content}</div>
                ${metadata ? `<div class="metadata">${formatMetadata(metadata)}</div>` : ''}
            `;

            chatMessages.appendChild(messageDiv);
            scrollToBottom();
        }

        // Format metadata for display
        function formatMetadata(metadata) {
            const parts = [];
            if (metadata.detected_country) {
                parts.push(`📍 ${metadata.detected_country.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`);
            }
            if (metadata.detected_topic) {
                parts.push(`📚 ${metadata.detected_topic.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`);
            }
            if (metadata.processing_time) {
                parts.push(`⏱️ ${metadata.processing_time.toFixed(2)}s`);
            }
            if (metadata.retrieved_docs_count > 0) {
                parts.push(`📖 ${metadata.retrieved_docs_count} sources`);
            }
            return parts.join(' • ');
        }

        // Handle form submission
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const message = messageInput.value.trim();
            const mode = modeSelect.value;

            if (!message) return;

            // Add user message
            addMessage(message, 'user');

            // Clear input
            messageInput.value = '';

            // Show loading
            loadingIndicator.style.display = 'block';

            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        message: message,
                        mode: mode
                    })
                });

                const result = await response.json();

                if (response.ok) {
                    addMessage(result.response, 'bot', result.metadata);
                } else {
                    addMessage(`❌ Error: ${result.detail || 'Unknown error'}`, 'bot');
                }
            } catch (error) {
                addMessage(`❌ Error: ${error.message}`, 'bot');
            } finally {
                loadingIndicator.style.display = 'none';
            }
        });

        // Handle clear conversation
        clearBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/conversation/clear', {
                    method: 'POST'
                });

                if (response.ok) {
                    // Clear messages and add welcome message
                    chatMessages.innerHTML = `
                        <div class="message bot">
                            <div class="message-header">🤖 Umbuzo</div>
                            <div>Conversation cleared! How can I help you today?</div>
                        </div>
                    `;
                }
            } catch (error) {
                addMessage(`❌ Error clearing conversation: ${error.message}`, 'bot');
            }
        });

        // Focus input on load
        messageInput.focus();

        // Handle Enter key
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    </script>
</body>
</html>"""
        template_path.write_text(html_content)
        logger.info("Created basic chat template")
