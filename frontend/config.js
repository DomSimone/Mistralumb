/**
 * Frontend Configuration
 * Environment-specific settings for API communication
 */

const CONFIG = {
    // API Configuration
    API_BASE_URL: 'https://dingy-choking-dutiful.ngrok-free.dev',
    API_TIMEOUT: 60000, // 60 seconds for model inference

    // Frontend Server
    FRONTEND_PORT: 8080,

    // Environment Settings
    ENVIRONMENT: 'development', // 'development' | 'production'

    // Feature Flags
    ENABLE_DEBUG_LOGGING: true,
    ENABLE_CHAT_HISTORY: true,
    ENABLE_APPS: true,
    ENABLE_USER_AUTHENTICATION: true,
    ENABLE_CHAT_SAVING: true, // For signed-in users only
    ENABLE_MODEL_SWITCHING: true,
    ENABLE_GEMMA_MODEL: true, // Enhanced Gemma 3B model
    ENABLE_RAG_SYSTEM: true, // RAG as primary data retrieval
    ENABLE_CRITICAL_ANALYSIS: true, // Critical analysis capabilities
    ENABLE_MATHEMATICAL_REASONING: true, // Mathematical reasoning
    ENABLE_SCIENTIFIC_INQUIRY: true, // Scientific analysis capabilities
    ENABLE_ANALYSIS_METADATA: true, // Show analysis metadata in responses

    // UI Settings
    MAX_CHAT_HISTORY_ITEMS: 50,
    DEFAULT_MODEL_MODE: 'auto',
    MAX_MESSAGE_LENGTH: 4000,

    // App Configurations
    APPS: {
        report: {
            title: 'Report Generator',
            description: 'Generate comprehensive reports with data visualization',
            endpoint: '/chat',
            maxTokens: 1000
        },
        image: {
            title: 'Image Generator',
            description: 'Create AI-powered images from text descriptions',
            endpoint: '/images',
            defaultWidth: 512,
            defaultHeight: 512
        },
        analyzer: {
            title: 'Data Analyzer',
            description: 'Statistical analysis, correlation, and regression',
            endpoint: '/data-analysis/stats'
        },
        math: {
            title: 'Math Calculator',
            description: 'Complex calculus, solving equations, and symbolic math',
            endpoint: '/math'
        },
        visualize: {
            title: 'Data Visualization',
            description: 'Create charts and graphs from your data',
            endpoint: '/visualize'
        },
        country: {
            title: 'Country Insights',
            description: 'Get detailed information about African countries',
            endpoint: '/chat',
            maxTokens: 500
        }
    }
};

// Environment-specific overrides
if (typeof window !== 'undefined') {
    // Browser environment
    const hostname = window.location.hostname;
    const port = window.location.port;

    // Detect if running on different ports
    if (port === '3000') {
        CONFIG.FRONTEND_PORT = 3000;
    }

    // Production environment detection
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
        CONFIG.ENVIRONMENT = 'production';
        CONFIG.ENABLE_DEBUG_LOGGING = false;
        // In production, you might want to use relative URLs or different API endpoints
        // CONFIG.API_BASE_URL = '/api'; // For same-domain deployment
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
} else if (typeof window !== 'undefined') {
    window.UmbuzoConfig = CONFIG;
}
