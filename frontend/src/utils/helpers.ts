export const formatDate = (dateString: string): string => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString();
};

type Status = 'running' | 'complete' | 'error' | 'initializing';

export const getStatusColor = (status: Status): string => {
  const colors: Record<Status, string> = {
    running: 'bg-yellow-500',
    complete: 'bg-green-500',
    error: 'bg-red-500',
    initializing: 'bg-blue-500',
  };
  return colors[status] || 'bg-gray-500';
};

type Agent = 'LogAgent' | 'MetricsAgent' | 'FixerAgent' | 'TesterAgent' | 'ReporterAgent' | 'Coordinator';

export const getAgentColor = (agent: Agent): string => {
  const colors: Record<Agent, string> = {
    LogAgent: 'border-blue-500',
    MetricsAgent: 'border-purple-500',
    FixerAgent: 'border-green-500',
    TesterAgent: 'border-orange-500',
    ReporterAgent: 'border-pink-500',
    Coordinator: 'border-cyan-500',
  };
  return colors[agent] || 'border-gray-500';
};

export const downloadFile = (url: string, filename: string): void => {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
