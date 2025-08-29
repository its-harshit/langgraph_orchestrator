#!/usr/bin/env python3
"""
Test script for custom LLM integration with pure LangGraph
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_custom_llm_connection():
    """Test basic connection to custom LLM endpoint"""
    print("🔍 Testing Custom LLM Connection...")
    
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        
        # Get configuration from environment
        base_url = os.getenv("CUSTOM_LLM_BASE_URL")
        api_key = os.getenv("CUSTOM_LLM_API_KEY", "dummy-key")
        model = os.getenv("CUSTOM_LLM_MODEL", "llama2:7b")
        
        if not base_url:
            print("❌ CUSTOM_LLM_BASE_URL not set in environment")
            return False
        
        print(f"📍 Testing endpoint: {base_url}")
        print(f"🤖 Using model: {model}")
        
        # Create LLM instance
        llm = ChatOpenAI(
            model=model,
            base_url=base_url,
            api_key=api_key,
            temperature=0,
            max_tokens=500
        )
        
        # Test simple message
        response = llm.invoke([HumanMessage(content="Hello, can you help me with a seat change?")])
        
        print(f"✅ Custom LLM Response: {response.content[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

async def test_triage_agent():
    """Test triage agent with custom LLM"""
    print("\n🎯 Testing Triage Agent with Custom LLM...")
    
    try:
        from langgraph_pure import process_message_pure
        
        # Test messages that should route to different agents
        test_messages = [
            "Can I change my seat?",
            "What's the status of my flight?",
            "I want to cancel my flight",
            "How many seats are on the plane?"
        ]
        
        for message in test_messages:
            print(f"\n📝 Testing: '{message}'")
            result = await process_message_pure(message)
            
            print(f"   ✅ Routing: {' → '.join(result['routing_history'])}")
            print(f"   ✅ Final Agent: {result['current_agent']}")
            
            # Check if routing worked
            if len(result['routing_history']) > 1:
                print(f"   ✅ Routing successful!")
            else:
                print(f"   ⚠️  Routing may have failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Triage test failed: {e}")
        return False

async def test_full_conversation():
    """Test a full conversation flow"""
    print("\n🔄 Testing Full Conversation Flow...")
    
    try:
        from langgraph_pure import process_message_pure
        
        # Simulate a conversation
        conversation = [
            "Can I change my seat?",
            "I want seat 23A",
            "What's my flight status?",
            "How many seats are on the plane?"
        ]
        
        conversation_state = None
        
        for i, message in enumerate(conversation):
            print(f"\n💬 Turn {i+1}: '{message}'")
            
            result = await process_message_pure(message, conversation_state)
            conversation_state = result
            
            print(f"   ✅ Agent: {result['current_agent']}")
            print(f"   ✅ Routing: {' → '.join(result['routing_history'])}")
            
            # Show last assistant message
            if result['messages']:
                last_assistant = None
                for msg in reversed(result['messages']):
                    if hasattr(msg, 'content') and not hasattr(msg, 'role'):
                        last_assistant = msg.content
                        break
                if last_assistant:
                    print(f"   💬 Response: {last_assistant[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversation test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Custom LLM Integration Test")
    print("=" * 50)
    
    # Check environment
    use_custom = os.getenv("USE_CUSTOM_LLM", "false").lower() == "true"
    if not use_custom:
        print("⚠️  USE_CUSTOM_LLM is not set to 'true'")
        print("   Set USE_CUSTOM_LLM=true in your .env file")
        return
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Basic connection
    if test_custom_llm_connection():
        tests_passed += 1
    
    # Test 2: Triage agent
    if asyncio.run(test_triage_agent()):
        tests_passed += 1
    
    # Test 3: Full conversation
    if asyncio.run(test_full_conversation()):
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your custom LLM is working correctly.")
        print("\n🚀 You can now run the full application:")
        print("   cd ui && npm run dev")
    else:
        print("❌ Some tests failed. Check the error messages above.")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Make sure your LLM server is running")
        print("   2. Check your .env configuration")
        print("   3. Verify the endpoint URL is correct")
        print("   4. Ensure your model name is correct")

if __name__ == "__main__":
    main()
