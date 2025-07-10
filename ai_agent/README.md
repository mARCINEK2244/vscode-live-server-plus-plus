# AI Agent System

A comprehensive AI agent system with conversation capabilities, tool usage, and extensible architecture.

## Features

- 🤖 **Conversational AI**: Natural language interaction with context awareness
- 🛠️ **Tool Integration**: Extensible tool system for various tasks
- 💾 **Memory Management**: Persistent conversation history and context
- 🌐 **Web Interface**: Clean, modern web UI for interactions
- 📊 **Analytics**: Performance tracking and usage analytics
- 🔌 **Plugin System**: Easy to extend with custom tools and capabilities

## Quick Start

1. **Install Dependencies**:
   ```bash
   cd ai_agent
   pip install -r requirements.txt
   npm install
   ```

2. **Configure API Keys**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the Agent**:
   ```bash
   # Web interface
   python app.py
   
   # CLI interface
   python cli_agent.py
   ```

## Architecture

- `agent/` - Core AI agent logic
- `tools/` - Available tools and functions
- `memory/` - Context and conversation management
- `web/` - Web interface components
- `config/` - Configuration and settings

## Extending the Agent

Add new tools by creating a file in `tools/` directory:

```python
from tools.base import BaseTool

class MyCustomTool(BaseTool):
    name = "my_tool"
    description = "Description of what this tool does"
    
    def execute(self, params):
        # Tool implementation
        return result
```

## License

MIT License