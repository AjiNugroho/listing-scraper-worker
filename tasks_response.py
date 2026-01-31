from celery import shared_task
import requests
from requests.exceptions import RequestException

MAX_RETRIES = 3

@shared_task(
    name="handle_scrape_response",
    bind=True,
    autoretry_for=(RequestException,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=5,
    default_retry_delay=60
)
def handle_scrape_response(self, payload: dict):
    url = "https://api.brightdata.com/datasets/v3/trigger"
    headers = {
        "Authorization": "Bearer 1025af24-494a-4249-8b75-14c5aa71e0ac",
        "Content-Type": "application/json",
    }
    content_type = payload.get("content_type", "post")
    webhookendpoint = payload.get("webhook_endpoint", "no-webhook")

    # retry_count = payload.get('retry_count', 0)


    # if retry_count > MAX_RETRIES:
    #     print(f"Max retries exceeded for dropping message")
    #     failed_posts = payload.get("posts", [])
    #     webhookendpoint = payload.get("webhook_endpoint", "no-webhook")
    #     # write to csv
    #     with open("failed_posts.csv", "a") as f:
    #         for post in failed_posts:
    #             f.write(f"{post},{webhookendpoint}\n")

    #     return

    params_post = {
        "dataset_id": "gd_lk5ns7kz21pck8jpis",
        "endpoint": webhookendpoint,
        "format": "json",
        "uncompressed_webhook": "true",
        "include_errors": "true",
    }

    params_reel = {
        "dataset_id": "gd_lyclm20il4r5helnj",
        "endpoint": webhookendpoint,
        "format": "json",
        "uncompressed_webhook": "true",
        "include_errors": "true",
    }

    params = params_reel if content_type == 'reel' else params_post
    total_collected_post = payload["collected"]
    posts = payload["posts"]

    failed_chunks = []

    # Loop through posts in chunks
    for chunk in range(0, total_collected_post, 50):
        data = posts[chunk:chunk + 50]
        posts_data = [{"url": post_url} for post_url in data]

        try:
            response = requests.post(
                url, 
                headers=headers, 
                params=params, 
                json=posts_data,
                timeout=30
            )
            
            # Check for 502 or other server errors
            if response.status_code == 502:
                print(f"✗ Got 502 Bad Gateway for chunk {chunk}. Will retry entire task.")
                raise self.retry(
                    exc=RequestException(f"502 Bad Gateway for chunk {chunk}"),
                    countdown=60
                )
            
            # Raise exception for other non-200 status codes
            response.raise_for_status()
            
            print(f"✓ Successfully sent chunk starting at index {chunk} to Brightdata.")
            
        except requests.exceptions.Timeout as e:
            print(f"✗ Timeout for chunk {chunk}. Will retry.")
            raise self.retry(exc=e, countdown=30)
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed for chunk {chunk}: {str(e)}")
            # Track failed chunks for potential partial retry
            failed_chunks.append(chunk)
            
            # If it's a server error (5xx), retry the entire task
            if hasattr(e.response, 'status_code') and 500 <= e.response.status_code < 600:
                raise self.retry(exc=e, countdown=60)
            else:
                # For client errors (4xx), log and continue to next chunk
                print(f"  Client error - continuing to next chunk")
                continue

    # If we had failures, log them
    if failed_chunks:
        print(f"⚠ Completed with {len(failed_chunks)} failed chunks: {failed_chunks}")
        return {"status": "partial_success", "failed_chunks": failed_chunks}
    
    return True