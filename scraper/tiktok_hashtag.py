from TikTokApi import TikTokApi
import asyncio
import os

ms_token = os.environ.get("ms_token", "oY7zKdPrJlXOMJNHFQnEI0Y3Zt97a1TaxNnn3D7Qgvj7V87VYhHOl56ias8ipn9ENAY1VrIsPNm7lXZkfmKFfJwknmJUjrBUTTVyy19OqvuPsruOorzILV_gpRH4j6k")  # set your own ms_token


async def get_hashtag_videos():
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=3,
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
        )
        tag = api.hashtag(name="wardah")
        async for video in tag.videos(count=30):
            print(video)
            print(video.as_dict)


if __name__ == "__main__":
    asyncio.run(get_hashtag_videos())