import React from 'react';
import { X } from 'lucide-react';
import { Button } from '../ui/button';

interface ErrorBannerProps {
  message: string;
  onDismiss: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ message, onDismiss }) => {
  return (
    <div
      role="alert"
      className="mx-4 mt-4 flex items-start justify-between gap-3 rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive"
    >
      <span>{message}</span>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        onClick={onDismiss}
        className="h-7 w-7 shrink-0 text-destructive hover:bg-destructive/10"
        aria-label="Dismiss error"
      >
        <X className="h-4 w-4" />
      </Button>
    </div>
  );
};
