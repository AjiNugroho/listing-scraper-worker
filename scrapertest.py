import requests
import json

headers = {
    "Authorization": "Bearer abaafc8c-1859-4e9c-949c-5d18220b7b2b",
    "Content-Type": "application/json",
}

data = json.dumps({
    "input": [{"url":"https://www.instagram.com/p/DRlhTDLj0-B/"}],
})

response = requests.post(
    "https://api.brightdata.com/datasets/v3/trigger?dataset_id=gd_lk5ns7kz21pck8jpis&endpoint=https%3A%2F%2Ffair-studio.com%2Fwebhook&notify=false&format=json&uncompressed_webhook=true&force_deliver=false&include_errors=true",
    headers=headers,
    data=data
)
print(response.text)
print(response.json())