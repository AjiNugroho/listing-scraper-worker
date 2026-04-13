FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirement.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirement.txt

# Install Playwright system dependencies and browsers into a shared path
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN pip install playwright && \
    playwright install-deps chromium && \
    playwright install chromium && \
    chmod -R 755 /ms-playwright

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x /app/startup.sh

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose ports if needed (though not typically required for Celery)
EXPOSE 8000

# Health check
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1

# Start both Celery workers using startup script
CMD ["/app/startup.sh"]