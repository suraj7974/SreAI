import React from 'react';
import { Link, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path ? 'bg-blue-600' : 'hover:bg-gray-700';
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="text-white text-xl font-bold">
                🤖 AI Chaos Handler
              </Link>
            </div>
            <div className="flex space-x-4">
              <Link
                to="/"
                className={`text-gray-300 px-3 py-2 rounded-md text-sm font-medium ${isActive('/')}`}
              >
                Home
              </Link>
              <Link
                to="/incidents"
                className={`text-gray-300 px-3 py-2 rounded-md text-sm font-medium ${isActive('/incidents')}`}
              >
                Incidents
              </Link>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
