/**
 * OpenWebUI Extensions Integration
 * Manages extension loading, registration, and execution
 */

class ExtensionManager {
    constructor() {
        this.extensions = new Map();
        this.activeExtensions = new Set();
        this.extensionConfigs = new Map();
        this.eventListeners = new Map();

        // Initialize core extensions
        this.initializeCoreExtensions();
    }

    /**
     * Initialize built-in core extensions
     */
    initializeCoreExtensions() {
        // Web Search Extension
        this.registerExtension({
            id: 'web_search',
            name: 'Web Search',
            description: 'Search the web for current information',
            version: '1.0.0',
            author: 'Umbuzo',
            type: 'tool',
            capabilities: ['web_search'],
            config: {
                enabled: true,
                max_results: 5,
                search_engine: 'duckduckgo'
            },
            execute: this.webSearch.bind(this)
        });

        // Code Execution Extension
        this.registerExtension({
            id: 'code_execution',
            name: 'Code Execution',
            description: 'Execute code in various programming languages',
            version: '1.0.0',
            author: 'Umbuzo',
            type: 'tool',
            capabilities: ['code_execution'],
            config: {
                enabled: true,
                supported_languages: ['python', 'javascript', 'bash'],
                timeout: 30
            },
            execute: this.executeCode.bind(this)
        });

        // Calculator Extension
        this.registerExtension({
            id: 'calculator',
            name: 'Advanced Calculator',
            description: 'Perform complex mathematical calculations',
            version: '1.0.0',
            author: 'Umbuzo',
            type: 'tool',
            capabilities: ['math_calculation'],
            config: {
                enabled: true,
                precision: 6
            },
            execute: this.calculate.bind(this)
        });

        // File Analysis Extension
        this.registerExtension({
            id: 'file_analysis',
            name: 'File Analysis',
            description: 'Analyze and process uploaded files',
            version: '1.0.0',
            author: 'Umbuzo',
            type: 'tool',
            capabilities: ['file_processing'],
            config: {
                enabled: true,
                max_file_size: 10 * 1024 * 1024, // 10MB
                supported_types: ['.txt', '.pdf', '.docx', '.csv', '.json']
            },
            execute: this.analyzeFile.bind(this)
        });

        // Image Generation Extension
        this.registerExtension({
            id: 'image_generation',
            name: 'Image Generation',
            description: 'Generate images from text descriptions',
            version: '1.0.0',
            author: 'Umbuzo',
            type: 'tool',
            capabilities: ['image_generation'],
            config: {
                enabled: true,
                default_size: '512x512',
                style: 'realistic'
            },
            execute: this.generateImage.bind(this)
        });
    }

    /**
     * Register a new extension
     */
    registerExtension(extension) {
        this.extensions.set(extension.id, extension);
        this.extensionConfigs.set(extension.id, { ...extension.config });

        // Emit extension registered event
        this.emit('extensionRegistered', extension);
    }

    /**
     * Enable an extension
     */
    enableExtension(extensionId) {
        const extension = this.extensions.get(extensionId);
        if (extension) {
            this.activeExtensions.add(extensionId);
            this.emit('extensionEnabled', extension);
            return true;
        }
        return false;
    }

    /**
     * Disable an extension
     */
    disableExtension(extensionId) {
        if (this.activeExtensions.has(extensionId)) {
            this.activeExtensions.delete(extensionId);
            const extension = this.extensions.get(extensionId);
            this.emit('extensionDisabled', extension);
            return true;
        }
        return false;
    }

    /**
     * Get active extensions
     */
    getActiveExtensions() {
        return Array.from(this.activeExtensions).map(id => this.extensions.get(id));
    }

    /**
     * Get all registered extensions
     */
    getAllExtensions() {
        return Array.from(this.extensions.values());
    }

    /**
     * Update extension configuration
     */
    updateExtensionConfig(extensionId, config) {
        if (this.extensionConfigs.has(extensionId)) {
            this.extensionConfigs.set(extensionId, { ...this.extensionConfigs.get(extensionId), ...config });
            this.emit('extensionConfigUpdated', { extensionId, config });
            return true;
        }
        return false;
    }

    /**
     * Get extension configuration
     */
    getExtensionConfig(extensionId) {
        return this.extensionConfigs.get(extensionId);
    }

    /**
     * Execute extension function
     */
    async executeExtension(extensionId, params = {}) {
        const extension = this.extensions.get(extensionId);
        if (!extension || !this.activeExtensions.has(extensionId)) {
            throw new Error(`Extension ${extensionId} not found or not active`);
        }

        try {
            const result = await extension.execute(params, this.getExtensionConfig(extensionId));
            this.emit('extensionExecuted', { extensionId, params, result });
            return result;
        } catch (error) {
            this.emit('extensionError', { extensionId, params, error });
            throw error;
        }
    }

    /**
     * Web Search Extension Implementation
     */
    async webSearch(params, config) {
        const { query, max_results = config.max_results } = params;

        try {
            const response = await axios.post('/api/extensions/web-search', {
                query,
                max_results,
                search_engine: config.search_engine
            });

            return {
                success: true,
                results: response.data.results,
                metadata: {
                    extension: 'web_search',
                    query,
                    results_count: response.data.results.length,
                    timestamp: new Date().toISOString()
                }
            };
        } catch (error) {
            throw new Error(`Web search failed: ${error.message}`);
        }
    }

    /**
     * Code Execution Extension Implementation
     */
    async executeCode(params, config) {
        const { code, language = 'python', timeout = config.timeout } = params;

        if (!config.supported_languages.includes(language)) {
            throw new Error(`Unsupported language: ${language}`);
        }

        try {
            const response = await axios.post('/api/extensions/code-execution', {
                code,
                language,
                timeout
            });

            return {
                success: true,
                output: response.data.output,
                error: response.data.error,
                execution_time: response.data.execution_time,
                metadata: {
                    extension: 'code_execution',
                    language,
                    timeout,
                    timestamp: new Date().toISOString()
                }
            };
        } catch (error) {
            throw new Error(`Code execution failed: ${error.message}`);
        }
    }

    /**
     * Calculator Extension Implementation
     */
    async calculate(params, config) {
        const { expression, precision = config.precision } = params;

        try {
            const response = await axios.post('/api/extensions/calculator', {
                expression,
                precision
            });

            return {
                success: true,
                result: response.data.result,
                steps: response.data.steps,
                metadata: {
                    extension: 'calculator',
                    expression,
                    precision,
                    timestamp: new Date().toISOString()
                }
            };
        } catch (error) {
            throw new Error(`Calculation failed: ${error.message}`);
        }
    }

    /**
     * File Analysis Extension Implementation
     */
    async analyzeFile(params, config) {
        const { file, analysis_type = 'summary' } = params;

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('analysis_type', analysis_type);

            const response = await axios.post('/api/extensions/file-analysis', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            return {
                success: true,
                analysis: response.data.analysis,
                metadata: response.data.metadata,
                extension_metadata: {
                    extension: 'file_analysis',
                    file_name: file.name,
                    file_size: file.size,
                    analysis_type,
                    timestamp: new Date().toISOString()
                }
            };
        } catch (error) {
            throw new Error(`File analysis failed: ${error.message}`);
        }
    }

    /**
     * Image Generation Extension Implementation
     */
    async generateImage(params, config) {
        const { prompt, size = config.default_size, style = config.style } = params;

        try {
            const response = await axios.post('/api/extensions/image-generation', {
                prompt,
                size,
                style
            });

            return {
                success: true,
                image_url: response.data.image_url,
                metadata: {
                    extension: 'image_generation',
                    prompt,
                    size,
                    style,
                    timestamp: new Date().toISOString()
                }
            };
        } catch (error) {
            throw new Error(`Image generation failed: ${error.message}`);
        }
    }

    /**
     * Event system for extension management
     */
    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }

    off(event, callback) {
        if (this.eventListeners.has(event)) {
            const listeners = this.eventListeners.get(event);
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }

    emit(event, data) {
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event listener for ${event}:`, error);
                }
            });
        }
    }

    /**
     * Load extension settings from localStorage
     */
    loadSettings() {
        try {
            const settings = localStorage.getItem('umbuzo_extension_settings');
            if (settings) {
                const parsed = JSON.parse(settings);
                this.activeExtensions = new Set(parsed.activeExtensions || []);
                this.extensionConfigs = new Map(Object.entries(parsed.configs || {}));
            }
        } catch (error) {
            console.error('Error loading extension settings:', error);
        }
    }

    /**
     * Save extension settings to localStorage
     */
    saveSettings() {
        try {
            const settings = {
                activeExtensions: Array.from(this.activeExtensions),
                configs: Object.fromEntries(this.extensionConfigs)
            };
            localStorage.setItem('umbuzo_extension_settings', JSON.stringify(settings));
        } catch (error) {
            console.error('Error saving extension settings:', error);
        }
    }
}

// Global extension manager instance
const extensionManager = new ExtensionManager();

// Export for global access
window.ExtensionManager = extensionManager;
window.extensions = extensionManager;
