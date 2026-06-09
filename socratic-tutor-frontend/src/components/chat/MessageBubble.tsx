import React from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import { cn } from '../../lib/utils';
import type { SourceCitation } from '../../services/chatService';
import 'highlight.js/styles/github-dark.css';

interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceCitation[];
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ role, content, sources }) => {
  const isUser = role === 'user';

  return (
    <div
      className={cn(
        'flex w-full mb-4 transition-all duration-300 ease-in-out',
        isUser ? 'justify-end' : 'justify-start',
      )}
    >
      <div
        className={cn(
          'max-w-xs lg:max-w-2xl px-5 py-4 rounded-2xl text-sm leading-relaxed transition-all duration-200 hover:shadow-md',
          isUser
            ? 'bg-blue-500 text-white rounded-br-sm shadow-sm hover:bg-blue-600 whitespace-pre-wrap'
            : 'bg-card text-foreground rounded-bl-sm border border-border shadow-sm hover:shadow-lg prose prose-sm dark:prose-invert max-w-none',
        )}
      >
        {isUser ? (
          content
        ) : (
          <>
            <ReactMarkdown rehypePlugins={[rehypeHighlight]}>{content}</ReactMarkdown>
            {sources && sources.length > 0 ? (
              <div className="mt-3 flex flex-wrap gap-2 not-prose">
                {sources.map((source, index) => (
                  <span
                    key={`${source.filename}-${source.locator}-${index}`}
                    className="inline-flex items-center rounded-full bg-muted px-2.5 py-0.5 text-xs text-muted-foreground"
                    title={`Relevance: ${Math.round(source.score * 100)}%`}
                  >
                    {source.filename}
                    {source.locator ? ` · ${source.locator}` : ''}
                  </span>
                ))}
              </div>
            ) : null}
          </>
        )}
      </div>
    </div>
  );
};
