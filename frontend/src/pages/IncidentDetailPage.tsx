import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download, FileText, RefreshCw } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TOKEN = import.meta.env.VITE_API_TOKEN || 'dev-token-change-in-production';

interface FileInfo {
  name: string;
  path: string;
  size: number;
  modified: number;
  content?: string;
  type: 'text' | 'binary';
}

interface IncidentDetails {
  incident_id: string;
  files: FileInfo[];
  trace: any[];
}

export default function IncidentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [details, setDetails] = useState<IncidentDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null);

  useEffect(() => {
    loadIncidentDetails();
  }, [id]);

  const loadIncidentDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API_BASE_URL}/incidents/${id}`, {
        headers: { Authorization: `Bearer ${API_TOKEN}` }
      });
      setDetails(response.data);
      if (response.data.files.length > 0) {
        setSelectedFile(response.data.files[0]);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = (file: FileInfo) => {
    const blob = new Blob([file.content || ''], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = file.name;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <Button variant="outline" onClick={() => navigate('/incidents')} className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Incidents
        </Button>
        <Card className="border-red-500">
          <CardContent className="p-6 text-red-500">
            Error loading incident: {error}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={() => navigate('/incidents')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-white">Incident: {id}</h1>
            <p className="text-gray-400 mt-1">{details?.files.length || 0} files</p>
          </div>
        </div>
        <Button variant="outline" onClick={loadIncidentDetails}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* File List */}
        <div className="col-span-3">
          <Card>
            <CardHeader>
              <CardTitle className="text-white text-lg">Files</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="space-y-1">
                {details?.files.map((file, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedFile(file)}
                    className={`w-full text-left px-4 py-2 text-sm flex items-center gap-2 hover:bg-gray-800 transition-colors ${
                      selectedFile?.path === file.path ? 'bg-gray-800 text-white' : 'text-gray-400'
                    }`}
                  >
                    <FileText className="h-4 w-4" />
                    <span className="truncate">{file.path}</span>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* File Content */}
        <div className="col-span-9">
          {selectedFile ? (
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-white text-lg">{selectedFile.name}</CardTitle>
                {selectedFile.type === 'text' && (
                  <Button size="sm" variant="outline" onClick={() => downloadFile(selectedFile)}>
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                )}
              </CardHeader>
              <CardContent>
                {selectedFile.type === 'text' ? (
                  <pre className="bg-gray-900 p-4 rounded-lg overflow-auto max-h-[600px] text-sm text-gray-300">
                    {selectedFile.content}
                  </pre>
                ) : (
                  <div className="text-center py-12 text-gray-400">
                    Binary file - {(selectedFile.size / 1024).toFixed(2)} KB
                    <br />
                    <a
                      href={`${API_BASE_URL}/incidents/${id}/artifacts/${selectedFile.path}`}
                      className="text-blue-500 hover:underline mt-2 inline-block"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Download File
                    </a>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-12 text-center text-gray-400">
                Select a file to view its contents
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
