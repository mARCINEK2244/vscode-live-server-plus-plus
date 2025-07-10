import asyncio
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import json
from datetime import datetime

from config.settings import settings
from agent.core import AIAgent

app = Flask(__name__)
app.secret_key = settings.SECRET_KEY
CORS(app)

# Initialize AI Agent
agent = AIAgent()

@app.route('/')
def index():
    """Main chat interface."""
    return render_template('index.html', agent_name=agent.agent_name)

@app.route('/api/chat', methods=['POST'])
async def chat():
    """Handle chat messages."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        model = data.get('model')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Process the message
        response = await agent.chat(message, conversation_id, model)
        
        return jsonify(response)
        
    except Exception as e:
        app.logger.error(f"Chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get list of conversations."""
    try:
        conversations = agent.conversation_manager.get_conversation_list()
        return jsonify({'conversations': conversations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get specific conversation history."""
    try:
        history = agent.get_conversation_history(conversation_id)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation."""
    try:
        success = agent.conversation_manager.delete_conversation(conversation_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>/clear', methods=['POST'])
def clear_conversation(conversation_id):
    """Clear conversation history."""
    try:
        agent.clear_conversation(conversation_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Get available tools."""
    try:
        tools = agent.get_available_tools()
        return jsonify({'tools': tools})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tools/<tool_name>/execute', methods=['POST'])
def execute_tool(tool_name):
    """Execute a specific tool."""
    try:
        data = request.get_json()
        parameters = data.get('parameters', {})
        
        result = agent.execute_tool(tool_name, **parameters)
        
        return jsonify({
            'success': result.success,
            'data': result.data,
            'error': result.error,
            'metadata': result.metadata
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get agent statistics."""
    try:
        agent_stats = agent.get_stats()
        memory_stats = agent.conversation_manager.get_stats()
        
        return jsonify({
            'agent': agent_stats,
            'memory': memory_stats,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_conversations():
    """Search conversations."""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = data.get('limit', 10)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        results = agent.conversation_manager.search_conversations(query, limit)
        return jsonify({'results': results})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'agent_name': agent.agent_name,
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def create_templates_directory():
    """Create templates directory and basic HTML template."""
    templates_dir = "templates"
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Create basic HTML template
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ agent_name }} - AI Agent</title>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; height: 100vh; display: flex; }
        .sidebar { width: 300px; background: white; border-right: 1px solid #e0e0e0; }
        .main { flex: 1; display: flex; flex-direction: column; background: white; }
        .header { padding: 20px; border-bottom: 1px solid #e0e0e0; background: #fff; }
        .header h1 { color: #333; font-size: 24px; }
        .chat-area { flex: 1; overflow-y: auto; padding: 20px; }
        .input-area { padding: 20px; border-top: 1px solid #e0e0e0; }
        .message { margin-bottom: 15px; padding: 10px 15px; border-radius: 10px; max-width: 70%; }
        .user-message { background: #007bff; color: white; margin-left: auto; }
        .assistant-message { background: #f8f9fa; color: #333; border: 1px solid #e0e0e0; }
        .input-container { display: flex; gap: 10px; }
        .input-container input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .input-container button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .input-container button:hover { background: #0056b3; }
        .input-container button:disabled { background: #6c757d; cursor: not-allowed; }
        .conversation-list { padding: 10px; }
        .conversation-item { padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; }
        .conversation-item:hover { background: #f8f9fa; }
        .conversation-item.active { background: #e3f2fd; }
        .new-chat-btn { width: 100%; padding: 10px; background: #28a745; color: white; border: none; border-radius: 5px; margin-bottom: 10px; cursor: pointer; }
        .new-chat-btn:hover { background: #218838; }
        .loading { text-align: center; color: #666; padding: 20px; }
        .error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .tool-calls { margin-top: 10px; padding: 10px; background: #e8f5e9; border-radius: 5px; border-left: 4px solid #4caf50; }
        .tool-call { margin-bottom: 5px; font-size: 0.9em; }
        .sidebar-header { padding: 15px; border-bottom: 1px solid #e0e0e0; background: #f8f9fa; }
        .sidebar-header h3 { color: #333; font-size: 16px; }
    </style>
</head>
<body>
    <div id="app" class="container">
        <div class="sidebar">
            <div class="sidebar-header">
                <h3>Conversations</h3>
            </div>
            <div class="conversation-list">
                <button class="new-chat-btn" @click="startNewChat">+ New Chat</button>
                <div v-for="conv in conversations" 
                     :key="conv.id" 
                     class="conversation-item"
                     :class="{ active: conv.id === currentConversationId }"
                     @click="selectConversation(conv.id)">
                    <div style="font-weight: bold; font-size: 14px;">{{ conv.title }}</div>
                    <div style="font-size: 12px; color: #666;">{{ formatDate(conv.updated_at) }}</div>
                </div>
            </div>
        </div>
        
        <div class="main">
            <div class="header">
                <h1>{{ agent_name }}</h1>
                <div style="font-size: 14px; color: #666; margin-top: 5px;">
                    AI Assistant with {{ toolCount }} tools available
                </div>
            </div>
            
            <div class="chat-area" ref="chatArea">
                <div v-if="loading" class="loading">Loading...</div>
                <div v-if="error" class="error">{{ error }}</div>
                
                <div v-for="message in messages" :key="message.timestamp" 
                     :class="['message', message.role + '-message']">
                    <div>{{ message.content }}</div>
                    <div v-if="message.tool_calls && message.tool_calls.length > 0" class="tool-calls">
                        <div v-for="tool in message.tool_calls" :key="tool.id" class="tool-call">
                            🔧 {{ tool.name }}: {{ tool.result.success ? 'Success' : 'Failed' }}
                        </div>
                    </div>
                    <div style="font-size: 11px; color: #999; margin-top: 5px;">
                        {{ formatTime(message.timestamp) }}
                    </div>
                </div>
            </div>
            
            <div class="input-area">
                <div class="input-container">
                    <input v-model="inputMessage" 
                           @keypress.enter="sendMessage"
                           placeholder="Type your message..."
                           :disabled="sending">
                    <button @click="sendMessage" :disabled="sending || !inputMessage.trim()">
                        {{ sending ? 'Sending...' : 'Send' }}
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const { createApp } = Vue;

        createApp({
            data() {
                return {
                    agent_name: '{{ agent_name }}',
                    messages: [],
                    inputMessage: '',
                    conversations: [],
                    currentConversationId: null,
                    sending: false,
                    loading: false,
                    error: null,
                    toolCount: 0
                }
            },
            async mounted() {
                await this.loadConversations();
                await this.loadTools();
            },
            methods: {
                async loadConversations() {
                    try {
                        const response = await axios.get('/api/conversations');
                        this.conversations = response.data.conversations;
                    } catch (err) {
                        this.error = 'Failed to load conversations';
                    }
                },
                async loadTools() {
                    try {
                        const response = await axios.get('/api/tools');
                        this.toolCount = response.data.tools.length;
                    } catch (err) {
                        console.error('Failed to load tools');
                    }
                },
                async selectConversation(conversationId) {
                    this.currentConversationId = conversationId;
                    this.loading = true;
                    try {
                        const response = await axios.get(`/api/conversations/${conversationId}`);
                        this.messages = response.data.history;
                        this.error = null;
                        this.$nextTick(() => this.scrollToBottom());
                    } catch (err) {
                        this.error = 'Failed to load conversation';
                        this.messages = [];
                    }
                    this.loading = false;
                },
                startNewChat() {
                    this.currentConversationId = null;
                    this.messages = [];
                    this.error = null;
                },
                async sendMessage() {
                    if (!this.inputMessage.trim() || this.sending) return;

                    const userMessage = this.inputMessage.trim();
                    this.inputMessage = '';
                    this.sending = true;
                    this.error = null;

                    // Add user message to UI immediately
                    this.messages.push({
                        role: 'user',
                        content: userMessage,
                        timestamp: new Date().toISOString()
                    });

                    this.$nextTick(() => this.scrollToBottom());

                    try {
                        const response = await axios.post('/api/chat', {
                            message: userMessage,
                            conversation_id: this.currentConversationId
                        });

                        // Update conversation ID if it was a new chat
                        if (!this.currentConversationId) {
                            this.currentConversationId = response.data.conversation_id;
                            await this.loadConversations();
                        }

                        // Add assistant response
                        this.messages.push({
                            role: 'assistant',
                            content: response.data.response,
                            tool_calls: response.data.tool_calls || [],
                            timestamp: new Date().toISOString()
                        });

                        this.$nextTick(() => this.scrollToBottom());

                    } catch (err) {
                        this.error = err.response?.data?.error || 'Failed to send message';
                        console.error('Chat error:', err);
                    }

                    this.sending = false;
                },
                scrollToBottom() {
                    const chatArea = this.$refs.chatArea;
                    if (chatArea) {
                        chatArea.scrollTop = chatArea.scrollHeight;
                    }
                },
                formatDate(dateStr) {
                    return new Date(dateStr).toLocaleDateString();
                },
                formatTime(dateStr) {
                    return new Date(dateStr).toLocaleTimeString();
                }
            }
        }).mount('#app');
    </script>
</body>
</html>"""
    
    with open(os.path.join(templates_dir, "index.html"), "w") as f:
        f.write(html_template)

if __name__ == '__main__':
    # Ensure templates directory exists
    create_templates_directory()
    
    # Validate configuration
    if not settings.validate():
        print("Configuration validation failed. Please check your .env file.")
        exit(1)
    
    print(f"Starting {agent.agent_name} on {settings.FLASK_HOST}:{settings.FLASK_PORT}")
    print(f"Available tools: {', '.join(agent.tools.keys())}")
    
    app.run(
        host=settings.FLASK_HOST,
        port=settings.FLASK_PORT,
        debug=settings.FLASK_DEBUG
    )