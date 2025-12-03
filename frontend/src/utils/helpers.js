export const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString();
};

export const getStatusColor = (status) => {
  const colors = {
    running: 'bg-yellow-500',
    complete: 'bg-green-500',
    error: 'bg-red-500',
    initializing: 'bg-blue-500',
  };
  return colors[status] || 'bg-gray-500';
};

export const getAgentColor = (agent) => {
  const colors = {
    LogAgent: 'border-blue-500',
    MetricsAgent: 'border-purple-500',
    FixerAgent: 'border-green-500',
    TesterAgent: 'border-orange-500',
    ReporterAgent: 'border-pink-500',
    Coordinator: 'border-cyan-500',
  };
  return colors[agent] || 'border-gray-500';
};

export const downloadFile = (url, filename) => {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
