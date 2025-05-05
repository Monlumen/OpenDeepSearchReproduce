from abc import ABC, abstractmethod
from typing import List, Union
import fasttext
from huggingface_hub import hf_hub_download
import re
import dotenv
import os
import requests

dotenv.load_dotenv()

JINA_CLASSIFIER_ID = "8a7f3888-a69f-48f3-8f41-323163197457"
JINA_CLASSIFY_BASE_URL = 'https://api.jina.ai/v1/classify'

class TextFilter(ABC):
    def filter(self, texts: List[str]) -> List[str]:
        pass

class LocalFastTextFilter(TextFilter):
    def __init__(self, quality_scores_requirement: float=0.2) -> None:
        super().__init__()
        self.value_model = fasttext.load_model(hf_hub_download("kenhktsui/llm-data-textbook-quality-fasttext-classifer-v2", "model_quantized.bin"))
        self.quality_scores_requirement = quality_scores_requirement
    
    @staticmethod
    def remove_new_lines(text: Union[str, List[str]]) -> Union[str, List[str]]:
        if isinstance(text, list):
            return [LocalFastTextFilter.remove_new_lines(element) for element in text]
        else:
            return re.sub("\n+", "", text)

    def filter(self, texts: List[str]) -> List[str]:
        results = []
        all_labels, all_probs = self.value_model.predict(LocalFastTextFilter.remove_new_lines(texts), k=-1)
        for idx, paragraph in enumerate(texts):
            labels = all_labels[idx]
            probs = all_probs[idx]
            scores = 0
            for label, prob in zip(labels, probs):
                if "High" in label:
                    scores += prob * 2
                elif "Mid" in label:
                    scores += prob
            if scores >= self.quality_scores_requirement:
                results.append(paragraph)
        return results
    
class JinaTextFilter(TextFilter):
    def __init__(self, jina_api_key: str=None, jina_base_url: str=JINA_CLASSIFY_BASE_URL, jina_classifer_id: str=JINA_CLASSIFIER_ID) -> None:
        super().__init__()
        self.jina_api_key = jina_api_key or os.getenv("JINA_API_KEY")
        self.jina_base_url = jina_base_url
        self.jina_classifier_id = jina_classifer_id

    def filter(self, texts: List[str]) -> List[str]:
        truncate = 1000
        available_retries = 2
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.jina_api_key
        }
        while available_retries:
            try:
                payload = {
                    "classifier_id": self.jina_classifier_id,
                    "input": [text[:truncate] for text in texts]
                }
                response = requests.post(self.jina_base_url, headers=headers, json=payload)
                response.raise_for_status()
                response_json = response.json()
                return [text for text, dict in zip(texts, response_json["data"]) if "Useful" in dict["prediction"]]
            
            except requests.HTTPError as e:
                available_retries -= 1
                truncate -= 100
                if not available_retries:
                    print(f"Error in JinaTextFilter: all retries failed")
        return []
    