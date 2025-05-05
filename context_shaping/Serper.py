import requests
import dotenv
import os
from typing import List, Dict, Union
from dataclasses import dataclass

dotenv.load_dotenv()
SERPER_BASE_URL = "https://google.serper.dev/search"


@dataclass
class SearchSources:
    organic: List[Dict]
    top_stories: List[str]
    answer_box: Dict

def filter_dict(dict: Union[Dict, List[Dict]], fields: List[str]) -> Union[Dict, List[Dict]]:
    if isinstance(dict, List):
        return [filter_dict(dict_element, fields) for dict_element in dict]
    else:
        return {key: dict[key] for key in fields if key in dict}

class SerperAPI:

    def __init__(self, serper_api_key: str=None, serper_base_url: str=SERPER_BASE_URL):
        self.serper_api_key = serper_api_key or os.getenv("SERPER_API_KEY")
        assert self.serper_api_key
        self.serper_base_url = serper_base_url

    def get_sources(self, query: str, num_sources=8, glb_pos="US") -> SearchSources:
        try:
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": max(1, min(num_sources, 10)),
                "gl": glb_pos.lower()
            }
            conversation = requests.post(self.serper_base_url, headers=headers, json=payload)
            conversation.raise_for_status()
            response = conversation.json()
            organic = filter_dict(response["organic"], [
                "title", "date", "link", "snippet"
            ])
            top_stories = [dict["title"] for dict in response.get("topStories", [])]
            answer_box = response.get("answerBox", None)
            if answer_box:
                print(answer_box)
                print("----")
            return SearchSources(organic, top_stories, answer_box)
        except Exception as e:
            print(f"Warning: Exception Encountered when searching: {str(e)}")
            return SearchSources([], [], None)

