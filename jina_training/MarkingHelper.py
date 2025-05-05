import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from context_shaping.Serper import SerperAPI
from context_shaping.Scraper import Scraper
from random import shuffle
import asyncio
import json
from litellm import completion
import re
import random

class MarkingHelper:
    def __init__(self, serper_api_key: str=None, n_links_per_query: int = 2, output_path="value_examples.jsonl", searched_query_path="searched_queries.txt", translating_model="openrouter/google/gemini-2.0-flash-001") -> None:
        self.serper = SerperAPI(serper_api_key)
        self.scraper = Scraper()
        self.search_queries = []
        self.links = []
        self.paragraphs = []
        self.n_links_per_query = n_links_per_query
        self.output_path = output_path
        self.translating_model = translating_model
        self.searched_query_path = searched_query_path
        self.searched_queries = set()
        if os.path.exists(searched_query_path):
            with open(searched_query_path, "r", encoding="utf-8") as f:
                self.searched_queries = set([line.strip() for line in f if line.strip()])
    
    def get_a_link(self) -> str:
        while (not self.links) and self.search_queries:
            query = None
            while (not query) and self.search_queries:
                query = self.search_queries[0]
                self.search_queries = self.search_queries[1:]
                if query.strip() in self.searched_queries:
                    query = None
            if query:
                with open(self.searched_query_path, "a", encoding="utf-8") as f:
                    f.write(query.strip() + "\n")
                search_sources = self.serper.get_sources(query)
                self.links.extend(dict["link"] for dict in search_sources.organic if ("link" in dict) and ("wikipedia" not in dict["link"]))
        if self.links:
            link = self.links[0]
            self.links = self.links[1:]
            return link
        else:
            return None
        
    def load_search_queries(self, path="search_queries.txt"):
        with open(path, "r", encoding="utf-8") as f:
            self.search_queries += [line.strip() for line in f if line.strip()]
        shuffle(self.search_queries)
    
    def get_a_paragraph(self) -> str:
        while not self.paragraphs:
            link = self.get_a_link()
            if not link:
                print("Queries, Links, Paragraphs all used up")
                return None
            text = asyncio.run(self.scraper.scrape(link, filter_by_value=False))
            separator = "\n\n"
            paragraphs = [paragraph.strip() for paragraph in text.content.split(separator) if paragraph.strip()]
            if paragraphs:
                self.paragraphs.extend(paragraphs)
        paragraph = self.paragraphs[0]
        self.paragraphs = self.paragraphs[1:]
        return paragraph

    def run(self):
        idx = 0
        paragraph = self.get_a_paragraph()
        while paragraph:
            idx += 1
            print(f"------------ please evaluate {idx} ------------")
            print(paragraph)
            print("y for 'Useful Information', n for 'Useless Information', j for jump, t for translation")
            ch = None
            while ch != 'y' and ch != 'n' and ch != 'j':
                ch = input("y/n: ")
                if ch == 't':
                    translation = completion(self.translating_model, [
                        {"role": "user", "content": "请将以下内容精准直译为中文:" + paragraph}
                    ]).choices[0].message.content
                    print(translation)
                    print("y for 'Useful Information', n for 'Useless Information', j for jump, t for translation")
            if ch == 'j':
                self.links = []
                self.paragraphs = []
                paragraph = self.get_a_paragraph()
                continue
            if ch == 'y':
                self.log_example(paragraph, "Useful Information")
            else:
                self.log_example(paragraph, "Useless Information")
            paragraph = self.get_a_paragraph()

    def log_example(self, text: str, label: str):
        with open(self.output_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "text": text,
                "label": label
            }, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    helper = MarkingHelper()
    helper.load_search_queries()
    helper.run()
        