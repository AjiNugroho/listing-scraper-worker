import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

CLOUDAMQP_URL = os.getenv("CLOUDAMQP_URL")

celery_app = Celery(
    "scraper_worker",
    broker=CLOUDAMQP_URL,
    backend=None,  # no result backend needed
    include=['tasks_request', 'tasks_response']
)

celery_app.conf.update(
    task_routes={
        "run_instagram_listing_scraper": {
            "queue": "scrape_request_listing",
        },
        "handle_scrape_response": {
            "queue": "scrape_response_listing",
        },
    },
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


