"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { AgentEvent } from "@/lib/types";
import {
  ArrowRightLeft,
  Wrench,
  WrenchIcon,
  RefreshCw,
  MessageSquareMore,
  Zap,
  Brain,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { PanelSection } from "./panel-section";

interface LangGraphEventTimelineProps {
  runnerEvents: AgentEvent[];
  routingHistory?: string[];
}

function formatEventName(type: string) {
  return (type.charAt(0).toUpperCase() + type.slice(1)).replace("_", " ");
}

function LangGraphEventIcon({ type }: { type: string }) {
  const className = "h-4 w-4";
  switch (type) {
    case "handoff":
      return <ArrowRightLeft className={`${className} text-blue-600`} />;
    case "tool_call":
      return <Wrench className={`${className} text-green-600`} />;
    case "tool_output":
      return <CheckCircle className={`${className} text-green-500`} />;
    case "context_update":
      return <RefreshCw className={`${className} text-orange-500`} />;
    case "message":
      return <MessageSquareMore className={`${className} text-purple-600`} />;
    case "routing_decision":
      return <Brain className={`${className} text-indigo-600`} />;
    default:
      return <Zap className={`${className} text-gray-500`} />;
  }
}

function EnhancedEventDetails({ event }: { event: AgentEvent }) {
  const baseClassName = "border border-gray-100 text-xs p-3 rounded-md flex flex-col gap-2";
  
  switch (event.type) {
    case "handoff":
      return event.metadata && (
        <div className={`${baseClassName} bg-blue-50 border-blue-200`}>
          <div className="flex items-center gap-2">
            <span className="font-medium text-blue-700">Agent Transition</span>
            <Badge variant="outline" className="text-blue-600 border-blue-300">
              LangGraph Routing
            </Badge>
          </div>
          <div className="text-blue-600">
            <span className="font-medium">From:</span> {event.metadata.source_agent}
          </div>
          <div className="text-blue-600">
            <span className="font-medium">To:</span> {event.metadata.target_agent}
          </div>
          {event.metadata.routing_reason && (
            <div className="text-blue-600 text-xs italic">
              Reason: {event.metadata.routing_reason}
            </div>
          )}
        </div>
      );

    case "tool_call":
      return event.metadata && (
        <div className={`${baseClassName} bg-green-50 border-green-200`}>
          <div className="flex items-center gap-2">
            <span className="font-medium text-green-700">Tool Execution</span>
            <Badge variant="outline" className="text-green-600 border-green-300">
              {event.metadata.tool_name}
            </Badge>
          </div>
          {event.metadata.tool_args && Object.keys(event.metadata.tool_args).length > 0 && (
            <div className="text-green-600">
              <span className="font-medium">Arguments:</span>
              <div className="mt-1 font-mono text-xs bg-green-100 p-2 rounded border">
                {JSON.stringify(event.metadata.tool_args, null, 2)}
              </div>
            </div>
          )}
        </div>
      );

    case "tool_output":
      return event.metadata && (
        <div className={`${baseClassName} bg-green-50 border-green-200`}>
          <div className="flex items-center gap-2">
            <span className="font-medium text-green-700">Tool Result</span>
            <CheckCircle className="h-3 w-3 text-green-500" />
          </div>
          <div className="text-green-600">
            <span className="font-medium">Tool:</span> {event.metadata.tool_name}
          </div>
          {event.metadata.tool_result && (
            <div className="text-green-600">
              <span className="font-medium">Result:</span> {event.metadata.tool_result}
            </div>
          )}
        </div>
      );

    case "message":
      return (
        <div className={`${baseClassName} bg-purple-50 border-purple-200`}>
          <div className="flex items-center gap-2">
            <span className="font-medium text-purple-700">
              {event.agent === "user" ? "User Message" : "Agent Response"}
            </span>
            <Badge variant="outline" className="text-purple-600 border-purple-300">
              {event.agent}
            </Badge>
          </div>
          <div className="text-purple-600 max-h-20 overflow-y-auto">
            {event.content}
          </div>
        </div>
      );

    case "context_update":
      return event.metadata?.changes && (
        <div className={`${baseClassName} bg-orange-50 border-orange-200`}>
          <div className="flex items-center gap-2">
            <span className="font-medium text-orange-700">Context Update</span>
            <Badge variant="outline" className="text-orange-600 border-orange-300">
              State Change
            </Badge>
          </div>
          {Object.entries(event.metadata.changes).map(([key, value]) => (
            <div key={key} className="text-orange-600">
              <span className="font-medium">{key}:</span> {String(value)}
            </div>
          ))}
        </div>
      );

    default:
      return (
        <div className={`${baseClassName} bg-gray-50 border-gray-200`}>
          <div className="text-gray-600">{event.content}</div>
        </div>
      );
  }
}

function TimeBadge({ timestamp }: { timestamp?: number | Date }) {
  if (!timestamp) return null;
  
  const date = timestamp instanceof Date ? timestamp : new Date(timestamp * 1000);
  const formattedDate = date.toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit',
    second: '2-digit'
  });

  return (
    <Badge
      variant="outline"
      className="text-[10px] h-5 bg-white text-zinc-500 border-gray-200"
    >
      {formattedDate}
    </Badge>
  );
}

function RoutingPathSummary({ routingHistory }: { routingHistory: string[] }) {
  if (!routingHistory || routingHistory.length <= 1) return null;

  return (
    <div className="mb-4 p-3 bg-indigo-50 rounded-lg border border-indigo-200">
      <div className="flex items-center gap-2 mb-2">
        <Brain className="h-4 w-4 text-indigo-600" />
        <span className="text-sm font-medium text-indigo-700">Workflow Path</span>
      </div>
      <div className="flex items-center space-x-2 text-xs">
        {routingHistory.map((agent, index) => (
          <div key={index} className="flex items-center">
            <span className="px-2 py-1 rounded bg-indigo-100 text-indigo-700 font-medium">
              {agent}
            </span>
            {index < routingHistory.length - 1 && (
              <ArrowRightLeft className="h-3 w-3 text-indigo-400 mx-2" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export function LangGraphEventTimeline({ 
  runnerEvents, 
  routingHistory = [] 
}: LangGraphEventTimelineProps) {
  return (
    <div className="flex-1 overflow-hidden">
      <PanelSection 
        title="Workflow Events" 
        icon={<MessageSquareMore className="h-4 w-4 text-blue-600" />}
      >
        <ScrollArea className="h-[calc(100%-2rem)] rounded-md border border-gray-200 bg-gray-100 shadow-sm">
          <div className="p-4 space-y-3">
            {/* Routing Path Summary */}
            <RoutingPathSummary routingHistory={routingHistory} />
            
            {runnerEvents.length === 0 ? (
              <p className="text-center text-zinc-500 p-4">
                No workflow events yet
              </p>
            ) : (
              runnerEvents.map((event) => (
                <Card
                  key={event.id}
                  className="border border-gray-200 bg-white shadow-sm rounded-lg hover:shadow-md transition-shadow"
                >
                  <CardHeader className="flex flex-row justify-between items-center p-4">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-800 text-sm">
                        {event.agent}
                      </span>
                      <Badge 
                        variant="outline" 
                        className="text-xs"
                        style={{
                          borderColor: event.type === 'handoff' ? '#3b82f6' : 
                                      event.type === 'tool_call' ? '#16a34a' :
                                      event.type === 'message' ? '#9333ea' : '#6b7280',
                          color: event.type === 'handoff' ? '#3b82f6' : 
                                event.type === 'tool_call' ? '#16a34a' :
                                event.type === 'message' ? '#9333ea' : '#6b7280'
                        }}
                      >
                        {formatEventName(event.type)}
                      </Badge>
                    </div>
                    <TimeBadge timestamp={event.timestamp} />
                  </CardHeader>

                  <CardContent className="flex items-start gap-3 p-4 pt-0">
                    <div className="rounded-full p-2 bg-gray-50 flex-shrink-0">
                      <LangGraphEventIcon type={event.type} />
                    </div>

                    <div className="flex-1 min-w-0">
                      <EnhancedEventDetails event={event} />
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </ScrollArea>
      </PanelSection>
    </div>
  );
}
