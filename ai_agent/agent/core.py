import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

# AI Provider imports
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

from config.settings import settings
from tools.base import BaseTool, ToolResult
from memory.conversation import ConversationManager

class AIAgent:
    """Core AI Agent that manages tools, conversations, and AI interactions."""
    
    def __init__(self, agent_name: str = None):
        self.agent_name = agent_name or settings.AGENT_NAME
        self.tools: Dict[str, BaseTool] = {}
        self.conversation_manager = ConversationManager()
        self.logger = self._setup_logging()
        
        # Initialize AI clients
        self.openai_client = None
        self.anthropic_client = None
        self._init_ai_clients()
        
        # Load default tools
        self._load_default_tools()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('ai_agent')
        logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _init_ai_clients(self):
        """Initialize AI provider clients."""
        if settings.OPENAI_API_KEY and openai:
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            self.logger.info("OpenAI client initialized")
        
        if settings.ANTHROPIC_API_KEY and anthropic:
            self.anthropic_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.logger.info("Anthropic client initialized")
        
        if not self.openai_client and not self.anthropic_client:
            self.logger.warning("No AI providers configured")
    
    def _load_default_tools(self):
        """Load default tools."""
        from tools.web_search import WebSearchTool, WebScrapeTool
        from tools.file_operations import ReadFileTool, WriteFileTool, ListDirectoryTool
        from tools.calculator import CalculatorTool, StatsTool
        from tools.datetime_tool import DateTimeTool, TimezoneInfoTool
        
        default_tools = [
            WebSearchTool(),
            WebScrapeTool(),
            ReadFileTool(),
            WriteFileTool(),
            ListDirectoryTool(),
            CalculatorTool(),
            StatsTool(),
            DateTimeTool(),
            TimezoneInfoTool(),
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: BaseTool):
        """Register a new tool with the agent."""
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def unregister_tool(self, tool_name: str):
        """Unregister a tool from the agent."""
        if tool_name in self.tools:
            del self.tools[tool_name]
            self.logger.info(f"Unregistered tool: {tool_name}")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with their schemas."""
        return [tool.get_schema() for tool in self.tools.values()]
    
    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a specific tool with given parameters."""
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found"
            )
        
        tool = self.tools[tool_name]
        
        if not tool.validate_parameters(kwargs):
            return ToolResult(
                success=False,
                error=f"Invalid parameters for tool '{tool_name}'"
            )
        
        try:
            self.logger.info(f"Executing tool: {tool_name}")
            result = tool.execute(**kwargs)
            self.logger.info(f"Tool {tool_name} executed {'successfully' if result.success else 'with error'}")
            return result
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            return ToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}"
            )
    
    async def chat(self, message: str, conversation_id: str = None, model: str = None) -> Dict[str, Any]:
        """Process a chat message and return the agent's response."""
        if not conversation_id:
            conversation_id = self.conversation_manager.create_conversation()
        
        # Add user message to conversation
        self.conversation_manager.add_message(
            conversation_id, "user", message
        )
        
        # Get conversation history
        history = self.conversation_manager.get_conversation(conversation_id)
        
        # Generate AI response
        response = await self._generate_response(history, model)
        
        # Add assistant response to conversation
        self.conversation_manager.add_message(
            conversation_id, "assistant", response["content"], response.get("tool_calls")
        )
        
        return {
            "conversation_id": conversation_id,
            "response": response["content"],
            "tool_calls": response.get("tool_calls", []),
            "model": response.get("model")
        }
    
    async def _generate_response(self, conversation_history: List[Dict], model: str = None) -> Dict[str, Any]:
        """Generate AI response using available providers."""
        model = model or settings.DEFAULT_MODEL
        
        # Try OpenAI first
        if self.openai_client and model.startswith("gpt"):
            return await self._openai_chat(conversation_history, model)
        
        # Try Anthropic
        if self.anthropic_client and model.startswith("claude"):
            return await self._anthropic_chat(conversation_history, model)
        
        # Fallback to any available provider
        if self.openai_client:
            return await self._openai_chat(conversation_history, "gpt-4")
        elif self.anthropic_client:
            return await self._anthropic_chat(conversation_history, "claude-3-sonnet-20240229")
        
        raise Exception("No AI providers available")
    
    async def _openai_chat(self, conversation_history: List[Dict], model: str) -> Dict[str, Any]:
        """Generate response using OpenAI."""
        messages = []
        
        # Convert conversation history to OpenAI format
        for msg in conversation_history:
            if msg["role"] == "system":
                messages.append({"role": "system", "content": msg["content"]})
            elif msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                assistant_msg = {"role": "assistant", "content": msg["content"]}
                if msg.get("tool_calls"):
                    assistant_msg["tool_calls"] = msg["tool_calls"]
                messages.append(assistant_msg)
        
        # Add system message if not present
        if not messages or messages[0]["role"] != "system":
            system_msg = {
                "role": "system",
                "content": f"You are {self.agent_name}, a helpful AI assistant with access to various tools. "
                          f"Use tools when necessary to help users with their requests."
            }
            messages.insert(0, system_msg)
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                tools=[{"type": "function", "function": tool_schema} for tool_schema in self.get_available_tools()],
                tool_choice="auto",
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE
            )
            
            choice = response.choices[0]
            result = {
                "content": choice.message.content or "",
                "model": model
            }
            
            # Handle tool calls
            if choice.message.tool_calls:
                tool_calls = []
                for tool_call in choice.message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # Execute tool
                    tool_result = self.execute_tool(tool_name, **tool_args)
                    
                    tool_calls.append({
                        "id": tool_call.id,
                        "name": tool_name,
                        "arguments": tool_args,
                        "result": tool_result.dict()
                    })
                
                result["tool_calls"] = tool_calls
                
                # Generate follow-up response with tool results
                messages.append({
                    "role": "assistant",
                    "content": choice.message.content,
                    "tool_calls": [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": json.dumps(tc["arguments"])
                            }
                        } for tc in tool_calls
                    ]
                })
                
                for tool_call in tool_calls:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(tool_call["result"])
                    })
                
                # Get final response
                final_response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=settings.MAX_TOKENS,
                    temperature=settings.TEMPERATURE
                )
                
                result["content"] = final_response.choices[0].message.content
            
            return result
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _anthropic_chat(self, conversation_history: List[Dict], model: str) -> Dict[str, Any]:
        """Generate response using Anthropic Claude."""
        messages = []
        
        # Convert conversation history to Anthropic format
        for msg in conversation_history:
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        try:
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                messages=messages
            )
            
            return {
                "content": response.content[0].text,
                "model": model
            }
            
        except Exception as e:
            self.logger.error(f"Anthropic API error: {e}")
            raise
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_manager.get_conversation(conversation_id)
    
    def clear_conversation(self, conversation_id: str):
        """Clear a conversation."""
        self.conversation_manager.clear_conversation(conversation_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "agent_name": self.agent_name,
            "tools_count": len(self.tools),
            "available_tools": list(self.tools.keys()),
            "ai_providers": {
                "openai": self.openai_client is not None,
                "anthropic": self.anthropic_client is not None
            },
            "conversations_count": len(self.conversation_manager.conversations)
        }