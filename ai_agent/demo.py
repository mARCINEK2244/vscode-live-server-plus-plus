#!/usr/bin/env python3
"""
AI Agent System Demo

This script demonstrates the capabilities of the AI Agent system.
"""

import sys
import os
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from agent.core import AIAgent

console = Console()

def show_welcome():
    """Display welcome message."""
    welcome_text = """
# 🤖 AI Agent System Demo

Welcome to the AI Agent System demonstration! This script will showcase the various capabilities 
of your AI agent including tool usage, conversation management, and extensible architecture.

## What we'll demonstrate:

1. **Tool Capabilities** - See all available tools
2. **Calculator Tool** - Mathematical calculations
3. **DateTime Tool** - Date and time operations  
4. **File Operations** - Reading and writing files
5. **Web Search** - Internet search capabilities
6. **Conversation Management** - Memory and persistence
7. **Agent Statistics** - System information

Let's get started! 🚀
    """
    
    console.print(Panel(
        Markdown(welcome_text),
        title="AI Agent Demo",
        border_style="blue"
    ))

def demo_tool_listing():
    """Demonstrate tool listing."""
    console.print("\n[bold blue]📋 Available Tools[/bold blue]")
    console.print("=" * 50)
    
    agent = AIAgent()
    
    table = Table()
    table.add_column("Tool Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Parameters", style="yellow")
    
    for tool_name, tool in agent.tools.items():
        params = ", ".join([p.name for p in tool.parameters[:3]])  # Show first 3 params
        if len(tool.parameters) > 3:
            params += f", ... (+{len(tool.parameters) - 3} more)"
        table.add_row(tool_name, tool.description[:60] + "...", params)
    
    console.print(table)
    console.print(f"\n✅ Total tools available: [bold]{len(agent.tools)}[/bold]")

def demo_calculator():
    """Demonstrate calculator tool."""
    console.print("\n[bold blue]🧮 Calculator Tool Demo[/bold blue]")
    console.print("=" * 50)
    
    agent = AIAgent()
    
    expressions = [
        "2 + 3 * 4",
        "sqrt(16) + cos(0)",
        "log(100) / log(10)",
        "pi * 2",
        "abs(-42)"
    ]
    
    for expr in expressions:
        result = agent.execute_tool("calculator", expression=expr)
        if result.success:
            console.print(f"✅ {expr:<20} = [green]{result.data['result']}[/green]")
        else:
            console.print(f"❌ {expr:<20} = [red]Error: {result.error}[/red]")

def demo_datetime():
    """Demonstrate datetime tool."""
    console.print("\n[bold blue]📅 DateTime Tool Demo[/bold blue]")
    console.print("=" * 50)
    
    agent = AIAgent()
    
    # Current time in different timezones
    timezones = ["UTC", "US/Eastern", "Europe/London", "Asia/Tokyo"]
    
    console.print("[dim]Current time in different timezones:[/dim]")
    for tz in timezones:
        result = agent.execute_tool("datetime", operation="current", timezone=tz)
        if result.success:
            console.print(f"  {tz:<15} {result.data['current_time']}")
    
    # Date calculations
    console.print("\n[dim]Date calculations:[/dim]")
    result = agent.execute_tool("datetime", operation="add_days", days=30)
    if result.success:
        console.print(f"  30 days from now: {result.data['result']}")
    
    result = agent.execute_tool("datetime", operation="add_days", days=-7)
    if result.success:
        console.print(f"  7 days ago: {result.data['result']}")

def demo_file_operations():
    """Demonstrate file operations."""
    console.print("\n[bold blue]📁 File Operations Demo[/bold blue]")
    console.print("=" * 50)
    
    agent = AIAgent()
    
    # Create a demo file
    demo_content = """# Demo File
This is a demonstration file created by the AI Agent system.

## Features:
- File reading and writing
- Directory listing
- Automatic directory creation

Generated at: """ + str(agent.execute_tool("datetime", operation="current").data['current_time'])
    
    # Write file
    result = agent.execute_tool("write_file", 
                                file_path="demo_files/test.md", 
                                content=demo_content)
    if result.success:
        console.print(f"✅ Created file: [green]{result.data['file_path']}[/green]")
        console.print(f"   Bytes written: {result.data['bytes_written']}")
    
    # Read file back
    result = agent.execute_tool("read_file", file_path="demo_files/test.md")
    if result.success:
        console.print(f"✅ Read file successfully ({result.data['size']} characters)")
        console.print("[dim]File content preview:[/dim]")
        preview = result.data['content'][:200] + "..." if len(result.data['content']) > 200 else result.data['content']
        console.print(f"[italic]{preview}[/italic]")
    
    # List directory
    result = agent.execute_tool("list_directory", directory_path="demo_files")
    if result.success:
        console.print(f"✅ Directory listing: {result.data['total_count']} items")
        for item in result.data['items'][:5]:  # Show first 5 items
            console.print(f"   {item['type']}: {item['name']}")

def demo_statistics():
    """Demonstrate statistics tool."""
    console.print("\n[bold blue]📊 Statistics Tool Demo[/bold blue]")
    console.print("=" * 50)
    
    agent = AIAgent()
    
    # Sample data
    sample_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25]
    
    result = agent.execute_tool("statistics", 
                                numbers=sample_numbers,
                                calculations=["mean", "median", "std", "min", "max"])
    
    if result.success:
        stats = result.data['statistics']
        console.print(f"Sample data: {sample_numbers}")
        console.print(f"  Mean: {stats.get('mean', 'N/A'):.2f}")
        console.print(f"  Median: {stats.get('median', 'N/A')}")
        console.print(f"  Std Dev: {stats.get('std', 'N/A'):.2f}")
        console.print(f"  Min: {stats.get('min', 'N/A')}")
        console.print(f"  Max: {stats.get('max', 'N/A')}")

def demo_conversation_management():
    """Demonstrate conversation management."""
    console.print("\n[bold blue]💬 Conversation Management Demo[/bold blue]")
    console.print("=" * 50)
    
    agent = AIAgent()
    
    # Create conversations
    conv_id1 = agent.conversation_manager.create_conversation("Demo Conversation 1")
    conv_id2 = agent.conversation_manager.create_conversation("Demo Conversation 2")
    
    # Add messages
    messages = [
        ("user", "Hello, what can you help me with?"),
        ("assistant", "I can help you with calculations, file operations, web searches, and more!"),
        ("user", "Can you calculate 15 * 8?"),
        ("assistant", "Sure! 15 * 8 = 120")
    ]
    
    for role, content in messages:
        agent.conversation_manager.add_message(conv_id1, role, content)
    
    # Show conversation list
    conversations = agent.conversation_manager.get_conversation_list()
    console.print(f"✅ Created {len(conversations)} conversations")
    
    for conv in conversations[-2:]:  # Show last 2
        console.print(f"   {conv['title']} ({conv['message_count']} messages)")
    
    # Show conversation summary
    summary = agent.conversation_manager.get_conversation_summary(conv_id1)
    console.print(f"✅ Conversation summary:")
    console.print(f"   Total messages: {summary['total_messages']}")
    console.print(f"   User messages: {summary['user_messages']}")
    console.print(f"   Assistant messages: {summary['assistant_messages']}")

def demo_agent_stats():
    """Show agent statistics."""
    console.print("\n[bold blue]📈 Agent Statistics[/bold blue]")
    console.print("=" * 50)
    
    agent = AIAgent()
    agent_stats = agent.get_stats()
    memory_stats = agent.conversation_manager.get_stats()
    
    stats_table = Table()
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="white")
    
    stats_table.add_row("Agent Name", agent_stats["agent_name"])
    stats_table.add_row("Available Tools", str(agent_stats["tools_count"]))
    stats_table.add_row("OpenAI Configured", "✅" if agent_stats["ai_providers"]["openai"] else "❌")
    stats_table.add_row("Anthropic Configured", "✅" if agent_stats["ai_providers"]["anthropic"] else "❌")
    stats_table.add_row("Total Conversations", str(memory_stats["total_conversations"]))
    stats_table.add_row("Total Messages", str(memory_stats["total_messages"]))
    stats_table.add_row("Database", "SQLite")
    stats_table.add_row("Web Interface", f"http://{settings.FLASK_HOST}:{settings.FLASK_PORT}")
    
    console.print(stats_table)

async def demo_chat_if_available():
    """Demonstrate chat functionality if AI providers are available."""
    console.print("\n[bold blue]💭 Chat Functionality[/bold blue]")
    console.print("=" * 50)
    
    agent = AIAgent()
    
    if not agent.openai_client and not agent.anthropic_client:
        console.print("⚠️  [yellow]Chat functionality requires AI provider API keys[/yellow]")
        console.print("   Configure OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file")
        console.print("   Then the agent can have natural conversations and use tools automatically!")
        return
    
    try:
        console.print("🤖 Testing chat with tool usage...")
        response = await agent.chat("What is the square root of 144 plus today's date?")
        
        console.print("✅ Chat response received!")
        console.print(f"Response: {response['response'][:200]}...")
        
        if response.get('tool_calls'):
            console.print(f"🔧 Used {len(response['tool_calls'])} tools:")
            for tool_call in response['tool_calls']:
                console.print(f"   - {tool_call['name']}")
    
    except Exception as e:
        console.print(f"❌ Chat test failed: {str(e)}")

def show_next_steps():
    """Show next steps for users."""
    next_steps = """
# 🎯 Next Steps

Congratulations! You've seen the AI Agent system in action. Here's what you can do next:

## 1. Configure AI Providers
```bash
# Edit .env file with your API keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## 2. Start the Web Interface
```bash
python app.py
```
Then visit http://localhost:5000 for a beautiful web interface.

## 3. Use the CLI Interface
```bash
python cli_agent.py
```
For a rich terminal-based interaction.

## 4. Extend with Custom Tools
Create new tools by inheriting from `BaseTool` in the `tools/` directory.

## 5. Integrate into Your Projects
```python
from agent.core import AIAgent
agent = AIAgent()
response = await agent.chat("Your message here")
```

## 6. Run Tests
```bash
python test_agent.py
```

Happy building! 🚀
    """
    
    console.print(Panel(
        Markdown(next_steps),
        title="What's Next?",
        border_style="green"
    ))

async def main():
    """Main demo function."""
    try:
        show_welcome()
        
        input("\nPress Enter to start the demo...")
        
        demo_tool_listing()
        input("\nPress Enter to continue...")
        
        demo_calculator()
        input("\nPress Enter to continue...")
        
        demo_datetime()
        input("\nPress Enter to continue...")
        
        demo_file_operations()
        input("\nPress Enter to continue...")
        
        demo_statistics()
        input("\nPress Enter to continue...")
        
        demo_conversation_management()
        input("\nPress Enter to continue...")
        
        demo_agent_stats()
        input("\nPress Enter to test chat functionality...")
        
        await demo_chat_if_available()
        
        console.print("\n🎉 [bold green]Demo completed successfully![/bold green]")
        
        show_next_steps()
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Demo failed: {str(e)}[/red]")

if __name__ == "__main__":
    asyncio.run(main())