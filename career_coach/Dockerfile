# -----------------------------
# Stage 1: Build Frontend
# -----------------------------
FROM node:18-alpine AS frontend-builder

# Set working directory
WORKDIR /app

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm install

# Copy frontend source code
COPY frontend/ ./

# Build React app
RUN npm run build

# -----------------------------
# Stage 2: Build Backend + Copy Frontend Build
# -----------------------------
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend

# Copy frontend build from previous stage
COPY --from=frontend-builder /app/build ./backend/frontend/build

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
