#!/usr/bin/env python3
"""
CLI interface for the AI Agent.
"""

import asyncio
import sys
import os
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
import click

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from agent.core import AIAgent

console = Console()

class CLIAgent:
    """Command-line interface for the AI Agent."""
    
    def __init__(self):
        self.agent = AIAgent()
        self.current_conversation_id = None
        self.conversation_title = None
    
    def display_welcome(self):
        """Display welcome message."""
        welcome_text = f"""
# Welcome to {self.agent.agent_name}

Your AI assistant with **{len(self.agent.tools)}** powerful tools available:

{self._format_tools_list()}

Type your messages to start chatting, or use these commands:
- `/help` - Show available commands
- `/tools` - List all available tools
- `/history` - Show conversation history
- `/new` - Start a new conversation
- `/stats` - Show agent statistics
- `/quit` or `/exit` - Exit the application
        """
        
        console.print(Panel(
            Markdown(welcome_text),
            title="AI Agent CLI",
            border_style="blue"
        ))
    
    def _format_tools_list(self):
        """Format the tools list for display."""
        tools_text = ""
        for tool_name, tool in self.agent.tools.items():
            tools_text += f"- **{tool_name}**: {tool.description}\n"
        return tools_text
    
    async def run(self):
        """Run the CLI interface."""
        self.display_welcome()
        
        # Validate configuration
        if not settings.validate():
            console.print("[red]Configuration validation failed. Please check your .env file.[/red]")
            return
        
        # Start new conversation
        self.current_conversation_id = self.agent.conversation_manager.create_conversation("CLI Session")
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask(
                    f"[bold blue]{self.agent.agent_name}[/bold blue]",
                    default=""
                ).strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    if await self._handle_command(user_input):
                        break
                    continue
                
                # Process as chat message
                await self._process_message(user_input)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Use /quit to exit gracefully.[/yellow]")
                continue
            except EOFError:
                break
    
    async def _handle_command(self, command: str) -> bool:
        """Handle CLI commands. Returns True if should exit."""
        cmd = command.lower().strip()
        
        if cmd in ['/quit', '/exit']:
            console.print("[green]Goodbye! 👋[/green]")
            return True
        
        elif cmd == '/help':
            self._show_help()
        
        elif cmd == '/tools':
            self._show_tools()
        
        elif cmd == '/history':
            self._show_history()
        
        elif cmd == '/new':
            self._new_conversation()
        
        elif cmd == '/stats':
            self._show_stats()
        
        elif cmd.startswith('/tool '):
            # Execute a specific tool
            parts = cmd.split(' ', 2)
            if len(parts) >= 2:
                await self._execute_tool_command(parts[1:])
            else:
                console.print("[red]Usage: /tool <tool_name> [parameters][/red]")
        
        else:
            console.print(f"[red]Unknown command: {command}[/red]")
            console.print("Type /help for available commands.")
        
        return False
    
    def _show_help(self):
        """Show help information."""
        help_text = """
## Available Commands

- `/help` - Show this help message
- `/tools` - List all available tools with descriptions
- `/history` - Show current conversation history
- `/new` - Start a new conversation
- `/stats` - Show agent and conversation statistics
- `/tool <name>` - Execute a specific tool (interactive)
- `/quit` or `/exit` - Exit the application

## Tool Usage

You can ask me to use tools naturally in conversation, or use `/tool <name>` to use them directly.

Example: "Search the web for latest AI news" or "/tool web_search"
        """
        
        console.print(Panel(
            Markdown(help_text),
            title="Help",
            border_style="green"
        ))
    
    def _show_tools(self):
        """Show available tools."""
        table = Table(title="Available Tools")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Parameters", style="yellow")
        
        for tool_name, tool in self.agent.tools.items():
            params = ", ".join([p.name for p in tool.parameters])
            table.add_row(tool_name, tool.description, params)
        
        console.print(table)
    
    def _show_history(self):
        """Show conversation history."""
        if not self.current_conversation_id:
            console.print("[yellow]No active conversation.[/yellow]")
            return
        
        history = self.agent.get_conversation_history(self.current_conversation_id)
        
        if not history:
            console.print("[yellow]No messages in current conversation.[/yellow]")
            return
        
        console.print(f"\n[bold]Conversation History ({len(history)} messages):[/bold]")
        
        for i, message in enumerate(history, 1):
            role_color = "blue" if message["role"] == "user" else "green"
            timestamp = message.get("timestamp", "")
            
            console.print(f"\n[{role_color}]{message['role'].title()}[/{role_color}] ({timestamp}):")
            console.print(message["content"])
            
            if message.get("tool_calls"):
                console.print(f"[dim]🔧 Used {len(message['tool_calls'])} tool(s)[/dim]")
    
    def _new_conversation(self):
        """Start a new conversation."""
        self.current_conversation_id = self.agent.conversation_manager.create_conversation("CLI Session")
        console.print("[green]Started new conversation! 🆕[/green]")
    
    def _show_stats(self):
        """Show agent statistics."""
        agent_stats = self.agent.get_stats()
        memory_stats = self.agent.conversation_manager.get_stats()
        
        stats_table = Table(title="Agent Statistics")
        stats_table.add_column("Category", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Agent Name", agent_stats["agent_name"])
        stats_table.add_row("Available Tools", str(agent_stats["tools_count"]))
        stats_table.add_row("OpenAI Available", "✅" if agent_stats["ai_providers"]["openai"] else "❌")
        stats_table.add_row("Anthropic Available", "✅" if agent_stats["ai_providers"]["anthropic"] else "❌")
        stats_table.add_row("Total Conversations", str(memory_stats["total_conversations"]))
        stats_table.add_row("Total Messages", str(memory_stats["total_messages"]))
        
        console.print(stats_table)
    
    async def _execute_tool_command(self, parts):
        """Execute a tool via command."""
        tool_name = parts[0]
        
        if tool_name not in self.agent.tools:
            console.print(f"[red]Tool '{tool_name}' not found.[/red]")
            self._show_tools()
            return
        
        tool = self.agent.tools[tool_name]
        
        # Collect parameters interactively
        params = {}
        for param in tool.parameters:
            if param.required:
                value = Prompt.ask(f"Enter {param.name} ({param.description})")
                params[param.name] = value
            else:
                value = Prompt.ask(
                    f"Enter {param.name} ({param.description}) [optional]",
                    default=""
                )
                if value:
                    params[param.name] = value
        
        # Execute tool
        with console.status(f"Executing {tool_name}..."):
            result = self.agent.execute_tool(tool_name, **params)
        
        if result.success:
            console.print(f"[green]✅ Tool executed successfully![/green]")
            if result.data:
                console.print(Panel(
                    str(result.data),
                    title=f"{tool_name} Result",
                    border_style="green"
                ))
        else:
            console.print(f"[red]❌ Tool execution failed: {result.error}[/red]")
    
    async def _process_message(self, message: str):
        """Process a chat message."""
        # Show typing indicator
        with Live(Spinner("dots", text=f"[dim]{self.agent.agent_name} is thinking...[/dim]"), refresh_per_second=10):
            try:
                response = await self.agent.chat(
                    message,
                    conversation_id=self.current_conversation_id
                )
                
                # Display response
                console.print(f"\n[bold green]{self.agent.agent_name}:[/bold green]")
                
                if response.get("tool_calls"):
                    console.print(f"[dim]🔧 Used {len(response['tool_calls'])} tool(s)[/dim]")
                    for tool_call in response["tool_calls"]:
                        status = "✅" if tool_call["result"]["success"] else "❌"
                        console.print(f"[dim]  {status} {tool_call['name']}[/dim]")
                
                # Display the main response
                if response["response"]:
                    console.print(Markdown(response["response"]))
                else:
                    console.print("[yellow]No response generated.[/yellow]")
                
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")


@click.command()
@click.option('--model', default=None, help='AI model to use (e.g., gpt-4, claude-3-sonnet)')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def main(model, debug):
    """Start the AI Agent CLI interface."""
    
    if debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    if model:
        settings.DEFAULT_MODEL = model
    
    cli_agent = CLIAgent()
    
    try:
        asyncio.run(cli_agent.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        if debug:
            console.print_exception()

if __name__ == "__main__":
    main()