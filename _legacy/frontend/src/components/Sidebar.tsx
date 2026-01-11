import { useState } from "react";
import {
  Home,
  AlertCircle,
  Activity,
  Settings,
  ChevronLeft,
  ChevronRight,
  Bot,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
}

export function Sidebar({ currentPage, onNavigate }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);

  const menuItems = [
    { id: "home", label: "Home", icon: Home },
    { id: "dashboard", label: "Dashboard", icon: Activity },
    { id: "incidents", label: "Incidents", icon: AlertCircle },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <div
      className={`
        relative h-screen bg-gray-950 border-r border-gray-800
        transition-all duration-300 ease-in-out
        ${collapsed ? "w-16" : "w-64"}
      `}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 h-16 border-b border-gray-800">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <Bot className="h-6 w-6 text-blue-500" />
            <h1 className="text-xl font-bold text-white">DevAI</h1>
          </div>
        )}
        {collapsed && <Bot className="h-6 w-6 text-blue-500 mx-auto" />}
      </div>

      {/* Toggle Button */}
      <Button
        variant="ghost"
        size="icon"
        className="absolute -right-3 top-1/2 -translate-y-1/2 h-6 w-6 rounded-full border-2 border-gray-700 bg-gray-900 hover:bg-gray-800 hover:border-gray-600 z-10 flex items-center justify-center"
        onClick={() => setCollapsed(!collapsed)}
      >
        {collapsed ? (
          <ChevronRight className="h-4 w-4 text-gray-300" />
        ) : (
          <ChevronLeft className="h-4 w-4 text-gray-300" />
        )}
      </Button>

      {/* Menu Items */}
      <ScrollArea className="flex-1 py-4">
        <nav className="space-y-1 px-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPage === item.id;

            return (
              <Button
                key={item.id}
                variant={isActive ? "secondary" : "ghost"}
                className={`
                  w-full justify-start gap-3 h-11
                  ${collapsed ? "px-3" : "px-4"}
                  ${isActive ? "bg-gray-800 text-white" : "text-gray-400 hover:text-white hover:bg-gray-900"}
                `}
                onClick={() => onNavigate(item.id)}
                title={collapsed ? item.label : undefined}
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </Button>
            );
          })}
        </nav>
      </ScrollArea>
    </div>
  );
}
