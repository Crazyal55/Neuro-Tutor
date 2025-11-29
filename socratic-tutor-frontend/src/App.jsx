import React from 'react';
import { ChatPage } from './pages/ChatPage';
import { ThemeProvider } from './components/ThemeProvider';

function App() {
  return (
    <ThemeProvider>
      <ChatPage />
    </ThemeProvider>
  );
}

export default App;
