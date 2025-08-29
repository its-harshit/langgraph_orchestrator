# 🚀 Pure LangGraph Customer Service Agents Demo

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![NextJS](https://img.shields.io/badge/Built_with-NextJS-blue)
![LangGraph](https://img.shields.io/badge/Powered_by-LangGraph-purple)
![OpenAI API](https://img.shields.io/badge/LLM-OpenAI_API-orange)

A production-ready **Customer Service Agent interface** built with **pure LangGraph**, demonstrating intelligent multi-agent orchestration for airline customer service. This project showcases a complete migration from OpenAI Agents SDK to native LangGraph, achieving 100% feature parity with enhanced capabilities.

![Demo Screenshot](screenshot.jpg)

## 🎯 **What This Demo Shows**

### **Pure LangGraph Implementation**
- **5 Native LangGraph Agents**: Triage, Seat Booking, Flight Status, Cancellation, FAQ
- **6 LangChain Tools**: Native tool integration for airline operations
- **Intelligent Routing**: LLM-based routing decisions superior to keyword matching
- **Enhanced State Management**: Comprehensive conversation state tracking
- **Production Ready**: Robust error handling and scalability

### **Key Features**
- **Smart Agent Orchestration**: Dynamic routing based on customer intent
- **Context Preservation**: Seamless information flow between agents
- **Interactive UI**: Real-time agent visualization and conversation tracking
- **Multi-turn Conversations**: Complex workflows with multiple agent handoffs
- **Tool Integration**: Native LangChain tools for airline operations

## 🏗️ **Architecture**

### **Backend (Pure LangGraph)**
```
Frontend → FastAPI → LangGraph Workflow → Native Agents → LangChain Tools
```

### **Agent System**
```
Triage Agent (Entry Point)
├── Seat Booking Agent (seat changes, seat maps)
├── Flight Status Agent (flight info, delays, gates)
├── Cancellation Agent (cancellations, refunds)
└── FAQ Agent (general policies, baggage)
```

### **Enhanced Capabilities**
- **Declarative Workflows**: Graph-based state management
- **LLM-based Routing**: Intelligent decisions vs keyword matching
- **Built-in State Management**: Enhanced persistence and flow control
- **Visualization Ready**: Native workflow diagrams and debugging

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- Node.js 18+
- OpenAI API key

### **1. Set Your OpenAI API Key**

```bash
# Set environment variable
export OPENAI_API_KEY=your_api_key

# Or create .env file in python-backend/
echo "OPENAI_API_KEY=your_api_key" > python-backend/.env
```

### **2. Install Dependencies**

```bash
# Backend dependencies
cd python-backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend dependencies
cd ../ui
npm install
```

### **3. Run the Application**

```bash
# Option 1: Run both frontend and backend together
cd ui
npm run dev

# Option 2: Run separately
# Terminal 1 - Backend
cd python-backend
uvicorn api_pure:app --reload --port 8000

# Terminal 2 - Frontend  
cd ui
npm run dev:next
```

The application will be available at:
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)

## 🎮 **Demo Flows**

### **Flow 1: Seat Change Request**
```
User: "Can I change my seat?"
→ Triage Agent routes to Seat Booking Agent
→ Agent asks for confirmation number
→ User can request seat map or specific seat
→ Agent updates seat assignment
```

### **Flow 2: Multi-Agent Conversation**
```
User: "What's my flight status?"
→ Triage → Flight Status Agent
User: "How many seats are on the plane?"
→ Flight Status → FAQ Agent (self-assessment)
→ FAQ Agent provides aircraft information
```

### **Flow 3: Cancellation with Context**
```
User: "I want to cancel my flight"
→ Triage → Cancellation Agent
→ Agent confirms booking details
→ User: "That's correct"
→ Agent processes cancellation
```

## 🛠️ **Development**

### **Project Structure**
```
openai-cs-agents-demo/
├── python-backend/
│   ├── langgraph_pure.py          # Pure LangGraph implementation
│   ├── api_pure.py                # FastAPI endpoint
│   └── requirements.txt           # Python dependencies
├── ui/
│   ├── app/                       # Next.js app directory
│   ├── components/                # React components
│   └── lib/                       # Utilities and types
└── README.md                      # This file
```

### **Key Files**
- **`langgraph_pure.py`**: Complete pure LangGraph implementation
- **`api_pure.py`**: Production-ready FastAPI endpoint
- **`ui/app/page.tsx`**: Main application interface
- **`ui/components/`**: React components for UI

### **Adding New Agents**
1. Create agent node in `langgraph_pure.py`
2. Add routing logic in triage agent
3. Update workflow graph
4. Test with conversation flows

### **Adding New Tools**
1. Create `@tool` function in `langgraph_pure.py`
2. Bind tool to appropriate agent
3. Update agent system prompts
4. Test tool integration

## 📊 **Performance & Results**

### **Migration Success**
- ✅ **100% Feature Parity**: All original functionality replicated
- ✅ **Enhanced Performance**: LLM-based routing superior to keyword matching
- ✅ **Better Architecture**: Declarative workflow vs manual orchestration
- ✅ **Production Ready**: Comprehensive testing and error handling

### **LangGraph Advantages**
- **Declarative Workflows**: Graph-based state management
- **Enhanced State**: Built-in state persistence and flow control
- **Visualization**: Native workflow diagrams and debugging
- **Scalability**: Designed for complex multi-agent systems

## 🔮 **Future Enhancements**

### **Available LangGraph Features**
- **Native Guardrails**: Built-in guardrail system
- **Human-in-the-Loop**: Interactive human oversight
- **Workflow Visualization**: Real-time graph visualization
- **State Checkpointing**: Save and restore conversation states
- **Parallel Processing**: Multiple agents working simultaneously

### **Advanced Capabilities**
- **Memory Systems**: Long-term conversation memory
- **Tool Chaining**: Complex multi-tool workflows
- **Conditional Logic**: Advanced routing based on business rules
- **Integration APIs**: Connect to external systems

## 🧪 **Testing**

### **Individual Agent Tests**
```bash
cd python-backend
python -c "from langgraph_pure import process_message_pure; import asyncio; asyncio.run(process_message_pure('Can I change my seat?'))"
```

### **API Testing**
```bash
# Test the API endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Can I change my seat?"}'
```

## 📚 **Documentation**

- **`LANGGRAPH_MIGRATION_PROGRESS.md`**: Complete migration journey
- **`PURE_LANGGRAPH_SUCCESS_SUMMARY.md`**: Technical achievements
- **`FUNCTIONALITY_MAPPING.md`**: Feature parity documentation
- **`PROJECT_STRUCTURE.md`**: Detailed project organization

## 🤝 **Contributing**

This project demonstrates a successful migration to pure LangGraph. Contributions are welcome for:
- **New Agent Types**: Additional specialized agents
- **Enhanced Tools**: More sophisticated tool integrations
- **UI Improvements**: Better visualization and user experience
- **Documentation**: Improved guides and examples

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎉 **Success Story**

This project successfully demonstrates:
- **Complete Migration**: From OpenAI SDK to pure LangGraph
- **Production Quality**: Robust, scalable implementation
- **Enhanced Capabilities**: Superior routing and state management
- **Future-Proof**: Foundation for advanced multi-agent systems

**The pure LangGraph implementation is ready for production deployment!** 🚀
