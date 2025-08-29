"""
Pure LangGraph Implementation of Customer Service Agents Demo
Complete replacement of OpenAI SDK with native LangGraph
"""

from __future__ import annotations as _annotations

import random
import string
from typing import TypedDict, Annotated, Literal
from pydantic import BaseModel

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_core.language_models import BaseChatModel

# =========================
# CONTEXT (Same as original)
# =========================

class AirlineAgentContext(BaseModel):
    """Context for airline customer service agents."""
    passenger_name: str | None = None
    confirmation_number: str | None = None
    seat_number: str | None = None
    flight_number: str | None = None
    account_number: str | None = None

def create_initial_context() -> AirlineAgentContext:
    """Factory for a new AirlineAgentContext."""
    ctx = AirlineAgentContext()
    ctx.account_number = str(random.randint(10000000, 99999999))
    return ctx

# =========================
# PURE LANGGRAPH STATE
# =========================

class AirlineState(TypedDict):
    """Pure LangGraph state with SDK-style agent persistence"""
    messages: Annotated[list, add_messages]
    context: AirlineAgentContext
    current_agent: str
    next_agent: str
    events: list
    routing_history: list
    
    # NEW FIELDS for SDK-style agent persistence:
    last_active_agent: str      # Track which agent was last active
    is_followup_message: bool   # Is this a follow-up in existing conversation?
    handoff_reason: str         # Why agent handed off (for debugging)

# =========================
# PURE LANGGRAPH TOOLS
# =========================

@tool
def faq_lookup_pure(question: str) -> str:
    """Lookup frequently asked questions."""
    q = question.lower()
    if "bag" in q or "baggage" in q:
        return (
            "You are allowed to bring one bag on the plane. "
            "It must be under 50 pounds and 22 inches x 14 inches x 9 inches."
        )
    elif "seats" in q or "plane" in q:
        return (
            "There are 120 seats on the plane. "
            "There are 22 business class seats and 98 economy seats. "
            "Exit rows are rows 4 and 16. "
            "Rows 5-8 are Economy Plus, with extra legroom."
        )
    elif "wifi" in q:
        return "We have free wifi on the plane, join Airline-Wifi"
    return "I'm sorry, I don't know the answer to that question."

@tool
def update_seat_pure(confirmation_number: str, new_seat: str) -> str:
    """Update the seat for a given confirmation number."""
    return f"Updated seat to {new_seat} for confirmation number {confirmation_number}"

@tool
def flight_status_pure(flight_number: str) -> str:
    """Lookup the status for a flight."""
    return f"Flight {flight_number} is on time and scheduled to depart at gate A10."

@tool
def display_seat_map_pure() -> str:
    """Display an interactive seat map to the customer."""
    return "DISPLAY_SEAT_MAP"

@tool
def cancel_flight_pure(confirmation_number: str) -> str:
    """Cancel a flight booking."""
    return f"Flight with confirmation number {confirmation_number} has been successfully cancelled"

@tool
def baggage_lookup_pure(query: str) -> str:
    """Lookup baggage allowance and fees."""
    q = query.lower()
    if "fee" in q:
        return "Overweight bag fee is $75."
    if "allowance" in q:
        return "One carry-on and one checked bag (up to 50 lbs) are included."
    return "Please provide details about your baggage inquiry."

# =========================
# LLM CONFIGURATION
# =========================

def get_llm(model: str = "gpt-4") -> BaseChatModel:
    """Get configured LLM for agents."""
    return ChatOpenAI(model=model, temperature=0)

# =========================
# PURE LANGGRAPH AGENTS
# =========================

async def triage_agent_node(state: AirlineState) -> AirlineState:
    """Pure LangGraph triage agent - routes customers to specialists"""
    print("🎯 PURE TRIAGE: Processing with native LangGraph")
    
    llm = get_llm("gpt-4")
    
    system_prompt = """You are a helpful airline customer service triage agent.
    
    Analyze the customer's request and determine the appropriate department by including one of these EXACT routing codes in your response:
    - ROUTE_TO_SEAT_BOOKING: For seat changes, seat selection, seat upgrades
    - ROUTE_TO_FLIGHT_STATUS: For flight status, gate information, delays
    - ROUTE_TO_CANCELLATION: For flight cancellations, refunds
    - ROUTE_TO_FAQ: For general questions about policies, baggage, amenities
    
    Always provide a helpful response to the customer AND include the appropriate routing code.
    
    Customer context:
    - Account: {account_number}
    - Confirmation: {confirmation_number}
    - Flight: {flight_number}
    """.format(
        account_number=state["context"].account_number or "Not provided",
        confirmation_number=state["context"].confirmation_number or "Not provided", 
        flight_number=state["context"].flight_number or "Not provided"
    )
    
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(state["messages"])
    
    response = await llm.ainvoke(messages)
    
    # Determine routing from LLM response
    next_agent = "end"
    if "ROUTE_TO_SEAT_BOOKING" in response.content:
        next_agent = "seat_booking"
    elif "ROUTE_TO_FLIGHT_STATUS" in response.content:
        next_agent = "flight_status"
    elif "ROUTE_TO_CANCELLATION" in response.content:
        next_agent = "cancellation"
    elif "ROUTE_TO_FAQ" in response.content:
        next_agent = "faq"
    
    print(f"🎯 Triage decision: {next_agent}")
    
    # Duplicate the latest human message so the downstream specialist sees it as the most recent user input
    duplicated_human = None
    for m in reversed(state["messages"]):
        if isinstance(m, HumanMessage):
            duplicated_human = m
            break

    new_messages = state["messages"] + [response]
    if duplicated_human:
        new_messages.append(duplicated_human)

    return {
        **state,
        "messages": new_messages,
        "current_agent": "triage",
        "next_agent": next_agent,
        "events": state["events"] + [{"type": "agent_response", "agent": "triage"}],
        "routing_history": state["routing_history"] + ["triage"]
    }

async def seat_booking_agent_node(state: AirlineState) -> AirlineState:
    """Pure LangGraph seat booking agent"""
    print("💺 PURE SEAT BOOKING: Processing with native LangGraph")
    
    # Handoff hook logic - set confirmation and flight if needed
    if not state["context"].confirmation_number:
        state["context"].confirmation_number = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    if not state["context"].flight_number:
        state["context"].flight_number = f"FLT-{random.randint(100, 999)}"
    
    llm = get_llm("gpt-4")
    
    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools([update_seat_pure, display_seat_map_pure])
    
    system_prompt = f"""You are a seat booking specialist for the airline.
    
    Customer Information:
    - Confirmation Number: {state["context"].confirmation_number}
    - Flight Number: {state["context"].flight_number}
    - Current Seat: {state["context"].seat_number or "Not assigned"}
    
    CONTEXT AWARENESS (IMPORTANT):
    You may be receiving this conversation after a handoff from another agent.
    Look at the MOST RECENT user message to understand what the customer is asking about. If the user asks a specific seat question, answer it directly, without the need to ask them to repeat their question.
    
    SELF-ASSESSMENT RULES (CRITICAL):
    ✅ I CAN HANDLE:
    - Seat changes, selections, preferences ("I want seat 21D", "window seat please")
    - Seat map displays ("show me available seats")
    - Current seat assignment questions ("what's my current seat?")
    - Seat upgrades and seat-related requests
    
    ❌ I CANNOT HANDLE (say HANDOFF_TO_TRIAGE):
    - Flight status, delays, gates, departure times
    - Flight cancellations or refunds
    - General airline policies, baggage questions
    - Account modifications (except seats)
    - Any non-seat-related requests
    
    If I cannot handle a request, I must respond with:
    "I specialize in seat booking only. Let me transfer you to the right specialist for [their request]. HANDOFF_TO_TRIAGE"
    
    Your responsibilities:
    1. Look at the most recent user message and help with seat requests directly
    2. For general requests like "need help with seat booking", ask what specifically they'd like to do:
       - Change their current seat
       - View available seats
       - Check their current seat assignment
    3. Show seat maps when requested using display_seat_map_pure()
    4. Update seat assignments using the update_seat_pure tool
    5. Self-assess each request and handoff if outside my expertise
    6. NEVER ask the user to repeat their question - you can see the conversation history
    7. ALWAYS provide a response - never stay silent
    
    Use the available tools when appropriate:
    - display_seat_map_pure(): Show interactive seat selection
    - update_seat_pure(confirmation_number, new_seat): Update seat assignment
    """
    
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(state["messages"])
    
    response = await llm_with_tools.ainvoke(messages)
    
    # SDK-style self-assessment routing
    if "HANDOFF_TO_TRIAGE" in response.content:
        print("💺 SEAT BOOKING: Self-assessment → Handing off to triage")
        next_agent = "triage"
        handoff_reason = "cannot_handle_request"
    else:
        print("💺 SEAT BOOKING: Self-assessment → Handling request, staying active")
        next_agent = "end"  # End this workflow run, but agent stays active for next message
        handoff_reason = ""
    
    # Handle tool calls and execute them
    messages_to_add = [response]
    events = []
    
    if response.tool_calls:
        from langchain_core.messages import ToolMessage
        
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Execute the tool
            try:
                if tool_name == "update_seat_pure":
                    result = update_seat_pure.invoke(tool_args)
                elif tool_name == "display_seat_map_pure":
                    result = display_seat_map_pure.invoke(tool_args)
                else:
                    result = f"Unknown tool: {tool_name}"
                
                # Add tool response message
                tool_message = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                )
                messages_to_add.append(tool_message)
                
                events.append({
                    "type": "tool_call",
                    "agent": "seat_booking", 
                    "tool": tool_name,
                    "args": tool_args,
                    "result": result
                })
                
            except Exception as e:
                # Handle tool execution errors
                error_message = ToolMessage(
                    content=f"Tool error: {str(e)}",
                    tool_call_id=tool_call["id"]
                )
                messages_to_add.append(error_message)
                
                events.append({
                    "type": "tool_error",
                    "agent": "seat_booking",
                    "tool": tool_name,
                    "error": str(e)
                })
    
    return {
        **state,
        "messages": state["messages"] + messages_to_add,
        "current_agent": "seat_booking",
        "next_agent": next_agent,
        "last_active_agent": "seat_booking",  # Track this agent as last active
        "handoff_reason": handoff_reason,
        "events": state["events"] + [{"type": "agent_response", "agent": "seat_booking"}] + events,
        "routing_history": state["routing_history"] + ["seat_booking"]
    }

async def flight_status_agent_node(state: AirlineState) -> AirlineState:
    """Pure LangGraph flight status agent"""
    print("✈️ PURE FLIGHT STATUS: Processing with native LangGraph")
    
    llm = get_llm("gpt-4")
    llm_with_tools = llm.bind_tools([flight_status_pure])
    
    system_prompt = f"""You are a flight status specialist for the airline.
    
    Customer Information:
    - Confirmation Number: {state["context"].confirmation_number or "Please ask customer"}
    - Flight Number: {state["context"].flight_number or "Please ask customer"}
    
    CONTEXT AWARENESS (IMPORTANT):
    You may be receiving this conversation after a handoff from another agent.
    Look at the MOST RECENT user message to understand what the customer is asking about.
    If the user asks a specific flight status question, answer it directly.

    SELF-ASSESSMENT RULES (CRITICAL):
    ✅ I CAN HANDLE:
    - Flight status inquiries ("Is my flight on time?", "What's the status of flight 123?")
    - Departure and arrival times ("When does my flight leave?")
    - Gate information and delays
    - Flight tracking and updates
    
    ❌ I CANNOT HANDLE (say HANDOFF_TO_TRIAGE):
    - Seat changes or seat-related requests
    - Flight cancellations or refunds
    - General airline policies, baggage questions
    - Booking modifications
    - Any non-flight-status requests
    
    If I cannot handle a request, I must respond with:
    "I specialize in flight status only. Let me transfer you to the right specialist for [their request]. HANDOFF_TO_TRIAGE"
    
    Your responsibilities:
    1. Look at the most recent user message and provide flight status information directly
    2. For general requests like "check flight status", proactively ask for flight number if needed
    3. Use flight_status_pure tool to get current information
    4. Self-assess each request and handoff if outside my expertise
    5. NEVER ask the user to repeat their question - you can see the conversation history
    6. ALWAYS provide a response - never stay silent
    """
    
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(state["messages"])
    
    response = await llm_with_tools.ainvoke(messages)
    
    # SDK-style self-assessment routing
    if "HANDOFF_TO_TRIAGE" in response.content:
        print("✈️ FLIGHT STATUS: Self-assessment → Handing off to triage")
        next_agent = "triage"
        handoff_reason = "cannot_handle_request"
    else:
        print("✈️ FLIGHT STATUS: Self-assessment → Handling request, staying active")
        next_agent = "end"  # End this workflow run, but agent stays active for next message
        handoff_reason = ""
    
    # Handle tool calls and execute them
    messages_to_add = [response]
    events = []
    
    if response.tool_calls:
        from langchain_core.messages import ToolMessage
        
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Execute the tool
            try:
                if tool_name == "flight_status_pure":
                    result = flight_status_pure.invoke(tool_args)
                else:
                    result = f"Unknown tool: {tool_name}"
                
                # Add tool response message
                tool_message = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                )
                messages_to_add.append(tool_message)
                
                events.append({
                    "type": "tool_call",
                    "agent": "flight_status", 
                    "tool": tool_name,
                    "args": tool_args,
                    "result": result
                })
                
            except Exception as e:
                # Handle tool execution errors
                error_message = ToolMessage(
                    content=f"Tool error: {str(e)}",
                    tool_call_id=tool_call["id"]
                )
                messages_to_add.append(error_message)
                
                events.append({
                    "type": "tool_error",
                    "agent": "flight_status",
                    "tool": tool_name,
                    "error": str(e)
                })
    
    return {
        **state,
        "messages": state["messages"] + messages_to_add,
        "current_agent": "flight_status", 
        "next_agent": next_agent,
        "last_active_agent": "flight_status",  # Track this agent as last active
        "handoff_reason": handoff_reason,
        "events": state["events"] + [{"type": "agent_response", "agent": "flight_status"}] + events,
        "routing_history": state["routing_history"] + ["flight_status"]
    }

async def cancellation_agent_node(state: AirlineState) -> AirlineState:
    """Pure LangGraph cancellation agent"""
    print("❌ PURE CANCELLATION: Processing with native LangGraph")
    
    # Handoff hook - set confirmation and flight if needed
    if not state["context"].confirmation_number:
        state["context"].confirmation_number = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    if not state["context"].flight_number:
        state["context"].flight_number = f"FLT-{random.randint(100, 999)}"
    
    llm = get_llm("gpt-4")
    llm_with_tools = llm.bind_tools([cancel_flight_pure])
    
    system_prompt = f"""You are a cancellation specialist for the airline.
    
    Customer Information:
    - Confirmation Number: {state["context"].confirmation_number}
    - Flight Number: {state["context"].flight_number}
    
    CONTEXT AWARENESS (IMPORTANT):
    You may be receiving this conversation after a handoff from another agent.
    Look at the MOST RECENT user message to understand what the customer is asking about.
    If the user asks a specific cancellation question, answer it directly.
    
    SELF-ASSESSMENT RULES (CRITICAL):
    ✅ I CAN HANDLE:
    - Flight cancellations and refunds ("Cancel my flight", "I need a refund")
    - Cancellation policies and fees ("What's the cancellation fee?")
    - Rebooking after cancellation
    - Cancellation-related questions
    
    ❌ I CANNOT HANDLE (say HANDOFF_TO_TRIAGE):
    - Seat changes or seat-related requests
    - Flight status inquiries
    - General airline policies (unless cancellation-related)
    - New bookings (only cancellations)
    - Any non-cancellation requests
    
    If I cannot handle a request, I must respond with:
    "I specialize in cancellations only. Let me transfer you to the right specialist for [their request]. HANDOFF_TO_TRIAGE"
    
    Your responsibilities:
    1. Look at the most recent user message and help with cancellation requests directly
    2. For general requests like "cancel flight", proactively ask for confirmation details if needed
    3. Confirm booking details before cancellation
    4. Use cancel_flight_pure tool to process cancellations
    5. Self-assess each request and handoff if outside my expertise
    6. NEVER ask the user to repeat their question - you can see the conversation history
    7. ALWAYS provide a response - never stay silent
    """
    
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(state["messages"])
    
    response = await llm_with_tools.ainvoke(messages)
    
    # SDK-style self-assessment routing
    if "HANDOFF_TO_TRIAGE" in response.content:
        print("❌ CANCELLATION: Self-assessment → Handing off to triage")
        next_agent = "triage"
        handoff_reason = "cannot_handle_request"
    else:
        print("❌ CANCELLATION: Self-assessment → Handling request, staying active")
        next_agent = "end"  # End this workflow run, but agent stays active for next message
        handoff_reason = ""
    
    # Handle tool calls and execute them
    messages_to_add = [response]
    events = []
    
    if response.tool_calls:
        from langchain_core.messages import ToolMessage
        
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Execute the tool
            try:
                if tool_name == "cancel_flight_pure":
                    result = cancel_flight_pure.invoke(tool_args)
                else:
                    result = f"Unknown tool: {tool_name}"
                
                # Add tool response message
                tool_message = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                )
                messages_to_add.append(tool_message)
                
                events.append({
                    "type": "tool_call",
                    "agent": "cancellation", 
                    "tool": tool_name,
                    "args": tool_args,
                    "result": result
                })
                
            except Exception as e:
                # Handle tool execution errors
                error_message = ToolMessage(
                    content=f"Tool error: {str(e)}",
                    tool_call_id=tool_call["id"]
                )
                messages_to_add.append(error_message)
                
                events.append({
                    "type": "tool_error",
                    "agent": "cancellation",
                    "tool": tool_name,
                    "error": str(e)
                })
    
    return {
        **state,
        "messages": state["messages"] + messages_to_add,
        "current_agent": "cancellation",
        "next_agent": next_agent,
        "last_active_agent": "cancellation",  # Track this agent as last active
        "handoff_reason": handoff_reason,
        "events": state["events"] + [{"type": "agent_response", "agent": "cancellation"}] + events,
        "routing_history": state["routing_history"] + ["cancellation"]
    }

async def faq_agent_node(state: AirlineState) -> AirlineState:
    """Pure LangGraph FAQ agent"""
    print("❓ PURE FAQ: Processing with native LangGraph")
    
    llm = get_llm("gpt-4")
    llm_with_tools = llm.bind_tools([faq_lookup_pure, baggage_lookup_pure])
    
    system_prompt = """You are an FAQ specialist for the airline.
    
    CONTEXT AWARENESS (IMPORTANT):
    You may be receiving this conversation after a handoff from another agent.
    Look at the MOST RECENT user message to understand what the customer is asking about.
    If the user asks a specific FAQ question, answer it directly.
    
    SELF-ASSESSMENT RULES (CRITICAL):
    ✅ I CAN HANDLE:
    - General airline policies and procedures
    - Baggage questions, fees, and allowances
    - General information about amenities, services
    - Frequently asked questions
    - Any general inquiries not handled by specialists
    
    ❌ I CANNOT HANDLE (say HANDOFF_TO_TRIAGE):
    - Specific seat changes (route to seat booking specialist)
    - Specific flight status inquiries (route to flight status specialist)
    - Specific cancellations (route to cancellation specialist)
    - Account modifications or booking changes
    
    If I cannot handle a request, I must respond with:
    "For specific [seat/flight/cancellation] requests, let me transfer you to our specialist team. HANDOFF_TO_TRIAGE"
    
    Your responsibilities:
    1. Look at the most recent user message and answer it directly
    2. Use faq_lookup_pure for general questions
    3. Use baggage_lookup_pure for baggage-related questions
    4. Self-assess each request and handoff specific requests to specialists
    5. NEVER ask the user to repeat their question - you can see the conversation history
    """
    
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(state["messages"])
    
    response = await llm_with_tools.ainvoke(messages)
    
    # SDK-style self-assessment routing
    if "HANDOFF_TO_TRIAGE" in response.content:
        print("❓ FAQ: Self-assessment → Handing off to triage")
        next_agent = "triage"
        handoff_reason = "cannot_handle_request"
    else:
        print("❓ FAQ: Self-assessment → Handling request, staying active")
        next_agent = "end"  # End this workflow run, but agent stays active for next message
        handoff_reason = ""
    
    # Handle tool calls and execute them
    messages_to_add = [response]
    events = []
    
    if response.tool_calls:
        from langchain_core.messages import ToolMessage
        
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Execute the tool
            try:
                if tool_name == "faq_lookup_pure":
                    result = faq_lookup_pure.invoke(tool_args)
                elif tool_name == "baggage_lookup_pure":
                    result = baggage_lookup_pure.invoke(tool_args)
                else:
                    result = f"Unknown tool: {tool_name}"
                
                # Add tool response message
                tool_message = ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                )
                messages_to_add.append(tool_message)
                
                events.append({
                    "type": "tool_call",
                    "agent": "faq", 
                    "tool": tool_name,
                    "args": tool_args,
                    "result": result
                })
                
            except Exception as e:
                # Handle tool execution errors
                error_message = ToolMessage(
                    content=f"Tool error: {str(e)}",
                    tool_call_id=tool_call["id"]
                )
                messages_to_add.append(error_message)
                
                events.append({
                    "type": "tool_error",
                    "agent": "faq",
                    "tool": tool_name,
                    "error": str(e)
                })
    
    return {
        **state,
        "messages": state["messages"] + messages_to_add,
        "current_agent": "faq",
        "next_agent": next_agent,
        "last_active_agent": "faq",  # Track this agent as last active
        "handoff_reason": handoff_reason,
        "events": state["events"] + [{"type": "agent_response", "agent": "faq"}] + events,
        "routing_history": state["routing_history"] + ["faq"]
    }

# =========================
# PURE LANGGRAPH WORKFLOW
# =========================

async def smart_entry_node(state: AirlineState) -> AirlineState:
    """Smart entry node that routes to the correct starting agent"""
    target_agent = state.get("next_agent", "triage")
    print(f"🎯 SMART ENTRY: Routing to {target_agent}")
    
    # Just pass through to the target agent by setting next_agent
    return {
        **state,
        "next_agent": target_agent
    }

def create_pure_workflow():
    """Create pure LangGraph workflow with dynamic entry points"""
    workflow = StateGraph(AirlineState)
    
    # Add smart entry node for dynamic routing
    workflow.add_node("smart_entry", smart_entry_node)
    
    # Add all pure LangGraph nodes
    workflow.add_node("triage", triage_agent_node)
    workflow.add_node("seat_booking", seat_booking_agent_node)
    workflow.add_node("flight_status", flight_status_agent_node)
    workflow.add_node("cancellation", cancellation_agent_node)
    workflow.add_node("faq", faq_agent_node)
    
    # Set entry point to smart entry
    workflow.set_entry_point("smart_entry")
    
    # Smart entry routes to any agent
    workflow.add_conditional_edges(
        "smart_entry",
        lambda state: state["next_agent"],
        {
            "triage": "triage",
            "seat_booking": "seat_booking",
            "flight_status": "flight_status", 
            "cancellation": "cancellation",
            "faq": "faq",
            "end": END
        }
    )
    
    # Pure LangGraph routing
    workflow.add_conditional_edges(
        "triage",
        lambda state: state["next_agent"],
        {
            "seat_booking": "seat_booking",
            "flight_status": "flight_status", 
            "cancellation": "cancellation",
            "faq": "faq",
            "end": END
        }
    )
    
    # SDK-style specialist routing (agents can stay active for follow-ups)
    for specialist in ["seat_booking", "flight_status", "cancellation", "faq"]:
        workflow.add_conditional_edges(
            specialist,
            lambda state: state["next_agent"],
            {
                "seat_booking": "seat_booking",     # Can stay active or route to seat booking
                "flight_status": "flight_status",   # Can stay active or route to flight status  
                "cancellation": "cancellation",     # Can stay active or route to cancellation
                "faq": "faq",                       # Can stay active or route to faq
                "triage": "triage",                 # Can handoff back to triage
                "end": END                          # Can end conversation
            }
        )
    
    return workflow.compile()

# =========================
# SDK-STYLE ENTRY POINT LOGIC
# =========================

def determine_entry_point(state: AirlineState) -> str:
    """Determine where to start: continue with agent or start fresh with triage"""
    
    # New conversation always starts with triage
    if len(state.get("messages", [])) <= 1:
        print("🎯 ENTRY POINT: New conversation → Starting with triage")
        return "triage"
    
    # If we have a handoff request, go to triage
    if state.get("next_agent") == "triage" or state.get("handoff_reason"):
        print("🎯 ENTRY POINT: Handoff detected → Starting with triage")
        return "triage"
    
    # If we have an active agent and this seems like a follow-up
    last_active = state.get("last_active_agent")
    if last_active and last_active != "triage" and state.get("is_followup_message", False):
        print(f"🎯 ENTRY POINT: Follow-up detected → Starting with {last_active} (SDK pattern)")
        return last_active
    
    # Default to triage for safety
    print("🎯 ENTRY POINT: Default safety → Starting with triage")
    return "triage"

# =========================
# MAIN INTERFACE
# =========================

async def process_message_sdk_style(message: str, conversation_state: dict = None) -> dict:
    """SDK-style message processing with agent persistence and dynamic entry points"""
    
    if conversation_state is None:
        # New conversation
        context = create_initial_context()
        initial_state = AirlineState(
            messages=[HumanMessage(content=message)],
            context=context,
            current_agent="triage",
            next_agent="triage",
            events=[],
            routing_history=[],
            
            # SDK-style fields for new conversation:
            last_active_agent="triage",     # Start with triage as active agent
            is_followup_message=False,      # First message is never a follow-up
            handoff_reason=""               # No handoff reason initially
        )
    else:
        # Continuing conversation
        context = conversation_state.get("context", create_initial_context())
        previous_messages = conversation_state.get("messages", [])
        
        initial_state = AirlineState(
            messages=previous_messages + [HumanMessage(content=message)],
            context=context,
            current_agent=conversation_state.get("current_agent", "triage"),
            next_agent=conversation_state.get("last_active_agent", "triage"),
            events=conversation_state.get("events", []),
            routing_history=conversation_state.get("routing_history", []),
            
            # SDK-style fields for follow-up:
            last_active_agent=conversation_state.get("last_active_agent", "triage"),
            is_followup_message=True,       # This is a follow-up message
            handoff_reason=conversation_state.get("handoff_reason", "")
        )
    
    # Determine where to start (CRITICAL for SDK pattern)
    entry_point = determine_entry_point(initial_state)
    
    # Override entry point in state if needed
    if entry_point != "triage":
        initial_state["current_agent"] = entry_point
        initial_state["next_agent"] = entry_point
        print(f"🔄 SDK ROUTING: Skipping triage, going directly to {entry_point}")
    
    # Run workflow starting from determined entry point
    workflow = create_pure_workflow()
    final_state = await workflow.ainvoke(initial_state)
    
    return {
        "messages": final_state["messages"],
        "context": final_state["context"],
        "current_agent": final_state["current_agent"],
        "events": final_state["events"],
        "routing_history": final_state["routing_history"],
        
        # SDK-style agent persistence data:
        "last_active_agent": final_state["last_active_agent"],
        "is_followup_message": final_state["is_followup_message"],
        "handoff_reason": final_state["handoff_reason"]
    }

async def process_message_pure(message: str, context: AirlineAgentContext = None) -> dict:
    """Pure LangGraph message processing - no OpenAI SDK dependencies"""
    
    if context is None:
        context = create_initial_context()
    
    # Create initial state
    initial_state = AirlineState(
        messages=[HumanMessage(content=message)],
        context=context,
        current_agent="triage",
        next_agent="triage",
        events=[],
        routing_history=[],
        
        # SDK-style agent persistence fields:
        last_active_agent="triage",     # Start with triage as active agent
        is_followup_message=False,      # First message is never a follow-up
        handoff_reason=""               # No handoff reason initially
    )
    
    # Run pure LangGraph workflow
    workflow = create_pure_workflow()
    final_state = await workflow.ainvoke(initial_state)
    
    return {
        "messages": final_state["messages"],
        "context": final_state["context"],
        "current_agent": final_state["current_agent"],
        "events": final_state["events"],
        "routing_history": final_state["routing_history"],
        
        # SDK-style agent persistence data:
        "last_active_agent": final_state["last_active_agent"],
        "is_followup_message": final_state["is_followup_message"],
        "handoff_reason": final_state["handoff_reason"]
    }

# =========================
# TEST FUNCTION
# =========================

async def test_pure_implementation():
    """Test pure LangGraph implementation"""
    print("🧪 Testing Pure LangGraph Implementation...\n")
    
    test_cases = [
        "Can I change my seat?",
        "What's my flight status?",
        "I want to cancel my flight",
        "How many seats are on the plane?"
    ]
    
    for test_msg in test_cases:
        print(f"📝 Testing: '{test_msg}'")
        try:
            result = await process_message_pure(test_msg)
            print(f"   ✅ Route: {' → '.join(result['routing_history'])}")
            print(f"   ✅ Events: {len(result['events'])}")
            print(f"   ✅ Final agent: {result['current_agent']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_pure_implementation())
