import dotenv
import os
from .Serper import SearchSources
from typing import Dict, List, Callable
from .Scraper import Scraper, ScrapeResult
import asyncio
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .rerankers import PureJinaReranker
import re

dotenv.load_dotenv()

class SourceProcessor:

    def __init__(self, jina_api_key: str=None, length_funciton: Callable[[str], int]=len):
        self.scraper = Scraper()
        self.chunker = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=50, separators=["\n\n", "\n"],
                                                      length_function=length_funciton)
        self.reranker = PureJinaReranker(jina_api_key)
        

    async def process_sources(self, sources: SearchSources, query: str, num_scrapes: int = 2, pro_mode: bool=False) -> SearchSources:
        try:
            if pro_mode:
                valid_sources = SourceProcessor._get_valid_sources(sources, num_scrapes)
            else:
                valid_sources = [(idx, entry) for idx, entry in enumerate(sources.organic) 
                                if entry and entry["link"] and ("wikipedia.org/wiki/" in entry["link"])]
                
            if not valid_sources:
                return sources
            scrape_tasks = [self.scraper.scrape(source["link"]) for idx, source in valid_sources]
            scrape_results: List[ScrapeResult] = await asyncio.gather(*scrape_tasks)
            self._update_sources_by_html(valid_sources, 
                                        [result.content for result in scrape_results],
                                        query)
        except Exception as e:
            print("error when processing sources: " + str(e))
        return sources
    
    @staticmethod
    def _get_valid_sources(sources: SearchSources, num_scrapes: int=2) -> List[tuple[int, Dict]]:
        return [(idx, entry) for idx, entry in enumerate(sources.organic) if entry and entry["link"]][:num_scrapes]
    
    def _update_sources_by_html(self, valid_sources: List[tuple[int, Dict]], htmls: List[str], query: str):
        for (idx, organic), html in zip(valid_sources, htmls):
            documents = self.chunker.split_text(html)
            reranked_documents = self.reranker.rerank(query, documents)
            organic["html"] = re.sub("\n+", "\n", "\n".join(reranked_documents))
    
