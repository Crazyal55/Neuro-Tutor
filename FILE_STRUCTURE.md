# Socratic Tutor - Complete File Structure Outline

## 📁 **Project Root Directory**

```
socratic-tutor/
├── 📁 backend/                          # Python FastAPI backend service
├── 📁 socratic-tutor-frontend/          # React TypeScript frontend application
├── 📄 .env                              # Root environment variables (Docker compose)
├── 📄 .gitignore                        # Git ignore rules for entire project
├── 📄 docker-compose.yml                # Docker orchestration configuration
├── 📄 README.md                         # Main project documentation
├── 📄 PROGRESS.md                       # Development progress tracking
├── 📄 FRONTEND.md                       # Frontend-specific documentation
├── 📄 BACKEND.md                        # Backend-specific documentation
├── 📄 OPENROUTER_SETUP.md               # OpenRouter API setup guide
├── 📄 RUN_LOCAL.md                     # Local development setup instructions
├── 📄 DEPLOYMENT.md                    # Deployment guide and instructions
└── 📄 FILE_STRUCTURE.md                # This file - complete project structure
```

---

## 🚀 **Backend Directory Structure**

```
backend/
├── 📁 app/                              # Main application package
│   ├── 📁 api/                         # API route handlers
│   │   ├── 📄 __init__.py              # API package initialization
│   │   └── 📄 chat.py                  # Chat API endpoints implementation
│   ├── 📁 core/                        # Core application components
│   │   ├── 📄 __init__.py              # Core package initialization
│   │   ├── 📄 config.py                # Application configuration settings
│   │   ├── 📄 db.py                    # Database connection and setup
│   │   └── 📄 openrouter_secrets.py    # OpenRouter API key management
│   ├── 📁 models/                      # Database models and schemas
│   │   ├── 📄 __init__.py              # Models package initialization
│   │   └── 📄 chat.py                  # Chat session and message models
│   ├── 📁 services/                    # Business logic services
│   │   ├── 📄 __init__.py              # Services package initialization
│   │   ├── 📄 llm_client.py            # OpenRouter LLM client implementation
│   │   └── 📄 sessions.py              # Chat session management service
│   └── 📄 __init__.py                  # Main application package initialization
├── 📁 tests/                            # Test suite
│   └── 📄 test_chat.py                 # Chat API unit tests
├── 📄 .env                             # Backend environment variables
├── 📄 .env.example                     # Backend environment variables template
├── 📄 Dockerfile                       # Docker container configuration
├── 📄 main.py                          # FastAPI application entry point
├── 📄 requirements.txt                  # Python dependencies list
├── 📄 test_openrouter.py              # OpenRouter API testing script
└── 📄 README.md                        # Backend-specific documentation
```

### 🐍 **Backend File Descriptions**

#### **Core Application Files**
- **`main.py`** - FastAPI application entry point, router configuration, and server startup
- **`requirements.txt`** - Python package dependencies including FastAPI, SQLAlchemy, OpenAI SDK
- **`.env`** - Environment variables for API keys, database URLs, and configuration
- **`.env.example`** - Template for environment variables with documentation

#### **API Layer (`app/api/`)**
- **`__init__.py`** - Marks directory as Python package for imports
- **`chat.py`** - REST API endpoints for chat functionality including `/api/chat/` and session management

#### **Core Components (`app/core/`)**
- **`__init__.py`** - Core package initialization
- **`config.py`** - Application configuration settings including CORS, database, and environment variables
- **`db.py`** - Database connection setup using SQLAlchemy with SQLite configuration
- **`openrouter_secrets.py`** - Secure OpenRouter API key management and access functions

#### **Data Models (`app/models/`)**
- **`__init__.py`** - Models package initialization
- **`chat.py`** - SQLAlchemy models for ChatSession and Message tables with relationships

#### **Business Logic (`app/services/`)**
- **`__init__.py`** - Services package initialization
- **`llm_client.py`** - OpenRouter API client with Socratic methodology implementation
- **`sessions.py`** - Chat session CRUD operations and management logic

#### **Testing (`tests/`)**
- **`test_chat.py`** - Unit tests for chat API endpoints and business logic

#### **Development Tools**
- **`test_openrouter.py`** - Standalone script for testing OpenRouter API connectivity
- **`Dockerfile`** - Docker container build configuration for backend service
- **`README.md`** - Backend-specific setup, configuration, and API documentation

---

## ⚛️ **Frontend Directory Structure**

```
socratic-tutor-frontend/
├── 📁 public/                           # Static assets and HTML template
│   ├── 📄 index.html                   # Main HTML template file
│   ├── 📄 vite.svg                     # Vite logo
│   └── 📄 project-logo.svg             # Application logo
├── 📁 src/                             # Source code directory
│   ├── 📁 components/                   # React components
│   │   ├── 📁 chat/                    # Chat-specific components
│   │   │   ├── 📄 ChatPage.tsx         # Main chat interface layout
│   │   │   ├── 📄 ChatSidebar.tsx      # Chat history and session list
│   │   │   ├── 📄 MessageList.tsx      # Message display container
│   │   │   ├── 📄 ChatInput.tsx        # Message input and send functionality
│   │   │   ├── 📄 TypingIndicator.tsx  # Loading/typing animation
│   │   │   └── 📄 MessageBubble.tsx     # Individual message display
│   │   ├── 📁 layout/                  # Layout and UI components
│   │   │   ├── 📄 Header.tsx           # Application header with branding
│   │   │   ├── 📄 ThemeToggle.tsx      # Light/dark mode toggle
│   │   │   └── 📄 PreferencesDrawer.tsx # Settings and preferences modal
│   │   └── 📁 ui/                     # shadcn/ui base components
│   │       ├── 📄 button.tsx           # Button component
│   │       ├── 📄 input.tsx            # Input field component
│   │       ├── 📄 label.tsx            # Form label component
│   │       ├── 📄 scroll-area.tsx       # Scrollable container
│   │       ├── 📄 sheet.tsx            # Modal/sheet component
│   │       ├── 📄 select.tsx           # Dropdown select
│   │       ├── 📄 checkbox.tsx         # Checkbox component
│   │       └── 📄 slider.tsx           # Range slider component
│   ├── 📁 lib/                         # Utility libraries
│   │   └── 📄 utils.ts                # Utility functions and helpers
│   ├── 📁 pages/                       # Page-level components
│   │   └── 📄 ChatPage.tsx            # Main chat application page
│   ├── 📁 services/                    # API and external services
│   │   └── 📄 chatService.ts           # Backend API integration
│   ├── 📄 App.jsx                      # Main React application component
│   ├── 📄 index.css                    # Global styles and Tailwind imports
│   ├── 📄 main.jsx                     # Application entry point
│   └── 📄 ThemeProvider.tsx            # Theme context and provider
├── 📄 .env                             # Frontend environment variables
├── 📄 .env.example                     # Frontend environment variables template
├── 📄 Dockerfile                       # Docker container configuration
├── 📄 index.html                       # Root HTML template (legacy)
├── 📄 package.json                     # NPM dependencies and scripts
├── 📄 postcss.config.js                # PostCSS configuration
├── 📄 tailwind.config.js                # Tailwind CSS configuration
└── 📄 vite.config.js                   # Vite build tool configuration
```

### ⚛️ **Frontend File Descriptions**

#### **Configuration Files**
- **`package.json`** - NPM dependencies, scripts, and project metadata
- **`vite.config.js`** - Vite development server and build configuration
- **`tailwind.config.js`** - Tailwind CSS customization and theme configuration
- **`postcss.config.js`** - PostCSS plugin configuration for Tailwind
- **`.env`** - Environment variables for API URLs and configuration
- **`.env.example`** - Template for frontend environment variables

#### **Application Entry Points**
- **`main.jsx`** - React application entry point with DOM mounting
- **`App.jsx`** - Main application component with routing and providers
- **`index.html`** - HTML template file for the application

#### **Core Components (`src/components/`)**
- **Chat Components (`chat/`)**:
  - **`ChatPage.tsx`** - Main chat interface with layout and state management
  - **`ChatSidebar.tsx`** - Session list, navigation, and chat history
  - **`MessageList.tsx`** - Scrollable message display container
  - **`ChatInput.tsx`** - Message composition and send functionality
  - **`TypingIndicator.tsx`** - Loading animation during AI responses
  - **`MessageBubble.tsx`** - Individual message rendering with styling

- **Layout Components (`layout/`)**:
  - **`Header.tsx`** - Application header with logo, title, and controls
  - **`ThemeToggle.tsx`** - Light/dark mode toggle button
  - **`PreferencesDrawer.tsx`** - Settings modal with user preferences

- **UI Components (`ui/`)**:
  - **`button.tsx`** - Reusable button component with variants
  - **`input.tsx`** - Form input component with validation
  - **`label.tsx`** - Form label component
  - **`scroll-area.tsx`** - Customizable scrollable container
  - **`sheet.tsx`** - Modal/slide-out panel component
  - **`select.tsx`** - Dropdown select component
  - **`checkbox.tsx`** - Checkbox input component
  - **`slider.tsx`** - Range slider for numeric inputs

#### **Utilities and Services**
- **`lib/utils.ts`** - Utility functions and helper methods
- **`services/chatService.ts`** - Backend API integration with error handling
- **`pages/ChatPage.tsx`** - Page-level chat component wrapper
- **`ThemeProvider.tsx`** - Theme context and state management

#### **Styling**
- **`index.css`** - Global styles, Tailwind imports, and base CSS

#### **Development**
- **`Dockerfile`** - Docker container build configuration for frontend
- **`public/`** - Static assets and HTML template files

---

## 🐳 **Docker & Configuration Files**

### Root Configuration Files
- **`docker-compose.yml`** - Multi-container orchestration with service dependencies
- **`.env`** - Root environment variables for Docker compose
- **`.gitignore`** - Git ignore patterns for all project files

### Documentation Files
- **`README.md`** - Main project overview and setup instructions
- **`PROGRESS.md`** - Detailed development progress tracking
- **`FRONTEND.md`** - Frontend-specific documentation and setup
- **`BACKEND.md`** - Backend API documentation and setup
- **`OPENROUTER_SETUP.md`** - OpenRouter API key configuration guide
- **`RUN_LOCAL.md`** - Local development environment setup
- **`DEPLOYMENT.md`** - Production deployment instructions
- **`FILE_STRUCTURE.md`** - This comprehensive file structure documentation

---

## 🎯 **Purpose and Architecture Summary**

### **Backend Architecture (FastAPI + Python)**
- **Purpose**: RESTful API server with OpenRouter AI integration
- **Key Features**: Session management, message persistence, Socratic methodology
- **Technology Stack**: FastAPI, SQLAlchemy, SQLite, OpenRouter API
- **Design Patterns**: Service layer architecture, dependency injection, async operations

### **Frontend Architecture (React + TypeScript)**
- **Purpose**: Interactive chat interface with neurodivergent-friendly design
- **Key Features**: Real-time messaging, theme switching, responsive layout
- **Technology Stack**: React, TypeScript, Tailwind CSS, shadcn/ui
- **Design Patterns**: Component composition, context providers, service layer

### **Docker Architecture**
- **Purpose**: Containerized development and deployment environment
- **Key Features**: Service orchestration, health checks, volume mounting
- **Networking**: Internal service communication with proper DNS resolution
- **Environment Management**: Separate configurations for development and production

### **Documentation Structure**
- **Purpose**: Comprehensive onboarding and maintenance guides
- **Coverage**: Setup, development, deployment, and API documentation
- **Audience**: Developers, team members, and system administrators

---

## 🔄 **Data Flow Architecture**

```
User Interface (React)
       ↓
   chatService.ts
       ↓
   Backend API (FastAPI)
       ↓
   LLM Client Service
       ↓
   OpenRouter API
       ↓
   AI Response (Socratic Method)
       ↓
   Database Storage (SQLite)
       ↓
   Real-time UI Update
```

---

## 🛠️ **Development Workflow**

### **Local Development**
1. Backend: `uvicorn app.main:app --reload --port 8000`
2. Frontend: `npm run dev` (Vite dev server on port 5180)
3. Database: SQLite with automatic schema creation

### **Docker Development**
1. Build: `docker compose up --build`
2. Services: Backend (port 8000), Frontend (port 5173)
3. Networking: Internal service communication via Docker network

### **Production Deployment**
1. Containers: Built from Dockerfiles
2. Environment: Production variables from `.env` files
3. Monitoring: Health checks and logging configured

---

*Last Updated: 2025-11-30*
*Project: Socratic Tutor - AI-Powered Learning Assistant*
