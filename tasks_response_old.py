from celery import shared_task
import requests

@shared_task(name="handle_scrape_response")
def handle_scrape_response(payload: dict):
    """
    payload example:
    {
      "url": "...",
      "posts": [...],
      "collected": 100,
      "status": "completed"
    }
    """

    url = "https://api.brightdata.com/datasets/v3/trigger"
    headers = {
        "Authorization": "Bearer 1025af24-494a-4249-8b75-14c5aa71e0ac",
        "Content-Type": "application/json",
    }
    content_type = payload.get("content_type","post")
    
    webhookendpoint = payload.get("webhook_endpoint","no-webhook")

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
    # chuckt the posts into separate requests to avoid payload size limits
    total_collected_post = payload["collected"]
    posts = payload["posts"]
    # loop posts
    for chunk in range(0, total_collected_post, 50):
        data = posts[chunk:chunk + 50]
        
        posts_data = []

        for post_url in data:
            posts_data.append({
                "url": post_url
        })

        
        response = requests.post(url, headers=headers, params=params, json=posts_data)
        if(response.status_code == 200):
            print(f"✓ Successfully sent chunk starting at index {chunk} to Brightdata.")
        else:
            print(f"✗ Failed to send chunk starting at index {chunk}. Status code: {response.status_code}, Response: {response.text}")


    
    return True