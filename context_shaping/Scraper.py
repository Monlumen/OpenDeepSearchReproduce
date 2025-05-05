from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai import DefaultMarkdownGenerator, PruningContentFilter, CacheMode
from typing import Union, Callable
import asyncio
from .scraper_utils import clean_text, filter_text_by_value
import wikipediaapi
from tenacity import retry, stop_after_attempt, wait_fixed
from asyncio import Semaphore


class ScrapeResult:
    def __init__(self, info: Union[str, Exception]):
        if isinstance(info, Exception):
            self.success = False
            self.error = str(info)
            self.content = ""
        else:
            self.success = True
            self.error = ""
            self.content = info

class Scraper:
    def __init__(self, browser_config: BrowserConfig=None, use_filter: bool=True):
        self.browser_config = browser_config or BrowserConfig(
            headless=True, verbose=True
        )
        self.use_filter = use_filter
        self.wiki = wikipediaapi.Wikipedia("opendeepresearch")
    
    # @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def scrape(self, url: str, filter_by_value: bool = True) -> ScrapeResult:
        if "wikipedia.org/wiki/" in url:
            page = self.wiki.page(url.split("/wiki/")[-1])
            if page.exists:
                return ScrapeResult(page.text)
            
        crawler_config = CrawlerRunConfig(
            markdown_generator=DefaultMarkdownGenerator(PruningContentFilter()),
            cache_mode=CacheMode.BYPASS
        )

        try:
            async with AsyncWebCrawler(config=self.browser_config) as crawler:
                response = await asyncio.wait_for(crawler.arun(url, crawler_config), timeout=30)
        except Exception as e:
            print("exception when crawling:" + str(e))
            response = None

        # handling content
        result = ScrapeResult("")
        try:
            if response and response.success:
                content = str(response.markdown.raw_markdown)
                if self.use_filter:
                    content = clean_text(content)
                    if filter_by_value:
                        content = filter_text_by_value(content)
                result = ScrapeResult(content)
            else:
                result = ScrapeResult(Exception(response.__dict__ if response else ""))
        except Exception as e:
            result = ScrapeResult(e)
        return result

    
if __name__ == "__main__":
    scraper = Scraper()
    url = "https://en.wikipedia.org/wiki/London"
    print(asyncio.run(scraper.scrape(url)).content)
