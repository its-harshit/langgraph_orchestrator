"use client";

import { PanelSection } from "./panel-section";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BookText, User, Plane, MapPin, CreditCard, Clock, Activity } from "lucide-react";

interface LangGraphContextPanelProps {
  context: {
    passenger_name?: string;
    confirmation_number?: string;
    seat_number?: string;
    flight_number?: string;
    account_number?: string;
  };
  currentAgent?: string;
  routingHistory?: string[];
}

function getContextIcon(key: string) {
  const iconClass = "h-3 w-3";
  switch (key) {
    case "passenger_name":
      return <User className={`${iconClass} text-blue-500`} />;
    case "confirmation_number":
      return <CreditCard className={`${iconClass} text-green-500`} />;
    case "seat_number":
      return <MapPin className={`${iconClass} text-orange-500`} />;
    case "flight_number":
      return <Plane className={`${iconClass} text-purple-500`} />;
    case "account_number":
      return <CreditCard className={`${iconClass} text-gray-500`} />;
    default:
      return <Activity className={`${iconClass} text-gray-400`} />;
  }
}

function formatContextKey(key: string): string {
  return key
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function getContextValueStatus(value: any): { status: 'present' | 'missing' | 'auto-generated', color: string } {
  if (!value || value === 'null') {
    return { status: 'missing', color: 'text-gray-400' };
  }
  
  // Check if value looks auto-generated (pattern-based heuristic)
  if (typeof value === 'string') {
    if (value.match(/^[A-Z0-9]{6}$/) || value.match(/^FLT-\d+$/)) {
      return { status: 'auto-generated', color: 'text-green-600' };
    }
  }
  
  return { status: 'present', color: 'text-zinc-900' };
}

export function LangGraphContextPanel({ 
  context, 
  currentAgent, 
  routingHistory = [] 
}: LangGraphContextPanelProps) {
  const contextEntries = Object.entries(context).filter(([_, value]) => value !== undefined);
  const filledFields = contextEntries.filter(([_, value]) => value && value !== 'null').length;
  const totalFields = contextEntries.length;

  return (
    <PanelSection
      title="Workflow Context"
      icon={<BookText className="h-4 w-4 text-blue-600" />}
    >
      {/* Context Completion Status */}
      <div className="mb-3 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-blue-700">Context Completion</span>
          <Badge 
            variant="outline" 
            className={`${filledFields === totalFields ? 'border-green-300 text-green-700' : 'border-blue-300 text-blue-700'}`}
          >
            {filledFields}/{totalFields}
          </Badge>
        </div>
        <div className="w-full bg-blue-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${totalFields > 0 ? (filledFields / totalFields) * 100 : 0}%` }}
          ></div>
        </div>
      </div>

      {/* Current Workflow State */}
      {currentAgent && (
        <div className="mb-3 p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-green-700">Current State</span>
            </div>
            <Badge className="bg-green-600 text-white">
              {currentAgent}
            </Badge>
          </div>
          {routingHistory.length > 1 && (
            <div className="mt-2 text-xs text-green-600">
              Journey: {routingHistory.join(' → ')}
            </div>
          )}
        </div>
      )}

      {/* Context Fields */}
      <Card className="bg-gradient-to-r from-white to-gray-50 border-gray-200 shadow-sm">
        <CardHeader className="pb-2">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Customer Information</span>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-2">
            {contextEntries.map(([key, value]) => {
              const valueStatus = getContextValueStatus(value);
              
              return (
                <div
                  key={key}
                  className="flex items-center gap-3 bg-white p-3 rounded-md border border-gray-200 shadow-sm transition-all hover:shadow-md"
                >
                  <div className="flex-shrink-0">
                    {getContextIcon(key)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-zinc-600">
                        {formatContextKey(key)}
                      </span>
                      {valueStatus.status === 'auto-generated' && (
                        <Badge variant="outline" className="text-[10px] text-green-600 border-green-300">
                          Auto
                        </Badge>
                      )}
                    </div>
                    <div className={`text-sm font-medium ${valueStatus.color} truncate`}>
                      {value || "Not provided"}
                    </div>
                  </div>
                  
                  <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                    valueStatus.status === 'present' ? 'bg-blue-500' :
                    valueStatus.status === 'auto-generated' ? 'bg-green-500' :
                    'bg-gray-300'
                  }`}></div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* LangGraph Workflow Stats */}
      {routingHistory.length > 0 && (
        <div className="mt-3 p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="h-4 w-4 text-purple-600" />
            <span className="text-sm font-medium text-purple-700">Workflow Statistics</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="text-purple-600">
              <span className="font-medium">Agents Visited:</span> {routingHistory.length}
            </div>
            <div className="text-purple-600">
              <span className="font-medium">Current Step:</span> {routingHistory.length}
            </div>
          </div>
        </div>
      )}
    </PanelSection>
  );
}
