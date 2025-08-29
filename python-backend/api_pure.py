"""
Pure LangGraph API - Complete replacement of OpenAI SDK API
Maintains exact same interface for seamless frontend integration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import uuid4
import time
import logging
import asyncio
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

# Import pure LangGraph implementation
from langgraph_pure import process_message_pure, process_message_sdk_style, create_initial_context, AirlineAgentContext
from langchain_core.messages import HumanMessage, AIMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Pure LangGraph Customer Service API")

# CORS configuration (matches original)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Models (EXACT SAME as original)
# =========================

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class MessageResponse(BaseModel):
    content: str
    agent: str

class AgentEvent(BaseModel):
    id: str
    type: str
    agent: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None

class GuardrailCheck(BaseModel):
    id: str
    name: str
    input: str
    reasoning: str
    passed: bool
    timestamp: float

class ChatResponse(BaseModel):
    conversation_id: str
    current_agent: str
    messages: List[MessageResponse]
    events: List[AgentEvent]
    context: Dict[str, Any]
    agents: List[Dict[str, Any]]
    guardrails: List[GuardrailCheck] = []
    routing_history: List[str] = []  # Add routing history for LangGraph UI

# =========================
# In-memory store (same as original)
# =========================

class ConversationStore:
    def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        pass

    def save(self, conversation_id: str, state: Dict[str, Any]):
        pass

class InMemoryConversationStore(ConversationStore):
    _conversations: Dict[str, Dict[str, Any]] = {}

    def get(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        return self._conversations.get(conversation_id)

    def save(self, conversation_id: str, state: Dict[str, Any]):
        self._conversations[conversation_id] = state

    def list(self) -> List[str]:
        return list(self._conversations.keys())

conversation_store = InMemoryConversationStore()

# =========================
# Helper functions for SDK-style conversation state
# =========================

def context_to_dict(context: AirlineAgentContext) -> dict:
    """Convert context object to dictionary for storage"""
    return {
        "passenger_name": context.passenger_name,
        "confirmation_number": context.confirmation_number,
        "seat_number": context.seat_number,
        "flight_number": context.flight_number,
        "account_number": context.account_number
    }

def dict_to_context(data: dict) -> AirlineAgentContext:
    """Convert dictionary back to context object"""
    context = AirlineAgentContext()
    context.passenger_name = data.get("passenger_name")
    context.confirmation_number = data.get("confirmation_number")
    context.seat_number = data.get("seat_number")
    context.flight_number = data.get("flight_number")
    context.account_number = data.get("account_number")
    return context

def result_to_langgraph_messages(stored_messages: List[dict]) -> List:
    """Convert stored message dictionaries back to LangChain message objects"""
    messages = []
    for msg in stored_messages:
        if msg.get("agent") == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    return messages

# =========================
# Agent definitions (matches original structure)
# =========================

def get_agents_info():
    """Get agent information - compatible with both old and new UI"""
    return [
        {
            "name": "triage",
            "description": "Routes customers to appropriate specialists",
            "tools": [],
            "handoffs": ["seat_booking", "flight_status", "cancellation", "faq"],  # Legacy compatibility
            "can_route_to": ["seat_booking", "flight_status", "cancellation", "faq"],  # LangGraph
            "input_guardrails": []  # Legacy compatibility
        },
        {
            "name": "seat_booking", 
            "description": "Handles seat changes and assignments", 
            "tools": ["update_seat_pure", "display_seat_map_pure"],
            "handoffs": ["triage"],  # Legacy compatibility
            "can_route_to": ["triage"],  # LangGraph
            "input_guardrails": []  # Legacy compatibility
        },
        {
            "name": "flight_status",
            "description": "Provides flight status information",
            "tools": ["flight_status_pure"], 
            "handoffs": ["triage"],  # Legacy compatibility
            "can_route_to": ["triage"],  # LangGraph
            "input_guardrails": []  # Legacy compatibility
        },
        {
            "name": "cancellation",
            "description": "Processes flight cancellations",
            "tools": ["cancel_flight_pure"],
            "handoffs": ["triage"],  # Legacy compatibility
            "can_route_to": ["triage"],  # LangGraph
            "input_guardrails": []  # Legacy compatibility
        },
        {
            "name": "faq",
            "description": "Answers general questions about policies and procedures", 
            "tools": ["faq_lookup_pure", "baggage_lookup_pure"],
            "handoffs": ["triage"],  # Legacy compatibility
            "can_route_to": ["triage"],  # LangGraph
            "input_guardrails": []  # Legacy compatibility
        }
    ]

# =========================
# Helper functions
# =========================

def context_to_dict(context: AirlineAgentContext) -> Dict[str, Any]:
    """Convert AirlineAgentContext to dictionary"""
    return {
        "passenger_name": context.passenger_name,
        "confirmation_number": context.confirmation_number,
        "seat_number": context.seat_number,
        "flight_number": context.flight_number,
        "account_number": context.account_number
    }

def dict_to_context(data: Dict[str, Any]) -> AirlineAgentContext:
    """Convert dictionary to AirlineAgentContext"""
    context = AirlineAgentContext()
    context.passenger_name = data.get("passenger_name")
    context.confirmation_number = data.get("confirmation_number") 
    context.seat_number = data.get("seat_number")
    context.flight_number = data.get("flight_number")
    context.account_number = data.get("account_number")
    return context

def langgraph_messages_to_api_format(
    langgraph_messages: List,
    langgraph_events: List[Dict[str, Any]],
    prev_count: int,
    routing_history: List[str] | None = None,
    current_agent: str = "unknown",
) -> tuple[List[MessageResponse], List[AgentEvent]]:
    """Convert LangGraph output to API format matching original OpenAI SDK structure"""
    messages = []
    events = []
    
    # Generate handoff events from routing history
    if routing_history and len(routing_history) > 1:
        for i in range(len(routing_history) - 1):
            source_agent = routing_history[i]
            target_agent = routing_history[i + 1]
            
            events.append(AgentEvent(
                id=uuid4().hex,
                type="handoff",
                agent=target_agent,
                content=f"Handoff from {source_agent} to {target_agent}",
                metadata={
                    "source_agent": source_agent,
                    "target_agent": target_agent
                },
                timestamp=time.time()
            ))
    
    # Process messages - convert LangGraph messages to MessageResponse format
    # Return ONLY the new assistant messages generated after the previous API call (prev_count)
    for idx, msg in enumerate(langgraph_messages):
        if idx < prev_count:
            # Skip messages that the frontend has already seen
            continue

        if hasattr(msg, "content") and hasattr(msg, "type"):
            if msg.type == "human":
                # User message → event only
                events.append(
                    AgentEvent(
                        id=uuid4().hex,
                        type="message",
                        agent="user",
                        content=msg.content,
                        timestamp=time.time(),
                    )
                )
            elif msg.type == "ai":
                agent_name = current_agent if current_agent != "unknown" else "assistant"
                messages.append(
                    MessageResponse(content=msg.content, agent=agent_name)
                )
                events.append(
                    AgentEvent(
                        id=uuid4().hex,
                        type="message",
                        agent=agent_name,
                        content=msg.content,
                        timestamp=time.time(),
                    )
                )
             
            elif msg.type == "tool":
                # Tool message → convert to event
                events.append(
                    AgentEvent(
                        id=uuid4().hex,
                        type="tool_call",
                        agent=current_agent,
                        content=f"Tool executed: {msg.content}",
                        metadata={"tool_response": msg.content},
                        timestamp=time.time(),
                    )
                )
    
    # Process LangGraph events - convert to API events
    for event in langgraph_events:
        timestamp = time.time()
        
        if event.get("type") == "agent_response":
            # Agent responded - this was already handled in messages
            pass
            
        elif event.get("type") == "tool_call":
            tool_name = event.get("tool", "")
            agent_name = event.get("agent", "unknown")
            
            # Add tool_call event
            events.append(AgentEvent(
                id=uuid4().hex,
                type="tool_call",
                agent=agent_name,
                content=tool_name,
                metadata={
                    "tool_name": tool_name,
                    "tool_args": event.get("args", {})
                },
                timestamp=timestamp
            ))
            
            # Add tool_output event (simulate tool execution result)
            events.append(AgentEvent(
                id=uuid4().hex,
                type="tool_output", 
                agent=agent_name,
                content=f"Tool {tool_name} executed",
                metadata={
                    "tool_name": tool_name,
                    "tool_result": "Tool executed successfully"
                },
                timestamp=timestamp
            ))
            
            # Special handling for display_seat_map (like original)
            if tool_name == "display_seat_map_pure":
                messages.append(MessageResponse(
                    content="DISPLAY_SEAT_MAP",
                    agent=agent_name
                ))
    
    return messages, events

# =========================
# Main Chat Endpoint
# =========================

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Pure LangGraph chat endpoint - maintains exact same interface as original
    """
    logger.info(f"Pure LangGraph Chat request: {req.message[:50]}...")
    
    # Initialize or retrieve conversation state
    is_new = not req.conversation_id or conversation_store.get(req.conversation_id) is None
    
    if is_new:
        conversation_id = uuid4().hex
        context = create_initial_context()
        previous_messages = []
        
        # Handle empty message (initialization)
        if req.message.strip() == "":
            state = {
                "context": context_to_dict(context),
                "messages": [],
                "current_agent": "triage",
                "events": []
            }
            conversation_store.save(conversation_id, state)
            
            return ChatResponse(
                conversation_id=conversation_id,
                current_agent="triage",
                messages=[],
                events=[],
                context=context_to_dict(context),
                agents=get_agents_info(),
                guardrails=[]
            )
    else:
        conversation_id = req.conversation_id
        stored_state = conversation_store.get(conversation_id)
        context = dict_to_context(stored_state["context"])
        previous_messages = stored_state.get("messages", [])
    
    try:
        # Process message through SDK-style LangGraph
        logger.info("Processing with SDK-style LangGraph...")
        
        # Prepare conversation state for SDK processing
        if is_new:
            conversation_state = None  # New conversation
        else:
            # Convert stored state to SDK format
            stored_state = conversation_store.get(conversation_id)
            conversation_state = {
                "messages": result_to_langgraph_messages(stored_state.get("messages", [])),
                "context": dict_to_context(stored_state["context"]),
                "current_agent": stored_state.get("current_agent", "triage"),
                "events": stored_state.get("events", []),
                "routing_history": stored_state.get("routing_history", []),
                # SDK-style fields:
                "last_active_agent": stored_state.get("last_active_agent", "triage"),
                "is_followup_message": stored_state.get("is_followup_message", False),
                "handoff_reason": stored_state.get("handoff_reason", "")
            }
        
        result = await process_message_sdk_style(req.message, conversation_state)
        
        # Convert LangGraph output to API format (matching original structure)
        messages, api_events = langgraph_messages_to_api_format(
            result["messages"], 
            result["events"], 
            len(previous_messages), # Pass the count of previous messages to the helper
            result.get("routing_history", []),
            result["current_agent"]
        )
        
        # Update conversation state with SDK fields
        # Persist full conversation history (all LangGraph messages) so prev_count is accurate
        serialized_messages = []
        for m in result["messages"]:
            role = "user" if getattr(m, "type", "") == "human" else "assistant"
            serialized_messages.append({"content": m.content, "agent": role})

        updated_state = {
            "context": context_to_dict(result["context"]),
            "messages": serialized_messages,
            "current_agent": result["current_agent"],
            "events": result["events"],
            "routing_history": result["routing_history"],
            # SDK-style persistence fields:
            "last_active_agent": result["last_active_agent"],
            "is_followup_message": result["is_followup_message"],
            "handoff_reason": result["handoff_reason"]
        }
        conversation_store.save(conversation_id, updated_state)
        
        logger.info(f"Pure LangGraph response: Agent={result['current_agent']}, Events={len(api_events)}")
        
        return ChatResponse(
            conversation_id=conversation_id,
            current_agent=result["current_agent"],
            messages=messages,
            events=api_events,
            context=context_to_dict(result["context"]),
            agents=get_agents_info(),
            guardrails=[],  # TODO: Add pure LangGraph guardrails
            routing_history=result.get("routing_history", [])  # Add routing history
        )
        
    except Exception as e:
        logger.error(f"Pure LangGraph error: {e}")
        raise e

# =========================
# Additional endpoints (matching original)
# =========================

@app.get("/conversations")
async def list_conversations():
    """List all conversation IDs"""
    return {"conversations": conversation_store.list()}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "implementation": "pure_langgraph"}

@app.get("/agents")
async def get_agents():
    """Get available agents"""
    return {"agents": get_agents_info()}

# =========================
# Development endpoints
# =========================

@app.post("/test")
async def test_endpoint(message: str = "Hello"):
    """Quick test endpoint for development"""
    try:
        result = await process_message_pure(message)
        return {
            "success": True,
            "current_agent": result["current_agent"],
            "routing_history": result["routing_history"],
            "events_count": len(result["events"]),
            "response_preview": result["messages"][-1].content[:100] if result["messages"] else "No response"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Different port to avoid conflicts
