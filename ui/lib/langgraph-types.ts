/**
 * Pure LangGraph Types - Enhanced for workflow state
 */

export interface LangGraphAgent {
  name: string
  description: string
  tools: string[]
  // Dynamic routing instead of static handoffs
  can_route_to?: string[]  // Possible next agents (optional)
}

export interface LangGraphState {
  current_agent: string
  routing_history: string[]
  context: Record<string, any>
  workflow_complete?: boolean
}

export interface LangGraphEvent {
  id: string
  type: "agent_response" | "tool_call" | "routing_decision" | "state_change"
  agent: string
  content: string
  timestamp: number
  metadata?: {
    routing_reason?: string
    tool_name?: string
    tool_args?: Record<string, any>
    state_changes?: Record<string, any>
  }
}

export interface LangGraphMessage {
  id: string
  content: string
  role: "user" | "assistant"
  agent: string
  timestamp: Date
}

// Enhanced conversation response with LangGraph data
export interface LangGraphChatResponse {
  conversation_id: string
  current_agent: string
  routing_history: string[]
  messages: LangGraphMessage[]
  events: LangGraphEvent[]
  context: Record<string, any>
  agents: LangGraphAgent[]
  workflow_state: LangGraphState
}
