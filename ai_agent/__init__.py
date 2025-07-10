"""
AI Agent System

A comprehensive AI agent system with conversation capabilities, tool usage, and extensible architecture.
"""

__version__ = "1.0.0"
__author__ = "AI Agent Developer"

from .agent.core import AIAgent
from .tools.base import BaseTool, ToolResult, ToolParameter
from .memory.conversation import ConversationManager
from .config.settings import settings

__all__ = [
    'AIAgent',
    'BaseTool', 
    'ToolResult',
    'ToolParameter',
    'ConversationManager',
    'settings'
]