import { AlertCircle, Clock, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Incident } from '@/types';
import { ReactElement } from 'react';
import { useNavigate } from 'react-router-dom';

interface IncidentCardProps {
  incident: Incident;
}

const severityColors = {
  critical: 'bg-red-500 hover:bg-red-600',
  high: 'bg-orange-500 hover:bg-orange-600',
  medium: 'bg-yellow-500 hover:bg-yellow-600',
  low: 'bg-blue-500 hover:bg-blue-600',
};

const statusIcons: Record<Incident['status'], ReactElement> = {
  open: <AlertCircle className="h-4 w-4" />,
  investigating: <Clock className="h-4 w-4" />,
  resolved: <CheckCircle className="h-4 w-4" />,
  closed: <CheckCircle className="h-4 w-4" />,
};

export function IncidentCard({ incident }: IncidentCardProps) {
  const navigate = useNavigate();
  
  return (
    <Card 
      className="hover:border-gray-600 transition-colors cursor-pointer" 
      onClick={() => navigate(`/incidents/${incident.incident_id}`)}
    >
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg text-white flex items-center gap-2">
              {statusIcons[incident.status]}
              {incident.title}
            </CardTitle>
            <CardDescription className="mt-1 text-gray-400">
              {incident.description}
            </CardDescription>
          </div>
          <Badge className={`${severityColors[incident.severity]} text-white ml-2`}>
            {incident.severity.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-4 text-gray-400">
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {new Date(incident.created_at).toLocaleString()}
            </span>
            <Badge variant="outline" className="text-gray-300 border-gray-600">
              {incident.status}
            </Badge>
          </div>
          {incident.assigned_to && (
            <span className="text-gray-400">
              Assigned to: <span className="text-white">{incident.assigned_to}</span>
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
