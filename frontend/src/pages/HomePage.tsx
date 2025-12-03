import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  AlertCircle,
  Activity,
  CheckCircle,
  Clock,
  TrendingUp,
  TrendingDown,
  Cpu,
  HardDrive,
  Wifi,
  Server,
} from "lucide-react";
import axios from "axios";

interface SystemMetrics {
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  activeIncidents: number;
  resolvedToday: number;
  avgResponseTime: number;
  uptime: string;
  activeAgents: number;
  vmConnected: boolean;
}

export default function HomePage() {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    cpuUsage: 0,
    memoryUsage: 0,
    diskUsage: 0,
    activeIncidents: 0,
    resolvedToday: 0,
    avgResponseTime: 0,
    uptime: "unknown",
    activeAgents: 3,
    vmConnected: false,
  });
  const [loading, setLoading] = useState(true);

  const [recentActivity, setRecentActivity] = useState<
    Array<{
      id: string;
      type: "info" | "warning" | "success" | "error";
      message: string;
      timestamp: Date;
      service?: string;
    }>
  >([]);

  useEffect(() => {
    // Fetch real VM metrics
    const fetchVMMetrics = async () => {
      try {
        const response = await axios.get("http://localhost:8000/vm/metrics");
        if (response.data.error) {
          setMetrics((prev) => ({ ...prev, vmConnected: false }));
          setLoading(false);
          return;
        }

        setMetrics((prev) => ({
          ...prev,
          cpuUsage: response.data.cpuUsage || 0,
          memoryUsage: response.data.memoryUsage || 0,
          diskUsage: response.data.diskUsage || 0,
          uptime: response.data.uptime || "unknown",
          vmConnected: true,
        }));
        setLoading(false);
      } catch (error) {
        console.error("Failed to fetch VM metrics:", error);
        setMetrics((prev) => ({ ...prev, vmConnected: false }));
        setLoading(false);
      }
    };

    // Fetch real VM logs for incidents
    const fetchVMLogs = async () => {
      try {
        const response = await axios.get("http://localhost:8000/vm/logs");
        if (response.data.error || !response.data.incidents) {
          return;
        }

        // Convert incidents to activity feed format
        const newActivities = response.data.incidents.map((incident: any) => ({
          id: `${incident.service}-${Date.now()}-${Math.random()}`,
          type: incident.type as "info" | "warning" | "success" | "error",
          message: `[${incident.service}] ${incident.message}`,
          timestamp: new Date(incident.timestamp),
          service: incident.service,
        }));

        setRecentActivity(newActivities.slice(0, 10));
      } catch (error) {
        console.error("Failed to fetch VM logs:", error);
      }
    };

    // Initial fetch
    fetchVMMetrics();
    fetchVMLogs();

    // Poll metrics every 5 seconds
    const metricsInterval = setInterval(fetchVMMetrics, 5000);

    // Poll logs every 10 seconds
    const logsInterval = setInterval(fetchVMLogs, 10000);

    return () => {
      clearInterval(metricsInterval);
      clearInterval(logsInterval);
    };
  }, []);

  const getStatusColor = (value: number, max: number, inverse = false) => {
    const percentage = (value / max) * 100;
    if (inverse) {
      if (percentage < 50) return "text-green-500";
      if (percentage < 75) return "text-yellow-500";
      return "text-red-500";
    }
    if (percentage > 75) return "text-green-500";
    if (percentage > 50) return "text-yellow-500";
    return "text-red-500";
  };

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">AI SRE</h1>
          <p className="text-gray-400 mt-1">
            Real-time monitoring of your cloud infrastructure
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <div
            className={`h-2 w-2 rounded-full ${metrics.vmConnected ? "bg-green-500 animate-pulse" : "bg-red-500"}`}
          />
          <span className="text-gray-400">
            {metrics.vmConnected ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>

      {!metrics.vmConnected && !loading && (
        <Card className="bg-yellow-500/10 border-yellow-500/30">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-yellow-500" />
              <div>
                <p className="text-yellow-500 font-medium">VM Not Configured</p>
                <p className="text-sm text-gray-400 mt-1">
                  Set VM_HOST, VM_USER, and VM_KEY_PATH in your .env file to see
                  live metrics from your VM.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Key Metrics Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-gradient-to-br from-blue-500/10 to-blue-600/5 border-blue-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              CPU Usage
            </CardTitle>
            <Cpu className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div
              className={`text-2xl font-bold ${getStatusColor(metrics.cpuUsage, 100, true)}`}
            >
              {metrics.cpuUsage.toFixed(1)}%
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2 mt-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${metrics.cpuUsage}%` }}
              />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500/10 to-purple-600/5 border-purple-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              Memory Usage
            </CardTitle>
            <HardDrive className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div
              className={`text-2xl font-bold ${getStatusColor(metrics.memoryUsage, 100, true)}`}
            >
              {metrics.memoryUsage.toFixed(1)}%
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2 mt-2">
              <div
                className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${metrics.memoryUsage}%` }}
              />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500/10 to-green-600/5 border-green-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              Disk Usage
            </CardTitle>
            <Wifi className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div
              className={`text-2xl font-bold ${getStatusColor(metrics.diskUsage, 100, true)}`}
            >
              {metrics.diskUsage.toFixed(1)}%
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2 mt-2">
              <div
                className="bg-green-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${metrics.diskUsage}%` }}
              />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-yellow-500/10 to-yellow-600/5 border-yellow-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              VM Uptime
            </CardTitle>
            <Server className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold text-green-500">
              {metrics.uptime}
            </div>
            <p className="text-xs text-gray-500 mt-1">Time since boot</p>
          </CardContent>
        </Card>
      </div>

      {/* Incidents & Response */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="hover:border-red-500/50 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              Active Incidents
            </CardTitle>
            <AlertCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white">
              {metrics.activeIncidents}
            </div>
            <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
              {metrics.activeIncidents > 0 ? (
                <>
                  <TrendingUp className="h-3 w-3 text-red-500" /> Needs
                  attention
                </>
              ) : (
                <>
                  <CheckCircle className="h-3 w-3 text-green-500" /> All clear
                </>
              )}
            </p>
          </CardContent>
        </Card>

        <Card className="hover:border-green-500/50 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              Resolved Today
            </CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white">
              {metrics.resolvedToday}
            </div>
            <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
              <CheckCircle className="h-3 w-3 text-green-500" /> Automated
              resolution
            </p>
          </CardContent>
        </Card>

        <Card className="hover:border-blue-500/50 transition-colors">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-400">
              Avg Response Time
            </CardTitle>
            <Clock className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-white">
              {metrics.avgResponseTime.toFixed(0)}s
            </div>
            <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
              <TrendingDown className="h-3 w-3 text-green-500" /> Faster than
              average
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity Feed */}
      <Card>
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {recentActivity.length === 0 ? (
            <p className="text-gray-500 text-center py-4">
              Waiting for system events...
            </p>
          ) : (
            recentActivity.map((activity) => (
              <div
                key={activity.id}
                className="flex items-start gap-3 p-3 rounded-lg bg-gray-900/50 hover:bg-gray-900 transition-colors"
              >
                {activity.type === "success" && (
                  <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                )}
                {activity.type === "warning" && (
                  <AlertCircle className="h-5 w-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                )}
                {activity.type === "error" && (
                  <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                )}
                {activity.type === "info" && (
                  <Activity className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-300">{activity.message}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {activity.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      {/* Active AI Agents Status */}
      <Card className="bg-gradient-to-r from-blue-600/10 to-purple-600/10 border-blue-500/30">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold text-white mb-2">
                AI Agents Active
              </h3>
              <p className="text-gray-400">
                All agents are monitoring your infrastructure
              </p>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold text-blue-500">
                {metrics.activeAgents}
              </div>
              <p className="text-sm text-gray-500">Agents Online</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
