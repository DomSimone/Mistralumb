/**
 * Apps page JavaScript
 * Handles app directory and tool integrations
 */

const API_BASE_URL = window.UmbuzoConfig?.API_BASE_URL || 'http://localhost:8000';

// Axios configuration for efficient communication
axios.defaults.baseURL = API_BASE_URL;
axios.defaults.timeout = window.UmbuzoConfig?.API_TIMEOUT || 30000; // Use config timeout
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Add response interceptor for error handling
axios.interceptors.response.use(
    response => response,
    error => {
        if (window.UmbuzoConfig?.ENABLE_DEBUG_LOGGING) {
            if (error.code === 'ECONNREFUSED') {
                console.error(`Cannot connect to backend server. Make sure it's running on ${API_BASE_URL}`);
                alert('Backend server is not running. Please start the server first.');
            } else if (error.response) {
                console.error(`API Error ${error.response.status}:`, error.response.data);
            } else {
                console.error('Network Error:', error.message);
            }
        }
        return Promise.reject(error);
    }
);

// App configurations
const apps = {
    report: {
        title: 'Report Generator',
        description: 'Generate comprehensive reports with data visualization',
        endpoint: '/chat',
        modal: 'report'
    },
    image: {
        title: 'Image Generator',
        description: 'Create AI-powered images from text descriptions',
        endpoint: '/images',
        modal: 'image'
    },
    analyzer: {
        title: 'Data Analyzer',
        description: 'Statistical analysis, correlation, and regression',
        endpoint: '/data-analysis/stats',
        modal: 'analyzer'
    },
    math: {
        title: 'Math Calculator',
        description: 'Complex calculus, solving equations, and symbolic math',
        endpoint: '/math',
        modal: 'math'
    },
    visualize: {
        title: 'Data Visualization',
        description: 'Create charts and graphs from your data',
        endpoint: '/visualize',
        modal: 'visualize'
    },
    country: {
        title: 'Country Insights',
        description: 'Get detailed information about African countries',
        endpoint: '/chat',
        modal: 'country'
    }
};

// Open app modal
function openApp(appId) {
    const app = apps[appId];
    if (!app) return;

    const modal = document.getElementById('appModal');
    const modalBody = document.getElementById('appModalBody');

    if (!modal || !modalBody) return;

    // Load app-specific content
    modalBody.innerHTML = getAppContent(appId);
    modal.style.display = 'flex';

    // Initialize app-specific functionality
    initializeApp(appId);
}

// Close app modal
function closeApp() {
    const modal = document.getElementById('appModal');
    if (modal) modal.style.display = 'none';
}

// Get app content HTML
function getAppContent(appId) {
    const templates = {
        report: `
            <h2>Report Generator</h2>
            <p>Generate comprehensive reports on African topics</p>
            <div class="app-form">
                <textarea id="reportTopic" placeholder="Enter topic for report..." rows="5" style="width: 100%; padding: 12px; background: #1A1A1A; border: 1px solid #333; border-radius: 8px; color: #FFF; font-family: inherit; margin-bottom: 16px;"></textarea>
                <button class="btn-primary" onclick="generateReport()">Generate Report</button>
            </div>
            <div id="reportResult" style="margin-top: 20px;"></div>
        `,
        image: `
            <h2>Image Generator</h2>
            <p>Create AI-powered images from descriptions</p>
            <div class="app-form">
                <input type="text" id="imagePrompt" placeholder="Describe the image you want to create..." style="width: 100%; padding: 12px; background: #1A1A1A; border: 1px solid #333; border-radius: 8px; color: #FFF; font-family: inherit; margin-bottom: 16px;">
                <div style="display: flex; gap: 12px; margin-bottom: 16px;">
                    <input type="number" id="imageWidth" value="512" min="256" max="1024" style="flex: 1; padding: 12px; background: #1A1A1A; border: 1px solid #333; border-radius: 8px; color: #FFF;">
                    <input type="number" id="imageHeight" value="512" min="256" max="1024" style="flex: 1; padding: 12px; background: #1A1A1A; border: 1px solid #333; border-radius: 8px; color: #FFF;">
                </div>
                <button class="btn-primary" onclick="generateImage()">Generate Image</button>
            </div>
            <div id="imageResult" style="margin-top: 20px; text-align: center;"></div>
        `,
        analyzer: `
            <h2>Data Analyzer</h2>
            <p>Statistical analysis and correlation</p>
            <div class="app-form">
                <label style="display: block; margin-bottom: 8px;">X values (comma-separated):</label>
                <input type="text" id="analyzerX" placeholder="1, 2, 3, 4, 5" style="width: 100%; padding: 12px; background: #1A1A1A; border: 1px solid #333; border-radius: 8px; color: #FFF; font-family: inherit; margin-bottom: 16px;">
                <label style="display: block; margin-bottom: 8px;">Y values (comma-separated):</label>
                <input type="text" id="analyzerY" placeholder="2, 4, 6, 8, 10" style="width: 100%; padding: 12px; background: #1A1A1A; border: 1px solid #333; border-radius: 8px; color: #FFF; font-family: inherit; margin-bottom: 16px;">
                <button class="btn-primary" onclick="analyzeData()">Analyze</button>
            </div>
            <div id="analyzerResult" style="margin-top: 20px; font-family: monospace; background: #1A1A1A; padding: 16px; border-radius: 8px;"></div>
        `,
        math: `
            <h2>Math Calculator</h2>
            <p>Complex calculus and symbolic math</p>
            <div class="app-form">
                <input type="text" id="mathExpression" placeholder="e.g., sin(x)^2 + cos(x)^2" style="width: 100%; padding: 12px; background: #1A1A1A; border: 1px solid #333; border-radius: 8px; color: #FFF; font-family: inherit; margin-bottom: 12px;">
                <select id="mathOperation" style="width: 100%; padding: 12px; background: #1A1A1A; border: 1px solid #333; border-radius: 8px; color: #FFF; font-family: inherit; margin-bottom: 12px;">
                    <option value="simplify">Simplify</option>
                    <option value="differentiate">Differentiate</option>
                    <option value="integrate">Integrate</option>
                    <option value="solve">Solve</option>
                    <option value="evaluate">Evaluate</option>
                </select>
                <input type="text" id="mathVariable" value="x" placeholder="Variable" style="width: 100%; padding: 12px; background: #1A1A1A; border: 1px solid #333; border-radius: 8px; color: #FFF; font-family: inherit; margin-bottom: 16px;">
                <button class="btn-primary" onclick="calculateMath()">Calculate</button>
            </div>
            <div id="mathResult" style="margin-top: 20px; font-family: monospace; background: #1A1A1A; padding: 16px; border-radius: 8px;"></div>
        `,
        visualize: `
            <h2>Data Visualization</h2>
            <p>Create charts from your data</p>
            <div class="app-form">
                <input type="text" id="chartTitle" placeholder="Chart Title" style="width: 100%; padding: 12px; background: #1A1A1A; border: 1px solid #333; border-radius: 8px; color: #FFF; font-family: inherit; margin-bottom: 12px;">
                <select id="chartType" style="width: 100%; padding: 12px; background: #1A1A1A; border: 1px solid #333; border-radius: 8px; color: #FFF; font-family: inherit; margin-bottom: 12px;">
                    <option value="line">Line Chart</option>
                    <option value="bar">Bar Chart</option>
                    <option value="scatter">Scatter Plot</option>
                    <option value="pie">Pie Chart</option>
                    <option value="histogram">Histogram</option>
                </select>
                <textarea id="chartData" placeholder='JSON format: [{"name": "Series 1", "x": [1,2,3], "y": [10,20,30]}]' rows="5" style="width: 100%; padding: 12px; background: #1A1A1A; border: 1px solid #333; border-radius: 8px; color: #FFF; font-family: monospace; margin-bottom: 16px;"></textarea>
                <button class="btn-primary" onclick="createChart()">Create Chart</button>
            </div>
            <div id="chartResult" style="margin-top: 20px; text-align: center;"></div>
        `,
        country: `
            <h2>Country Insights</h2>
            <p>Get detailed information about African countries</p>
            <div class="app-form">
                <input type="text" id="countryName" placeholder="Enter country name (e.g., Nigeria, South Africa)" style="width: 100%; padding: 12px; background: #1A1A1A; border: 1px solid #333; border-radius: 8px; color: #FFF; font-family: inherit; margin-bottom: 16px;">
                <button class="btn-primary" onclick="getCountryInfo()">Get Insights</button>
            </div>
            <div id="countryResult" style="margin-top: 20px;"></div>
        `
    };

    return templates[appId] || '<p>App content not available</p>';
}

// Initialize app-specific functionality
function initializeApp(appId) {
    // App-specific initialization if needed
}

// App functions
async function generateReport() {
    const topic = document.getElementById('reportTopic').value;
    if (!topic) return alert('Please enter a topic');

    const resultDiv = document.getElementById('reportResult');
    resultDiv.innerHTML = '<p>Generating report...</p>';

    try {
        const response = await axios.post(`${API_BASE_URL}/chat`, {
            conversation: [{ role: 'user', content: `Generate a comprehensive report about: ${topic}` }],
            mode: 'factual',
            max_tokens: 1000
        });

        resultDiv.innerHTML = `<div style="background: #1A1A1A; padding: 20px; border-radius: 8px; white-space: pre-wrap;">${escapeHtml(response.data.reply || response.data.message)}</div>`;
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: #ff4444;">Error: ${error.message}</p>`;
    }
}

async function generateImage() {
    const prompt = document.getElementById('imagePrompt').value;
    const width = parseInt(document.getElementById('imageWidth').value) || 512;
    const height = parseInt(document.getElementById('imageHeight').value) || 512;

    if (!prompt) return alert('Please enter an image description');

    const resultDiv = document.getElementById('imageResult');
    resultDiv.innerHTML = '<p>Generating image...</p>';

    try {
        const response = await axios.post(`${API_BASE_URL}/images`, {
            prompt,
            width,
            height
        });

        const img = document.createElement('img');
        img.src = `data:image/png;base64,${response.data.image_base64}`;
        img.style.maxWidth = '100%';
        img.style.borderRadius = '8px';
        resultDiv.innerHTML = '';
        resultDiv.appendChild(img);
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: #ff4444;">Error: ${error.message}</p>`;
    }
}

async function analyzeData() {
    const xStr = document.getElementById('analyzerX').value;
    const yStr = document.getElementById('analyzerY').value;

    if (!xStr || !yStr) return alert('Please enter both X and Y values');

    const x = xStr.split(',').map(v => parseFloat(v.trim())).filter(v => !isNaN(v));
    const y = yStr.split(',').map(v => parseFloat(v.trim())).filter(v => !isNaN(v));

    if (x.length !== y.length || x.length < 2) {
        return alert('X and Y must have the same length (minimum 2 values)');
    }

    const resultDiv = document.getElementById('analyzerResult');
    resultDiv.innerHTML = '<p>Analyzing...</p>';

    try {
        const response = await axios.post(`${API_BASE_URL}/data-analysis/stats`, {
            x,
            y
        });

        const stats = response.data;
        resultDiv.innerHTML = `
            <h3>Statistical Analysis</h3>
            <p><strong>Sample Size:</strong> ${stats.n}</p>
            <p><strong>Mean X:</strong> ${stats.mean_x.toFixed(4)}</p>
            <p><strong>Mean Y:</strong> ${stats.mean_y.toFixed(4)}</p>
            <p><strong>Std Dev X:</strong> ${stats.std_x.toFixed(4)}</p>
            <p><strong>Std Dev Y:</strong> ${stats.std_y.toFixed(4)}</p>
            <p><strong>Correlation:</strong> ${stats.correlation.toFixed(4)}</p>
            <p><strong>Linear Regression:</strong></p>
            <p style="margin-left: 20px;">Slope: ${stats.regression.slope.toFixed(4)}</p>
            <p style="margin-left: 20px;">Intercept: ${stats.regression.intercept.toFixed(4)}</p>
            <p style="margin-left: 20px;">R²: ${stats.regression.r2.toFixed(4)}</p>
        `;
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: #ff4444;">Error: ${error.message}</p>`;
    }
}

async function calculateMath() {
    const expression = document.getElementById('mathExpression').value;
    const operation = document.getElementById('mathOperation').value;
    const variable = document.getElementById('mathVariable').value;

    if (!expression) return alert('Please enter a mathematical expression');

    const resultDiv = document.getElementById('mathResult');
    resultDiv.innerHTML = '<p>Calculating...</p>';

    try {
        const response = await axios.post(`${API_BASE_URL}/math`, {
            expression,
            operation,
            variable
        });

        resultDiv.innerHTML = `
            <h3>Result</h3>
            <p><strong>Original:</strong> ${escapeHtml(response.data.original)}</p>
            <p><strong>Result:</strong> ${escapeHtml(response.data.result)}</p>
            ${response.data.steps ? `<p><strong>Steps:</strong><br>${escapeHtml(response.data.steps)}</p>` : ''}
        `;
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: #ff4444;">Error: ${error.message}</p>`;
    }
}

async function createChart() {
    const title = document.getElementById('chartTitle').value || 'Chart';
    const type = document.getElementById('chartType').value;
    const dataStr = document.getElementById('chartData').value;

    if (!dataStr) return alert('Please enter chart data');

    let series;
    try {
        series = JSON.parse(dataStr);
        if (!Array.isArray(series)) series = [series];
    } catch (e) {
        return alert('Invalid JSON format');
    }

    const resultDiv = document.getElementById('chartResult');
    resultDiv.innerHTML = '<p>Creating chart...</p>';

    try {
        const response = await axios.post(`${API_BASE_URL}/visualize`, {
            title,
            kind: type,
            series,
            x_label: 'X',
            y_label: 'Y'
        });

        const img = document.createElement('img');
        img.src = `data:image/png;base64,${response.data.image_base64}`;
        img.style.maxWidth = '100%';
        img.style.borderRadius = '8px';
        resultDiv.innerHTML = '';
        resultDiv.appendChild(img);
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: #ff4444;">Error: ${error.message}</p>`;
    }
}

async function getCountryInfo() {
    const country = document.getElementById('countryName').value;
    if (!country) return alert('Please enter a country name');

    const resultDiv = document.getElementById('countryResult');
    resultDiv.innerHTML = '<p>Fetching country information...</p>';

    try {
        const response = await axios.post(`${API_BASE_URL}/chat`, {
            conversation: [{ role: 'user', content: `Tell me about ${country}` }],
            country: country,
            mode: 'factual',
            max_tokens: 500
        });

        resultDiv.innerHTML = `<div style="background: #1A1A1A; padding: 20px; border-radius: 8px; white-space: pre-wrap;">${escapeHtml(response.data.reply || response.data.message)}</div>`;
    } catch (error) {
        resultDiv.innerHTML = `<p style="color: #ff4444;">Error: ${error.message}</p>`;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal on outside click
document.addEventListener('click', (e) => {
    const modal = document.getElementById('appModal');
    if (e.target === modal) {
        closeApp();
    }
});
