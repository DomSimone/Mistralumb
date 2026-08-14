# Umbuzo Frontend

A modern web interface for the Umbuzo AI assistant, featuring document-augmented responses and specialized tools.

## Features

### 🤖 AI Chat Interface
- **Conversational AI**: Interactive chat with the trained Mistral model
- **RAG-Enhanced**: Responses augmented with relevant document knowledge
- **Multi-Mode Support**: Factual, reasoning, creative, and auto modes
- **Country-Aware**: Specialized responses for African countries

### 📚 Knowledge Retrieval
- **Document Integration**: Access to MIT course materials and academic content
- **Formula Support**: Mathematical and statistical formulas from documents
- **Research Methods**: Information on experimental design and analysis
- **Real-time Retrieval**: Context pulled from 400+ academic documents

### 🛠️ Specialized Tools
- **Math Calculator**: Symbolic mathematics with step-by-step solutions
- **Data Analyzer**: Statistical analysis and regression tools
- **Visualization**: Chart generation from data
- **Report Generator**: AI-powered report creation
- **Country Insights**: Detailed information about African nations

### 🔧 Technical Features
- **Efficient Communication**: Optimized Axios configuration
- **Environment Awareness**: Automatic configuration for dev/prod
- **Error Resilience**: Comprehensive error handling and user feedback
- **Chat History**: Persistent conversation storage
- **Responsive Design**: Mobile-friendly interface

## Architecture

```
Frontend (Port 8080 / ngrok)
├── Static Files Server
├── HTML/CSS/JavaScript
├── Axios API Client
└── Local Storage

Backend (Port 8000)
├── FastAPI Server
├── RAG System
├── Document Corpus
├── Model Inference
└── Multiple Endpoints
```

## API Integration

The frontend communicates with the backend through multiple endpoints:

- `POST /chat` - Main conversational AI
- `POST /math` - Mathematical calculations
- `POST /visualize` - Data visualization
- `POST /images` - Image generation
- `POST /data-analysis/stats` - Statistical analysis
- `GET /v1/models` - OpenAI-compatible model listing

## Document Knowledge Base

The system includes a comprehensive document corpus:

- **Mathematics**: Differential equations, linear algebra, calculus
- **Statistics**: Probability, inference, regression analysis
- **Research Methods**: Experimental design, causal inference
- **Physics**: Mechanics, electromagnetism, wave equations
- **Economics**: Development economics, policy analysis
- **Engineering**: Matrix applications, system analysis

## Getting Started

1. **Start Backend**:
   ```bash
   python api.py
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   python start_frontend.py
   ```

3. **Access Application**:
   - Frontend: https://dingy-choking-dutiful.ngrok-free.dev
   - Backend API: http://localhost:8000

## Configuration

The frontend uses a centralized configuration system (`config.js`) for:
- API endpoints and timeouts
- Feature flags
- Environment detection
- UI settings

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

### Adding New Features
1. Update `config.js` for new settings
2. Add functionality to appropriate JavaScript files
3. Test with backend API endpoints
4. Update documentation

### API Testing
Use the provided test scripts:
- `test_all_capabilities.py` - Full system test
- `test_rag_knowledge.py` - Knowledge retrieval verification

## Troubleshooting

### Common Issues
- **Backend Connection Failed**: Ensure API server is running on port 8000
- **Slow Responses**: Model loading may take time on first request
- **Missing Features**: Check browser console for JavaScript errors

### Debug Mode
Enable debug logging in browser console:
```javascript
window.UmbuzoConfig.ENABLE_DEBUG_LOGGING = true;
