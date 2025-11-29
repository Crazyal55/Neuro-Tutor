import React from 'react';
import { Button } from '../ui/button';
import { Settings } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

interface HeaderProps {
  onOpenPreferences?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenPreferences }) => {
  return (
    <header className="px-6 py-4 border-b border-border bg-background shadow-sm transition-all duration-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-lg flex items-center justify-center overflow-hidden">
            <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center logo">
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l10-5z"/>
              </svg>
            </div>
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Neuro Tutor</h1>
            <p className="text-sm text-muted-foreground">Your AI learning companion</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <ThemeToggle />
          <Button
            variant="outline"
            size="sm"
            onClick={onOpenPreferences}
            className="flex items-center space-x-2 transition-all duration-200 hover:bg-accent"
          >
            <Settings className="w-4 h-4" />
            <span>Preferences</span>
          </Button>
        </div>
      </div>
    </header>
  );
};
