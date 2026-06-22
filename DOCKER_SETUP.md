# Umbuzo Docker Setup

This guide explains how to run the Umbuzo chatbot application using Docker containers.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User's Browser                           │
│                    https://dingy-choking-dutiful.ngrok-free.dev   │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│         Frontend (Nginx)             │
│         Port 8080                    │
│                                      │
│  Serves: index.html, app.js,         │
│  styles.css, etc.                    │
│                                      │
│  Proxies /api/*, /chat, /health,     │
│  /math, /visualize, /images, etc.    │
│  → https://dingy-choking-dutiful.ngrok-free.dev              │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│         Backend (FastAPI)            │
│         Port 8000                    │
│                                      │
│  - Chat API                          │
│  - Math engine                       │
│  - Data visualization                │
│  - Image generation                  │
│  - Data analysis                     │
│  - Health checks                     │
└──────────────────────────────────────┘
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0+)
- At least 4GB RAM allocated to Docker

## Quick Start

### Build and Run

```bash
# Build and start all services in the background
docker compose up -d

# Or rebuild images without cache (if dependencies changed)
docker compose build --no-cache
docker compose up -d
```

### Access the Application

| Service    | URL                       |
|------------|---------------------------|
| Frontend   | https://dingy-choking-dutiful.ngrok-free.dev |
| Backend API| https://dingy-choking-dutiful.ngrok-free.dev     |
| API Docs   | https://dingy-choking-dutiful.ngrok-free.dev/docs|
| Health     | https://dingy-choking-dutiful.ngrok-free.dev/health |

### View Logs

```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f backend

# Frontend only
docker compose logs -f frontend
```

### Stop Services

```bash
# Stop but keep containers
docker compose stop

# Stop and remove containers
docker compose down
```

## Configuration

### Environment Variables

The following environment variables can be set in `docker-compose.yml`:

| Variable       | Default                    | Description                     |
|----------------|----------------------------|---------------------------------|
| `ENVIRONMENT`  | `production`               | App environment mode            |
| `API_BASE_URL` | `https://dingy-choking-dutiful.ngrok-free.dev`      | Backend URL (frontend→backend)  |
| `FRONTEND_URL` | `https://dingy-choking-dutiful.ngrok-free.dev` | Frontend URL (for CORS) |

### Persistent Data

Conversation history and application data are stored in a Docker volume:

- **Volume name:** `umbuzo_umbuzo_data`
- **Mounted at:** `/app/data` (inside the backend container)
- **Conversation file:** `./umbuzo_conversation.json` is mounted directly

To inspect the volume:
```bash
docker volume inspect umbuzo_umbuzo_data
```

## Advanced Commands

### Rebuild a Single Service

```bash
docker compose build backend
# or
docker compose build frontend
```

### Scale Backend (if needed)

```bash
docker compose up -d --scale backend=2
```

### Run Backend Shell

```bash
docker compose exec backend bash
```

### Run Frontend Shell

```bash
docker compose exec frontend sh
```

### Check Container Health

```bash
docker compose ps
docker compose exec backend python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read())"
```

## Troubleshooting

### Backend fails to start

1. Check logs:
   ```bash
   docker compose logs backend
   ```

2. Ensure the `umbuzo_conversation.json` file exists in the project root:
   ```bash
   ls -la umbuzo_conversation.json
   ```
   If missing, create an empty one:
   ```bash
   echo '[]' > umbuzo_conversation.json
   ```

3. Verify all Python source files are present:
   ```bash
   ls -la *.py
   ```

### Frontend shows blank page

1. Check nginx logs:
   ```bash
   docker compose logs frontend
   ```

2. Verify the API base URL in the browser's developer console (F12 → Console)

3. Ensure the backend is healthy:
   ```bash
   curl https://dingy-choking-dutiful.ngrok-free.dev/health
   ```

### Port conflicts

If ports 8000 or 8080 are already in use, modify the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Backend
  - "8081:80"    # Frontend
```

Then update the `FRONTEND_URL` environment variable accordingly.

## File Structure

```
├── Dockerfile.backend        # Backend container definition
├── docker-compose.yml        # Orchestration configuration
├── .dockerignore             # Files excluded from Docker build
├── DOCKER_SETUP.md           # This file
├── fastapi_server.py         # FastAPI application
├── umbuzo_chatbot.py         # Chatbot core logic
├── rag_system.py             # RAG system
├── ... (other Python files)
├── frontend/
│   ├── Dockerfile.frontend   # Frontend container definition
│   ├── nginx.conf            # Nginx configuration
│   ├── index.html            # Main HTML page
│   ├── app.js                # Chat interface logic
│   ├── config.js             # Frontend configuration
│   ├── styles.css            # Styles
│   └── ... (other static files)
└── requirements.txt          # Python dependencies
```

## Production Deployment

For production deployment, consider:

1. **Use a reverse proxy** (e.g., Traefik, Caddy) in front for SSL/TLS
2. **Set up proper logging** - mount log directories as volumes
3. **Resource limits** - add memory limits to `docker-compose.yml`:
   ```yaml
   backend:
     deploy:
       resources:
         limits:
           memory: 4G
   ```
4. **Docker secrets** for sensitive configuration
5. **Multi-stage build** to reduce image size (see `Dockerfile.backend.prod` for the optimized version)
