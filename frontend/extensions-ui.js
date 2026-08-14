/**
 * Extensions UI Components
 * Provides UI controls for managing and interacting with extensions
 */

class ExtensionsUI {
    constructor(extensionManager) {
        this.extensionManager = extensionManager;
        this.isPanelVisible = false;
        this.currentExtension = null;

        this.initializeUI();
        this.setupEventListeners();
        this.loadExtensionSettings();
    }

    /**
     * Initialize the extensions UI
     */
    initializeUI() {
        this.createExtensionsPanel();
        this.createExtensionsButton();
        this.updateExtensionsList();
    }

    /**
     * Create the extensions panel
     */
    createExtensionsPanel() {
        const panel = document.createElement('div');
        panel.id = 'extensionsPanel';
        panel.className = 'extensions-panel';
        panel.innerHTML = `
            <div class="extensions-header">
                <h3>Extensions</h3>
                <button class="btn-close-extensions" id="btnCloseExtensions">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>

            <div class="extensions-content">
                <div class="extensions-list" id="extensionsList">
                    <!-- Extensions will be populated here -->
                </div>

                <div class="extension-details" id="extensionDetails" style="display: none;">
                    <div class="extension-info">
                        <h4 id="extensionTitle"></h4>
                        <p id="extensionDescription"></p>
                        <div class="extension-meta">
                            <span class="extension-version" id="extensionVersion"></span>
                            <span class="extension-author" id="extensionAuthor"></span>
                        </div>
                    </div>

                    <div class="extension-config" id="extensionConfig">
                        <!-- Configuration options will be populated here -->
                    </div>

                    <div class="extension-actions">
                        <button class="btn-extension-toggle" id="btnToggleExtension">
                            Enable
                        </button>
                        <button class="btn-extension-test" id="btnTestExtension">
                            Test
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(panel);
        this.panel = panel;
    }

    /**
     * Create the extensions toggle button
     */
    createExtensionsButton() {
        const button = document.createElement('button');
        button.id = 'btnExtensions';
        button.className = 'btn-extensions';
        button.title = 'Extensions';
        button.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="9" cy="9" r="2"></circle>
                <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"></path>
            </svg>
            <span class="extension-count" id="extensionCount">0</span>
        `;

        // Add to navigation
        const navRight = document.querySelector('.nav-right');
        if (navRight) {
            navRight.insertBefore(button, navRight.firstChild);
        }

        button.addEventListener('click', () => this.togglePanel());
        this.extensionsButton = button;
        this.updateExtensionCount();
    }

    /**
     * Toggle the extensions panel visibility
     */
    togglePanel() {
        this.isPanelVisible = !this.isPanelVisible;
        this.panel.classList.toggle('visible', this.isPanelVisible);

        if (this.isPanelVisible) {
            this.updateExtensionsList();
        }
    }

    /**
     * Update the extensions list in the panel
     */
    updateExtensionsList() {
        const extensionsList = document.getElementById('extensionsList');
        if (!extensionsList) return;

        const extensions = this.extensionManager.getAllExtensions();
        const activeExtensions = new Set(this.extensionManager.activeExtensions);

        extensionsList.innerHTML = extensions.map(ext => `
            <div class="extension-item ${activeExtensions.has(ext.id) ? 'active' : ''}"
                 data-extension-id="${ext.id}">
                <div class="extension-icon">
                    ${this.getExtensionIcon(ext.type)}
                </div>
                <div class="extension-info">
                    <div class="extension-name">${ext.name}</div>
                    <div class="extension-description">${ext.description}</div>
                    <div class="extension-capabilities">
                        ${ext.capabilities.map(cap => `<span class="capability-tag">${cap.replace('_', ' ')}</span>`).join('')}
                    </div>
                </div>
                <div class="extension-status">
                    <label class="extension-toggle">
                        <input type="checkbox"
                               ${activeExtensions.has(ext.id) ? 'checked' : ''}
                               data-extension-id="${ext.id}">
                        <span class="toggle-slider"></span>
                    </label>
                </div>
            </div>
        `).join('');

        // Add click handlers
        extensionsList.querySelectorAll('.extension-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.closest('.extension-toggle')) {
                    this.showExtensionDetails(item.dataset.extensionId);
                }
            });
        });

        extensionsList.querySelectorAll('.extension-toggle input').forEach(input => {
            input.addEventListener('change', (e) => {
                const extensionId = e.target.dataset.extensionId;
                if (e.target.checked) {
                    this.extensionManager.enableExtension(extensionId);
                } else {
                    this.extensionManager.disableExtension(extensionId);
                }
                this.updateExtensionCount();
                this.updateExtensionsList();
            });
        });
    }

    /**
     * Show extension details
     */
    showExtensionDetails(extensionId) {
        const extension = this.extensionManager.extensions.get(extensionId);
        if (!extension) return;

        this.currentExtension = extension;

        document.getElementById('extensionTitle').textContent = extension.name;
        document.getElementById('extensionDescription').textContent = extension.description;
        document.getElementById('extensionVersion').textContent = `v${extension.version}`;
        document.getElementById('extensionAuthor').textContent = `by ${extension.author}`;

        this.updateExtensionConfig(extensionId);
        this.updateExtensionActions(extensionId);

        document.getElementById('extensionsList').style.display = 'none';
        document.getElementById('extensionDetails').style.display = 'block';
    }

    /**
     * Update extension configuration UI
     */
    updateExtensionConfig(extensionId) {
        const configContainer = document.getElementById('extensionConfig');
        const config = this.extensionManager.getExtensionConfig(extensionId);

        if (!config || Object.keys(config).length === 0) {
            configContainer.innerHTML = '<p>No configuration options available.</p>';
            return;
        }

        configContainer.innerHTML = Object.entries(config).map(([key, value]) => `
            <div class="config-item">
                <label for="config-${key}">${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</label>
                ${this.createConfigInput(key, value)}
            </div>
        `).join('');

        // Add change handlers
        configContainer.querySelectorAll('input, select').forEach(input => {
            input.addEventListener('change', () => {
                const configKey = input.id.replace('config-', '');
                let value = input.value;

                if (input.type === 'checkbox') {
                    value = input.checked;
                } else if (input.type === 'number') {
                    value = parseFloat(value);
                }

                const newConfig = { [configKey]: value };
                this.extensionManager.updateExtensionConfig(extensionId, newConfig);
            });
        });
    }

    /**
     * Create configuration input element
     */
    createConfigInput(key, value) {
        const inputId = `config-${key}`;

        if (typeof value === 'boolean') {
            return `<input type="checkbox" id="${inputId}" ${value ? 'checked' : ''}>`;
        } else if (typeof value === 'number') {
            return `<input type="number" id="${inputId}" value="${value}">`;
        } else if (Array.isArray(value)) {
            return `<input type="text" id="${inputId}" value="${value.join(', ')}" placeholder="Comma-separated values">`;
        } else if (key.includes('engine') || key.includes('style') || key.includes('type')) {
            const options = this.getSelectOptions(key);
            return `
                <select id="${inputId}">
                    ${options.map(option => `<option value="${option}" ${option === value ? 'selected' : ''}>${option}</option>`).join('')}
                </select>
            `;
        } else {
            return `<input type="text" id="${inputId}" value="${value}">`;
        }
    }

    /**
     * Get select options for configuration
     */
    getSelectOptions(key) {
        if (key === 'search_engine') {
            return ['duckduckgo', 'google', 'bing'];
        } else if (key === 'style') {
            return ['realistic', 'artistic', 'minimalist', 'cartoon'];
        } else if (key === 'supported_languages') {
            return ['python', 'javascript', 'bash', 'r', 'sql'];
        }
        return [];
    }

    /**
     * Update extension actions
     */
    updateExtensionActions(extensionId) {
        const isActive = this.extensionManager.activeExtensions.has(extensionId);
        const toggleBtn = document.getElementById('btnToggleExtension');

        toggleBtn.textContent = isActive ? 'Disable' : 'Enable';
        toggleBtn.className = `btn-extension-toggle ${isActive ? 'active' : ''}`;
    }

    /**
     * Get extension icon based on type
     */
    getExtensionIcon(type) {
        const icons = {
            tool: '🔧',
            pipeline: '⚡',
            ui: '🎨',
            integration: '🔗'
        };
        return icons[type] || '📦';
    }

    /**
     * Update extension count badge
     */
    updateExtensionCount() {
        const count = this.extensionManager.activeExtensions.size;
        const countElement = document.getElementById('extensionCount');
        if (countElement) {
            countElement.textContent = count;
            countElement.style.display = count > 0 ? 'inline' : 'none';
        }
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Close panel button
        document.getElementById('btnCloseExtensions')?.addEventListener('click', () => {
            this.togglePanel();
        });

        // Close panel when clicking outside
        document.addEventListener('click', (e) => {
            if (this.isPanelVisible &&
                !this.panel.contains(e.target) &&
                !this.extensionsButton.contains(e.target)) {
                this.togglePanel();
            }
        });

        // Extension manager events
        this.extensionManager.on('extensionEnabled', () => {
            this.updateExtensionCount();
            this.updateExtensionsList();
        });

        this.extensionManager.on('extensionDisabled', () => {
            this.updateExtensionCount();
            this.updateExtensionsList();
        });

        this.extensionManager.on('extensionConfigUpdated', () => {
            if (this.currentExtension) {
                this.updateExtensionConfig(this.currentExtension.id);
            }
        });

        // Extension toggle button in details
        document.getElementById('btnToggleExtension')?.addEventListener('click', () => {
            if (!this.currentExtension) return;

            const extensionId = this.currentExtension.id;
            const isActive = this.extensionManager.activeExtensions.has(extensionId);

            if (isActive) {
                this.extensionManager.disableExtension(extensionId);
            } else {
                this.extensionManager.enableExtension(extensionId);
            }

            this.updateExtensionActions(extensionId);
        });

        // Test extension button
        document.getElementById('btnTestExtension')?.addEventListener('click', async () => {
            if (!this.currentExtension) return;

            const extensionId = this.currentExtension.id;
            try {
                const result = await this.testExtension(extensionId);
                this.showTestResult(result);
            } catch (error) {
                this.showTestResult({ success: false, error: error.message });
            }
        });

        // Keyboard shortcut (Ctrl+E)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'e') {
                e.preventDefault();
                this.togglePanel();
            }
        });
    }

    /**
     * Test an extension
     */
    async testExtension(extensionId) {
        const extension = this.extensionManager.extensions.get(extensionId);
        if (!extension) {
            throw new Error('Extension not found');
        }

        // Test with sample parameters based on extension type
        const testParams = this.getTestParams(extensionId);
        return await this.extensionManager.executeExtension(extensionId, testParams);
    }

    /**
     * Get test parameters for extension
     */
    getTestParams(extensionId) {
        const testParams = {
            web_search: { query: 'test search query' },
            code_execution: { code: 'print("Hello, World!")', language: 'python' },
            calculator: { expression: '2 + 2 * 3' },
            file_analysis: { file: null, analysis_type: 'summary' }, // Would need actual file
            image_generation: { prompt: 'a simple test image of a smiley face' }
        };

        return testParams[extensionId] || {};
    }

    /**
     * Show test result
     */
    showTestResult(result) {
        const testBtn = document.getElementById('btnTestExtension');

        if (result.success) {
            testBtn.textContent = '✓ Test Passed';
            testBtn.className = 'btn-extension-test success';
        } else {
            testBtn.textContent = '✗ Test Failed';
            testBtn.className = 'btn-extension-test error';
        }

        // Reset button after 3 seconds
        setTimeout(() => {
            testBtn.textContent = 'Test';
            testBtn.className = 'btn-extension-test';
        }, 3000);
    }

    /**
     * Load extension settings
     */
    loadExtensionSettings() {
        this.extensionManager.loadSettings();
        this.updateExtensionCount();
    }

    /**
     * Save extension settings
     */
    saveExtensionSettings() {
        this.extensionManager.saveSettings();
    }

    /**
     * Show extensions list (back from details)
     */
    showExtensionsList() {
        document.getElementById('extensionDetails').style.display = 'none';
        document.getElementById('extensionsList').style.display = 'block';
        this.currentExtension = null;
    }

    /**
     * Add back button to extension details
     */
    addBackButton() {
        const details = document.getElementById('extensionDetails');
        if (details && !details.querySelector('.btn-back')) {
            const backBtn = document.createElement('button');
            backBtn.className = 'btn-back';
            backBtn.innerHTML = '← Back to Extensions';
            backBtn.addEventListener('click', () => this.showExtensionsList());

            details.insertBefore(backBtn, details.firstChild);
        }
    }
}

// Initialize extensions UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (window.ExtensionManager) {
        window.extensionsUI = new ExtensionsUI(window.ExtensionManager);
    }
});

// Export for global access
window.ExtensionsUI = ExtensionsUI;
