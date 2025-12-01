# Use Node.js 20 LTS as base image
FROM node:20-alpine

# Install wget for health check before setting working directory
RUN apk add --no-cache wget

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build application
RUN npm run build

# Install a lightweight server to serve the built app
RUN npm install -g serve

# Expose port
EXPOSE 5173

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:5173 || exit 1

# Serve the built application
CMD ["serve", "-s", "dist", "-l", "5173"]
