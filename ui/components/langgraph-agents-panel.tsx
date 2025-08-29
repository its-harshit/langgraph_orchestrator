"use client";

import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bot, ArrowRight, Zap } from "lucide-react";
import { PanelSection } from "./panel-section";
import type { LangGraphAgent } from "@/lib/langgraph-types";

interface LangGraphAgentsPanelProps {
  agents: LangGraphAgent[];
  currentAgent: string;
  routingHistory: string[];
}

export function LangGraphAgentsPanel({ 
  agents, 
  currentAgent, 
  routingHistory 
}: LangGraphAgentsPanelProps) {
  
  // Determine which agents are accessible based on routing history
  const getAgentStatus = (agentName: string) => {
    if (agentName === currentAgent) {
      return { active: true, accessible: true, visited: true };
    }
    
    const visited = routingHistory.includes(agentName);
    // In LangGraph, agents can route dynamically - show as accessible if visited or is triage
    const accessible = visited || agentName === "triage" || routingHistory.length === 0;
    
    return { active: false, accessible, visited };
  };

  return (
    <PanelSection
      title="Agent Workflow"
      icon={<Bot className="h-4 w-4 text-blue-600" />}
    >
      {/* Routing History Visualization */}
      {routingHistory.length > 1 && (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-100">
          <div className="text-xs font-medium text-blue-700 mb-2">Routing Path:</div>
          <div className="flex items-center space-x-2 text-xs">
            {routingHistory.map((agent, index) => (
              <div key={index} className="flex items-center">
                <span className={`px-2 py-1 rounded text-xs ${
                  agent === currentAgent 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-blue-200 text-blue-700'
                }`}>
                  {agent}
                </span>
                {index < routingHistory.length - 1 && (
                  <ArrowRight className="h-3 w-3 text-blue-400 mx-1" />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Agents Grid */}
      <div className="grid grid-cols-3 gap-3">
        {agents.map((agent) => {
          const status = getAgentStatus(agent.name);
          
          return (
            <Card
              key={agent.name}
              className={`bg-white border-gray-200 transition-all duration-200 ${
                status.accessible
                  ? "hover:shadow-md"
                  : "opacity-50 filter grayscale cursor-not-allowed pointer-events-none"
              } ${
                status.active 
                  ? "ring-2 ring-blue-500 shadow-lg bg-blue-50" 
                  : status.visited 
                    ? "border-green-200 bg-green-50" 
                    : ""
              }`}
            >
              <CardHeader className="p-3 pb-1">
                <CardTitle className="text-sm flex items-center justify-between text-zinc-900">
                  <span>{agent.name}</span>
                  {status.visited && !status.active && (
                    <div className="h-2 w-2 bg-green-400 rounded-full"></div>
                  )}
                  {status.active && (
                    <Zap className="h-3 w-3 text-blue-600" />
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="p-3 pt-1">
                <p className="text-xs font-light text-zinc-600 mb-2">
                  {agent.description}
                </p>
                
                {/* Status Badge */}
                {status.active && (
                  <Badge className="bg-blue-600 hover:bg-blue-700 text-white text-xs">
                    Active
                  </Badge>
                )}
                {status.visited && !status.active && (
                  <Badge variant="outline" className="border-green-300 text-green-700 text-xs">
                    Visited
                  </Badge>
                )}
                
                {/* Tools Count */}
                {agent.tools && agent.tools.length > 0 && (
                  <div className="mt-2">
                    <span className="text-xs text-gray-500">
                      {agent.tools.length} tool{agent.tools.length !== 1 ? 's' : ''}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Current Agent Details */}
      {currentAgent && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-100">
          <div className="text-xs font-medium text-gray-700 mb-1">Current Agent:</div>
          <div className="text-sm font-semibold text-blue-600">{currentAgent}</div>
          {agents.find(a => a.name === currentAgent)?.tools && (
            <div className="text-xs text-gray-600 mt-1">
              Available tools: {agents.find(a => a.name === currentAgent)?.tools.join(", ")}
            </div>
          )}
        </div>
      )}
    </PanelSection>
  );
}
