/**
 * Enhanced Umbuzo Chat Interface with Gemma Model Integration
 * Handles chat interactions, API calls, and UI updates with advanced capabilities
 */

const API_BASE_URL = window.UmbuzoConfig?.API_BASE_URL || 'https://dingy-choking-dutiful.ngrok-free.dev';
const API_URL = `${API_BASE_URL}/chat`; // Umbuzo backend chat API

// Axios configuration for efficient communication with enhanced timeout for complex analysis
axios.defaults.baseURL = API_BASE_URL;
axios.defaults.timeout = window.UmbuzoConfig?.API_TIMEOUT || 120000; // Increased timeout for Gemma analysis
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Enhanced response interceptor for better error handling
axios.interceptors.response.use(
    response => response,
    error => {
        if (window.UmbuzoConfig?.ENABLE_DEBUG_LOGGING) {
            if (error.code === 'ECONNREFUSED') {
                console.error(`Cannot connect to Umbuzo backend. Make sure the server is running on ${API_BASE_URL}`);
                console.error('Run: python umbuzo_api.py');
            } else if (error.response) {
                console.error(`API Error ${error.response.status}:`, error.response.data);
                if (error.response.status === 500) {
                    console.error('Backend model loading issue. Check if Gemma model files exist.');
                }
            } else if (error.code === 'ECONNABORTED') {
                console.error('Request timeout - Gemma analysis may be complex. Try again.');
            } else {
                console.error('Network Error:', error.message);
            }
        }
        return Promise.reject(error);
    }
);

// State management
const state = {
    currentChatId: null,
    conversation: [],
    mode: 'auto',
    country: null,
    chatHistory: [],
    isLoggedIn: false,
    userId: null,
    savedChats: [] // For signed-in users only
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkLoginStatus();
    loadChatHistory();
    setupEventListeners();

    // Check if we should load a specific chat from history page
    const loadChatId = localStorage.getItem('umbuzo_load_chat_id');
    if (loadChatId) {
        localStorage.removeItem('umbuzo_load_chat_id');
        loadChat(loadChatId);
    } else {
        // Only load persisted chat for signed-in users
        if (state.isLoggedIn) {
            loadPersistedChat();
        } else {
            // Anonymous users start fresh
            startFreshSession();
        }
    }
});

// Event Listeners
function setupEventListeners() {
    const chatInput = document.getElementById('chatInput');
    const btnSend = document.getElementById('btnSend');
    const btnNewChat = document.getElementById('btnNewChat');
    const btnAttach = document.getElementById('btnAttach');
    const modelSelector = document.getElementById('modelSelector');

    // Send message on Enter (Shift+Enter for new line)
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    btnSend.addEventListener('click', sendMessage);
    btnNewChat.addEventListener('click', startNewChat);
    btnAttach.addEventListener('click', handleAttach);
    modelSelector.addEventListener('change', (e) => {
        state.mode = e.target.value;
        saveState();
    });
}

// Send message to API with enhanced extension integration
async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();

    if (!message) return;

    // Hide welcome section
    const welcomeSection = document.getElementById('welcomeSection');
    const messagesContainer = document.getElementById('messagesContainer');
    if (welcomeSection) welcomeSection.style.display = 'none';
    if (messagesContainer) messagesContainer.style.display = 'block';

    // Add user message to UI
    addMessage('user', message);
    chatInput.value = '';

    // Add to conversation state
    state.conversation.push({ role: 'user', content: message });
    saveState();

    // Check if message requires extension usage
    const extensionUsage = await detectExtensionUsage(message);

    if (extensionUsage) {
        // Handle extension-based response
        await handleExtensionResponse(message, extensionUsage);
    } else {
        // Handle regular LLM response
        await handleLLMResponse(message);
    }

    // Update chat history
    updateChatHistory();
}

// Detect if message requires extension usage
async function detectExtensionUsage(message) {
    // Check active extensions and their capabilities
    if (!window.ExtensionManager) return null;

    const activeExtensions = window.ExtensionManager.getActiveExtensions();
    if (activeExtensions.length === 0) return null;

    const lowerMessage = message.toLowerCase();

    // Web search patterns
    if (activeExtensions.some(ext => ext.capabilities.includes('web_search'))) {
        const searchPatterns = [
            'search for', 'find information about', 'look up', 'what is the latest',
            'current news about', 'research', 'find out about', 'google', 'search'
        ];
        if (searchPatterns.some(pattern => lowerMessage.includes(pattern))) {
            return { extension: 'web_search', query: extractSearchQuery(message) };
        }
    }

    // Calculator patterns
    if (activeExtensions.some(ext => ext.capabilities.includes('math_calculation'))) {
        const calcPatterns = [
            'calculate', 'compute', 'solve', 'what is', 'how much is', 'equals',
            'plus', 'minus', 'times', 'divided by', '+', '-', '*', '/', '='
        ];
        const hasCalcPattern = calcPatterns.some(pattern => lowerMessage.includes(pattern));
        const hasNumbers = /\d/.test(message);
        if (hasCalcPattern && hasNumbers) {
            return { extension: 'calculator', expression: extractMathExpression(message) };
        }
    }

    // Code execution patterns
    if (activeExtensions.some(ext => ext.capabilities.includes('code_execution'))) {
        const codePatterns = [
            'run this code', 'execute', 'python', 'javascript', 'bash',
            'def ', 'function', 'print(', 'console.log'
        ];
        if (codePatterns.some(pattern => lowerMessage.includes(pattern))) {
            return { extension: 'code_execution', code: extractCodeBlock(message) };
        }
    }

    return null;
}

// Extract search query from message
function extractSearchQuery(message) {
    const patterns = [
        /search for (.+)/i,
        /find information about (.+)/i,
        /look up (.+)/i,
        /what is the latest (.+)/i,
        /research (.+)/i
    ];

    for (const pattern of patterns) {
        const match = message.match(pattern);
        if (match) return match[1].trim();
    }

    // Fallback: remove common prefixes
    return message.replace(/^(can you |please |i want to |i need to )/, '').trim();
}

// Extract mathematical expression from message
function extractMathExpression(message) {
    // Remove common prefixes and extract the expression
    let expression = message
        .replace(/^(calculate|compute|solve|what is|how much is)/i, '')
        .replace(/(equals?|is|=)$/, '')
        .trim();

    // Look for actual math expressions
    const mathMatch = expression.match(/[\d\s\+\-\*\/\(\)\.\^]+/);
    if (mathMatch) {
        return mathMatch[0].trim();
    }

    return expression;
}

// Extract code block from message
function extractCodeBlock(message) {
    // Look for code blocks with ```language
    const codeBlockMatch = message.match(/```(\w+)?\n?([\s\S]*?)```/);
    if (codeBlockMatch) {
        return codeBlockMatch[2].trim();
    }

    // Look for inline code
    const inlineCodeMatch = message.match(/`([^`]+)`/);
    if (inlineCodeMatch) {
        return inlineCodeMatch[1].trim();
    }

    // Return the whole message if no code markers found
    return message.trim();
}

// Handle extension-based response
async function handleExtensionResponse(message, extensionUsage) {
    const { extension, ...params } = extensionUsage;

    showLoading(`Using ${extension.replace('_', ' ')} extension...`);

    try {
        const result = await window.ExtensionManager.executeExtension(extension, params);

        // Format and display extension result
        const formattedResult = formatExtensionResult(extension, result);
        addMessage('Umbuzo', formattedResult, {
            extension: extension,
            capabilities: ['Extension Execution'],
            features: `${extension.replace('_', ' ').toUpperCase()} Extension`,
            timestamp: new Date().toISOString()
        });

        // Update conversation
        state.conversation.push({
            role: 'assistant',
            content: formattedResult,
            metadata: { extension, result }
        });
        saveState();

    } catch (error) {
        console.error('Extension execution error:', error);
        addMessage('System', `Extension error: ${error.message}`, { type: 'error' });

        // Fallback to regular LLM response
        await handleLLMResponse(message);
    } finally {
        hideLoading();
    }
}

// Handle regular LLM response
async function handleLLMResponse(message) {
    // Show enhanced loading for analysis
    showLoading('Umbuzo is analyzing your query with advanced AI capabilities...');

    try {
        // Prepare conversation for API (include full conversation history)
        const conversationForAPI = state.conversation.map(msg => ({
            role: msg.role,
            content: msg.content
        }));

        // API Call to Umbuzo backend with enhanced parameters
        const response = await axios.post(API_URL, {
            conversation: conversationForAPI,
            mode: state.mode,
            country: state.country,
            max_tokens: 1024  // Allow longer responses for complex analysis
        }, {
            timeout: 120000  // Extended timeout for analysis
        });

        // Extract enhanced response data from API
        const botResponse = response.data.reply;
        const usage = response.data.usage || {};

        // Display response with enhanced metadata
        addMessage('Umbuzo', botResponse, {
            model: usage.model || 'Enhanced AI',
            mode: usage.mode || state.mode,
            capabilities: usage.capabilities || ['Critical Analysis', 'Mathematical Reasoning', 'Scientific Inquiry'],
            tokens: usage.tokens_generated || 0,
            features: usage.features || 'RAG Primary Retrieval'
        });

        // Update conversation with assistant response
        state.conversation.push({ role: 'assistant', content: botResponse });
        saveState();

        // Log enhanced analytics
        console.log(`Response - Mode: ${usage.mode}, Tokens: ${usage.tokens_generated}, Model: ${usage.model}`);

        // Show success feedback for complex queries
        if (usage.tokens_generated > 500) {
            showTemporaryMessage('Complex analysis completed successfully!', 'success');
        }

    } catch (error) {
        console.error("API Error:", error);

        // Enhanced error handling
        let errorMessage = 'Failed to reach the AI assistant.';
        let errorType = 'error';

        if (error.response) {
            const status = error.response.status;
            const data = error.response.data;

            if (status === 404) {
                errorMessage = 'API endpoint not found. Make sure the Umbuzo backend server is running on port 8000.';
            } else if (status === 500) {
                errorMessage = 'Model loading error. The AI model may be initializing. Please try again in a moment.';
                errorType = 'warning';
            } else if (status === 503) {
                errorMessage = 'Service temporarily unavailable. Analysis is processing another request.';
                errorType = 'warning';
            } else {
                errorMessage = `API Error (${status}): ${data?.detail || 'Unknown server error'}`;
            }
        } else if (error.code === 'ECONNREFUSED') {
            errorMessage = 'Cannot connect to Umbuzo backend. Please ensure the server is running:<br><code>python fastapi_server.py</code>';
        } else if (error.code === 'ECONNABORTED') {
            errorMessage = 'Request timeout. Complex analysis may take longer. Please try again.';
            errorType = 'warning';
        }

        addMessage('System', errorMessage, { type: errorType });

        // Show helpful suggestions for common errors
        if (error.code === 'ECONNREFUSED') {
            setTimeout(() => {
                showTemporaryMessage('💡 Tip: Start the backend server with "python fastapi_server.py"', 'info');
            }, 2000);
        }
    } finally {
        hideLoading();
    }
}

// Format extension result for display
function formatExtensionResult(extension, result) {
    switch (extension) {
        case 'web_search':
            if (result.success && result.results) {
                let formatted = `🔍 **Search Results for "${result.metadata.query}"**\n\n`;
                result.results.slice(0, 5).forEach((item, index) => {
                    formatted += `${index + 1}. **${item.title}**\n`;
                    formatted += `   ${item.snippet}\n`;
                    formatted += `   🔗 ${item.url}\n\n`;
                });
                if (result.results.length > 5) {
                    formatted += `*And ${result.results.length - 5} more results...*`;
                }
                return formatted;
            }
            break;

        case 'calculator':
            if (result.success) {
                return `🧮 **Calculation Result**\n\n` +
                       `Expression: \`${result.metadata.expression}\`\n` +
                       `Result: **${result.result}**\n\n` +
                       `Steps: ${result.steps.join(', ')}`;
            }
            break;

        case 'code_execution':
            if (result.success) {
                let formatted = `💻 **Code Execution Result**\n\n`;
                formatted += `Language: ${result.language}\n`;
                formatted += `Execution Time: ${result.execution_time.toFixed(2)}s\n\n`;

                if (result.output) {
                    formatted += `**Output:**\n\`\`\`\n${result.output}\`\`\`\n\n`;
                }

                if (result.error) {
                    formatted += `**Errors:**\n\`\`\`\n${result.error}\`\`\`\n\n`;
                }

                return formatted;
            }
            break;

        case 'file_analysis':
            if (result.success) {
                const analysis = result.analysis;
                let formatted = `📄 **File Analysis: ${analysis.file_name}**\n\n`;
                formatted += `Type: ${result.metadata.file_type}\n`;
                formatted += `Size: ${formatFileSize(analysis.file_size)}\n`;

                if (analysis.line_count) {
                    formatted += `Lines: ${analysis.line_count}\n`;
                }

                if (analysis.word_count) {
                    formatted += `Words: ${analysis.word_count}\n`;
                }

                return formatted;
            }
            break;

        case 'image_generation':
            if (result.success) {
                return `🎨 **Image Generated**\n\n` +
                       `Prompt: "${result.metadata.prompt}"\n` +
                       `Style: ${result.metadata.style}\n` +
                       `Size: ${result.metadata.size}\n\n` +
                       `*[Image generation requires external API integration]*`;
            }
            break;
    }

    // Fallback for any unhandled cases
    return `Extension ${extension} executed successfully.`;
}

// Helper function to format file sizes
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Add message to UI with enhanced Gemma metadata display
function addMessage(sender, text, metadata = {}) {
    const messagesContainer = document.getElementById('messagesContainer');
    if (!messagesContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender.toLowerCase().replace(/[^a-z]/g, '')}`;

    // Enhanced message content with metadata
    let contentHTML = `<strong>${sender}:</strong> ${text}`;

    // Add metadata for Umbuzo responses
    if (sender === 'Umbuzo' && Object.keys(metadata).length > 0) {
        contentHTML += '<div class="message-metadata">';

        if (metadata.model) {
            contentHTML += `<span class="metadata-item model">🤖 ${metadata.model}</span>`;
        }

        if (metadata.mode) {
            const modeIcons = {
                'factual': '📊',
                'reasoning': '🧠',
                'creative': '🎨',
                'auto': '⚡'
            };
            contentHTML += `<span class="metadata-item mode">${modeIcons[metadata.mode] || '⚡'} ${metadata.mode}</span>`;
        }

        if (metadata.capabilities && metadata.capabilities.length > 0) {
            contentHTML += `<span class="metadata-item capabilities">✨ ${metadata.capabilities.join(', ')}</span>`;
        }

        if (metadata.tokens > 0) {
            contentHTML += `<span class="metadata-item tokens">📝 ${metadata.tokens} tokens</span>`;
        }

        if (metadata.features) {
            contentHTML += `<span class="metadata-item features">🔍 ${metadata.features}</span>`;
        }

        contentHTML += '</div>';
    }

    // Handle error messages with different styling
    if (metadata.type === 'error' || sender === 'Error') {
        messageDiv.classList.add('error');
    } else if (metadata.type === 'warning' || sender === 'System') {
        messageDiv.classList.add('warning');
    }

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = contentHTML;

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Show/hide loading with custom message
function showLoading(message = 'Umbuzo is thinking...') {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        const textElement = overlay.querySelector('p');
        if (textElement) textElement.textContent = message;
        overlay.style.display = 'flex';
    }

    // Add loading bubble
    const messagesContainer = document.getElementById('messagesContainer');
    if (messagesContainer) {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading-bubble';
        loadingDiv.textContent = message;
        loadingDiv.id = 'loadingBubble';
        messagesContainer.appendChild(loadingDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Show temporary message for feedback
function showTemporaryMessage(message, type = 'info', duration = 3000) {
    // Remove existing temporary messages
    const existingMessages = document.querySelectorAll('.temp-message');
    existingMessages.forEach(msg => msg.remove());

    // Create new temporary message
    const messageDiv = document.createElement('div');
    messageDiv.className = `temp-message ${type}`;
    messageDiv.innerHTML = `
        <span class="temp-message-icon">
            ${type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : '💡'}
        </span>
        <span class="temp-message-text">${message}</span>
    `;

    // Add to page
    document.body.appendChild(messageDiv);

    // Trigger animation
    setTimeout(() => messageDiv.classList.add('show'), 10);

    // Auto-remove after duration
    setTimeout(() => {
        messageDiv.classList.remove('show');
        setTimeout(() => messageDiv.remove(), 300);
    }, duration);
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.style.display = 'none';

    // Remove loading bubble
    const loadingBubble = document.getElementById('loadingBubble');
    if (loadingBubble) loadingBubble.remove();
}

// Start new chat
function startNewChat() {
    state.currentChatId = null;
    state.conversation = [];
    
    const welcomeSection = document.getElementById('welcomeSection');
    const messagesContainer = document.getElementById('messagesContainer');
    
    if (welcomeSection) welcomeSection.style.display = 'block';
    if (messagesContainer) {
        messagesContainer.style.display = 'none';
        messagesContainer.innerHTML = '';
    }
    
    saveState();
}

// Handle file attachment
function handleAttach() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '*/*';
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (file) {
            // TODO: Implement file upload/processing
            console.log('File selected:', file.name);
            alert(`File attachment feature coming soon!\nSelected: ${file.name}`);
        }
    };
    input.click();
}

// Load chat history from localStorage
function loadChatHistory() {
    try {
        const stored = localStorage.getItem('umbuzo_chat_history');
        if (stored) {
            state.chatHistory = JSON.parse(stored);
            renderChatHistory();
        }
    } catch (e) {
        console.error('Error loading chat history:', e);
    }
}

// Render chat history in sidebar
function renderChatHistory() {
    const historyList = document.getElementById('chatHistoryList');
    if (!historyList) return;

    historyList.innerHTML = '';

    // Show last 10 chats
    const recentChats = state.chatHistory.slice(-10).reverse();
    
    recentChats.forEach((chat, index) => {
        const item = document.createElement('div');
        item.className = 'chat-history-item';
        item.textContent = chat.title || `Chat ${recentChats.length - index}`;
        item.onclick = () => loadChat(chat.id);
        historyList.appendChild(item);
    });
}

// Update chat history
function updateChatHistory() {
    if (state.conversation.length === 0) return;

    const chatId = state.currentChatId || `chat_${Date.now()}`;
    state.currentChatId = chatId;

    const firstMessage = state.conversation.find(m => m.role === 'user');
    const title = firstMessage ? firstMessage.content.substring(0, 50) : 'New Chat';

    const chatEntry = {
        id: chatId,
        title: title,
        conversation: state.conversation,
        timestamp: new Date().toISOString()
    };

    // Remove existing entry if updating
    state.chatHistory = state.chatHistory.filter(c => c.id !== chatId);
    state.chatHistory.push(chatEntry);

    // Keep only last 50 chats
    if (state.chatHistory.length > 50) {
        state.chatHistory = state.chatHistory.slice(-50);
    }

    localStorage.setItem('umbuzo_chat_history', JSON.stringify(state.chatHistory));
    renderChatHistory();
}

// Load a specific chat
function loadChat(chatId) {
    const chat = state.chatHistory.find(c => c.id === chatId);
    if (!chat) return;

    state.currentChatId = chatId;
    state.conversation = chat.conversation || [];

    // Render messages
    const welcomeSection = document.getElementById('welcomeSection');
    const messagesContainer = document.getElementById('messagesContainer');
    
    if (welcomeSection) welcomeSection.style.display = 'none';
    if (messagesContainer) {
        messagesContainer.style.display = 'block';
        messagesContainer.innerHTML = '';
        
        state.conversation.forEach(msg => {
            addMessage(msg.role, msg.content);
        });
    }
}

// Load persisted chat state
function loadPersistedChat() {
    try {
        const stored = localStorage.getItem('umbuzo_current_chat');
        if (stored) {
            const data = JSON.parse(stored);
            state.conversation = data.conversation || [];
            state.mode = data.mode || 'auto';
            state.country = data.country || null;
            state.currentChatId = data.currentChatId || null;

            // Restore UI
            const modelSelector = document.getElementById('modelSelector');
            if (modelSelector) modelSelector.value = state.mode;

            if (state.conversation.length > 0) {
                loadChat(state.currentChatId);
            }
        }
    } catch (e) {
        console.error('Error loading persisted chat:', e);
    }
}

// Save current state
function saveState() {
    try {
        localStorage.setItem('umbuzo_current_chat', JSON.stringify({
            conversation: state.conversation,
            mode: state.mode,
            country: state.country,
            currentChatId: state.currentChatId
        }));
    } catch (e) {
        console.error('Error saving state:', e);
    }
}

// Check login status
function checkLoginStatus() {
    // Check for authentication token or user session
    const authToken = localStorage.getItem('umbuzo_auth_token');
    const userData = localStorage.getItem('umbuzo_user_data');

    if (authToken && userData) {
        try {
            const user = JSON.parse(userData);
            state.isLoggedIn = true;
            state.userId = user.id;
            updateUIForLoggedInUser();
            console.log('User logged in:', user.username || user.email);
        } catch (e) {
            console.error('Error parsing user data:', e);
            state.isLoggedIn = false;
            state.userId = null;
        }
    } else {
        state.isLoggedIn = false;
        state.userId = null;
        updateUIForAnonymousUser();
    }
}

// Start fresh session for anonymous users
function startFreshSession() {
    // Clear any existing conversation for anonymous users
    state.currentChatId = null;
    state.conversation = [];

    // Clear localStorage for anonymous users (no persistence)
    localStorage.removeItem('umbuzo_current_chat');
    localStorage.removeItem('umbuzo_chat_history');

    // Reset UI to welcome state
    const welcomeSection = document.getElementById('welcomeSection');
    const messagesContainer = document.getElementById('messagesContainer');

    if (welcomeSection) welcomeSection.style.display = 'block';
    if (messagesContainer) {
        messagesContainer.style.display = 'none';
        messagesContainer.innerHTML = '';
    }

    console.log('Started fresh session for anonymous user');
}

// Update UI for logged-in users
function updateUIForLoggedInUser() {
    // Update navigation buttons
    const signInBtn = document.querySelector('.btn-signin');
    const signUpBtn = document.querySelector('.btn-signup');

    if (signInBtn && signUpBtn) {
        // Change to user menu or logout
        signInBtn.textContent = 'Profile';
        signUpBtn.textContent = 'Logout';
        signInBtn.onclick = () => window.location.href = 'profile.html';
        signUpBtn.onclick = logout;
    }

    // Load user's saved chats
    loadUserSavedChats();
}

// Update UI for anonymous users
function updateUIForAnonymousUser() {
    // Keep default sign in/sign up buttons
    const signInBtn = document.querySelector('.btn-signin');
    const signUpBtn = document.querySelector('.btn-signup');

    if (signInBtn && signUpBtn) {
        signInBtn.onclick = () => window.location.href = 'signin.html';
        signUpBtn.onclick = () => window.location.href = 'signup.html';
    }

    // Clear sidebar history for anonymous users
    const historyList = document.getElementById('chatHistoryList');
    if (historyList) {
        historyList.innerHTML = '<div class="chat-history-item" style="color: #666; font-style: italic;">Sign in to save chats</div>';
    }
}

// Logout function
function logout() {
    localStorage.removeItem('umbuzo_auth_token');
    localStorage.removeItem('umbuzo_user_data');
    localStorage.removeItem('umbuzo_current_chat');
    localStorage.removeItem('umbuzo_chat_history');

    state.isLoggedIn = false;
    state.userId = null;
    state.savedChats = [];

    // Reset UI
    updateUIForAnonymousUser();
    startFreshSession();

    // Redirect to home
    window.location.href = 'index.html';
}

// Load user's saved chats (for logged-in users only)
function loadUserSavedChats() {
    if (!state.isLoggedIn || !state.userId) return;

    try {
        const saved = localStorage.getItem(`umbuzo_saved_chats_${state.userId}`);
        if (saved) {
            state.savedChats = JSON.parse(saved);
            // Update chat history to show saved chats
            renderSavedChats();
        }
    } catch (e) {
        console.error('Error loading saved chats:', e);
    }
}

// Render saved chats for logged-in users
function renderSavedChats() {
    const historyList = document.getElementById('chatHistoryList');
    if (!historyList) return;

    historyList.innerHTML = '';

    // Show saved chats (recallable files)
    const savedChats = state.savedChats.slice(-10).reverse();

    savedChats.forEach((chat, index) => {
        const item = document.createElement('div');
        item.className = 'chat-history-item saved-chat';
        item.innerHTML = `
            <div class="chat-title">${chat.title || `Saved Chat ${savedChats.length - index}`}</div>
            <div class="chat-meta">${new Date(chat.timestamp).toLocaleDateString()}</div>
        `;
        item.onclick = () => loadSavedChat(chat.id);
        historyList.appendChild(item);
    });

    // Add save current chat option if there's an active conversation
    if (state.conversation.length > 0 && state.isLoggedIn) {
        const saveItem = document.createElement('div');
        saveItem.className = 'chat-history-item save-option';
        saveItem.innerHTML = '<div class="chat-title">💾 Save Current Chat</div>';
        saveItem.onclick = () => saveCurrentChat();
        historyList.appendChild(saveItem);
    }
}

// Save current chat for logged-in users
function saveCurrentChat() {
    if (!state.isLoggedIn || !state.userId || state.conversation.length === 0) return;

    const chatId = `saved_${Date.now()}`;
    const firstMessage = state.conversation.find(m => m.role === 'user');
    const title = firstMessage ? firstMessage.content.substring(0, 50) : 'Saved Chat';

    const savedChat = {
        id: chatId,
        title: title,
        conversation: [...state.conversation],
        timestamp: new Date().toISOString(),
        userId: state.userId
    };

    // Remove existing entry if updating
    state.savedChats = state.savedChats.filter(c => c.id !== chatId);
    state.savedChats.push(savedChat);

    // Keep only last 50 saved chats
    if (state.savedChats.length > 50) {
        state.savedChats = state.savedChats.slice(-50);
    }

    // Save to localStorage with user-specific key
    localStorage.setItem(`umbuzo_saved_chats_${state.userId}`, JSON.stringify(state.savedChats));

    renderSavedChats();
    console.log('Chat saved successfully');
}

// Load a saved chat
function loadSavedChat(chatId) {
    const chat = state.savedChats.find(c => c.id === chatId);
    if (!chat) return;

    state.currentChatId = chatId;
    state.conversation = chat.conversation || [];

    // Render messages
    const welcomeSection = document.getElementById('welcomeSection');
    const messagesContainer = document.getElementById('messagesContainer');

    if (welcomeSection) welcomeSection.style.display = 'none';
    if (messagesContainer) {
        messagesContainer.style.display = 'block';
        messagesContainer.innerHTML = '';

        state.conversation.forEach(msg => {
            addMessage(msg.role, msg.content);
        });
    }

    console.log('Loaded saved chat:', chat.title);
}

// Export for use in other scripts
window.umbuzoState = state;
window.umbuzoAPI = {
    sendMessage,
    startNewChat,
    loadChat,
    saveCurrentChat,
    logout,
    checkLoginStatus
};
