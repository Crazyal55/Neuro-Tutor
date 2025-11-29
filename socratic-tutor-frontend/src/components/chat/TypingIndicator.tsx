import React from 'react';
import { cn } from '../../lib/utils';

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex w-full mb-4 justify-start">
      <div className="max-w-xs lg:max-w-md px-4 py-3 rounded-2xl rounded-bl-sm border border-gray-200 bg-gray-100">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  );
};
