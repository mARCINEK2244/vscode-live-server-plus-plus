#!/usr/bin/env python3
"""
Test script for AI Agent system.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
from agent.core import AIAgent
from tools.calculator import CalculatorTool
from tools.file_operations import ReadFileTool
from tools.datetime_tool import DateTimeTool

def test_basic_functionality():
    """Test basic agent functionality."""
    print("🧪 Testing Basic Functionality")
    print("=" * 50)
    
    # Initialize agent
    agent = AIAgent()
    print(f"✅ Agent initialized: {agent.agent_name}")
    print(f"✅ Tools loaded: {len(agent.tools)}")
    
    # Test tools
    for tool_name in agent.tools:
        print(f"   - {tool_name}")
    
    return agent

def test_calculator_tool():
    """Test calculator tool."""
    print("\n🧮 Testing Calculator Tool")
    print("=" * 50)
    
    calc_tool = CalculatorTool()
    
    # Test basic calculation
    result = calc_tool.execute(expression="2 + 3 * 4")
    if result.success:
        print(f"✅ Calculation '2 + 3 * 4' = {result.data['result']}")
    else:
        print(f"❌ Calculation failed: {result.error}")
    
    # Test function
    result = calc_tool.execute(expression="sqrt(16)")
    if result.success:
        print(f"✅ Function 'sqrt(16)' = {result.data['result']}")
    else:
        print(f"❌ Function failed: {result.error}")
    
    return result.success

def test_datetime_tool():
    """Test datetime tool."""
    print("\n📅 Testing DateTime Tool")
    print("=" * 50)
    
    dt_tool = DateTimeTool()
    
    # Test current time
    result = dt_tool.execute(operation="current", timezone="UTC")
    if result.success:
        print(f"✅ Current UTC time: {result.data['current_time']}")
    else:
        print(f"❌ Current time failed: {result.error}")
    
    # Test date calculation
    result = dt_tool.execute(operation="add_days", days=7)
    if result.success:
        print(f"✅ Date + 7 days: {result.data['result']}")
    else:
        print(f"❌ Date calculation failed: {result.error}")
    
    return result.success

def test_conversation_manager():
    """Test conversation management."""
    print("\n💬 Testing Conversation Manager")
    print("=" * 50)
    
    agent = AIAgent()
    
    # Create conversation
    conv_id = agent.conversation_manager.create_conversation("Test Conversation")
    print(f"✅ Created conversation: {conv_id}")
    
    # Add messages
    agent.conversation_manager.add_message(conv_id, "user", "Hello, this is a test message")
    agent.conversation_manager.add_message(conv_id, "assistant", "Hello! I'm responding to your test message.")
    
    # Get history
    history = agent.get_conversation_history(conv_id)
    print(f"✅ Conversation has {len(history)} messages")
    
    for msg in history:
        print(f"   {msg['role']}: {msg['content'][:50]}...")
    
    return len(history) == 2

def test_tool_execution():
    """Test tool execution through agent."""
    print("\n🔧 Testing Tool Execution")
    print("=" * 50)
    
    agent = AIAgent()
    
    # Test calculator tool
    result = agent.execute_tool("calculator", expression="10 * 5 + 2")
    if result.success:
        print(f"✅ Calculator tool: 10 * 5 + 2 = {result.data['result']}")
    else:
        print(f"❌ Calculator tool failed: {result.error}")
    
    # Test datetime tool  
    result = agent.execute_tool("datetime", operation="current", timezone="US/Eastern")
    if result.success:
        print(f"✅ DateTime tool: Current Eastern time = {result.data['current_time']}")
    else:
        print(f"❌ DateTime tool failed: {result.error}")
    
    return result.success

async def test_chat_functionality():
    """Test chat functionality (without AI providers)."""
    print("\n💭 Testing Chat Functionality")
    print("=" * 50)
    
    agent = AIAgent()
    
    # Test if we have AI providers configured
    if not agent.openai_client and not agent.anthropic_client:
        print("⚠️  No AI providers configured - skipping chat test")
        print("   (Configure API keys in .env to test chat functionality)")
        return True
    
    try:
        # Simple chat test
        response = await agent.chat("What is 2+2?")
        print(f"✅ Chat response received: {response['response'][:100]}...")
        return True
    except Exception as e:
        print(f"❌ Chat failed: {str(e)}")
        return False

def test_configuration():
    """Test configuration loading."""
    print("\n⚙️  Testing Configuration")
    print("=" * 50)
    
    print(f"Agent Name: {settings.AGENT_NAME}")
    print(f"Default Model: {settings.DEFAULT_MODEL}")
    print(f"Max Tokens: {settings.MAX_TOKENS}")
    print(f"Temperature: {settings.TEMPERATURE}")
    print(f"Flask Host: {settings.FLASK_HOST}")
    print(f"Flask Port: {settings.FLASK_PORT}")
    
    # Check if API keys are set (without showing them)
    openai_configured = bool(settings.OPENAI_API_KEY)
    anthropic_configured = bool(settings.ANTHROPIC_API_KEY)
    
    print(f"OpenAI API Key: {'✅ Configured' if openai_configured else '❌ Not configured'}")
    print(f"Anthropic API Key: {'✅ Configured' if anthropic_configured else '❌ Not configured'}")
    
    if not openai_configured and not anthropic_configured:
        print("⚠️  No AI provider API keys configured")
        print("   Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env file")
    
    return True

async def run_all_tests():
    """Run all tests."""
    print("🤖 AI Agent System Test Suite")
    print("=" * 70)
    print(f"Test started at: {datetime.now()}")
    
    test_results = []
    
    # Run tests
    test_results.append(("Configuration", test_configuration()))
    test_results.append(("Basic Functionality", test_basic_functionality() is not None))
    test_results.append(("Calculator Tool", test_calculator_tool()))
    test_results.append(("DateTime Tool", test_datetime_tool()))
    test_results.append(("Conversation Manager", test_conversation_manager()))
    test_results.append(("Tool Execution", test_tool_execution()))
    test_results.append(("Chat Functionality", await test_chat_functionality()))
    
    # Print results
    print("\n" + "=" * 70)
    print("📋 Test Results Summary")
    print("=" * 70)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your AI Agent system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

def main():
    """Main test function."""
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()