# Stage 1: Builder
FROM node:18-slim as builder

WORKDIR /app/frontend

# Copy the rest of the application first
COPY . .

# Copy package files (already copied with . . but explicit for clarity)
COPY package*.json ./

# Install dependencies
RUN npm install

# Install tree for better directory listing (if not available by default)
RUN apt-get update && apt-get install -y tree

# Debugging: List files and show current directory before build
RUN ls -la /app/frontend
RUN pwd
RUN ls -la /app/frontend/src
RUN tree /app/frontend -L 3 # Use tree for a structured view up to 3 levels deep

# Build the application
RUN npm run build

# Stage 2: Runner
FROM node:18-slim

WORKDIR /app/frontend

# Copy the build output from the builder stage
COPY --from=builder /app/frontend/dist /app/frontend/dist

# Install http-server and curl
RUN apt-get update && apt-get install -y curl && \
    npm install -g http-server

# Expose the port
EXPOSE 3000

# Start the application using http-server with explicit rewrite for SPA
CMD ["http-server", "dist", "--host", "0.0.0.0", "-p", "3000", "--rewrite", "/index.html", "--cors"]