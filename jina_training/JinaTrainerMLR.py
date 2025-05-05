# import dotenv
# import os
# import json
# from typing import List
# import numpy as np
# import requests

# dotenv.load_dotenv()
# labels = ["Data", "Analysis", "Facts", "Page Metadata", "Promotion", "Clickbait", "Misinformation"]

# JINA_CLASSIFY_BASE_URL = 'https://api.jina.ai/v1/classify'

# class JinaTrainerMLR:
#     def __init__(self, jina_api_key: str=None, jina_base_url: str=JINA_CLASSIFY_BASE_URL):
#         self.jina_api_key = jina_api_key or os.getenv("JINA_API_KEY")
#         self.jina_base_url = jina_base_url
#         self.data = []

#     def load_data(self, path: str = "./value_examples.jsonl"):
#         with open(path, "r", encoding="utf-8") as f:
#             self.data += [json.loads(line.strip()) for line in f if line.strip()]

#     def get_classification(self, texts: List[str]) -> List[List[float]]:
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": "Bearer " + self.jina_api_key
#         }
#         payload = {
#             "model": "jina-embeddings-v3",
#             "input": [
#                 {"text": dict["text"]} for dict in texts
#             ],
#             "labels": labels
#         }
#         response = requests.post(self.jina_base_url, headers=headers, json=payload)
#         response.raise_for_status()
#         return response.json()

#     def train(self) -> List[float]:
#         pass

# if __name__ == "__main__":
#     trainer = JinaTrainerMLR()
#     trainer.load_data()
#     print(len(trainer.data))
#     print(trainer.get_classification(trainer.data[:10])["data"])