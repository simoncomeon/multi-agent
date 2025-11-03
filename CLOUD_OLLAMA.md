# Cloud Ollama Support

The multi-agent system now supports both local and remote/cloud Ollama instances!

## Quick Setup

### Option 1: Local Ollama (Default)
No configuration needed - works as before if you have Ollama installed locally.

### Option 2: Remote Ollama Server
Set these environment variables:
```bash
export OLLAMA_USE_REMOTE=true
export OLLAMA_REMOTE_HOST=your-server.com
export OLLAMA_REMOTE_PORT=11434
```

### Option 3: Cloud Ollama Service
```bash
export OLLAMA_USE_REMOTE=true
export OLLAMA_REMOTE_HOST=api.cloud-provider.com
export OLLAMA_REMOTE_PORT=443
export OLLAMA_API_KEY=your-api-key
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_USE_REMOTE` | `false` | Use remote API instead of local CLI |
| `OLLAMA_REMOTE_HOST` | `localhost` | Remote Ollama host |
| `OLLAMA_REMOTE_PORT` | `11434` | Remote Ollama port |
| `OLLAMA_API_KEY` | (empty) | API key for cloud services |
| `OLLAMA_MODEL` | `llama3.2` | Default model to use |
| `OLLAMA_CMD` | `ollama` | Local Ollama command |

## Usage Examples

### Using Environment Variables
```bash
# For remote server
OLLAMA_USE_REMOTE=true OLLAMA_REMOTE_HOST=my-server.com python3 smart_launcher.py

# For cloud service  
OLLAMA_USE_REMOTE=true OLLAMA_REMOTE_HOST=api.provider.com OLLAMA_API_KEY=key123 python3 smart_launcher.py
```

### Using .env File
Create a `.env` file in the multi-agent directory:
```bash
# Copy from ollama_config.example and modify
cp ollama_config.example .env
# Edit .env with your settings
```

## Features

✅ **Automatic Fallback**: If remote fails, gracefully handles errors  
✅ **API Compatibility**: Works with standard Ollama API endpoints  
✅ **Authentication Support**: Supports API keys for cloud providers  
✅ **Same Interface**: No changes needed in agent code  
✅ **Health Checks**: Automatically verifies Ollama availability  

## Cloud Provider Examples

### Self-Hosted Ollama Server
```bash
export OLLAMA_USE_REMOTE=true
export OLLAMA_REMOTE_HOST=192.168.1.100
export OLLAMA_REMOTE_PORT=11434
```

### Docker Ollama Container
```bash
# Start Ollama in Docker first:
# docker run -d -p 11434:11434 ollama/ollama

export OLLAMA_USE_REMOTE=true  
export OLLAMA_REMOTE_HOST=localhost
export OLLAMA_REMOTE_PORT=11434
```

### Cloud Services
For cloud providers that offer Ollama-compatible APIs:
```bash
export OLLAMA_USE_REMOTE=true
export OLLAMA_REMOTE_HOST=your-cloud-provider.com
export OLLAMA_REMOTE_PORT=443
export OLLAMA_API_KEY=your-api-key
```

## Troubleshooting

### Connection Issues
```bash
# Test if your remote Ollama is accessible
curl http://your-host:11434/api/tags

# Check if the client detects the remote server
python3 -c "from src.core.ollama_client import ollama_client; print(ollama_client.is_available())"
```

### Model Issues
```bash
# List available models on remote server
curl http://your-host:11434/api/tags

# Update your model name if different
export OLLAMA_MODEL=your-model-name
```

## Benefits of Cloud Ollama

1. **No Local Installation**: Run agents without installing Ollama locally
2. **Better Performance**: Use powerful cloud GPUs
3. **Shared Models**: Multiple users can share the same Ollama instance
4. **Always Available**: Cloud services provide better uptime
5. **Scalability**: Handle multiple concurrent requests

The system will automatically use the configured Ollama method (local or remote) transparently across all agents!