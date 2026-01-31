import asyncio
import json
import os
from celery import shared_task
from kombu import Producer, Connection
from dotenv import load_dotenv
import requests

from scraper.instagram_scraper import InstagramScraper

load_dotenv()

CLOUDAMQP_URL = os.getenv("CLOUDAMQP_URL")
RESPONSE_QUEUE = os.getenv("SCRAPER_RESPONSE_QUEUE","scrape_response_listing")

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


from celery_app import celery_app

@shared_task(bind=True, name="run_instagram_listing_scraper")
def run_instagram_listing_scraper(self, payload: dict):
    """
    Payload example:
    {
        "url": "https://www.instagram.com/mop.beauty/tagged/",
        "max_item": 100
    }
    """
    print(payload)

    target_url = payload["url"]
    max_item = payload["max_item"]

    scraper = InstagramScraper(
        username=INSTAGRAM_USERNAME,
        password=INSTAGRAM_PASSWORD,
    )

    

    # ---- run async scraper safely inside celery ----
    posts = asyncio.run(
        scraper.run(
            target_url=target_url,
            max_posts=max_item,
        )
    )

    print(f"✓ Scraped {len(posts)} posts from {target_url}")


    result = {
        "url": target_url,
        "requested_max_item": max_item,
        "collected": len(posts),
        "posts": posts,
        "status": "completed",
        "webhook_endpoint": payload.get("webhook_endpoint","no-webhook"),
    }

    # ---- publish result to response queue ----
    celery_app.send_task(
        'handle_scrape_response',
        kwargs={'payload': result},  
        queue='scrape_response_listing'
    )

    return True
