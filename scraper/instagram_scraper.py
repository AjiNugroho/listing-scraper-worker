import asyncio
import json
import os
from playwright.async_api import async_playwright
import time

class InstagramScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cookies_file = "instagram_cookies.json"
        self.post_urls = []
        
    async def save_cookies(self, context):
        """Save cookies to file"""
        cookies = await context.cookies()
        with open(self.cookies_file, 'w') as f:
            json.dump(cookies, f)
        print("✓ Cookies saved")
    
    async def load_cookies(self, context):
        """Load cookies from file if exists"""
        if os.path.exists(self.cookies_file):
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)
            print("✓ Cookies loaded")
            return True
        return False
    
    async def is_logged_in(self, page):
        """Check if user is logged in"""
        await page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        # Check if we see login form or user profile elements
        login_form = await page.locator('input[name="username"]').count()
        return login_form == 0
    
    async def login(self, page):
        """Login to Instagram"""
        print("→ Navigating to login page...")
        await page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
        await asyncio.sleep(4)
        
        # Fill username
        print("→ Entering username...")
        await page.fill('input[name="username"]', self.username)
        await asyncio.sleep(4)
        
        # Fill password
        print("→ Entering password...")
        await page.fill('input[name="password"]', self.password)
        await asyncio.sleep(4)
        
        # Click login button
        print("→ Clicking login...")
        await page.click('button[type="submit"]')
        
        # Wait for navigation
        await asyncio.sleep(5)
        
        # Handle "Save Login Info" prompt if appears
        try:
            save_info_button = page.locator('button:has-text("Not Now")').first
            if await save_info_button.count() > 0:
                await save_info_button.click()
                await asyncio.sleep(2)
        except:
            pass
        
        # Handle "Turn on Notifications" prompt if appears
        try:
            notif_button = page.locator('button:has-text("Not Now")').first
            if await notif_button.count() > 0:
                await notif_button.click()
                await asyncio.sleep(2)
        except:
            pass
        
        print("✓ Login completed")
    
    async def scrape_posts(self, page, target_url, max_posts=100):
        """Scrape post URLs from a profile or hashtag page"""
        print(f"→ Navigating to {target_url}...")
        await page.goto(target_url, wait_until="domcontentloaded")
        
        # Wait for posts to appear
        print("→ Waiting for posts to load...")
        try:
            await page.wait_for_selector('a[href*="/p/"], a[href*="/reel/"]', timeout=10000)
            print("✓ Posts loaded")
        except:
            print("⚠ Posts not found, attempting to continue anyway...")
        
        await asyncio.sleep(2)
        
        print(f"→ Scrolling and collecting posts (target: {max_posts} posts)...")
        
        post_urls_set = set()  # Use set to automatically handle duplicates
        previous_count = 0
        no_new_posts_count = 0
        
        while len(post_urls_set) < max_posts:
            # Get all post links on current page
            # Instagram post URLs typically match pattern /p/ or /reel/
            links = await page.locator('a[href*="/p/"], a[href*="/reel/"]').all()
            
            for link in links:
                href = await link.get_attribute('href')
                if href:
                    # Convert to full URL if needed
                    if href.startswith('/'):
                        href = f"https://www.instagram.com{href}"
                    
                    # Remove query parameters to avoid duplicates
                    href = href.split('?')[0]
                    href = href.replace('/reel/','/p/')
                    post_urls_set.add(href)
                    
                    if len(post_urls_set) >= max_posts:
                        break
            
            current_count = len(post_urls_set)
            print(f"  Collected: {current_count} unique posts")
            
            # Check if we got new posts
            if current_count == previous_count:
                no_new_posts_count += 1
                if no_new_posts_count >= 3:
                    print("  No new posts found after 3 scrolls. Stopping.")
                    break
            else:
                no_new_posts_count = 0
            
            previous_count = current_count
            
            if len(post_urls_set) >= max_posts:
                break
            
            # Get current scroll position before scrolling
            prev_height = await page.evaluate("document.body.scrollHeight")
            
            # Smooth scroll to 90% of page height
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)  # Small delay for scroll animation
            
            # Wait for new content to load (max 5 seconds)
            try:
                for _ in range(10):  # Check 10 times (0.5s each = 5s total)
                    await asyncio.sleep(0.5)
                    new_height = await page.evaluate("document.body.scrollHeight")
                    if new_height > prev_height:
                        print("  ✓ New content loaded")
                        break
            except:
                pass
            
            await asyncio.sleep(2)  # Additional delay between scrolls
        
        # Convert set back to list
        self.post_urls = list(post_urls_set)
        
        print(f"✓ Scraping completed! Total unique posts collected: {len(self.post_urls)}")
    
    async def run(self, target_url, max_posts=100):
        """Main execution method"""
        async with async_playwright() as p:
            # Launch browser (headless=False to see what's happening)
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            await self.block_media(page)
            # Try to load existing cookies
            cookies_loaded = await self.load_cookies(context)
            
            # Check if logged in
            if cookies_loaded:
                print("→ Checking session...")
                logged_in = await self.is_logged_in(page)
            else:
                logged_in = False
            
            # Login if needed
            if not logged_in:
                print("⚠ Session not available. Logging in...")
                await self.login(page)
                await self.save_cookies(context)
            else:
                print("✓ Session is active!")
            
            # Scrape posts
            await self.scrape_posts(page, target_url, max_posts)
            
            # # Save results
            # with open('scraped_posts.json', 'w') as f:
            #     json.dump(self.post_urls, f, indent=2)
            # print(f"✓ Results saved to scraped_posts.json")
            
            # Keep browser open for a moment
            await asyncio.sleep(2)
            await browser.close()
        
        return self.post_urls
    
    async def block_media(self, page):
        async def route_handler(route, request):
            if request.resource_type in ["image", "media", "font"]:
                await route.abort()
            else:
                await route.continue_()

        await page.route("**/*", route_handler)

    # async def attach_request_logger(self, page):
    #     async def on_request(request):
    #         if (
    #             request.url == "https://www.instagram.com/graphql/query"
    #             and request.method == "POST"
    #         ):
    #             print("\n" + "=" * 80)
    #             print("📡 INSTAGRAM GRAPHQL REQUEST")
    #             print("URL:", request.url)
    #             print("METHOD:", request.method)

    #             print("\n--- HEADERS ---")
    #             for k, v in request.headers.items():
    #                 print(f"{k}: {v}")

    #             print("\n--- PAYLOAD ---")
    #             print(request.post_data)
    #             print("=" * 80 + "\n")

    #     page.on("request", on_request)


async def main():
    # Configure your credentials
    USERNAME = "charged_lipo"
    PASSWORD = "16Juli1997"
    TARGET_URL = "https://www.instagram.com/mop.beauty/tagged/"
    
    # Maximum posts to collect
    MAX_POSTS = 20
    
    scraper = InstagramScraper(USERNAME, PASSWORD)
    posts = await scraper.run(TARGET_URL, MAX_POSTS)
    
    print(f"\n{'='*50}")
    print(f"Scraped {len(posts)} post URLs:")
    for i, url in enumerate(posts[:5], 1):  # Show first 5
        print(f"{i}. {url}")
    if len(posts) > 5:
        print(f"... and {len(posts) - 5} more")


if __name__ == "__main__":
    asyncio.run(main())