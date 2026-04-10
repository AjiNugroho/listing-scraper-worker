# Scraper Worker Docker Setup

This project contains a Dockerized version of the scraper worker that runs two Celery workers automatically when the container starts.

## Prerequisites

- Docker Desktop installed
- Docker Compose installed

## Setup

1. Ensure you have your `.env` file with all required environment variables
2. Make sure `instagram_cookies.json` exists in the project root (this will be created automatically after successful login)

## Running the Application

### Using Docker Compose (Recommended)

```bash
# Build and start the containers
docker compose up -d

# View logs
docker compose logs -f

# Stop the containers
docker compose down
```

### Using Docker directly

```bash
# Build the image
docker build -t scraper-worker .

# Run the container
docker run -d --env-file .env -v $(pwd)/instagram_cookies.json:/app/instagram_cookies.json --name scraper-worker scraper-worker
```

## Workers

The application runs two Celery workers:

1. **Request Worker**: 
   - Queue: `scrape_request_listing`
   - Concurrency: 1
   - Name: `request@hostname`

2. **Response Worker**:
   - Queue: `scrape_response_listing`
   - Concurrency: 2
   - Name: `response@hostname`

## Important Notes

- The container will automatically restart unless stopped manually (`restart: unless-stopped`)
- The `instagram_cookies.json` file is mounted as a volume so cookies persist between container restarts
- All environment variables are loaded from the `.env` file