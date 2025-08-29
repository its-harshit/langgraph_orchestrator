# 🚀 Custom LLM Setup Guide

This guide shows you how to configure your own self-hosted LLM for the triage agent in the pure LangGraph implementation.

## 🎯 **Overview**

The system now supports using custom LLMs for the triage agent while keeping specialist agents on OpenAI. This gives you flexibility to:
- Use your own models for routing decisions
- Reduce costs by using local models for triage
- Maintain high-quality responses from OpenAI for complex tasks

## 🔧 **Configuration**

### **1. Environment Variables**

Create a `.env` file in the `python-backend/` directory:

```bash
# OpenAI Configuration (for specialist agents)
OPENAI_API_KEY=your_openai_api_key_here

# Custom LLM Configuration (for triage agent)
USE_CUSTOM_LLM=true
CUSTOM_LLM_BASE_URL=http://your-server:port/v1
CUSTOM_LLM_API_KEY=dummy-key  # Some endpoints don't require real API key
```

### **2. Supported LLM Endpoints**

The system works with any OpenAI-compatible API endpoint. Here are common examples:

#### **Ollama (Local Models)**
```bash
# Install Ollama and run a model
ollama run llama2:7b

# Configuration
CUSTOM_LLM_BASE_URL=http://localhost:11434/v1
CUSTOM_LLM_API_KEY=dummy-key
```

#### **vLLM (High-Performance)**
```bash
# Run vLLM server
python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-2-7b-chat-hf

# Configuration
CUSTOM_LLM_BASE_URL=http://localhost:8000/v1
CUSTOM_LLM_API_KEY=dummy-key
```

#### **LM Studio (Local GUI)**
```bash
# Start LM Studio and run a model
# Then use the local server endpoint

# Configuration
CUSTOM_LLM_BASE_URL=http://localhost:1234/v1
CUSTOM_LLM_API_KEY=dummy-key
```

#### **Your Custom Endpoint**
```bash
# Any OpenAI-compatible API endpoint
CUSTOM_LLM_BASE_URL=http://your-server:port/v1
CUSTOM_LLM_API_KEY=your_api_key_if_needed
```

## 🧪 **Testing Your Setup**

### **1. Test Custom LLM Connection**

```bash
cd python-backend
python -c "
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Set environment variables
os.environ['USE_CUSTOM_LLM'] = 'true'
os.environ['CUSTOM_LLM_BASE_URL'] = 'http://localhost:11434/v1'  # Adjust to your endpoint

# Test the LLM
llm = ChatOpenAI(
    model='llama2:7b',  # Use your model name
    base_url='http://localhost:11434/v1',
    api_key='dummy-key',
    temperature=0
)

response = llm.invoke([HumanMessage(content='Hello, can you help me with a seat change?')])
print('✅ Custom LLM Response:', response.content)
"
```

### **2. Test Triage Agent with Custom LLM**

```bash
cd python-backend
python -c "
import asyncio
import os
from langgraph_pure import process_message_pure

# Set environment variables
os.environ['USE_CUSTOM_LLM'] = 'true'
os.environ['CUSTOM_LLM_BASE_URL'] = 'http://localhost:11434/v1'  # Adjust to your endpoint

# Test triage routing
async def test_triage():
    result = await process_message_pure('Can I change my seat?')
    print('✅ Triage Result:', result['routing_history'])
    print('✅ Final Agent:', result['current_agent'])

asyncio.run(test_triage())
"
```

## 🔍 **Troubleshooting**

### **Common Issues**

#### **1. Connection Refused**
```
Error: Connection refused to http://localhost:11434/v1
```
**Solution**: Make sure your LLM server is running and accessible.

#### **2. Model Not Found**
```
Error: Model 'llama2:7b' not found
```
**Solution**: Use the correct model name for your endpoint.

#### **3. API Format Issues**
```
Error: Invalid API format
```
**Solution**: Ensure your endpoint follows OpenAI API format.

### **Debug Mode**

Enable debug logging to see what's happening:

```bash
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from langgraph_pure import process_message_pure
import asyncio

async def debug_test():
    result = await process_message_pure('Test message')
    print(result)

asyncio.run(debug_test())
"
```

## 🎯 **Model Recommendations**

### **For Triage (Routing)**
- **Llama 2 7B**: Good balance of speed and accuracy
- **Mistral 7B**: Excellent reasoning for routing decisions
- **Phi-2**: Fast and efficient for simple routing

### **For Specialist Agents (Optional)**
You can also configure specialist agents to use custom LLMs by modifying the `get_llm()` calls in each agent function.

## 🔄 **Advanced Configuration**

### **Using Different Models for Different Agents**

You can extend the system to use different models for different agents:

```python
# In langgraph_pure.py, modify get_llm function:
def get_llm(model: str = "gpt-4", agent_type: str = "default") -> BaseChatModel:
    if agent_type == "triage":
        # Use custom LLM for triage
        return ChatOpenAI(base_url="http://localhost:11434/v1", model="llama2:7b")
    elif agent_type == "seat_booking":
        # Use different custom LLM for seat booking
        return ChatOpenAI(base_url="http://localhost:8000/v1", model="mistral:7b")
    else:
        # Use OpenAI for other agents
        return ChatOpenAI(model="gpt-4")
```

### **Load Balancing Multiple Endpoints**

For production use, you can implement load balancing:

```python
import random

def get_llm(model: str = "gpt-4", agent_type: str = "default") -> BaseChatModel:
    if agent_type == "triage":
        endpoints = [
            "http://server1:11434/v1",
            "http://server2:11434/v1",
            "http://server3:11434/v1"
        ]
        selected_endpoint = random.choice(endpoints)
        return ChatOpenAI(base_url=selected_endpoint, model="llama2:7b")
    # ... rest of function
```

## ✅ **Success Indicators**

When your custom LLM is working correctly, you should see:

1. **Console Output**: `🎯 Using custom LLM for triage: http://your-endpoint`
2. **Proper Routing**: Triage agent correctly routes to specialist agents
3. **Response Quality**: Reasonable responses from your custom model
4. **Performance**: Acceptable response times

## 🚀 **Next Steps**

1. **Test with your endpoint**: Follow the testing steps above
2. **Monitor performance**: Check response times and accuracy
3. **Optimize prompts**: Adjust system prompts for your model
4. **Scale up**: Consider using multiple endpoints for load balancing

Your custom LLM is now integrated with the pure LangGraph implementation! 🎉
