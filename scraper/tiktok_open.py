import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser, Route
from typing import Set, List
from datetime import datetime

class TikTokScraperNoLogin:
    def __init__(self,cookies_file: str = "tiktok_cookies.json"):
        self.browser: Browser = None
        self.page: Page = None
        self.collected_urls: Set[str] = set()
        self.xhr_responses: List[dict] = []
        self.xhr_interception_active = False
        self.cookies_file = cookies_file
        
    async def init_browser(self):
        """Initialize browser with persistent context"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=False,  # Set to True for production
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = await context.new_page()
        await self.load_cookies()
        # Visit homepage first
        await self.visit_homepage()
    
    async def visit_homepage(self):
        """Visit TikTok homepage on startup"""
        print("\n" + "="*60)
        print("Visiting TikTok homepage...")
        print("="*60)
        
        await self.page.goto('https://www.tiktok.com/', wait_until='domcontentloaded')
        await asyncio.sleep(30)
        
        # Handle cookie consent if appears
        # try:
        #     cookie_accept = await self.page.query_selector('button:has-text("Accept all")')
        #     if cookie_accept:
        #         print("→ Accepting cookies...")
        #         await cookie_accept.click()
        #         await self.page.wait_for_timeout(2000)
        # except:
        #     pass
        
        # # Close any popup if appears
        # try:
        #     close_button = await self.page.query_selector('button[aria-label="Close"]')
        #     if close_button:
        #         print("→ Closing popup...")
        #         await close_button.click()
        #         await self.page.wait_for_timeout(1000)
        # except:
        #     pass
        await self.save_cookies()
        print("✓ Homepage loaded successfully\n")
    
    async def setup_xhr_interception(self):
        """Set up XHR interception for API responses"""
        if self.xhr_interception_active:
            return
        
        async def handle_route(route: Route):
            # Continue the request
            response = await route.fetch()
            
            # Check if it's the target API
            if 'api/search/general/full/' in route.request.url:
                try:
                    # Get response body
                    body = await response.json()
                    
                    # Store the response data
                    self.xhr_responses.append({
                        'url': route.request.url,
                        'timestamp': datetime.now().isoformat(),
                        'data': body
                    })
                    
                    print(f"✓ Captured XHR response from: {route.request.url[:80]}...")
                    
                except Exception as e:
                    print(f"✗ Error parsing XHR response: {e}")
            
            # Continue with the response
            await route.fulfill(response=response)
        
        # Intercept all requests matching the pattern
        await self.page.route("**/*", handle_route)
        self.xhr_interception_active = True
        print("✓ XHR interception enabled\n")
    
    async def smooth_scroll(self):
        """Perform smooth scroll down"""
        await self.page.evaluate("""
            () => {
                return new Promise((resolve) => {
                    const distance = 800; // pixels to scroll
                    const duration = 1000; // ms
                    const start = window.pageYOffset;
                    const startTime = performance.now();
                    
                    function easeInOutQuad(t) {
                        return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
                    }
                    
                    function scroll() {
                        const currentTime = performance.now();
                        const elapsed = currentTime - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        
                        window.scrollTo(0, start + distance * easeInOutQuad(progress));
                        
                        if (progress < 1) {
                            requestAnimationFrame(scroll);
                        } else {
                            resolve();
                        }
                    }
                    
                    scroll();
                });
            }
        """)
    
    async def extract_video_urls(self) -> Set[str]:
        """Extract video URLs from current viewport"""
        urls = await self.page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a[href*="/video/"]'));
                return links
                    .map(link => link.href)
                    .filter(href => href.includes('/video/'));
            }
        """)
        return set(urls)
    
    async def scroll_and_collect(self, url: str, max_items: int = 50, scroll_delay: int = 3):
        """
        Scroll page and collect video URLs until max_items reached
        Args:
            url: TikTok page URL to scrape
            max_items: Maximum number of items to collect
            scroll_delay: Delay in seconds between scrolls
        """
        print(f"{'='*60}")
        print(f"Starting collection from: {url}")
        print(f"Target: {max_items} items | Scroll delay: {scroll_delay}s")
        print(f"{'='*60}\n")
        
        # Set up XHR interception AFTER visiting target URL
        print("→ Navigating to target URL...")

        await self.load_cookies()
        await self.page.goto(url, wait_until='domcontentloaded')
        await asyncio.sleep(15)
        
        # Now enable XHR interception
        await self.setup_xhr_interception()
        
        # Handle any popups
        
        
        scroll_count = 0
        no_new_items_count = 0
        max_no_new_items = 5  # Stop if no new items after 5 scrolls
        
        while len(self.collected_urls) < max_items:
            # Extract URLs from current viewport
            new_urls = await self.extract_video_urls()
            
            # Get only new URLs
            before_count = len(self.collected_urls)
            self.collected_urls.update(new_urls)
            after_count = len(self.collected_urls)
            new_count = after_count - before_count
            
            scroll_count += 1
            
            print(f"Scroll #{scroll_count}: Found {new_count} new items | Total: {len(self.collected_urls)}/{max_items}")
            
            # Check if we found new items
            if new_count == 0:
                no_new_items_count += 1
                print(f"  ⚠️  No new items found ({no_new_items_count}/{max_no_new_items})")
                
                if no_new_items_count >= max_no_new_items:
                    print(f"\n⚠️  Stopped: No new items after {max_no_new_items} consecutive scrolls")
                    break
            else:
                no_new_items_count = 0  # Reset counter
            
            # Check if we reached the limit
            if len(self.collected_urls) >= max_items:
                print(f"\n✓ Reached maximum items limit: {max_items}")
                break
            
            # Smooth scroll down
            await self.smooth_scroll()
            
            # Wait before next scroll
            print(f"  ⏳ Waiting {scroll_delay} seconds before next scroll...")
            await self.page.wait_for_timeout(scroll_delay * 1000)
        
        print(f"\n{'='*60}")
        print(f"Collection completed!")
        print(f"Total unique URLs collected: {len(self.collected_urls)}")
        print(f"Total XHR responses captured: {len(self.xhr_responses)}")
        print(f"{'='*60}\n")
        
        return self.collected_urls
    
    async def save_xhr_data(self, filename: str = None):
        """Save captured XHR data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tiktok_xhr_data_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.xhr_responses, f, indent=2, ensure_ascii=False)
            print(f"✓ XHR data saved to {filename}")
            print(f"  Total responses saved: {len(self.xhr_responses)}")
        except Exception as e:
            print(f"✗ Error saving XHR data: {e}")
    
    async def save_collected_urls(self, filename: str = None):
        """Save collected URLs to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tiktok_urls_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(list(self.collected_urls), f, indent=2, ensure_ascii=False)
            print(f"✓ URLs saved to {filename}")
            print(f"  Total URLs saved: {len(self.collected_urls)}")
        except Exception as e:
            print(f"✗ Error saving URLs: {e}")
    
    async def scrape_video(self, url: str) -> dict:
        """
        Scrape a TikTok video
        Args:
            url: TikTok video URL
        Returns:
            dict with video data
        """
        print(f"\nScraping video: {url}")
        await self.page.goto(url, wait_until='domcontentloaded')
        await self.page.wait_for_timeout(3000)
        
        video_data = {}
        
        try:
            # Extract video description
            desc_selector = 'h1[data-e2e="browse-video-desc"]'
            description = await self.page.text_content(desc_selector)
            video_data['description'] = description.strip() if description else None
            
            # Extract author username
            author_selector = 'a[data-e2e="browse-username"]'
            author = await self.page.text_content(author_selector)
            video_data['author'] = author.strip() if author else None
            
            # Extract likes count
            likes_selector = 'strong[data-e2e="like-count"]'
            likes = await self.page.text_content(likes_selector)
            video_data['likes'] = likes.strip() if likes else None
            
            # Extract comments count
            comments_selector = 'strong[data-e2e="comment-count"]'
            comments = await self.page.text_content(comments_selector)
            video_data['comments'] = comments.strip() if comments else None
            
            # Extract shares count
            shares_selector = 'strong[data-e2e="share-count"]'
            shares = await self.page.text_content(shares_selector)
            video_data['shares'] = shares.strip() if shares else None
            
            video_data['url'] = url
            video_data['success'] = True
            
            print("\n✓ Video data extracted successfully:")
            for key, value in video_data.items():
                print(f"  {key}: {value}")
                
        except Exception as e:
            print(f"\n✗ Error extracting video data: {e}")
            video_data['success'] = False
            video_data['error'] = str(e)
        
        return video_data
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            print("\n✓ Browser closed")

    async def load_cookies(self):
        """Load cookies from file"""
        try:
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
            await self.page.context.add_cookies(cookies)
            print(f"✓ Cookies loaded from {self.cookies_file}")
        except Exception as e:
            print(f"✗ Failed to load cookies: {e}")

    async def save_cookies(self):
        cookies = await self.page.context.cookies()
        with open(self.cookies_file, "w") as f:
            json.dump(cookies, f, indent=2)
async def main():
    """Example usage"""
    scraper = TikTokScraperNoLogin()
    
    try:
        # Initialize browser - will automatically visit homepage first
        await scraper.init_browser()
        
        # Example: Scroll and collect URLs from a search or profile page
        # Replace with actual TikTok URL (search results, hashtag, or profile)
        target_url = "https://vt.tiktok.com/ZS91HbAnVpoyQ-EyPwB/"  # Example: search results
        # target_url = "https://www.tiktok.com/@username"  # Example: profile page
        # target_url = "https://www.tiktok.com/tag/cooking"  # Example: hashtag page
        
        # Scroll and collect up to 50 video URLs with 2 second delay between scrolls
        await scraper.scroll_and_collect(
            url=target_url,
            max_items=50,
            scroll_delay=2
        )
        
        # Save collected URLs to file
        await scraper.save_collected_urls()
        
        # Save XHR data to file
        await scraper.save_xhr_data()
        
        # Example: Optionally scrape individual videos
        # for url in list(scraper.collected_urls)[:5]:  # Scrape first 5 videos
        #     video_data = await scraper.scrape_video(url)
        #     await asyncio.sleep(2)
        
        print("\n✓ All operations completed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())