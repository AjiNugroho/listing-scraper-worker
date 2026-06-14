FROM python:3.11-slim

WORKDIR /app

# System deps: Xvfb + everything Chromium needs
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    xvfb \
    fonts-liberation \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

# Install Playwright + Chromium as root so deps install cleanly
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN pip install playwright && \
    playwright install-deps chromium && \
    playwright install chromium

COPY . .
RUN chmod +x /app/startup.sh

# Pre-create X11 socket dir so Xvfb can run as non-root
RUN mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix

# Create non-root user and fix ownership of both /app and /ms-playwright
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app /ms-playwright

USER appuser

CMD ["/app/startup.sh"]